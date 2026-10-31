import json
import sys

OLD = "data/podiatry_dataset_v2.json"
OUT = "data/rewritten/podiatry_dataset_own.json"
CONTENT = ["overview", "pathophysiology", "symptoms", "causes", "risk_factors",
           "diagnosis", "differential_diagnosis", "treatment", "when_to_see_a_doctor"]

old = {x["id"]: x for x in json.load(open(OLD, encoding="utf-8"))}
try:
    out = {x["id"]: x for x in json.load(open(OUT, encoding="utf-8"))}
except FileNotFoundError:
    out = {}

for path in sys.argv[1:]:
    for fiche in json.load(open(path, encoding="utf-8")):
        fid = fiche["id"]
        if fid not in old:
            raise SystemExit("STOP: unknown id " + fid)
        missing = [k for k in CONTENT if not fiche.get(k)]
        if missing:
            raise SystemExit("STOP: " + fid + " has empty fields " + str(missing))
        new = dict(old[fid])
        for k in CONTENT:
            new[k] = fiche[k]
        src = old[fid]["source"]
        name = src["name"] if src["name"].startswith("Reference:") else "Reference: " + src["name"]
        new["source"] = {"name": name, "url": src["url"]}
        out[fid] = new
        print(fid, "|", new["title"], "|", new["category"])

json.dump(list(out.values()), open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(len(out), "fiches written to", OUT)