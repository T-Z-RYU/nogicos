# -*- coding: utf-8 -*-
"""
NogicOS API Keys Configuration

Copy this file to api_keys.py and fill in your API keys.
"""

# Google API Key (Gemini)
GOOGLE_API_KEY = ""

# Anthropic API Key (Claude Opus 4.5)
ANTHROPIC_API_KEY = ""

# OpenAI API Key
OPENAI_API_KEY = ""

# LangSmith API Key (Observability & Tracing)
# Get your key at: https://smith.langchain.com/settings
LANGSMITH_API_KEY = ""


def setup_env():
    """Set API keys as environment variables"""
    import os
    
    if GOOGLE_API_KEY:
        os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
    if ANTHROPIC_API_KEY:
        os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY
    if OPENAI_API_KEY:
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    if LANGSMITH_API_KEY:
        os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY
        os.environ["LANGSMITH_TRACING"] = "true"
        os.environ["LANGSMITH_PROJECT"] = "nogicos"
    
    print("[NogicOS] API Keys configured")


if __name__ == "__main__":
    setup_env()
    print(f"GOOGLE_API_KEY: {'Set' if GOOGLE_API_KEY else 'Not set'}")
    print(f"ANTHROPIC_API_KEY: {'Set' if ANTHROPIC_API_KEY else 'Not set'}")
    print(f"OPENAI_API_KEY: {'Set' if OPENAI_API_KEY else 'Not set'}")

