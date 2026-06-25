#!/usr/bin/env python3
"""
Initialize routes package
"""

from . import health_routes
from . import llm_routes
from . import agent_routes
from . import nlp_routes
from . import embedding_routes
from . import integration_routes

__all__ = [
    "health_routes",
    "llm_routes",
    "agent_routes",
    "nlp_routes",
    "embedding_routes",
    "integration_routes",
]
