# -*- coding: utf-8 -*-
"""
Simple LangGraph wrapper for LangSmith Studio testing.

This is a minimal wrapper that works with LangSmith Studio
without requiring all NogicOS dependencies.
"""

import operator
from typing import Annotated, TypedDict, Literal, List, Dict, Any

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver


class AgentState(TypedDict):
    """State for the LangGraph workflow"""
    messages: Annotated[List[Dict[str, Any]], operator.add]
    task: str
    response: str


async def extract_task(state: AgentState) -> dict:
    """Extract task from the latest user message."""
    messages = state.get("messages", [])
    task = ""
    for msg in reversed(messages):
        if isinstance(msg, dict) and msg.get("role") == "user":
            task = msg.get("content", "")
            break
    return {"task": task}


async def run_agent(state: AgentState) -> dict:
    """Run agent - simplified version for testing."""
    task = state.get("task", "")
    
    # For now, just echo back the task
    response = f"收到任务: {task}\n\n(这Yes LangGraph Studio Test模式，完整功能请用 hive_server.py)"
    
    return {
        "response": response,
        "messages": [{"role": "assistant", "content": response}],
    }


# Create graph
workflow = StateGraph(AgentState)
workflow.add_node("extract_task", extract_task)
workflow.add_node("run_agent", run_agent)
workflow.add_edge(START, "extract_task")
workflow.add_edge("extract_task", "run_agent")
workflow.add_edge("run_agent", END)

# Export for langgraph dev
graph = workflow

