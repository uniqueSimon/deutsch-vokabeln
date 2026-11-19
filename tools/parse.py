#!/usr/bin/env python3
"""entries.json -> words.json (id, de, article, plural, forms, note, ex[], letter)."""
import json, re
raw = json.load(open("tools/entries.json"))
out = []
for e in raw:
    r = e["raw"].strip()
    if re.fullmatch(r"[A-ZÄÖÜ]", r) or r.startswith("Ihre Notizen") or not r:
        continue
    note = ""
    m = re.search(r"\s*(\((?:D|A|CH|D, A|A, CH|D, CH)[^)]*\).*|→.*)$", r)
    if m:
        note = m.group(1).strip(); r = r[:m.start()].strip()
    art = ""
    m = re.match(r"^(\S+?)(der|die|das) (\S+)$", r)
    if m and m.group(1)[:1].isupper():
        r = m.group(2) + " " + m.group(3)
    m = re.match(r"^(der/die/das|der/die|die/der|die/das|das/der|das/die|der|die|das)\s+(.*)$", r)
    if m:
        art, r = m.group(1), m.group(2)
    reflexive = False
    if re.match(r"^sich\s", r):
        reflexive = True
    parts = [p.strip() for p in r.split(",")]
    de = parts[0]
    rest = ", ".join(parts[1:]).strip()
    kind = "noun" if art else ("verb" if re.search(r"\b(hat|ist|hat/ist|ist/hat)\s+\S+", rest) or (rest and re.search(r"(hat|ist) ", rest)) else "other")
    if kind == "other" and re.search(r"(en|ln|rn)$", de) and rest.count(",") >= 1 and not rest.startswith(("-", "¨")): kind = "verb"
    if reflexive and kind != "verb" and rest: kind = "verb"
    w = {"de": de, "kind": kind, "art": art, "extra": rest, "note": note, "ex": e["ex"], "sub": e["indent"]}
    out.append(w)
for i, w in enumerate(out):
    w["id"] = i + 1
    w["letter"] = re.sub(r"^[^A-Za-zÄÖÜäöü]+", "", w["de"].replace("sich ", ""))[:1].upper() or "?"
json.dump(out, open("tools/words.json", "w"), ensure_ascii=False, indent=0)
from collections import Counter
print(len(out), Counter(w["kind"] for w in out), sum(1 for w in out if not w["ex"]))
for w in out:
    if not w["ex"] or w["kind"]=="other" and w["extra"]: print(w)
