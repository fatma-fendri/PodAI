import json
import sys

PATTERNS = [
    "classic for",
    "characteristic of",
    "most consistent with",
    "typical of",
    "are typical of",
    "fits the pattern of",
    "commonly associated with",
    "is typically a",
    "sounds like",
    "est typiquement",
    "est typique",
    "typisch",
]

with open(sys.argv[1], encoding="utf-8") as f:
    results = json.load(f)

flagged = 0
for r in results:
    texte = r["answer"].lower()
    trouve = [p for p in PATTERNS if p in texte]
    if trouve:
        flagged += 1
        print(r["id"], trouve)

print(flagged, "réponses sur", len(results))