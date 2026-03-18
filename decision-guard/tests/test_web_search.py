import types

import web_search as ws


def test_client_profile_query_builds_reasonable_string():
    q1 = ws.client_profile_query("Acme Corp", None)
    assert "Acme Corp" in q1
    assert "overview" in q1.lower()

    q2 = ws.client_profile_query("Acme Corp", "churn rate and revenue")
    assert "Acme Corp" in q2
    assert "churn rate" in q2


def test_web_research_rate_limit(monkeypatch):
    # Force TAVILY_API_KEY to look "set"
    monkeypatch.setattr(ws, "TAVILY_API_KEY", "fake-key", raising=False)

    # Fake Tavily client to avoid real network
    class FakeClient:
        def __init__(self, api_key=None):
            self.api_key = api_key

        def search(self, query, max_results=4):
            return {
                "results": [
                    {
                        "title": "Result 1",
                        "content": "Some content about the client.",
                        "url": "https://example.com/1",
                    }
                ]
            }

    monkeypatch.setitem(
        __import__("sys").modules,
        "tavily",
        types.SimpleNamespace(TavilyClient=FakeClient),
    )

    # Temporarily lower window + cap for deterministic test
    monkeypatch.setattr(ws, "_window_seconds", 3600.0, raising=False)
    monkeypatch.setattr(ws, "_max_calls_per_window", 2, raising=False)
    ws._call_timestamps.clear()  # reset

    ctx1, src1 = ws.web_research("query one", max_results=2)
    assert "Some content" in ctx1
    assert src1 == ["https://example.com/1"]

    ctx2, src2 = ws.web_research("query two", max_results=2)
    assert ctx2  # still allowed

    # Third call should be rate-limited and return empty context
    ctx3, src3 = ws.web_research("query three", max_results=2)
    assert ctx3 == ""
    assert src3 == []

