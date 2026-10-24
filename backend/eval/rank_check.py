import json
from pathlib import Path

from app.rag import search
from eval.run_retrieval import ID_TO_TITLE, QUERY_EN

questions = json.loads(Path("eval/questions.json").read_text(encoding="utf-8"))

for q in questions:
    if q["expected_behavior"] != "kb":
        continue
    query = QUERY_EN.get(q["id"], q["question"])
    titles = [h["title"] for h in search(query, n_results=15)]
    expected = {ID_TO_TITLE[i] for i in q["expected_ids"]}
    ranks = [titles.index(t) + 1 for t in expected if t in titles]
    print(q["id"], "rank", min(ranks))