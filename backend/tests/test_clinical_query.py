from app import agent


def run_with(monkeypatch, clinical_text):
    seen = {}

    def fake_search(query, n_results=5):
        seen["query"] = query
        return []

    monkeypatch.setattr(agent, "to_english", lambda text: "heel pain")
    monkeypatch.setattr(agent, "to_clinical", lambda text: clinical_text)
    monkeypatch.setattr(agent, "search", fake_search)
    agent.search_knowledge_base("douleur au talon", [])
    return seen["query"]


def test_clinical_terms_are_appended(monkeypatch):
    assert run_with(monkeypatch, "calcaneus") == "heel pain calcaneus"


def test_empty_clinical_falls_back_to_english_query(monkeypatch):
    assert run_with(monkeypatch, "") == "heel pain"