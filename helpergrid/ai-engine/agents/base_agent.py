#!/usr/bin/env python3
"""
Base Agent Class

Abstract base class for all AI agents with common functionality:
- Message history management
- Tool usage
- Response generation
- Context awareness
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
from loguru import logger


@dataclass
class AgentMemory:
    """Agent conversation memory"""
    messages: List[Dict] = field(default_factory=list)
    context: Dict = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self, name: str, description: str, llm_service=None):
        self.name = name
        self.description = description
        self.llm_service = llm_service
        self.memory = AgentMemory()
        self.tools = {}
    
    @abstractmethod
    async def process_message(self, user_message: str) -> str:
        """Process user message and generate response"""
        pass
    
    @abstractmethod
    async def execute_tool(self, tool_name: str, **kwargs) -> str:
        """Execute a tool/action"""
        pass
    
    def add_message(self, role: str, content: str):
        """Add message to memory"""
        self.memory.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.memory.updated_at = datetime.now()
    
    def get_context(self) -> str:
        """Build context from memory"""
        context_str = f"Agent: {self.name}\n"
        context_str += f"Description: {self.description}\n"
        context_str += f"Recent messages:\n"
        
        for msg in self.memory.messages[-5:]:
            context_str += f"{msg['role']}: {msg['content']}\n"
        
        return context_str
    
    def clear_memory(self):
        """Clear conversation history"""
        self.memory = AgentMemory()
