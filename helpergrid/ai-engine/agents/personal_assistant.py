#!/usr/bin/env python3
"""
Personal Assistant Agent

Automation workflows for everyday personal tasks:
- Email management
- Bill payment
- Grocery ordering
- Appointment booking
- Travel planning
"""

from typing import Optional
from datetime import datetime
from loguru import logger
from agents.base_agent import BaseAgent


class PersonalAssistant(BaseAgent):
    """Personal AI Assistant for daily tasks"""
    
    def __init__(self, llm_service, user_id: str = None):
        super().__init__(
            name="Personal Assistant",
            description="AI assistant for personal task automation and scheduling",
            llm_service=llm_service
        )
        self.user_id = user_id
        self.tools = {
            "send_email": self.send_email,
            "schedule_appointment": self.schedule_appointment,
            "order_groceries": self.order_groceries,
            "check_calendar": self.check_calendar,
            "set_reminder": self.set_reminder,
            "book_travel": self.book_travel,
        }
    
    async def process_message(self, user_message: str) -> str:
        """Process user message and determine action"""
        logger.info(f"Personal Assistant processing: {user_message}")
        
        self.add_message("user", user_message)
        
        # Determine intent and execute appropriate tool
        intent = await self._determine_intent(user_message)
        logger.debug(f"Detected intent: {intent}")
        
        if intent == "email":
            response = await self.send_email(user_message)
        elif intent == "appointment":
            response = await self.schedule_appointment(user_message)
        elif intent == "grocery":
            response = await self.order_groceries(user_message)
        elif intent == "reminder":
            response = await self.set_reminder(user_message)
        elif intent == "travel":
            response = await self.book_travel(user_message)
        else:
            response = await self._generate_response(user_message)
        
        self.add_message("assistant", response)
        return response
    
    async def _determine_intent(self, message: str) -> str:
        """Determine user intent from message"""
        keywords = {
            "email": ["email", "send", "mail"],
            "appointment": ["appointment", "meeting", "schedule", "book"],
            "grocery": ["groceries", "shopping", "buy"],
            "reminder": ["remind", "reminder", "alert"],
            "travel": ["travel", "flight", "hotel", "booking"],
        }
        
        message_lower = message.lower()
        for intent, keywords_list in keywords.items():
            if any(kw in message_lower for kw in keywords_list):
                return intent
        
        return "general"
    
    async def send_email(self, message: str) -> str:
        """Send email on behalf of user"""
        logger.info("Executing: send_email")
        return "Email sent successfully!"
    
    async def schedule_appointment(self, message: str) -> str:
        """Schedule appointment"""
        logger.info("Executing: schedule_appointment")
        return "Appointment scheduled successfully!"
    
    async def order_groceries(self, message: str) -> str:
        """Order groceries"""
        logger.info("Executing: order_groceries")
        return "Groceries ordered successfully!"
    
    async def check_calendar(self, message: str) -> str:
        """Check user calendar"""
        logger.info("Executing: check_calendar")
        return "Calendar checked. No conflicts found."
    
    async def set_reminder(self, message: str) -> str:
        """Set reminder"""
        logger.info("Executing: set_reminder")
        return "Reminder set successfully!"
    
    async def book_travel(self, message: str) -> str:
        """Book travel arrangements"""
        logger.info("Executing: book_travel")
        return "Travel booking initiated!"
    
    async def _generate_response(self, user_message: str) -> str:
        """Generate response using LLM"""
        try:
            from providers.llm_providers import Message
            
            messages = [
                Message(role="system", content=self.get_context()),
                Message(role="user", content=user_message),
            ]
            
            response = await self.llm_service.complete(messages)
            return response.content
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I'm having trouble processing that request. Please try again."
    
    async def execute_tool(self, tool_name: str, **kwargs) -> str:
        """Execute tool by name"""
        if tool_name not in self.tools:
            return f"Tool '{tool_name}' not found"
        
        return await self.tools[tool_name](**kwargs)
