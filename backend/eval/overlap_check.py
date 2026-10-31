import json
import re
import sys


def words(text):
    return re.findall(r"[a-z0-9']+", text.lower())


def parts(f):
    out = [f["overview"], f["pathophysiology"], f["diagnosis"], f["when_to_see_a_doctor"]]
    for k in ("symptoms", "causes", "risk_factors", "differential_diagnosis", "treatment"):
        out.extend(f[k])
    return out


def shared_runs(a, grams, n):
    runs, i = [], 0
    while i <= len(a) - n:
        if tuple(a[i:i + n]) in grams:
            j = i + n
            while j < len(a) and tuple(a[j - n + 1:j + 1]) in grams:
                j += 1
            runs.append(" ".join(a[i:j]))
            i = j
        else:
            i += 1
    return runs


dataset, fid, source_path = sys.argv[1], sys.argv[2], sys.argv[3]
n = int(sys.argv[4]) if len(sys.argv) > 4 else 6
fiche = next(x for x in json.load(open(dataset, encoding="utf-8")) if x["id"] == fid)
src = words(open(source_path, encoding="utf-8").read())
grams = {tuple(src[i:i + n]) for i in range(len(src) - n + 1)}

total, covered, found = 0, 0, []
for p in parts(fiche):
    w = words(p)
    total += len(w)
    for run in shared_runs(w, grams, n):
        covered += len(run.split())
        found.append(run)

print(fid, "| words:", total, "| words in shared runs of", n, "+:", covered,
      "(" + str(round(100 * covered / max(total, 1), 1)) + " %)")
for r in found:
    print("  -", r)