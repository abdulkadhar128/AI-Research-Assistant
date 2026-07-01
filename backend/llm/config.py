import os

def load_env_file() -> None:
    """
    Helper function to load env values from the workspace root .env file.
    """
    # Resolve path to the workspace root directory (three levels up from backend/llm/config.py)
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
    """
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")

    TIMEOUT_SECONDS = float(os.getenv("LLM_TIMEOUT", "30.0"))
    MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "3"))
    ENABLE_PROVIDER_FALLBACK = os.getenv("ENABLE_PROVIDER_FALLBACK", "true").lower() == "true"

    # Resolve provider dynamically based on available environment API keys.
    # We NEVER fall back to mock unless LLM_PROVIDER is explicitly set to "mock".
    _raw_provider = os.getenv("LLM_PROVIDER", "").lower()
    if _raw_provider == "mock":
        PROVIDER = "mock"
    elif _raw_provider:
        PROVIDER = _raw_provider
    else:
        if os.getenv("GEMINI_API_KEY", ""):
            PROVIDER = "gemini"
        elif os.getenv("OPENAI_API_KEY", ""):
            PROVIDER = "openai"
        elif os.getenv("GROQ_API_KEY", ""):
            PROVIDER = "groq"
        else:
            PROVIDER = "gemini"  # Default to gemini to raise clear API errors on key miss rather than mock fallbacks

    @classmethod
    def get_fast_model(cls) -> str:
        provider = cls.PROVIDER.lower()
        if provider == "gemini":
            return "gemini-2.0-flash-lite"
        elif provider == "openai":
            return "gpt-4o-mini"
        elif provider == "groq":
            return "llama3-8b-8192"
        return ""

    @classmethod
    def get_quality_model(cls) -> str:
        provider = cls.PROVIDER.lower()
        if provider == "gemini":
            return cls.GEMINI_MODEL
        elif provider == "openai":
            return cls.OPENAI_MODEL
        elif provider == "groq":
            return cls.GROQ_MODEL
        return ""

print("=" * 50)
print("LLM Provider =", LLMConfig.PROVIDER)
print("Gemini Model =", LLMConfig.GEMINI_MODEL)
print("Gemini Key Loaded =", bool(LLMConfig.GEMINI_API_KEY))
print("=" * 50)

print("LLM_PROVIDER ENV =", os.getenv("LLM_PROVIDER"))
print("OPENAI_API_KEY Loaded =", bool(LLMConfig.OPENAI_API_KEY))
print("OPENAI_MODEL =", LLMConfig.OPENAI_MODEL)
print("Provider =", LLMConfig.PROVIDER)