import unittest
from unittest.mock import patch, MagicMock
from backend.llm.client import LangChainLLMService
from backend.llm.config import LLMConfig
from langchain_core.messages import SystemMessage, HumanMessage

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
        client = LangChainLLMService()
        messages = [
            SystemMessage(content="You are an Intent Analysis Agent."),
            HumanMessage(content="User Query: generative AI")
        ]
        res = client.invoke(messages)
        # Mock provider returns JSON for Intent Analyzer
        assert "confidence" in res.content
        assert "generative AI" in res.content

def test_openai_integration() -> None:
    """
    Tests that the OpenAI API client is correctly initialized.
    """
    with patch("backend.llm.config.LLMConfig.PROVIDER", "openai"), \
         patch("backend.llm.config.LLMConfig.OPENAI_API_KEY", "fake-key"), \
         patch("langchain_openai.ChatOpenAI.invoke") as mock_invoke:
        
        mock_message = MagicMock()
        mock_message.content = "OpenAI response text"
        mock_invoke.return_value = mock_message

        client = LangChainLLMService()
        messages = [HumanMessage(content="Test Prompt")]
        response = client.invoke(messages)
        
        assert response.content == "OpenAI response text"
        mock_invoke.assert_called_once_with(messages)

def test_groq_integration() -> None:
    """
    Tests that the Groq API client is correctly initialized.
    """
    with patch("backend.llm.config.LLMConfig.PROVIDER", "groq"), \
         patch("backend.llm.config.LLMConfig.GROQ_API_KEY", "fake-groq-key"), \
         patch("langchain_groq.ChatGroq.invoke") as mock_invoke:
        
        mock_message = MagicMock()
        mock_message.content = "Groq response text"
        mock_invoke.return_value = mock_message

        client = LangChainLLMService()
        messages = [HumanMessage(content="Test Prompt")]
        response = client.invoke(messages)
        
        assert response.content == "Groq response text"
        mock_invoke.assert_called_once_with(messages)

def test_gemini_integration() -> None:
    """
    Tests that the Gemini API client is correctly initialized.
    """
    with patch("backend.llm.config.LLMConfig.PROVIDER", "gemini"), \
         patch("backend.llm.config.LLMConfig.GEMINI_API_KEY", "fake-gemini-key"), \
         patch("langchain_google_genai.ChatGoogleGenerativeAI.invoke") as mock_invoke:
        
        mock_message = MagicMock()
        mock_message.content = "Gemini response text"
        mock_invoke.return_value = mock_message

        client = LangChainLLMService()
        messages = [HumanMessage(content="Test Prompt")]
        response = client.invoke(messages)
        
        assert response.content == "Gemini response text"
        mock_invoke.assert_called_once_with(messages)

def test_client_retry_and_backoff() -> None:
    """
    Tests that failures trigger exponential retry loops and throw after exhaustion.
    """
    with patch("backend.llm.config.LLMConfig.PROVIDER", "openai"), \
         patch("backend.llm.config.LLMConfig.OPENAI_API_KEY", "fake-key"), \
         patch("backend.llm.config.LLMConfig.MAX_RETRIES", 2), \
         patch("time.sleep") as mock_sleep, \
         patch("langchain_openai.ChatOpenAI.invoke", side_effect=Exception("API limit exceeded")) as mock_invoke:
        
        client = LangChainLLMService()
        messages = [HumanMessage(content="Test Prompt")]
        try:
            client.invoke(messages)
            assert False, "Should raise RuntimeError on exhausted retries"
        except RuntimeError as e:
            assert "API limit exceeded" in str(e)
            
        assert mock_invoke.call_count == 2
        mock_sleep.assert_called_once_with(2)
