"""
LLM Client for interacting with OpenAI ChatGPT models.

Provides a clean interface for chat completions, streaming, and token counting.
"""

import sys
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dotenv import load_dotenv

from openai import AsyncOpenAI
from openai import APIError, APITimeoutError

# Load environment variables from .env file before importing config
# This ensures OPENAI_API_KEY and other env vars are available
_project_root = Path(__file__).parent.parent.parent  # backend/agent/../.. = project_root
_env_path = _project_root / ".env"
if _env_path.exists():
    load_dotenv(_env_path)

# Handle both module and direct execution contexts
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    from .config import config
    from .models import LLMMesssage, LLMResponse
except ImportError:
    from config import config
    from models import LLMMesssage, LLMResponse

logger = logging.getLogger(__name__)


class LLMClientError(Exception):
    """Base exception for LLM-related errors."""
    pass


class ModelNotFoundError(LLMClientError):
    """Raised when the specified model is not available."""
    pass


class OpenAIClient:
    """Client for interacting with OpenAI Chat Completions API."""

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        organization: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        self.model = model or config.openai_model
        self.api_key = api_key or config.openai_api_key
        # Prefer explicit base_url argument, then OPENAI_API_BASE alias, then default base URL
        self.base_url = base_url or config.openai_api_base or config.openai_base_url
        self.organization = organization or config.openai_org_id
        self.timeout = timeout or config.llm_timeout

        if not self.api_key:
            raise LLMClientError(
                "OpenAI API key is not configured. "
                "Set OPENAI_API_KEY (or AGENT_OPENAI_API_KEY) in your environment or .env file."
            )

        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            organization=self.organization,
            timeout=self.timeout,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclose()

    async def aclose(self):
        """Close any underlying HTTP resources (if applicable)."""
        # AsyncOpenAI currently does not expose explicit close, but keep for future compatibility
        return None

    async def chat(
        self,
        messages: List[Union[LLMMesssage, Dict[str, str]]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> str:
        """
        Send a chat completion request to OpenAI.

        Args:
            messages: List of messages with role/content
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response

        Returns:
            Generated text content
        """
        if temperature is None:
            temperature = config.temperature
        if max_tokens is None:
            max_tokens = config.max_tokens

        # Convert messages to expected format
        formatted_messages: List[Dict[str, str]] = []
        for msg in messages:
            if isinstance(msg, LLMMesssage):
                formatted_messages.append(
                    {
                        "role": msg.role,
                        "content": msg.content,
                    }
                )
            else:
                formatted_messages.append(msg)

        for attempt in range(config.max_retries):
            try:
                if stream:
                    content = ""
                    async for chunk in self.client.chat.completions.create(
                        model=self.model,
                        messages=formatted_messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=True,
                    ):
                        delta = chunk.choices[0].delta
                        if delta and getattr(delta, "content", None):
                            content += delta.content
                    return content

                completion = await self.client.chat.completions.create(
                    model=self.model,
                    messages=formatted_messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=False,
                )
                message = completion.choices[0].message
                return message.content or ""

            except (APITimeoutError,) as e:
                if attempt < config.max_retries - 1:
                    delay = config.retry_delay * (config.retry_backoff ** attempt)
                    logger.warning(f"OpenAI request timed out, retrying in {delay}s... ({e})")
                    await asyncio.sleep(delay)
                else:
                    raise LLMClientError("OpenAI request timed out after all retries") from e
            except APIError as e:
                # Model not found or other API error
                if getattr(e, "status_code", None) == 404:
                    raise ModelNotFoundError(f"Model '{self.model}' not found") from e
                if attempt < config.max_retries - 1:
                    delay = config.retry_delay * (config.retry_backoff ** attempt)
                    logger.warning(f"OpenAI API error, retrying in {delay}s... ({e})")
                    await asyncio.sleep(delay)
                else:
                    raise LLMClientError(f"OpenAI request failed after retries: {e}") from e
            except Exception as e:
                if attempt < config.max_retries - 1:
                    delay = config.retry_delay * (config.retry_backoff ** attempt)
                    logger.warning(f"Unexpected OpenAI error, retrying in {delay}s... ({e})")
                    await asyncio.sleep(delay)
                else:
                    raise LLMClientError(f"Unexpected OpenAI error: {e}") from e

        # Should be unreachable
        raise LLMClientError("OpenAI chat request failed for unknown reasons")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Generate text using a simple prompt (completion-style).

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature

        Returns:
            Generated text
        """
        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        return await self.chat(messages, temperature=temperature)

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        This is a rough approximation - in production, use tiktoken or similar.
        """
        # Rough approximation: 1 token ≈ 4 characters for English
        return len(text) // 4

    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about available models."""
        try:
            models = await self.client.models.list()
            return {"data": [m.id for m in models.data]}
        except Exception as e:
            raise LLMClientError(f"Failed to get model info: {e}") from e


# Global LLM client instance used throughout the agent system
llm_client = OpenAIClient()
