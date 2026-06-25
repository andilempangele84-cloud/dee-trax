#!/usr/bin/env python3
"""
Customer Support Assistant

AI-powered customer service:
- Intelligent chatbot
- Multi-channel support
- FAQ automation
- Issue resolution
- Ticket escalation
"""

from typing import Optional, List
from loguru import logger
from agents.base_agent import BaseAgent


class CustomerSupportAssistant(BaseAgent):
    """Customer support AI assistant"""
    
    def __init__(self, llm_service, company: str = None):
        super().__init__(
            name="Customer Support Assistant",
            description="AI assistant for customer service and support",
            llm_service=llm_service
        )
        self.company = company
        self.tools = {
            "search_faq": self.search_faq,
            "create_ticket": self.create_ticket,
            "escalate_issue": self.escalate_issue,
            "get_order_status": self.get_order_status,
            "process_refund": self.process_refund,
        }
    
    async def process_message(self, user_message: str) -> str:
        """Process customer inquiry"""
        logger.info(f"Customer Support processing: {user_message}")
        
        self.add_message("user", user_message)
        
        # First, try to find FAQ answer
        faq_response = await self.search_faq(user_message)
        if faq_response and faq_response != "No FAQ found":
            self.add_message("assistant", faq_response)
            return faq_response
        
        # Generate personalized response
        response = await self._generate_support_response(user_message)
        self.add_message("assistant", response)
        return response
    
    async def search_faq(self, query: str) -> str:
        """Search FAQ database"""
        logger.info(f"Searching FAQ: {query}")
        # Mock FAQ search - integrate with real FAQ database
        faqs = {
            "shipping": "We ship within 2-3 business days",
            "returns": "30-day return policy on all items",
            "payment": "We accept all major credit cards",
        }
        
        for key, answer in faqs.items():
            if key in query.lower():
                return answer
        
        return "No FAQ found"
    
    async def create_ticket(self, description: str) -> str:
        """Create support ticket"""
        logger.info("Creating support ticket")
        return f"Ticket #12345 created. We'll respond within 24 hours."
    
    async def escalate_issue(self, reason: str) -> str:
        """Escalate to human agent"""
        logger.info(f"Escalating issue: {reason}")
        return "Issue escalated to our support team. A specialist will contact you soon."
    
    async def get_order_status(self, order_id: str) -> str:
        """Get order status"""
        logger.info(f"Checking order: {order_id}")
        return f"Order {order_id} is in transit and will arrive tomorrow."
    
    async def process_refund(self, order_id: str) -> str:
        """Process refund request"""
        logger.info(f"Processing refund for order: {order_id}")
        return f"Refund initiated for order {order_id}. You'll see it in 5-10 business days."
    
    async def _generate_support_response(self, user_message: str) -> str:
        """Generate support response using LLM"""
        try:
            from providers.llm_providers import Message
            
            system_prompt = f"""You are a helpful customer support representative for {self.company or 'our company'}.
            Be empathetic, professional, and helpful. Keep responses concise and clear.
            {self.get_context()}"""
            
            messages = [
                Message(role="system", content=system_prompt),
                Message(role="user", content=user_message),
            ]
            
            response = await self.llm_service.complete(messages)
            return response.content
        except Exception as e:
            logger.error(f"Error generating support response: {str(e)}")
            return "Thank you for reaching out. Please describe your issue and I'll help you."
    
    async def execute_tool(self, tool_name: str, **kwargs) -> str:
        """Execute support tool"""
        if tool_name not in self.tools:
            return f"Tool '{tool_name}' not found"
        
        return await self.tools[tool_name](**kwargs)
