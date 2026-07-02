import os

def load_env_file() -> None:
    """
    Helper function to load env values from the workspace root .env file.
    """
    env_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", ".env")
    )
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, val = line.split("=", 1)
                        key = key.strip()
                        val = val.strip().strip('"').strip("'")
                        os.environ[key] = val
        except Exception:
            pass

# Load environmental variables before resolving config properties
load_env_file()


class LLMConfig:
    """
    Configuration settings for LLM providers.
    All values are read from environment variables, with sensible defaults.
    """
    # --- OpenAI ---
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str  = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # --- Google Gemini ---
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str   = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    # --- Groq ---
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str   = os.getenv("GROQ_MODEL", "llama3-8b-8192")

    # --- Tavily ---
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")

    # --- Client settings ---
    TIMEOUT_SECONDS: float = float(os.getenv("LLM_TIMEOUT", "60.0"))
    MAX_RETRIES: int       = int(os.getenv("LLM_MAX_RETRIES", "3"))

    # --- Provider auto-selection ---
    # Precedence: LLM_PROVIDER env → available API key → default to gemini
    _raw_provider: str = os.getenv("LLM_PROVIDER", "").lower()
    if _raw_provider == "mock":
        PROVIDER = "mock"
    elif _raw_provider in ("openai", "gemini", "groq"):
        PROVIDER = _raw_provider
    else:
        # Auto-detect based on which API key is present
        if os.getenv("OPENAI_API_KEY", ""):
            PROVIDER = "openai"
        elif os.getenv("GEMINI_API_KEY", ""):
            PROVIDER = "gemini"
        elif os.getenv("GROQ_API_KEY", ""):
            PROVIDER = "groq"
        else:
            PROVIDER = "gemini"  # Raises a clear API error rather than silent mock

    @classmethod
    def get_fast_model(cls) -> str:
        """Return the fast/cheap model for the active provider."""
        provider = cls.PROVIDER.lower()
        if provider == "openai":
            return "gpt-4o-mini"
        elif provider == "gemini":
            return "gemini-2.0-flash-lite"
        elif provider == "groq":
            return "llama3-8b-8192"
        return ""

    @classmethod
    def get_quality_model(cls) -> str:
        """Return the high-quality model for the active provider."""
        provider = cls.PROVIDER.lower()
        if provider == "openai":
            return cls.OPENAI_MODEL
        elif provider == "gemini":
            return cls.GEMINI_MODEL
        elif provider == "groq":
            return cls.GROQ_MODEL
        return ""