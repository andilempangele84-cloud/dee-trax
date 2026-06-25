#!/usr/bin/env python3
"""
LLM Provider Interface and Implementations

Abstract base class and concrete implementations for various LLM providers:
- OpenAI (GPT-4, GPT-3.5-turbo)
- Anthropic (Claude)
- Google (Gemini, PaLM)
- Local models (Ollama)
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, AsyncIterator
from dataclasses import dataclass
from enum import Enum
import openai
import anthropic
import google.generativeai as genai
import aiohttp
from loguru import logger


class ModelProvider(str, Enum):
    """Available LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LOCAL = "local"


@dataclass
class Message:
    """Message data structure"""
    role: str
    content: str


@dataclass
class LLMResponse:
    """LLM API response structure"""
    content: str
    model: str
    provider: str
    stop_reason: str
    usage: Dict[str, int]
    metadata: Dict = None


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, api_key: str, model: str = None):
        self.api_key = api_key
        self.model = model
        self.provider_name = self.__class__.__name__
    
    @abstractmethod
    async def complete(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        top_p: float = 0.9,
        **kwargs
    ) -> LLMResponse:
        """Generate completion from messages"""
        pass
    
    @abstractmethod
    async def stream(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        top_p: float = 0.9,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream completion tokens"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if provider is available"""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API Provider (GPT-4, GPT-3.5-turbo)"""
    
    def __init__(self, api_key: str, model: str = "gpt-4", org_id: Optional[str] = None):
        super().__init__(api_key, model)
        openai.api_key = api_key
        if org_id:
            openai.organization = org_id
    
    async def complete(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        top_p: float = 0.9,
        **kwargs
    ) -> LLMResponse:
        try:
            message_list = [{"role": msg.role, "content": msg.content} for msg in messages]
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=message_list,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                **kwargs
            )
            return LLMResponse(
                content=response.choices[0].message.content,
                model=response.model,
                provider="openai",
                stop_reason=response.choices[0].finish_reason,
                usage={"input_tokens": response.usage.prompt_tokens, "output_tokens": response.usage.completion_tokens},
            )
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    async def stream(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        top_p: float = 0.9,
        **kwargs
    ) -> AsyncIterator[str]:
        try:
            message_list = [{"role": msg.role, "content": msg.content} for msg in messages]
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=message_list,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                stream=True,
                **kwargs
            )
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"OpenAI streaming error: {str(e)}")
            raise
    
    async def health_check(self) -> bool:
        try:
            await openai.Model.aretrieve(self.model)
            return True
        except Exception as e:
            logger.warning(f"OpenAI health check failed: {str(e)}")
            return False
