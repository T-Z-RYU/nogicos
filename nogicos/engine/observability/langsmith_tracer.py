# -*- coding: utf-8 -*-
"""
LangSmith Tracer - Unified observability for NogicOS Agent

This module provides tracing integration with LangSmith for:
- Request/response logging
- Tool execution tracking
- Performance monitoring
- Error analysis

Usage:
    from engine.observability.langsmith_tracer import trace_agent_run, trace_tool_call

    @trace_agent_run
    async def process_task(task: str) -> str:
        ...
        
    @trace_tool_call
    async def execute_tool(tool_name: str, args: dict) -> dict:
        ...
"""

import os
import time
import functools
from typing import Any, Callable, Optional, Dict, List
from contextlib import contextmanager

# Configure LangSmith environment before importing
from config import LANGSMITH_TRACING, LANGSMITH_PROJECT, LANGSMITH_API_KEY

if LANGSMITH_API_KEY:
    os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGSMITH_PROJECT"] = LANGSMITH_PROJECT
    os.environ["LANGSMITH_TRACING"] = "true" if LANGSMITH_TRACING else "false"

# Try to import LangSmith
try:
    from langsmith import traceable, Client
    from langsmith.run_trees import RunTree
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False
    traceable = None
    Client = None
    RunTree = None

# Logging
from engine.observability import get_logger
logger = get_logger("langsmith_tracer")


def is_enabled() -> bool:
    """Check if LangSmith tracing is enabled and configured."""
    return LANGSMITH_AVAILABLE and LANGSMITH_TRACING and bool(LANGSMITH_API_KEY)


def get_client() -> Optional["Client"]:
    """Get LangSmith client instance."""
    if not is_enabled():
        return None
    try:
        return Client()
    except Exception as e:
        logger.warning(f"Failed to create LangSmith client: {e}")
        return None


# ===========================================
# Decorators for Tracing
# ===========================================

def trace_agent_run(
    name: Optional[str] = None,
    run_type: str = "chain",
    metadata: Optional[Dict[str, Any]] = None,
):
    """
    Decorator to trace an agent run with LangSmith.
    
    Args:
        name: Custom name for the trace (defaults to function name)
        run_type: Type of run (chain, llm, tool, etc.)
        metadata: Additional metadata to attach
        
    Example:
        @trace_agent_run(name="process_task", metadata={"version": "1.0"})
        async def process_task(task: str) -> str:
            ...
    """
    def decorator(func: Callable):
        if not is_enabled():
            return func
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            trace_name = name or func.__name__
            try:
                # Use LangSmith traceable decorator
                traced_func = traceable(
                    name=trace_name,
                    run_type=run_type,
                    metadata=metadata or {},
                )(func)
                return await traced_func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Tracing error in {trace_name}: {e}")
                # Fallback to original function
                return await func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            trace_name = name or func.__name__
            try:
                traced_func = traceable(
                    name=trace_name,
                    run_type=run_type,
                    metadata=metadata or {},
                )(func)
                return traced_func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Tracing error in {trace_name}: {e}")
                return func(*args, **kwargs)
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def trace_tool_call(
    tool_name: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
):
    """
    Decorator to trace a tool call with LangSmith.
    
    Args:
        tool_name: Name of the tool (defaults to function name)
        metadata: Additional metadata to attach
        
    Example:
        @trace_tool_call(tool_name="browser_navigate")
        async def navigate(url: str) -> dict:
            ...
    """
    def decorator(func: Callable):
        if not is_enabled():
            return func
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            name = tool_name or func.__name__
            start_time = time.time()
            
            try:
                traced_func = traceable(
                    name=f"tool:{name}",
                    run_type="tool",
                    metadata={
                        "tool_name": name,
                        "args": str(kwargs)[:500],  # Truncate long args
                        **(metadata or {}),
                    },
                )(func)
                result = await traced_func(*args, **kwargs)
                
                # Log success
                duration_ms = (time.time() - start_time) * 1000
                logger.debug(f"Tool {name} completed in {duration_ms:.0f}ms")
                
                return result
                
            except Exception as e:
                # Log error
                duration_ms = (time.time() - start_time) * 1000
                logger.error(f"Tool {name} failed after {duration_ms:.0f}ms: {e}")
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            name = tool_name or func.__name__
            start_time = time.time()
            
            try:
                traced_func = traceable(
                    name=f"tool:{name}",
                    run_type="tool",
                    metadata={
                        "tool_name": name,
                        "args": str(kwargs)[:500],
                        **(metadata or {}),
                    },
                )(func)
                result = traced_func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                logger.debug(f"Tool {name} completed in {duration_ms:.0f}ms")
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(f"Tool {name} failed after {duration_ms:.0f}ms: {e}")
                raise
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


# ===========================================
# Context Manager for Manual Tracing
# ===========================================

@contextmanager
def trace_span(
    name: str,
    run_type: str = "chain",
    inputs: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
):
    """
    Context manager for manual span tracing.
    
    Args:
        name: Name of the span
        run_type: Type of run
        inputs: Input data to log
        metadata: Additional metadata
        
    Example:
        with trace_span("process_step", inputs={"task": task}) as span:
            result = do_something()
            span.end(outputs={"result": result})
    """
    if not is_enabled():
        # No-op context manager
        class NoOpSpan:
            def end(self, outputs=None, error=None):
                pass
        yield NoOpSpan()
        return
    
    try:
        run_tree = RunTree(
            name=name,
            run_type=run_type,
            inputs=inputs or {},
            extra={"metadata": metadata or {}},
        )
        
        class Span:
            def __init__(self, tree):
                self.tree = tree
                self.start_time = time.time()
            
            def end(self, outputs=None, error=None):
                duration_ms = (time.time() - self.start_time) * 1000
                self.tree.end(
                    outputs=outputs or {},
                    error=str(error) if error else None,
                )
                self.tree.post()
        
        span = Span(run_tree)
        yield span
        
    except Exception as e:
        logger.error(f"Failed to create trace span: {e}")
        class NoOpSpan:
            def end(self, outputs=None, error=None):
                pass
        yield NoOpSpan()


# ===========================================
# Anthropic Client Wrapper
# ===========================================

def wrap_anthropic_client(client):
    """
    Wrap Anthropic client with LangSmith tracing.
    
    Args:
        client: Anthropic client instance
        
    Returns:
        Wrapped client with tracing enabled
    """
    if not is_enabled():
        return client
    
    try:
        from langsmith.wrappers import wrap_anthropic
        wrapped = wrap_anthropic(client)
        logger.info("[LangSmith] Anthropic client wrapped for tracing")
        return wrapped
    except ImportError:
        logger.warning("[LangSmith] wrap_anthropic not available")
        return client
    except Exception as e:
        logger.error(f"[LangSmith] Failed to wrap Anthropic client: {e}")
        return client


# ===========================================
# Feedback & Evaluation
# ===========================================

def log_feedback(
    run_id: str,
    key: str,
    score: float,
    comment: Optional[str] = None,
):
    """
    Log feedback for a run to LangSmith.
    
    Args:
        run_id: ID of the run to provide feedback for
        key: Feedback key (e.g., "correctness", "helpfulness")
        score: Score value (0-1)
        comment: Optional comment
    """
    if not is_enabled():
        return
    
    try:
        client = get_client()
        if client:
            client.create_feedback(
                run_id=run_id,
                key=key,
                score=score,
                comment=comment,
            )
            logger.debug(f"Logged feedback for run {run_id}: {key}={score}")
    except Exception as e:
        logger.error(f"Failed to log feedback: {e}")


def log_evaluation_result(
    run_id: str,
    metrics: Dict[str, float],
    metadata: Optional[Dict[str, Any]] = None,
):
    """
    Log evaluation metrics for a run.
    
    Args:
        run_id: ID of the run
        metrics: Dictionary of metric name -> value
        metadata: Additional metadata
    """
    if not is_enabled():
        return
    
    try:
        client = get_client()
        if client:
            for key, score in metrics.items():
                client.create_feedback(
                    run_id=run_id,
                    key=key,
                    score=score,
                    comment=str(metadata) if metadata else None,
                )
            logger.debug(f"Logged {len(metrics)} metrics for run {run_id}")
    except Exception as e:
        logger.error(f"Failed to log evaluation result: {e}")


# ===========================================
# Initialization
# ===========================================

def init_langsmith():
    """
    Initialize LangSmith tracing.
    
    Call this at application startup to verify configuration.
    """
    if not LANGSMITH_AVAILABLE:
        logger.warning("[LangSmith] SDK not installed. Run: pip install langsmith")
        return False
    
    if not LANGSMITH_API_KEY:
        logger.warning("[LangSmith] API key not configured. Set LANGSMITH_API_KEY in api_keys.py")
        return False
    
    if not LANGSMITH_TRACING:
        logger.info("[LangSmith] Tracing disabled by configuration")
        return False
    
    # Test connection
    try:
        client = get_client()
        if client:
            # Simple connectivity test
            logger.info(f"[LangSmith] Tracing enabled for project: {LANGSMITH_PROJECT}")
            logger.info(f"[LangSmith] Dashboard: https://smith.langchain.com/o/default/projects/p/{LANGSMITH_PROJECT}")
            return True
    except Exception as e:
        logger.error(f"[LangSmith] Failed to initialize: {e}")
    
    return False


# Auto-initialize on module import
if is_enabled():
    init_langsmith()

