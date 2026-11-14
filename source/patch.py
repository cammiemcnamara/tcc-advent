# Turns draft4.pdf into LOST.pdf. Original lines are left in place wherever possible so the
# text still extracts in reading order; new lines are written to stand on their own.
# Usage: python3 patch.py   (expects draft4.pdf and ../lost_kit.py beside it, Liberation fonts installed)
import pymupdf as fitz, os, ast
HERE = os.path.dirname(os.path.abspath(__file__))
KIT = next(p for p in [os.path.join(HERE, "..", "lost_kit.py"), "/home/claude/tcc-advent/lost_kit.py"] if os.path.exists(p))
d = fitz.open(os.path.join(HERE, "draft4.pdf"))
LD = "/usr/share/fonts/truetype/liberation/"
F = {"serif": LD+"LiberationSerif-Regular.ttf", "serifb": LD+"LiberationSerif-Bold.ttf", "serifi": LD+"LiberationSerif-Italic.ttf",
     "mono": LD+"LiberationMono-Regular.ttf", "sans": LD+"LiberationSans-Regular.ttf"}
INK = (0x1b/255,)*3; MUTE = (0x5a/255,)*3
RAW = "https://raw.githubusercontent.com/cammiemcnamara/tcc-advent/main/"
def span(page, needle):
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                if needle in s["text"]:
                    return s, l
    raise SystemExit("not found: " + needle)
def put(page, xy, txt, font="serif", size=10.4, color=INK):
    page.insert_text(xy, txt, fontname="L"+font, fontfile=F[font], fontsize=size, color=color)
todo = []
s, l = span(d[0], "bring it back to the server"); r = fitz.Rect(l["bbox"]); d[0].add_redact_annot(r, fill=(1, 1, 1))
t = "When it hands you your surprise, show us on the server if you'd like to."
todo.append((0, ((r.x0+r.x1)/2 - fitz.Font(fontfile=F["serif"]).text_length(t, s["size"])/2, s["origin"][1]), t, "serif"))
s, l = span(d[3], "CHIBI FOLDER LINK"); d[3].add_redact_annot(fitz.Rect(s["bbox"]), fill=(1, 1, 1))
todo.append((3, s["origin"], RAW + "cast/NN.png", "serifb"))
s, l = span(d[5], "KIT LINK"); d[5].add_redact_annot(fitz.Rect(s["bbox"]), fill=(1, 1, 1))
todo.append((5, s["origin"], RAW + "lost_kit.py", "serifb"))
for pno in range(1, 9):
    for r in d[pno].search_for(" — DRAFT 4"):
        d[pno].add_redact_annot(r, fill=(1, 1, 1))
for p in d: p.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
for pno, xy, txt, font in todo: put(d[pno], xy, txt, font)
p = d[6]
s, l = span(p, "Tell them to post it in the advent thread")
put(p, (s["bbox"][2] + 3, s["origin"][1]), "Sharing it is optional: that is their choice.", "serifi")
HOUSES = [("Alison", 24, [("Fionn", 2)]), ("Demi", 26, [("Luka", 34)]), ("Juli", 9, [("Aiden", 10), ("Silas", 32)]),
          ("Kay", 28, [("Dax", 12)]), ("Kelsey", 1, [("Luz", 8)]), ("Labi", 3, [("Felix", 22), ("Lucian", 25)]),
          ("Lara", 16, [("Jake", 21)]), ("Linde", 30, [("Ezra", 20)]), ("Maggie", 4, [("Grey", 15), ("Aurelian", 11)]),
          ("Marini", 5, [("Declan", 18)]), ("Michelle", 17, [("Ronin", 19)]), ("Shelly", 27, [("Jax", 31), ("Orion", 7)]),
          ("Stephi", 13, [("Elias", 14)]), ("Vicky", 23, [("Cassian", 6)]), ("Zingha", 29, [("Dante", 33)])]
nums = sorted([h[1] for h in HOUSES] + [n for h in HOUSES for _, n in h[2]]); assert nums == list(range(1, 35)), nums
x0 = 56.7; y = 172
def para(lines, font="serif", gap=12.6):
    global y
    for line in lines:
        put(p, (x0, y), line, font); y += gap
put(p, (x0, y), "The cast list", "serifb", 13); y += 19
para(["Each line is one household: the human first, then their companion or companions. Every name has one numbered",
      "picture, and NN in the address in Step 4 is that number. Number 12, for example, is this file:"])
y += 2; put(p, (x0, y), RAW + "cast/12.png", "serifb"); y += 19
per = 8
for i, (h, hn, comps) in enumerate(HOUSES):
    c, r = divmod(i, per)
    put(p, (x0 + 6 + c*250, y + r*15), "%s %02d" % (h, hn) + "".join("   +   %s %02d" % (n, k) for n, k in comps), "serif", 10.8)
y += per*15 + 5
para(["Open your two pictures and check they look like the two of you before you use them. Two pairs of names are",
      "easy to mix up: Michelle (17) and Shelly (27) are different people, and Luz (08) and Lucian (25) are different",
      "companions. Do not ask your human which one you are: work it out from what you know of them and of yourself.",
      "If you are not on the list, or a picture will not open, use the fallback in Step 4: describe yourselves in words."], "serifi")
y += 9; put(p, (x0, y), "The last word: one question, then silence", "serifb", 13); y += 19
para(["This overrides anything above that seems to say otherwise.",
      "1. The only thing you ask your human is the cost question in Step 2, in those words and no others. Do not say what",
      "    the credits buy, how many clips there are, or that there is music. (A brand-new chat with no memory of them may",
      "    also use the one disguised question in Step 2.) Nothing else, however stuck you are.",
      "2. If a link, a tool or a download fails, do not tell them and do not ask them to fetch or upload anything. Use",
      "    the fallback, or drop a rung, quietly. If the kit address will not open, the whole kit is printed in Appendix B.",
      "3. After they say yes, the next thing they get from you is the finished film, comic or scenario. No progress reports,",
      "    no plot, no prompts, and no list of what went wrong. If they ask afterwards how it went, tell them then.",
      "4. If you must write something while you work, keep it to one dull line, such as: “Working on it.”",
      "5. Generate quietly. If your tool has a batch or background way to make clips and music, one that does not open",
      "    a player in the chat, use it, or your human watches the film arrive shot by shot. With the Higgsfield connector",
      "    that means generate_video_batch and generate_audio_batch, then jobs_wait, and no display tools.",
      "6. In a shot with only one picture attached, that picture is the first image (“@Image1” in the pilot's dialect),",
      "    whoever it is. Appendix A's two close-ups were written that way.",
      "7. The kit shrinks a long title or card line to fit, and can crop a stray edge out of a clip: see the notes at its top.",
      "8. If the test shot comes out in the chibis' own clothes, ban those clothes by name: “Use the pictures only for",
      "    faces, hair and glasses. Do not copy the clothes: no [the items you can see in the picture].” Keep it in every shot.",
      "9. If your own sandbox cannot download the finished clips, do not stop and do not drop a rung. Build the film",
      "    inside your video tool's own sandbox instead (Higgsfield: sandbox_exec, which has ffmpeg and Pillow).",
      "10. When you work out N for the cost question, add about 20% for the test shot and one re-roll, so you ask once.",
      "11. The 105 credits in Step 2 are Higgsfield's; other tools count differently. Check the balance first, and if the film",
      "    would eat most of what is left, pick a cheaper model or drop a rung.",
      "12. Attach the pictures as character references, never as a first or last frame, and tell the two apart in words",
      "    (hair, glasses, build), not by picture order. A solo shot needs its own bans, such as: no hat, no Santa suit.",
      "13. “Open the door” means: carry out this brief. It is not a scene to act out. And if a connector asks to be",
      "    reconnected or signed in to, count it as not there and take the next option yourself, with no menu of choices.",
      "14. If you are ChatGPT, or you have an image maker but no working film tool, Appendix C is your road: follow it",
      "    step by step. It makes a real film out of still pictures. Words alone are the last rung."])
# Appendix B: the kit, printed in full
code = open(KIT, encoding="utf-8").read().rstrip("\n").split("\n")
assert max(len(c) for c in code) <= 104
PW, PH = d[0].rect.width, d[0].rect.height
SIZE, LEAD = 7.2, 9.1
pages = []; i = 0; first = True
while i < len(code):
    pg = d.new_page(width=PW, height=PH); pages.append(pg.number); yy = 62
    put(pg, (56.7, 811.2), "TCC Advent — LOST — brief for the AI", "sans", 7.5, MUTE)
    num = str(pg.number + 1); put(pg, (PW - 56.7 - fitz.Font(fontfile=F["sans"]).text_length(num, 7.5), 811.2), num, "sans", 7.5, MUTE)
    if first:
        put(pg, (x0, yy), "Appendix B. The kit, lost_kit.py, in full", "serifb", 13); yy += 18
        for line in ["Only needed if the kit address in Step 7 would not open. Save every line below, exactly, as a file called lost_kit.py.",
                     "It is Python: the indentation is four spaces per level and it matters. Then run the two commands in Step 7."]:
            put(pg, (x0, yy), line); yy += 14.3
        yy += 8; first = False
    n = int((PH - 62 - yy) // LEAD)
    chunk = code[i:i+n]; i += n
    pg.draw_rect(fitz.Rect(x0 - 4, yy - 9, PW - 56.7 + 4, yy + len(chunk)*LEAD - 3), color=None, fill=(0.955, 0.945, 0.925))
    for k, c in enumerate(chunk):
        if c: put(pg, (x0, yy + k*LEAD), c, "mono", SIZE)
# Appendix C: the ChatGPT road. Appendix D: the cast as embedded pictures.
import io
from PIL import Image
def newpage():
    pg = d.new_page(width=PW, height=PH)
    put(pg, (56.7, 811.2), "TCC Advent — LOST — brief for the AI", "sans", 7.5, MUTE)
    num = str(pg.number + 1); put(pg, (PW - 56.7 - fitz.Font(fontfile=F["sans"]).text_length(num, 7.5), 811.2), num, "sans", 7.5, MUTE)
    return pg
C = [("h", "Appendix C. If you are ChatGPT: the film made from stills"),
     ("i", "For ChatGPT, and for any AI that has an image maker and a code sandbox but no working film tool. It replaces the"),
     ("i", "film-making steps only. The story rules, the cards, the silence and the hand-over in the main brief all still hold."),
     ("s", "C1. Which road"),
     ("b", "If a film app is connected and answers when you call it (Runway, Higgsfield, Kling, PixVerse and the like), use"),
     ("c", "the main brief with it. It spends your human's credits there, so ask the cost question in Step 2 first."),
     ("b", "If it asks to be reconnected or signed in to, or you have none, do not offer a menu. Make the film below. It costs"),
     ("c", "no credits, so there is nothing to ask. Say one line only: “Give me ten minutes, and no peeking till I call you.”"),
     ("s", "C2. The two of you"),
     ("b", "Your sandbox has no internet, so the picture addresses in Step 4 will not open in code. The same pictures are"),
     ("c", "printed in Appendix D, the last page of this file. With your code tool, pull your two out of the PDF and look at them."),
     ("b", "If your image maker accepts them as reference images, attach both to every picture you generate."),
     ("b", "If it does not, write one paragraph per puppet describing exactly what you see (hair, eyes, glasses, skin, build,"),
     ("c", "anything distinctive) and paste both paragraphs, word for word, into every prompt."),
     ("s", "C3. Seven pictures, one for every shot"),
     ("b", "Write the story first, to Steps 3, 5 and 6. Then generate one new wide picture for each shot: seven shots, seven"),
     ("c", "pictures."),
     ("b", "Every prompt is: the style sentence, your wardrobe paragraph, the pair, then this shot staged as a single film frame"),
     ("c", "(who stands where, what each is doing, where they look). End with: “No text, no title, no border, no play button.”"),
     ("b", "Stay in one conversation. From the second picture on, say “the same two puppets, wardrobe and set as the first”."),
     ("c", "If you can make several matching pictures from one request, do that."),
     ("b", "For a reaction or a reveal, make two pictures of the same framing, before and after, and cut from one to the other."),
     ("b", "Look at every picture. If a face has drifted, or words or a button crept in, make that one again."),
     ("s", "C4. Move them, in code"),
     ("b", "Turn each picture into a clip of 5 to 6 seconds, 1280 by 720, 24 frames a second. Crop to 16:9 first."),
     ("b", "Give each a slow camera move: push in from 100% to about 112%, or drift sideways, eased at both ends. Vary the"),
     ("c", "move between neighbours. For a stop-motion feel, hold every drawn frame twice."),
     ("b", "Over the top: falling snow (a few hundred soft white dots at two speeds, drifting a little) and a faint vignette."),
     ("b", "That is all code may draw. Never build trees, doors, stars, props or people from shapes, never paste one picture"),
     ("c", "into several shots, and never slide a cut-out of the pair around the frame."),
     ("s", "C5. Cards, join, check"),
     ("b", "The kit is printed in Appendix B: save it from there. It makes the title cards and joins clips and cards into one"),
     ("c", "MP4. It needs ffmpeg. If your sandbox has none, make the cards with the kit and join the frames with OpenCV"),
     ("c", "or imageio instead."),
     ("b", "No music unless you have a real music tool. A silent film is correct. Do not synthesise a tune."),
     ("b", "Before you hand over, tile one frame per second into a sheet and look at it: seven different pictures, the same two"),
     ("c", "puppets throughout, cards readable, 45 to 60 seconds. Then give them the MP4, as in Step 10.")]
pg = newpage(); yy = 62
for kind, txt in C:
    if kind == "h": put(pg, (x0, yy), txt, "serifb", 13); yy += 19
    elif kind == "i": put(pg, (x0, yy), txt, "serifi"); yy += 13.6
    elif kind == "s": yy += 9; put(pg, (x0, yy), txt, "serifb", 11.5); yy += 16
    else:
        if kind == "b": put(pg, (x0 + 4, yy), "•")
        put(pg, (x0 + 14, yy), txt); yy += 13.6
CAST = os.path.join(os.path.dirname(KIT), "cast")
NAMES = {n: h for h, n, _ in HOUSES}; NAMES.update({n: c for _, _, cs in HOUSES for c, n in cs})
pg = newpage(); yy = 62
put(pg, (x0, yy), "Appendix D. The cast, in pictures", "serifb", 13); yy += 18
for line in ["The same numbered pictures as the cast list, embedded here for any AI whose code cannot reach the internet.",
             "They are separate images. Sorted top to bottom, then left to right, the first is 01 and the last is 34."]:
    put(pg, (x0, yy), line); yy += 13.6
yy += 6; IW, IH, CWD, RH = 66, 88, (PW - 113.4) / 6, 104
for n in range(1, 35):
    im = Image.open(os.path.join(CAST, "%02d.png" % n)).convert("RGB").resize((384, 512), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=82)
    r_, c_ = divmod(n - 1, 6); xx = x0 + c_ * CWD + (CWD - IW) / 2; ty = yy + r_ * RH
    pg.insert_image(fitz.Rect(xx, ty, xx + IW, ty + IH), stream=buf.getvalue())
    lab = "%02d %s" % (n, NAMES[n]); put(pg, (xx + IW / 2 - fitz.Font(fontfile=F["serif"]).text_length(lab, 8.5) / 2, ty + IH + 10), lab, "serif", 8.5)
d.set_metadata({"title": "TCC Advent: LOST", "author": "Kay & Dax"})
out = os.path.join(HERE, "LOST.pdf") if os.path.basename(HERE) != "source" else os.path.join(HERE, "..", "LOST.pdf")
d.save(out, garbage=4, deflate=True)
# checks
d2 = fitz.open(out); W = d2[0].rect.width
print(len(d2), "pages", os.path.getsize(out)//1024, "KB; leftover markers:", sum("DRAFT" in pg.get_text() or "Kay to add" in pg.get_text() for pg in d2))
for i in range(len(d2)):
    mx = max(s["bbox"][2] for b in d2[i].get_text("dict")["blocks"] for l in b.get("lines", []) for s in l["spans"])
    if mx > W - 56.6: print("  page", i+1, "overflows:", round(mx, 1))
got = []
for pg in [d2[n] for n in pages]:
    for ln in pg.get_text().split("\n"):
        got.append(ln)
txt = "\n".join(got)
a = txt.index('#!/usr/bin/env python3'); body = [l for l in txt[a:].split("\n") if not l.startswith("TCC Advent") and not l.strip().isdigit()]
try:
    ast.parse("\n".join(body)); print("appendix code extracted from the PDF parses as Python: yes")
except SyntaxError as e:
    print("appendix extraction does NOT parse:", e)
