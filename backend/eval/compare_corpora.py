import json
from pathlib import Path

from app.rag import search, CORPUS
from eval.run_retrieval import ID_TO_TITLE, QUERY_EN

questions = json.loads(Path("eval/questions.json").read_text(encoding="utf-8"))
rows = []
for q in questions:
    if not q["expected_ids"]:
        continue
    query = QUERY_EN.get(q["id"], q["question"])
    titles = [h["title"] for h in search(query, n_results=30)]
    expected = {ID_TO_TITLE[i] for i in q["expected_ids"]}
    ranks = [titles.index(t) + 1 for t in expected if t in titles]
    rows.append((q["id"], min(ranks) if ranks else 99))

print("corpus", CORPUS)
print(" ".join(f"{i}:{r}" for i, r in rows))
n = len(rows)
print("hit@3", sum(r <= 3 for _, r in rows), "/", n)
print("hit@5", sum(r <= 5 for _, r in rows), "/", n)