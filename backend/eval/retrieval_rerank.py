import json
from app.rag import search, rerank

QUESTIONS = "eval/questions.json"
DATASET = "data/podiatry_dataset_v2.json"  # sert seulement à relier un titre à un id

title_to_id = {f["title"]: f["id"] for f in json.load(open(DATASET, encoding="utf-8"))}
questions = [q for q in json.load(open(QUESTIONS, encoding="utf-8"))
             if q["expected_behavior"] == "kb" and q["language"] == "en"]


def rank_of(expected, hits):
    ids = [title_to_id.get(h["title"]) for h in hits]
    for pos, i in enumerate(ids, start=1):
        if i in expected:
            return pos
    return None


def show(r):
    return "-" if r is None else str(r)


base_ranks, rr_ranks = [], []
for q in questions:
    candidates = search(q["question"], n_results=10)
    base = rank_of(q["expected_ids"], candidates)
    reranked = rerank(q["question"], candidates, 10)
    rr = rank_of(q["expected_ids"], reranked)
    base_ranks.append(base)
    rr_ranks.append(rr)
    flag = "" if base == rr else "  <-- change"
    print(q["id"], q["expected_ids"], "sans:", show(base), "| avec:", show(rr), flag)


def hit(ranks, k):
    return sum(1 for r in ranks if r is not None and r <= k)


n = len(questions)
print("\nQuestions:", n)
for k in (1, 3, 5):
    print("hit@" + str(k), "-> sans reranker:", hit(base_ranks, k), "/", n,
          "| avec reranker:", hit(rr_ranks, k), "/", n)
print("Absente du top 10 (le reranker ne peut rien y faire):",
      sum(1 for r in base_ranks if r is None))