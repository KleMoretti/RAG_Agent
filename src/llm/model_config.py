"""
Configuration classes for LLM models.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class ModelConfig:
    """Base configuration for language models."""
    model_name: str
    max_tokens: int = 1024
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: List[str] = field(default_factory=list)


@dataclass
class OpenAIConfig(ModelConfig):
    """Configuration for OpenAI models."""
    api_key: Optional[str] = None
    api_base: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    organization: Optional[str] = None
    extra_body: Optional[Dict[str, Any]] = None

    def to_request_params(self) -> Dict[str, Any]:
        """Convert config to request parameters."""
        params = {
            "model": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "stop": self.stop_sequences if self.stop_sequences else None
        }
        if self.extra_body:
            params["extra_body"] = self.extra_body
        return params


@dataclass
class HuggingFaceConfig(ModelConfig):
    """Configuration for HuggingFace models."""
    api_key: Optional[str] = None
    api_base: str = "https://api-inference.huggingface.co/models"
    device: str = "cuda"
    quantization: Optional[str] = None  # "8bit" or "4bit" for quantized models

    def to_request_params(self) -> Dict[str, Any]:
        """Convert config to request parameters."""
        return {
            "inputs": "",  # Placeholder, filled at request time
            "parameters": {
                "max_new_tokens": self.max_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "repetition_penalty": 1.0 + self.frequency_penalty,
                "stop": self.stop_sequences if self.stop_sequences else None
            }
        }