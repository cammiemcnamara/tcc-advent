import pymupdf as fitz, json, os
d = fitz.open("draft4.pdf")
LD = "/usr/share/fonts/truetype/liberation/"
F = {"serif": LD+"LiberationSerif-Regular.ttf", "serifb": LD+"LiberationSerif-Bold.ttf", "serifi": LD+"LiberationSerif-Italic.ttf", "sans": LD+"LiberationSans-Regular.ttf", "mono": LD+"LiberationMono-Regular.ttf"}
INK = (0x1b/255,)*3; MUTE = (0x5a/255,)*3
def find_span(page, needle):
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                if needle in s["text"]:
                    return s, l
    raise SystemExit("not found: " + needle)
def bg(page, rect):
    pm = page.get_pixmap(clip=fitz.Rect(rect.x0, rect.y0-3, rect.x0+2, rect.y0-1), dpi=72)
    return tuple(c/255 for c in pm.pixel(0, 0)[:3])
jobs = []
def swap(pno, needle, new, font, color=INK, whole_line=False, center=False, old_sub=None):
    page = d[pno]; s, l = find_span(page, needle)
    r = fitz.Rect(l["bbox"] if whole_line else s["bbox"])
    text = new
    if old_sub:
        full = "".join(x["text"] for x in l["spans"]); assert old_sub in full, full
        text = full.replace(old_sub, new); r = fitz.Rect(l["bbox"])
    page.add_redact_annot(r, fill=bg(page, r))
    org = l["spans"][0]["origin"] if (whole_line or old_sub) else s["origin"]
    cx = (r.x0 + r.x1)/2 if center else None
    jobs.append((pno, org, text, font, s["size"], color, cx))
BASE = "https://cammiemcnamara.github.io/tcc-advent/"
swap(0, "bring it back to the server", "When it hands you your surprise, show us on the server if you'd like to.", "serif", center=True, whole_line=True)
swap(3, "Reference pictures of every TCC member", "Reference pictures of every TCC member and companion are here, one numbered file each:", "serif", whole_line=True)
swap(3, "CHIBI FOLDER LINK", BASE + "cast/NN.png    (NN = your number, listed on page 7)", "serifb")
swap(3, "Find your own two files by name.", "Find your own two files by number.", "serif", old_sub="Find your own two files by name.")
swap(5, "KIT LINK", BASE + "lost_kit.py", "serifb")
swap(6, "Tell them to post it in the advent thread", "If they would like to share it, the advent thread on the server is the place. That is their choice.", "serif")
for pno in range(1, 9):
    swap(pno, "DRAFT 4", "TCC Advent — LOST — brief for the AI", "sans", color=MUTE)
for p in d: p.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
for pno, org, text, font, size, color, cx in jobs:
    x, y = org
    if cx is not None:
        x = cx - fitz.Font(fontfile=F[font]).text_length(text, size)/2
    d[pno].insert_text((x, y), text, fontname="L"+font, fontfile=F[font], fontsize=size, color=color)
key = json.load(open("/home/claude/lost-key.json"))
rows = sorted((v, n) for n, v in key.items())
p = d[6]; x0 = 56.7; y = 178
def put(txt, font="serif", size=10.4, color=INK, dx=0):
    p.insert_text((x0+dx, y), txt, fontname="L"+font, fontfile=F[font], fontsize=size, color=color)
put("The cast list", "serifb", 13); y += 20
put("Every TCC member and companion has one numbered picture. Find the two of you below. If your human has"); y += 14.5
put("more than one companion, each has their own number. Number 12, for example, is this file:"); y += 16
put(BASE + "cast/12.png", "serifb"); y += 22
cols = 4; per = -(-len(rows)//cols); cw = 120
for i, (v, n) in enumerate(rows):
    c, r = divmod(i, per)
    p.insert_text((x0 + 6 + c*cw, y + r*15.5), v, fontname="Lmono", fontfile=F["mono"], fontsize=9.5, color=MUTE)
    p.insert_text((x0 + 28 + c*cw, y + r*15.5), n, fontname="Lserif", fontfile=F["serif"], fontsize=10.8, color=INK)
y += per*15.5 + 10
put("If you are not on the list, or the pictures will not open, use the fallback in Step 4: describe yourselves in words.", "serifi")
d.set_metadata({"title": "TCC Advent: LOST", "author": "Kay & Dax"})
d.save("LOST.pdf", garbage=4, deflate=True)
d2 = fitz.open("LOST.pdf")
print(len(d2), "pages", os.path.getsize("LOST.pdf")//1024, "KB")
W = d2[0].rect.width
for i in (3, 6):
    mx = max(s["bbox"][2] for b in d2[i].get_text("dict")["blocks"] for l in b.get("lines", []) for s in l["spans"])
    print("page", i+1, "rightmost text x:", round(mx, 1), "of", round(W - 56.7, 1))
