import unittest
from unittest.mock import patch, MagicMock
from backend.llm.client import LLMClient
from backend.llm.config import LLMConfig

def test_config_defaults() -> None:
    """
    Verifies that the LLMConfig loading class parses properties correctly.
    """
    assert hasattr(LLMConfig, "PROVIDER")
    assert hasattr(LLMConfig, "TIMEOUT_SECONDS")
    assert hasattr(LLMConfig, "MAX_RETRIES")

def test_mock_provider_fallback() -> None:
    """
    Verifies the client uses local mock parsing when the provider is set to mock.
    """
    with patch("backend.llm.config.LLMConfig.PROVIDER", "mock"):
        client = LLMClient()
        res = client.generate("User Query: generative AI\nResearch Planner")
        assert "Define and clarify" in res

def test_openai_integration() -> None:
    """
    Tests that the OpenAI API call correctly parses payload and returns responses.
    """
    with patch("backend.llm.config.LLMConfig.PROVIDER", "openai"), \
         patch("backend.llm.config.LLMConfig.OPENAI_API_KEY", "fake-key"), \
         patch("httpx.post") as mock_post:
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "OpenAI response text"}}]
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        client = LLMClient()
        response = client.generate("Test Prompt")
        
        assert response == "OpenAI response text"
        mock_post.assert_called_once()
        
        args, kwargs = mock_post.call_args
        assert kwargs["headers"]["Authorization"] == "Bearer fake-key"
        assert kwargs["json"]["model"] == LLMConfig.OPENAI_MODEL

def test_groq_integration() -> None:
    """
    Tests that the Groq API call formats headers and handles completions correctly.
    """
    with patch("backend.llm.config.LLMConfig.PROVIDER", "groq"), \
         patch("backend.llm.config.LLMConfig.GROQ_API_KEY", "fake-groq-key"), \
         patch("httpx.post") as mock_post:
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Groq response text"}}]
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        client = LLMClient()
        response = client.generate("Test Prompt")
        
        assert response == "Groq response text"
        mock_post.assert_called_once()
        
        args, kwargs = mock_post.call_args
        assert kwargs["headers"]["Authorization"] == "Bearer fake-groq-key"
        assert kwargs["json"]["model"] == LLMConfig.GROQ_MODEL

def test_gemini_integration() -> None:
    """
    Tests that the Gemini API call generates correct model endpoints and schemas.
    """
    with patch("backend.llm.config.LLMConfig.PROVIDER", "gemini"), \
         patch("backend.llm.config.LLMConfig.GEMINI_API_KEY", "fake-gemini-key"), \
         patch("httpx.post") as mock_post:
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": "Gemini response text"}]}}]
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        client = LLMClient()
        response = client.generate("Test Prompt")
        
        assert response == "Gemini response text"
        mock_post.assert_called_once()
        
        args, kwargs = mock_post.call_args
        assert "key=fake-gemini-key" in args[0]
        assert model := LLMConfig.GEMINI_MODEL in args[0]

def test_client_retry_and_backoff() -> None:
    """
    Tests that failures trigger exponential retry loops and throw after exhaustion.
    """
    with patch("backend.llm.config.LLMConfig.PROVIDER", "openai"), \
         patch("backend.llm.config.LLMConfig.OPENAI_API_KEY", "fake-key"), \
         patch("backend.llm.config.LLMConfig.MAX_RETRIES", 2), \
         patch("time.sleep") as mock_sleep, \
         patch("httpx.post", side_effect=Exception("API limit exceeded")) as mock_post:
        
        client = LLMClient()
        try:
            client.generate("Test Prompt")
            assert False, "Should raise RuntimeError on exhausted retries"
        except RuntimeError as e:
            assert "API limit exceeded" in str(e)
            
        assert mock_post.call_count == 2
        mock_sleep.assert_called_once_with(2)
