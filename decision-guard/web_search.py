import threading
import time
from typing import List, Tuple

from config import TAVILY_API_KEY

_lock = threading.Lock()
_window_seconds = 60.0
_max_calls_per_window = 10  # simple safety cap for free-tier credits
_call_timestamps: List[float] = []


def _within_rate_limit() -> bool:
    now = time.time()
    with _lock:
        # drop timestamps older than window
        cutoff = now - _window_seconds
        while _call_timestamps and _call_timestamps[0] < cutoff:
            _call_timestamps.pop(0)
        if len(_call_timestamps) >= _max_calls_per_window:
            return False
        _call_timestamps.append(now)
        return True


def client_profile_query(client_name: str, focus: str | None = None) -> str:
    """
    Build a Tavily search query focused on the client.

    Example:
        client_profile_query("Netflix", "pricing plans and recent outages")
    """
    name = (client_name or "").strip()
    # Expand short forms for better search hit-rate.
    if name.upper() == "TCS":
        name = "Tata Consultancy Services (TCS)"
    if not name:
        return (focus or "").strip()
    if not focus:
        return f"{name} company overview key metrics recent news"
    return f"{name}: {focus}"


def web_research(query: str, max_results: int = 4) -> Tuple[str, List[str]]:
    """
    Perform a rate-limited Tavily search and return a text block and sources.

    Returns (context_text, sources).
    If Tavily is not configured or rate limit is hit, returns ("", []).
    """
    q = (query or "").strip()
    if not q:
        return "", []

    if not TAVILY_API_KEY:
        return "", []

    if not _within_rate_limit():
        # Soft-fail: no web context, but do not raise.
        return "", []

    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=TAVILY_API_KEY)
        resp = client.search(query=q, max_results=max_results)
    except Exception:
        return "", []

    results = resp.get("results") if isinstance(resp, dict) else None
    if not results:
        return "", []

    snippets: List[str] = []
    sources: List[str] = []
    for r in results:
        title = r.get("title") or ""
        content = r.get("content") or ""
        url = r.get("url") or ""
        # Some providers return empty content for certain results; still include title/url
        # so downstream logic (and integration tests) can confirm search worked.
        if content:
            snippets.append(f"[{title or 'web result'}]\n{content}")
        elif title or url:
            snippets.append(f"[{title or 'web result'}]\n{url}".strip())
        if url:
            sources.append(url)

    return "\n\n".join(snippets), sources

