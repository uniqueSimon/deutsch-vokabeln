#!/usr/bin/env python3
"""Extracts the alphabetical B1 word list from the PDF into tools/entries.json."""
import json, re, sys, warnings
warnings.filterwarnings("ignore")
import pymupdf

PDF = "Goethe-Zertifikat_B1_Wortliste.pdf"
doc = pymupdf.open(PDF)

def lines_of(page):
    out = []
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            t = "".join(s["text"] for s in l["spans"]).strip()
            x0, y0 = l["bbox"][0], l["bbox"][1]
            if t and 80 < y0 < 790:
                out.append((x0, y0, t))
    return out

def cluster(ls, gap=14):
    groups = []
    for x, y, t in sorted(ls, key=lambda a: a[1]):
        if groups and y - groups[-1][-1][1] <= gap:
            groups[-1].append((x, y, t))
        else:
            groups.append([(x, y, t)])
    return groups

def join(parts):
    s = ""
    for p in parts:
        s = s[:-1] + p if s.endswith("-") and p[:1].islower() and not s.endswith(" -") else (s + " " + p if s else p)
    return s.strip()

entries = []
started = False
for pno in range(len(doc)):
    page = doc[pno]
    txt = page.get_text()
    if "WORTLISTE" not in txt:
        continue
    ls = lines_of(page)
    if not ls:
        continue
    if not started:
        if not any(t.startswith("Achtung!") or t == "Abend" for _, _, t in ls) and pno < 15:
            continue
        started = True
    for lo, hi, ex_lo in ((0, 300, 128), (300, 600, 405)):
        col = [l for l in ls if lo <= l[0] < hi]
        ent = [l for l in col if l[0] < ex_lo]
        exs = [l for l in col if l[0] >= ex_lo]
        eg = cluster(ent)
        for i, g in enumerate(eg):
            y0 = g[0][1] - 3
            y1 = eg[i + 1][0][1] - 3 if i + 1 < len(eg) else 9999
            sents, cur = [], None
            for x, y, t in sorted((e for e in exs if y0 <= e[1] < y1), key=lambda a: a[1]):
                if re.match(r"^\d\.\s", t):
                    cur = [t[2:].strip()]; sents.append(cur)
                elif cur is not None and x - ex_lo > 5 and not re.match(r"^\d\.", t):
                    cur.append(t)
                else:
                    cur = [t]; sents.append(cur)
            entries.append({
                "raw": join([t for _, _, t in g]),
                "indent": g[0][0] - (35 if lo == 0 else 315) > 10,
                "ex": [join(s) for s in sents],
                "page": pno + 1,
            })
json.dump(entries, open("tools/entries.json", "w"), ensure_ascii=False, indent=0)
print(len(entries))
