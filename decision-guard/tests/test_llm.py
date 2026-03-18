import types


def test_openai_responses_payload_shape(monkeypatch):
    """
    Ensures we call OpenAI Responses API with content-parts objects:
    input[i].content must be a list of {"type":"text","text":...} objects.
    """

    captured = {}

    class FakeResponses:
        def create(self, **kwargs):
            captured["kwargs"] = kwargs
            # minimal object compatible with llm.py parsing
            return types.SimpleNamespace(output_text='{"ok": true}')

    class FakeOpenAIClient:
        def __init__(self, api_key=None):
            self.responses = FakeResponses()

    fake_openai_module = types.SimpleNamespace(OpenAI=FakeOpenAIClient)

    # Force provider selection to OpenAI
    import config as config_module

    monkeypatch.setattr(config_module, "LLM_PROVIDER", "openai", raising=False)
    monkeypatch.setattr(config_module, "OPENAI_API_KEY", "test-key", raising=False)
    monkeypatch.setattr(config_module, "OPENAI_MODEL", "gpt-4o-mini", raising=False)

    # Replace "openai" import used inside llm.py
    import llm as llm_module

    monkeypatch.setitem(llm_module.__dict__, "openai", fake_openai_module)
    monkeypatch.setitem(__import__("builtins").__dict__, "__openai_fake__", fake_openai_module)
    monkeypatch.setattr(llm_module, "openai", fake_openai_module, raising=False)

    # Also patch the module loader path (import openai inside function)
    monkeypatch.setitem(__import__("sys").modules, "openai", fake_openai_module)

    out = llm_module.llm_json(system="SYS", user="USER", default={"ok": False})
    assert out == {"ok": True}

    kwargs = captured["kwargs"]
    assert "input" in kwargs
    assert isinstance(kwargs["input"], list)
    assert kwargs["input"][0]["role"] == "system"
    assert kwargs["input"][1]["role"] == "user"
    assert kwargs["input"][0]["content"][0]["type"] == "input_text"
    assert kwargs["input"][0]["content"][0]["text"] == "SYS"
    assert kwargs["input"][1]["content"][0]["text"] == "USER"


def test_extract_json_fallback_parses_embedded_json():
    import llm as llm_module

    text = "some junk before {\"a\": 1, \"b\": [2, 3]} trailing junk"
    assert llm_module._extract_json(text, default={}) == {"a": 1, "b": [2, 3]}


def test_agent_prompts_are_strings(monkeypatch):
    """
    Regression test: ensure agent prompt variables are not tuples
    (a trailing comma after a triple-quoted string turns it into a tuple).
    """

    captured = {}

    def fake_llm_json(*, system, user, default, temperature=0.1):
        captured["system_type"] = type(system)
        captured["user_type"] = type(user)
        return []

    import agent1_listener as a1

    monkeypatch.setattr(a1, "llm_json", fake_llm_json)
    a1.extract_claims("hello")
    assert captured["system_type"] is str
    assert captured["user_type"] is str

