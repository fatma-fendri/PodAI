from app import agent

HITS = [
    {"title": "A", "source_url": "u1", "distance": 0.5, "document": "doc A"},
    {"title": "B", "source_url": "u2", "distance": 0.6, "document": "doc B"},
    {"title": "far", "source_url": "u3", "distance": 1.9, "document": "doc far"},
]


def _patch(monkeypatch):
    monkeypatch.setattr(agent, "to_english", lambda q: q)
    monkeypatch.setattr(agent, "to_clinical", lambda q: "")
    monkeypatch.setattr(agent, "add_source", lambda sources, title, url, origin: 1)


def test_reranker_off_by_default(monkeypatch):
    _patch(monkeypatch)
    monkeypatch.delenv("PODAI_RERANK", raising=False)
    calls = {}

    def fake_search(q, n_results=3):
        calls["n"] = n_results
        return HITS

    monkeypatch.setattr(agent, "search", fake_search)
    agent.search_knowledge_base("heel pain", [])
    assert calls["n"] == 5


def test_reranker_on_reorders_and_keeps_distance_filter(monkeypatch):
    _patch(monkeypatch)
    monkeypatch.setenv("PODAI_RERANK", "1")
    calls = {}

    def fake_search(q, n_results=3):
        calls["n"] = n_results
        return HITS

    def fake_rerank(question, hits, n_results):
        calls["titles"] = [h["title"] for h in hits]
        return list(reversed(hits))[:n_results]

    monkeypatch.setattr(agent, "search", fake_search)
    monkeypatch.setattr(agent, "rerank", fake_rerank)
    result = agent.search_knowledge_base("heel pain", [])
    assert calls["n"] == 10
    assert calls["titles"] == ["A", "B"]  # the far hit is removed before reranking
    assert result.index("doc B") < result.index("doc A")