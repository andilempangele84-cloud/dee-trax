#!/usr/bin/env python3
"""
LLM Service - High-level interface for interacting with LLM providers

Handles:
- Provider selection and initialization
- Request routing to appropriate provider
- Response formatting and caching
- Error handling and fallback mechanisms
"""

from typing import List, Optional, AsyncIterator, Dict
from loguru import logger
from config.environment import settings
from providers.llm_providers import (
    BaseLLMProvider,
    OpenAIProvider,
    AnthropicProvider,
    GoogleProvider,
    LocalProvider,
    Message,
    LLMResponse,
    ModelProvider,
)


class LLMService:
    """High-level LLM service managing multiple providers"""
    
    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.default_provider = settings.DEFAULT_LLM_PROVIDER
        self.default_model = settings.DEFAULT_MODEL
    
    async def initialize(self):
        """Initialize all configured LLM providers"""
        logger.info("Initializing LLM Service...")
        
        if settings.OPENAI_API_KEY:
            try:
                self.providers["openai"] = OpenAIProvider(
                    api_key=settings.OPENAI_API_KEY,
                    model="gpt-4",
                    org_id=settings.OPENAI_ORG_ID,
                )
                logger.info("✅ OpenAI provider initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {str(e)}")
        
        if settings.ANTHROPIC_API_KEY:
            try:
                self.providers["anthropic"] = AnthropicProvider(
                    api_key=settings.ANTHROPIC_API_KEY,
                    model="claude-3-opus",
                )
                logger.info("✅ Anthropic provider initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic: {str(e)}")
        
        if settings.GOOGLE_API_KEY:
            try:
                self.providers["google"] = GoogleProvider(
                    api_key=settings.GOOGLE_API_KEY,
                    model="gemini-pro",
                )
                logger.info("✅ Google provider initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Google: {str(e)}")
        
        try:
            self.providers["local"] = LocalProvider(model="llama2")
            logger.info("✅ Local provider initialized")
        except Exception as e:
            logger.warning(f"Local provider not available: {str(e)}")
    
    async def shutdown(self):
        """Shutdown all providers"""
        logger.info("Shutting down LLM Service...")
    
    async def health_check(self) -> bool:
        """Check if at least one provider is available"""
        for provider_name, provider in self.providers.items():
            try:
                if await provider.health_check():
                    logger.debug(f"{provider_name} provider is healthy")
                    return True
            except Exception as e:
                logger.debug(f"{provider_name} health check failed: {str(e)}")
        return False
    
    def get_provider(self, provider_name: Optional[str] = None) -> BaseLLMProvider:
        """Get LLM provider by name"""
        if provider_name is None:
            provider_name = self.default_provider
        
        if provider_name not in self.providers:
            raise ValueError(f"Provider '{provider_name}' not found. Available: {list(self.providers.keys())}")
        
        return self.providers[provider_name]
    
    async def complete(
        self,
        messages: List[Message],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        top_p: float = 0.9,
        **kwargs
    ) -> LLMResponse:
        """Generate completion from specified provider"""
        try:
            llm_provider = self.get_provider(provider)
            logger.info(f"Generating completion with {provider} provider")
            
            response = await llm_provider.complete(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                **kwargs
            )
            
            logger.debug(f"Completion generated: {response.model}")
            return response
        
        except Exception as e:
            logger.error(f"LLM completion failed: {str(e)}")
            raise
    
    async def stream(
        self,
        messages: List[Message],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        top_p: float = 0.9,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream completion tokens from specified provider"""
        try:
            llm_provider = self.get_provider(provider)
            logger.info(f"Streaming completion with {provider} provider")
            
            async for token in llm_provider.stream(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                **kwargs
            ):
                yield token
        
        except Exception as e:
            logger.error(f"LLM streaming failed: {str(e)}")
            raise
