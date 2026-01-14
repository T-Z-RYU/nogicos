# -*- coding: utf-8 -*-
"""
NogicOS Configuration
"""

import os

# Default LLM Model
DEFAULT_MODEL = "claude-opus-4-5-20251101"

# ===========================================
# LangSmith Configuration (Observability)
# ===========================================
# To enable LangSmith tracing, set your API key in environment or api_keys.py
# Get your API key at: https://smith.langchain.com/settings
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "true").lower() == "true"
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "nogicos")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY", "")

# Load from api_keys.py if not set in environment
if not LANGSMITH_API_KEY:
    try:
        from api_keys import LANGSMITH_API_KEY as _KEY
        LANGSMITH_API_KEY = _KEY
    except ImportError:
        pass

# ===========================================
# DSPy Configuration (Prompt Optimization)
# ===========================================
DSPY_ENABLED = os.getenv("DSPY_ENABLED", "true").lower() == "true"
DSPY_CACHE_DIR = os.path.join(os.path.dirname(__file__), "data", "dspy_cache")

# Ensure DSPy cache directory exists
os.makedirs(DSPY_CACHE_DIR, exist_ok=True)

# Browser Settings
BROWSER_HEADLESS = False
BROWSER_SLOW_MO = 100
BROWSER_WIDTH = 1280
BROWSER_HEIGHT = 720
BROWSER_TIMEOUT = 15000
BROWSER_NAVIGATION_TIMEOUT = 30000

# Knowledge Base Settings
KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(__file__), "knowledge", "data")
KNOWLEDGE_MATCH_THRESHOLD = 0.8

# Logging
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
LOG_LEVEL = "INFO"

# Ensure directories exist
os.makedirs(KNOWLEDGE_BASE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

