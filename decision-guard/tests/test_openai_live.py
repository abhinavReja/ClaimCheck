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

    # If user runs pytest with the *global* python (old openai SDK), skip with a clear hint.
    try:
        import openai  # type: ignore

        if not hasattr(openai, "OpenAI"):
            pytest.skip(
                "OpenAI SDK is too old (missing openai.OpenAI). Run tests using the venv: "
                r".\.venv\Scripts\python -m pytest -m integration"
            )
    except Exception:
        pytest.skip("OpenAI SDK not importable; skipping live OpenAI test.")

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

