from app import rag


class FakeRanker:
    def rerank(self, request):
        return list(reversed(request.passages))


def test_search_reranked_reorders_and_truncates(monkeypatch):
    hits = [{"title": t, "distance": d, "document": t}
            for t, d in [("A", 0.5), ("B", 0.6), ("C", 0.7)]]
    monkeypatch.setattr(rag, "search", lambda q, n_results=3: hits)
    monkeypatch.setattr(rag, "get_ranker", lambda: FakeRanker())
    result = rag.search_reranked("q", n_results=2, n_candidates=3)
    assert [h["title"] for h in result] == ["C", "B"]