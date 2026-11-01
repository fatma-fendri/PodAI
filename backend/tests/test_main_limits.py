import httpx
from fastapi.testclient import TestClient
from groq import RateLimitError

from app import main
from app.limits import DailyLimiter

client = TestClient(main.app)
QUESTION = {"question": "heel pain in the morning"}


def fake_agent(question):
    return {"answer": "ok", "sources": []}


def test_visitor_limit_returns_429(monkeypatch):
    monkeypatch.setattr(main, "agent_answer", fake_agent)
    monkeypatch.setattr(main, "limiter", DailyLimiter(per_visitor=2, total=0))
    assert client.post("/ask", json=QUESTION).status_code == 200
    assert client.post("/ask", json=QUESTION).status_code == 200
    response = client.post("/ask", json=QUESTION)
    assert response.status_code == 429
    assert "daily limit of questions" in response.json()["detail"]


def test_total_limit_returns_429(monkeypatch):
    monkeypatch.setattr(main, "agent_answer", fake_agent)
    monkeypatch.setattr(main, "limiter", DailyLimiter(per_visitor=0, total=1))
    assert client.post("/ask", json=QUESTION).status_code == 200
    response = client.post("/ask", json=QUESTION)
    assert response.status_code == 429
    assert "daily capacity" in response.json()["detail"]


def test_no_limit_by_default(monkeypatch):
    monkeypatch.setattr(main, "agent_answer", fake_agent)
    monkeypatch.setattr(main, "limiter", DailyLimiter())
    assert all(client.post("/ask", json=QUESTION).status_code == 200 for _ in range(20))


def test_limit_blocks_before_calling_the_agent(monkeypatch):
    calls = []

    def counting_agent(question):
        calls.append(question)
        return {"answer": "ok", "sources": []}

    monkeypatch.setattr(main, "agent_answer", counting_agent)
    monkeypatch.setattr(main, "limiter", DailyLimiter(per_visitor=1, total=0))
    client.post("/ask", json=QUESTION)
    client.post("/ask", json=QUESTION)
    assert len(calls) == 1  # the second question never reached the agent


def test_groq_quota_error_returns_503_with_clear_message(monkeypatch):
    def quota_agent(question):
        response = httpx.Response(429, request=httpx.Request("POST", "https://api.groq.com"))
        raise RateLimitError("rate limit", response=response, body=None)

    monkeypatch.setattr(main, "agent_answer", quota_agent)
    monkeypatch.setattr(main, "limiter", DailyLimiter())
    response = client.post("/ask", json=QUESTION)
    assert response.status_code == 503
    assert "daily capacity" in response.json()["detail"]


def test_too_long_or_empty_question_is_rejected(monkeypatch):
    monkeypatch.setattr(main, "agent_answer", fake_agent)
    monkeypatch.setattr(main, "limiter", DailyLimiter())
    assert client.post("/ask", json={"question": "x" * 1001}).status_code == 422
    assert client.post("/ask", json={"question": ""}).status_code == 422