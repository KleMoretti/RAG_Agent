from __future__ import annotations

from typing import Any, AsyncIterator, Optional
import asyncio

from dotenv import load_dotenv

from src.llm.model_config import OpenAIConfig

load_dotenv()


class LLMError(Exception):
    pass


class LLMClient:
    """Minimal extensible LLM client abstraction.

    Provides a synchronous `generate(prompt) -> str` method. Concrete clients
    may implement synchronous or asynchronous behaviour; this base class
    provides a compatibility layer.
    """

    def __init__(self, model: str = "echo", timeout: float = 30.0) -> None:
        self.model = model
        self.timeout = timeout

    def generate(self, prompt: str) -> str:
        """Synchronous generate API - default echo behaviour.

        Subclasses may override this with a real provider implementation.
        """
        # Default: simple echo behaviour. Keep it synchronous so callers
        # don't have to await in the common case.
        return f"[{self.model}] {prompt.strip()}"

    async def generate_stream(self, prompt: str) -> AsyncIterator[str]:
        # Stream tokens (naive split) as an async iterator
        for token in prompt.split():
            await asyncio.sleep(0)
            yield token


class EchoClient(LLMClient):
    """Synchronous echo client used as a local fallback when no API key is set."""

    def __init__(self, model: str = "echo") -> None:
        super().__init__(model=model)

    def generate(self, prompt: str) -> str:
        # Slightly more informative echo for clarity
        return f"[echo:{self.model}] {prompt.strip()}"


# -*- coding: utf-8 -*-
"""
LLM client for interfacing with OpenAI-compatible APIs.
"""
from openai import OpenAI


class OpenAIClient(LLMClient):
    """A client for interacting with an OpenAI-compatible LLM."""

    def __init__(self, config: OpenAIConfig, system_prompt: str | None = None):
        super().__init__(model=config.model_name)
        self.config = config
        self.system_prompt = system_prompt
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.api_base,
        )

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """
        Generates a response from the LLM based on a given prompt.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt override (uses instance default if not provided)
        """
        try:
            # Use provided system_prompt, or fall back to instance's system_prompt
            effective_system_prompt = system_prompt or self.system_prompt

            messages = []
            if effective_system_prompt:
                messages.append(
                    {
                        "role": "system",
                        "content": effective_system_prompt,
                    }
                )
            messages.append(
                {
                    "role": "user",
                    "content": prompt,
                }
            )

            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.config.model_name,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )
            content = getattr(chat_completion.choices[0].message, "content", None)
            if isinstance(content, str):
                return content.strip()
            return ""
        except Exception as e:
            print(f"Error during LLM generation: {e}")
            return "Sorry, I encountered an error while processing your request."
