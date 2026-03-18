import json


def _extract_json(text: str, default):
    try:
        return json.loads(text)
    except Exception:
        pass

    start = min([i for i in [text.find("["), text.find("{")] if i != -1], default=-1)
    if start == -1:
        return default

    end_brace = text.rfind("}")
    end_bracket = text.rfind("]")
    end = max(end_brace, end_bracket)
    if end == -1 or end < start:
        return default
    return json.loads(text[start : end + 1])


def llm_json(*, system: str, user: str, default, temperature: float = 0.1):
    """
    Return parsed JSON from the selected provider (OpenAI GPT or Anthropic Claude).
    Provider selection is controlled by config.LLM_PROVIDER.
    """
    from config import (
        ANTHROPIC_API_KEY,
        ANTHROPIC_MODEL,
        LLM_PROVIDER,
        OPENAI_API_KEY,
        OPENAI_MODEL,
    )

    provider = (LLM_PROVIDER or "openai").strip().lower()

    if provider == "anthropic":
        from anthropic import Anthropic

        client = Anthropic(api_key=ANTHROPIC_API_KEY)
        msg = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=1200,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": user}],
        )

        text = ""
        for block in getattr(msg, "content", []) or []:
            if getattr(block, "type", None) == "text":
                text += getattr(block, "text", "") or ""
        return _extract_json(text, default)

    # default: openai
    import openai

    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    # Use the Responses API for broad compatibility with newer OpenAI SDKs/models.
    resp = client.responses.create(
        model=OPENAI_MODEL,
        input=[
            # For Responses API, "content" must be a list of content-part objects.
            {"role": "system", "content": [{"type": "input_text", "text": system}]},
            {"role": "user", "content": [{"type": "input_text", "text": user}]},
        ],
        temperature=temperature,
    )

    text = getattr(resp, "output_text", None)
    if not text:
        # Fallback: best-effort extract from structured output blocks
        text_parts = []
        for item in getattr(resp, "output", []) or []:
            for block in getattr(item, "content", []) or []:
                if getattr(block, "type", None) in ("output_text", "text"):
                    text_parts.append(getattr(block, "text", "") or "")
        text = "".join(text_parts)

    return _extract_json(text or "", default)

