# -*- coding: utf-8 -*-
"""
LangGraph Wrapper for NogicOS ReAct Agent

This module wraps the existing ReActAgent as a LangGraph node,
enabling LangSmith Studio visualization and debugging without rewriting the agent.

Usage:
    # Start with LangGraph Studio
    cd nogicos
    langgraph dev
    
    # Or programmatically
    from engine.langgraph_wrapper import app
    result = await app.ainvoke({"messages": [{"role": "user", "content": "桌面有什么File"}]})

Benefits:
    - Visual debugging in LangSmith Studio
    - Persistent execution (resume from failures)
    - Human-in-the-loop capabilities
    - Full tracing in LangSmith
"""

import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load API keys from api_keys.py
try:
    from api_keys import setup_env
    setup_env()
except ImportError:
    print("[LangGraph] Warning: api_keys.py not found, using environment variables")

import asyncio
import operator
from typing import Annotated, TypedDict, Literal, Optional, List, Dict, Any

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# Import our existing agent
from engine.agent.react_agent import ReActAgent, AgentResult
from engine.observability import get_logger

logger = get_logger("langgraph_wrapper")


# ===========================================
# State Definition
# ===========================================

class AgentState(TypedDict):
    """State for the LangGraph workflow"""
    # Messages use add operator for accumulation
    messages: Annotated[List[Dict[str, Any]], operator.add]
    # Task extracted from last user message
    task: str
    # Session ID for context
    session_id: str
    # Agent result
    result: Optional[AgentResult]
    # Iteration count (for debugging)
    iteration: int


# ===========================================
# Node Functions
# ===========================================

async def extract_task(state: AgentState) -> dict:
    """
    Extract task from the latest user message.
    
    This is a preprocessing node that prepares the task for the agent.
    """
    messages = state.get("messages", [])
    
    # Find the last user message
    task = ""
    for msg in reversed(messages):
        if isinstance(msg, dict) and msg.get("role") == "user":
            content = msg.get("content", "")
            if isinstance(content, str):
                task = content
                break
            elif isinstance(content, list):
                # Handle parts format
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        task = part.get("text", "")
                        break
                if task:
                    break
    
    logger.info(f"[LangGraph] Extracted task: {task[:50]}...")
    
    return {
        "task": task,
        "iteration": state.get("iteration", 0) + 1,
    }


async def run_agent(state: AgentState) -> dict:
    """
    Run the NogicOS ReAct Agent.
    
    This node wraps our existing agent implementation,
    allowing us to use LangGraph's features without rewriting the agent.
    """
    task = state.get("task", "")
    session_id = state.get("session_id", "default")
    
    if not task:
        logger.warning("[LangGraph] No task provided")
        return {
            "result": AgentResult(
                success=False,
                response="No task provided",
                error="Empty task",
            ),
            "messages": [{"role": "assistant", "content": "请告诉我你想做什么？"}],
        }
    
    logger.info(f"[LangGraph] Running agent for task: {task[:50]}...")
    
    # Create and run agent
    agent = ReActAgent(
        status_server=None,  # No WebSocket in LangGraph mode
        max_iterations=20,
    )
    
    try:
        result = await agent.run(
            task=task,
            session_id=session_id,
        )
        
        logger.info(f"[LangGraph] Agent completed: success={result.success}, iterations={result.iterations}")
        
        # Format response as message
        response_message = {
            "role": "assistant",
            "content": result.response if result.success else f"Error: {result.error}",
        }
        
        return {
            "result": result,
            "messages": [response_message],
        }
        
    except Exception as e:
        logger.error(f"[LangGraph] Agent error: {e}")
        return {
            "result": AgentResult(
                success=False,
                response="",
                error=str(e),
            ),
            "messages": [{"role": "assistant", "content": f"Execute出错: {str(e)}"}],
        }


def should_continue(state: AgentState) -> Literal["continue", "end"]:
    """
    Determine if the agent should continue or end.
    
    For now, we always end after one agent run.
    This can be extended for multi-turn conversations or retry logic.
    """
    result = state.get("result")
    
    if result is None:
        return "continue"
    
    # Check if we need to retry (could add retry logic here)
    if not result.success and state.get("iteration", 0) < 3:
        # Could implement retry logic
        pass
    
    return "end"


# ===========================================
# Graph Construction
# ===========================================

def create_graph() -> StateGraph:
    """
    Create the LangGraph workflow for NogicOS.
    
    Graph structure:
        START → extract_task → run_agent → END
                                   ↑
                                   └── (optional retry loop)
    """
    # Create graph with state
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("extract_task", extract_task)
    workflow.add_node("run_agent", run_agent)
    
    # Add edges
    workflow.add_edge(START, "extract_task")
    workflow.add_edge("extract_task", "run_agent")
    
    # Conditional edge for potential retry/continuation
    workflow.add_conditional_edges(
        "run_agent",
        should_continue,
        {
            "continue": "run_agent",  # Retry
            "end": END,
        }
    )
    
    return workflow


def create_app(checkpointer=None):
    """
    Create the compiled LangGraph app.
    
    Args:
        checkpointer: Optional checkpoint saver for persistence
        
    Returns:
        Compiled LangGraph app
    """
    workflow = create_graph()
    
    # Use memory saver for persistence if not provided
    if checkpointer is None:
        checkpointer = MemorySaver()
    
    # Compile with checkpointer
    app = workflow.compile(checkpointer=checkpointer)
    
    return app


# ===========================================
# Default App Instance
# ===========================================

# Create default app instance
app = create_app()


# ===========================================
# Convenience Functions
# ===========================================

async def run_task(
    task: str,
    session_id: str = "default",
    thread_id: str = "default",
) -> AgentResult:
    """
    Convenience function to run a task through the LangGraph app.
    
    Args:
        task: User task/question
        session_id: Session ID for context
        thread_id: Thread ID for LangGraph checkpointing
        
    Returns:
        AgentResult from the agent
    """
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {
        "messages": [{"role": "user", "content": task}],
        "task": "",
        "session_id": session_id,
        "result": None,
        "iteration": 0,
    }
    
    final_state = await app.ainvoke(initial_state, config=config)
    
    return final_state.get("result") or AgentResult(
        success=False,
        response="",
        error="No result from agent",
    )


# ===========================================
# Entry Point for langgraph dev
# ===========================================

# This is what LangGraph Studio will use
graph = create_graph()


if __name__ == "__main__":
    # Test the wrapper
    async def test():
        result = await run_task("当BeforeDirectory有什么File")
        print(f"Success: {result.success}")
        print(f"Response: {result.response}")
        print(f"Iterations: {result.iterations}")
    
    asyncio.run(test())

