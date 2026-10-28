import json
import sys

with open(sys.argv[1], encoding="utf-8") as f:
    data = json.load(f)

counts = {"OK": 0, "PARTIAL": 0, "NO": 0}
answers = 0
answers_with_no = 0
for qid, sentences in data.items():
    if isinstance(sentences, dict):  # {"error": ...}
        print(qid, "ignoré (erreur)")
        continue
    answers += 1
    labels = [s["label"] for s in sentences]
    for label in labels:
        counts[label] = counts.get(label, 0) + 1
    if "NO" in labels:
        answers_with_no += 1

total = sum(counts.values())
print("réponses jugées:", answers)
print("phrases jugées:", total, counts)
print("réponses avec au moins une phrase NO:", answers_with_no)