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

    Provides synchronous generate and async streaming generate.
    Current implementation is an echo placeholder so other layers (agent, reasoning)
    can depend on a stable interface without requiring a real provider.
    """

    def __init__(self, model: str = "echo", timeout: float = 30.0) -> None:
        self.model = model
        self.timeout = timeout

    async def generate(self, prompt: str) -> str:
        # Simple echo behaviour; replace with real provider logic later
        await asyncio.sleep(0)
        return f"[{self.model}] {prompt.strip()}"

    async def generate_stream(self, prompt: str) -> AsyncIterator[str]:
        # Stream tokens (naive split) as an async iterator
        for token in prompt.split():
            await asyncio.sleep(0)
            yield token

# -*- coding: utf-8 -*-
"""
LLM client for interfacing with OpenAI-compatible APIs.
"""
from openai import OpenAI

class OpenAIClient:
    """A client for interacting with an OpenAI-compatible LLM."""
    def __init__(self, config: OpenAIConfig):
        self.config = config
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.api_base,
        )

    def generate(self, prompt: str) -> str:
        """
        Generates a response from the LLM based on a given prompt.
        """
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.config.model_name,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error during LLM generation: {e}")
            return "Sorry, I encountered an error while processing your request."

