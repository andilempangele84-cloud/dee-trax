#!/usr/bin/env python3
"""
Agent Routes

API endpoints for agent operations:
- Agent creation
- Message processing
- Tool execution
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel
from loguru import logger

router = APIRouter()


class AgentMessage(BaseModel):
    """Agent message input"""
    message: str
    agent_type: str = "personal_assistant"


class AgentResponse(BaseModel):
    """Agent response output"""
    response: str
    agent: str
    metadata: dict = {}


@router.post("/message", response_model=AgentResponse)
async def send_agent_message(request: Request, agent_msg: AgentMessage):
    """
    Send message to AI agent
    """
    try:
        logger.info(f"Agent message: {agent_msg.message} (type: {agent_msg.agent_type})")
        
        # Get appropriate agent based on type
        from agents.personal_assistant import PersonalAssistant
        from agents.customer_support import CustomerSupportAssistant
        
        llm_service = request.app.state.llm_service
        
        if agent_msg.agent_type == "personal_assistant":
            agent = PersonalAssistant(llm_service)
        elif agent_msg.agent_type == "customer_support":
            agent = CustomerSupportAssistant(llm_service)
        else:
            return {"error": f"Unknown agent type: {agent_msg.agent_type}"}
        
        response = await agent.process_message(agent_msg.message)
        
        return AgentResponse(
            response=response,
            agent=agent.name,
            metadata={"message_count": len(agent.memory.messages)}
        )
    
    except Exception as e:
        logger.error(f"Agent error: {str(e)}")
        raise


@router.get("/agents")
async def list_agents():
    """
    List available agents
    """
    return {
        "agents": [
            {
                "type": "personal_assistant",
                "name": "Personal Assistant",
                "description": "AI assistant for personal task automation"
            },
            {
                "type": "customer_support",
                "name": "Customer Support Assistant",
                "description": "AI assistant for customer service"
            }
        ]
    }
