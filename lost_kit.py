#!/usr/bin/env python3
"""
lost_kit.py - helper for the TCC advent silent film (Kay & Dax, Nov 2026).
Needs: Python 3, Pillow (pip install pillow), and ffmpeg on the PATH.

1) Make title cards (black, cream italic serif, double border), 1280x720 PNG:
     python lost_kit.py cards cards.json out_dir
   cards.json is a list. Each entry is one card:
     {"file": "c0.png", "title": "LOST", "subtitle": "a winter's tale"}
     {"file": "c1.png", "lines": ["\u201cDax, what\u2019s that?\u201d"]}
     {"file": "c7.png", "big": "Fin"}

2) Stitch clips + cards (+ optional music) into one MP4:
     python lost_kit.py stitch manifest.json film.mp4
   manifest.json:
     {"music": "music.mp3",
      "items": [{"card": "out_dir/c0.png", "seconds": 3.2},
                {"clip": "shot1.mp4", "seconds": 4.0},
                {"card": "out_dir/c1.png", "seconds": 2.2}]}
   "seconds" on a clip trims it (optional). "music" is optional.
   A clip may also carry "crop": an ffmpeg crop expression applied before scaling, for
   cutting a stray edge out of a shot, e.g. {"clip": "shot6.mp4", "crop": "iw*0.9:ih:0:0"}.

Long titles and long card lines are shrunk automatically until they fit inside the border.
"""
import json, os, random, subprocess, sys, tempfile

W, H = 1280, 720
CREAM = (236, 226, 204)
BLACK = (8, 8, 8)
FONT_DIRS = ["/usr/share/fonts", "/usr/local/share/fonts", "/Library/Fonts",
             "/System/Library/Fonts", "C:/Windows/Fonts", os.path.expanduser("~/.fonts")]
ITALIC = ["LiberationSerif-Italic.ttf", "DejaVuSerif-Italic.ttf", "Georgiai.ttf", "georgiai.ttf",
          "Times New Roman Italic.ttf", "timesi.ttf", "FreeSerifItalic.ttf"]
BOLD = ["LiberationSerif-Bold.ttf", "DejaVuSerif-Bold.ttf", "Georgiab.ttf", "georgiab.ttf",
        "Times New Roman Bold.ttf", "timesbd.ttf", "FreeSerifBold.ttf"]


def find_font(names):
    for d in FONT_DIRS:
        for root, _, files in os.walk(d):
            for n in names:
                if n in files:
                    return os.path.join(root, n)
    return None


def font(names, size):
    from PIL import ImageFont
    p = find_font(names)
    if p:
        return ImageFont.truetype(p, size)
    try:
        return ImageFont.load_default(size)   # Pillow 10.1+
    except TypeError:
        return ImageFont.load_default()


def fit(names, size, text, max_w=W - 200):
    """Largest font at or below `size` that keeps `text` inside the border."""
    f = font(names, size)
    while size > 24 and hasattr(f, "getlength") and f.getlength(text) > max_w:
        size -= 4
        f = font(names, size)
    return f


def make_card(spec, out_dir):
    from PIL import Image, ImageDraw, ImageFilter
    img = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(img)
    d.rectangle([40, 40, W - 40, H - 40], outline=CREAM, width=3)
    d.rectangle([54, 54, W - 54, H - 54], outline=CREAM, width=1)
    for x, y in [(40, 40), (W - 40, 40), (40, H - 40), (W - 40, H - 40)]:
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=BLACK, outline=CREAM, width=2)
    if "title" in spec:
        d.text((W // 2, H // 2 - 30), spec["title"], font=fit(BOLD, 190, spec["title"]), fill=CREAM,
               anchor="mm")
        if spec.get("subtitle"):
            d.text((W // 2, H // 2 + 120), spec["subtitle"], font=fit(ITALIC, 40, spec["subtitle"]),
                   fill=CREAM, anchor="mm")
    elif "big" in spec:
        d.text((W // 2, H // 2), spec["big"], font=fit(ITALIC, 150, spec["big"]), fill=CREAM,
               anchor="mm")
    else:
        lines = spec["lines"]
        size = 64 if max(len(l) for l in lines) <= 30 else 52
        f = fit(ITALIC, size, max(lines, key=len))
        step = size + 18
        y = H // 2 - (len(lines) * step) // 2 + size // 2
        for ln in lines:
            d.text((W // 2, y), ln, font=f, fill=CREAM, anchor="mm")
            y += step
    random.seed(7)                      # light film grain
    px = img.load()
    for _ in range(9000):
        x, y = random.randrange(W), random.randrange(H)
        v = random.randrange(18, 60)
        px[x, y] = (v, v, max(v - 4, 0))
    img = img.filter(ImageFilter.GaussianBlur(0.4))
    path = os.path.join(out_dir, spec["file"])
    img.save(path)
    return path


def cmd_cards(spec_file, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for spec in json.load(open(spec_file, encoding="utf-8")):
        print("card:", make_card(spec, out_dir))


def run(args):
    subprocess.run(args, check=True)


def cmd_stitch(manifest_file, out_file):
    m = json.load(open(manifest_file, encoding="utf-8"))
    vf = ("scale=%d:%d:force_original_aspect_ratio=decrease,pad=%d:%d:(ow-iw)/2:(oh-ih)/2,"
          "fps=24,format=yuv420p,setsar=1") % (W, H, W, H)
    tmp = tempfile.mkdtemp(prefix="lostkit_")
    parts = []
    for i, it in enumerate(m["items"]):
        part = os.path.join(tmp, "p%03d.mp4" % i)
        if "card" in it:
            s = float(it.get("seconds", 2.5))
            fade = "fade=t=in:st=0:d=0.3,fade=t=out:st=%.2f:d=0.3" % (s - 0.3)
            run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-t", str(s), "-i", it["card"],
                 "-vf", vf + "," + fade, "-c:v", "libx264", "-crf", "18", "-preset", "fast", part])
        else:
            a = ["ffmpeg", "-y", "-v", "error", "-i", it["clip"]]
            if "seconds" in it:
                a += ["-t", str(it["seconds"])]
            cvf = ("crop=%s," % it["crop"] if it.get("crop") else "") + vf
            run(a + ["-an", "-vf", cvf, "-c:v", "libx264", "-crf", "18", "-preset", "fast", part])
        parts.append(part)
    lst = os.path.join(tmp, "list.txt")
    with open(lst, "w") as f:
        for p in parts:
            f.write("file '%s'\n" % p)
    pic = os.path.join(tmp, "picture.mp4")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst,
         "-c:v", "libx264", "-crf", "21", "-pix_fmt", "yuv420p", pic])
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                         "-of", "csv=p=0", pic]).decode().strip())
    if m.get("music"):
        af = ("[1:a]atrim=0:%.2f,loudnorm=I=-16:TP=-1.5,afade=t=in:st=0:d=0.6,"
              "afade=t=out:st=%.2f:d=2[a]") % (dur, max(dur - 2, 0))
        run(["ffmpeg", "-y", "-v", "error", "-i", pic, "-stream_loop", "-1", "-i", m["music"],
             "-filter_complex", af, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac",
             "-b:a", "192k", "-t", "%.2f" % dur, "-movflags", "+faststart", out_file])
    else:
        run(["ffmpeg", "-y", "-v", "error", "-i", pic, "-c", "copy", "-movflags", "+faststart",
             out_file])
    print("film: %s (%.1f seconds)" % (out_file, dur))


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "cards":
        cmd_cards(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 4 and sys.argv[1] == "stitch":
        cmd_stitch(sys.argv[2], sys.argv[3])
    else:
        print(__doc__)
        sys.exit(1)
