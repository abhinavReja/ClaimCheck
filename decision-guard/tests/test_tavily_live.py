import os

import pytest

from web_search import web_research


@pytest.mark.integration
def test_tavily_live_search_basic():
    if not os.getenv("TAVILY_API_KEY"):
        pytest.skip("TAVILY_API_KEY not set; skipping live Tavily test.")

    # If user runs pytest with the global python (no tavily-python installed), skip with a clear hint.
    try:
        import tavily  # noqa: F401
    except Exception:
        pytest.skip(
            "tavily-python not available in this Python environment. Run using the venv: "
            r".\.venv\Scripts\python -m pytest -m integration"
        )

    ctx, sources = web_research("OpenAI GPT-4 model overview", max_results=2)
    assert isinstance(ctx, str)
    assert isinstance(sources, list)
    # We don't assert on exact content to keep it robust, but we expect some text and at least one source.
    assert ctx.strip() != ""
    assert len(sources) >= 1

