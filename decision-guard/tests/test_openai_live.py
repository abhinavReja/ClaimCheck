import os

import pytest


@pytest.mark.integration
def test_openai_live_llm_json_roundtrip():
    """
    Real OpenAI integration test (requires OPENAI_API_KEY).

    Run explicitly:
      pytest -m integration
    """
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set; skipping live OpenAI test.")

    # Force OpenAI path for this test even if your .env sets anthropic.
    import config as config_module

    config_module.LLM_PROVIDER = "openai"

    from llm import llm_json

    out = llm_json(
        system="Return ONLY valid JSON with a single key 'ping' set to 'pong'.",
        user="ping",
        default={"ping": "fail"},
        temperature=0.0,
    )

    assert isinstance(out, dict)
    assert out.get("ping") == "pong"

