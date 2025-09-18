from __future__ import annotations

from typing import Any, AsyncIterator, Optional
import asyncio


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


__all__ = ["LLMClient", "LLMError"]
