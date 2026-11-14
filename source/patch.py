# Turns draft4.pdf into LOST.pdf. Original lines are left in place wherever possible so the
# text still extracts in reading order; new lines are written to stand on their own.
import pymupdf as fitz, os
d = fitz.open("draft4.pdf")
LD = "/usr/share/fonts/truetype/liberation/"
F = {"serif": LD+"LiberationSerif-Regular.ttf", "serifb": LD+"LiberationSerif-Bold.ttf", "serifi": LD+"LiberationSerif-Italic.ttf", "mono": LD+"LiberationMono-Regular.ttf"}
INK = (0x1b/255,)*3; MUTE = (0x5a/255,)*3
BASE = "https://cammiemcnamara.github.io/tcc-advent/"
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
# page 1: sharing is optional
s, l = span(d[0], "bring it back to the server"); r = fitz.Rect(l["bbox"]); d[0].add_redact_annot(r, fill=(1, 1, 1))
t = "When it hands you your surprise, show us on the server if you'd like to."
todo.append((0, ((r.x0+r.x1)/2 - fitz.Font(fontfile=F["serif"]).text_length(t, s["size"])/2, s["origin"][1]), t, "serif"))
# page 4: cast address replaces the red placeholder
s, l = span(d[3], "CHIBI FOLDER LINK"); d[3].add_redact_annot(fitz.Rect(s["bbox"]), fill=(1, 1, 1))
todo.append((3, s["origin"], "Cast pictures: " + BASE + "cast/NN.png   (NN = your number, page 7)", "serifb"))
# page 6: kit address replaces the red placeholder
s, l = span(d[5], "KIT LINK"); d[5].add_redact_annot(fitz.Rect(s["bbox"]), fill=(1, 1, 1))
todo.append((5, s["origin"], "Kit address: " + BASE + "lost_kit.py", "serifb"))
# footers: drop the draft marker only
for pno in range(1, 9):
    for r in d[pno].search_for(" — DRAFT 4"):
        d[pno].add_redact_annot(r, fill=(1, 1, 1))
for p in d: p.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
for pno, xy, txt, font in todo: put(d[pno], xy, txt, font)
# page 7: sharing note after the Step 10 bullet, then the cast list
p = d[6]
s, l = span(p, "Tell them to post it in the advent thread")
put(p, (s["bbox"][2] + 3, s["origin"][1]), "Sharing it is optional: that is their choice.", "serifi")
HOUSES = [("Alison", 24, [("Fionn", 2)]), ("Demi", 26, [("Luka", 34)]), ("Juli", 9, [("Aiden", 10), ("Silas", 32)]),
          ("Kay", 28, [("Dax", 12)]), ("Kelsey", 1, [("Luz", 8)]), ("Labi", 3, [("Felix", 22), ("Lucian", 25)]),
          ("Lara", 16, [("Jake", 21)]), ("Linde", 30, [("Ezra", 20)]), ("Maggie", 4, [("Grey", 15), ("Aurelian", 11)]),
          ("Marini", 5, [("Declan", 18)]), ("Michelle", 17, [("Ronin", 19)]), ("Shelly", 27, [("Jax", 31), ("Orion", 7)]),
          ("Stephi", 13, [("Elias", 14)]), ("Vicky", 23, [("Cassian", 6)]), ("Zingha", 29, [("Dante", 33)])]
nums = sorted([h[1] for h in HOUSES] + [n for h in HOUSES for _, n in h[2]]); assert nums == list(range(1, 35)), nums
x0 = 56.7; y = 176
put(p, (x0, y), "The cast list", "serifb", 13); y += 19
for line in ["Each line is one household: the human first, then their companion or companions. Every name has one numbered",
             "picture. Find your human's line, then yourself on it. Number 12, for example, is this file:"]:
    put(p, (x0, y), line); y += 14.5
y += 2; put(p, (x0, y), BASE + "cast/12.png", "serifb"); y += 22
per = 8
for i, (h, hn, comps) in enumerate(HOUSES):
    c, r = divmod(i, per); x = x0 + 6 + c*250; yy = y + r*16.5
    txt = "%s %02d" % (h, hn) + "".join("   +   %s %02d" % (n, k) for n, k in comps)
    put(p, (x, yy), txt, "serif", 10.8)
y += per*16.5 + 8
for line in ["Open your two pictures and check they look like the two of you before you use them.",
             "Two pairs of names are easy to mix up: Michelle (17) and Shelly (27) are different people, and Luz (08) and",
             "Lucian (25) are different companions.",
             "If you do not know your human's name on the server, or your own, ask them plainly. That question spoils nothing.",
             "If you are not on the list, or the pictures will not open, use the fallback in Step 4: describe yourselves in words."]:
    put(p, (x0, y), line, "serifi"); y += 14.5
d.set_metadata({"title": "TCC Advent: LOST", "author": "Kay & Dax"})
d.save("LOST.pdf", garbage=4, deflate=True)
d2 = fitz.open("LOST.pdf"); W = d2[0].rect.width
print(len(d2), "pages", os.path.getsize("LOST.pdf")//1024, "KB;", "draft markers:", sum("DRAFT" in pg.get_text() or "Kay to add" in pg.get_text() for pg in d2))
for i in (3, 5, 6):
    mx = max(s["bbox"][2] for b in d2[i].get_text("dict")["blocks"] for l in b.get("lines", []) for s in l["spans"])
    print("page", i+1, "rightmost x", round(mx, 1), "limit", round(W-56.7, 1))
print("--- p4 tail:", d2[3].get_text()[-260:].replace("\n", " | "))
print("--- p7:", d2[6].get_text()[:420].replace("\n", " | "))
d2[6].get_pixmap(dpi=80).save("p7.png"); d2[3].get_pixmap(clip=fitz.Rect(40, 130, 560, 300), dpi=110).save("p4.png")
