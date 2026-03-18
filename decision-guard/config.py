import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# LLM routing:
# - openai: GPT models
# - anthropic: Claude models
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").strip().lower()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")

CHROMA_COLLECTION = "company_docs"
DOCS_FOLDER = "sample_data"

# Optional default provider/company name for web research (can be overridden in UI later).
# Defaulting to TCS so the MVP web research targets Tata Consultancy Services.
DEFAULT_CLIENT_NAME = os.getenv("DEFAULT_CLIENT_NAME", "TCS").strip()

