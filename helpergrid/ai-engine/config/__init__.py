#!/usr/bin/env python3
"""
Initialize config package
"""

from .environment import settings
from .logging_config import setup_logging

__all__ = ["settings", "setup_logging"]
