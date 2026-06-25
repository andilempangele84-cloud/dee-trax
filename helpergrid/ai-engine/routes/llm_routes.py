#!/usr/bin/env python3
"""
LLM Routes

API endpoints for LLM operations:
- Completions
- Streaming
- Model information
"""

from typing import List
from fastapi import APIRouter, Request, status
from pydantic import BaseModel
from loguru import logger

router = APIRouter()


class Message(BaseModel):
    """Message input model"""
    role: str
    content: str


class CompletionRequest(BaseModel):
    """Completion request model"""
    messages: List[Message]
    provider: str = "openai"
    model: str = None
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 0.9


class CompletionResponse(BaseModel):
    """Completion response model"""
    content: str
    model: str
    provider: str
    stop_reason: str
    usage: dict


@router.post("/completions", response_model=CompletionResponse)
async def create_completion(request: Request, completion_request: CompletionRequest):
    """
    Generate LLM completion
    """
    try:
        llm_service = request.app.state.llm_service
        
        from providers.llm_providers import Message as LLMMessage
        
        messages = [
            LLMMessage(role=msg.role, content=msg.content)
            for msg in completion_request.messages
        ]
        
        response = await llm_service.complete(
            messages=messages,
            provider=completion_request.provider,
            temperature=completion_request.temperature,
            max_tokens=completion_request.max_tokens,
            top_p=completion_request.top_p,
        )
        
        return CompletionResponse(
            content=response.content,
            model=response.model,
            provider=response.provider,
            stop_reason=response.stop_reason,
            usage=response.usage,
        )
    
    except Exception as e:
        logger.error(f"Completion error: {str(e)}")
        raise


@router.post("/stream")
async def stream_completion(request: Request, completion_request: CompletionRequest):
    """
    Stream LLM completion tokens
    """
    from fastapi.responses import StreamingResponse
    
    async def generate():
        try:
            llm_service = request.app.state.llm_service
            
            from providers.llm_providers import Message as LLMMessage
            
            messages = [
                LLMMessage(role=msg.role, content=msg.content)
                for msg in completion_request.messages
            ]
            
            async for token in llm_service.stream(
                messages=messages,
                provider=completion_request.provider,
                temperature=completion_request.temperature,
                max_tokens=completion_request.max_tokens,
                top_p=completion_request.top_p,
            ):
                yield token
        
        except Exception as e:
            logger.error(f"Stream error: {str(e)}")
            yield f"Error: {str(e)}"
    
    return StreamingResponse(generate(), media_type="text/plain")


@router.get("/models")
async def list_models(request: Request):
    """
    List available models and providers
    """
    try:
        llm_service = request.app.state.llm_service
        
        models = {}
        for provider_name, provider in llm_service.providers.items():
            models[provider_name] = {
                "model": provider.model,
                "provider_name": provider.provider_name,
            }
        
        return {"models": models, "default_provider": llm_service.default_provider}
    
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        raise
