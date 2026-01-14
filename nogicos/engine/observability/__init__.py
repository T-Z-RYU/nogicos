# -*- coding: utf-8 -*-
"""
NogicOS Observability - Logging, tracing, and metrics

Includes:
- Basic logging (get_logger, setup_logging)
- Module tracing (ModuleTracer)
- LangSmith integration (langsmith_tracer)
- Performance metrics (PerformanceMetrics, PerformanceSLO)
"""

import logging
import os
from datetime import datetime
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Optional

# Log directory
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# LangSmith tracing (lazy import to avoid circular deps)
def get_langsmith_tracer():
    """Get LangSmith tracer module (lazy import)."""
    try:
        from engine.observability import langsmith_tracer
        return langsmith_tracer
    except ImportError:
        return None


_logging_initialized = False

def setup_logging(level: str = "INFO"):
    """Configure logging (only runs once)"""
    global _logging_initialized
    if _logging_initialized:
        return  # Prevent duplicate handlers
    
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console
    console = logging.StreamHandler()
    console.setLevel(log_level)
    console.setFormatter(formatter)
    
    # File
    log_file = f"nogicos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(
        os.path.join(LOG_DIR, log_file),
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Root logger
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(console)
    root.addHandler(file_handler)
    
    _logging_initialized = True
    logging.info("[NogicOS] Logging initialized")


def get_logger(name: str) -> logging.Logger:
    """Get logger for module"""
    return logging.getLogger(name)


@dataclass
class TraceSpan:
    """Trace span for operations"""
    module: str
    operation: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"
    error: Optional[str] = None


class ModuleTracer:
    """Module-level tracer"""

    def __init__(self, module: str):
        self._spans: list = []
        self.module = module
        self.logger = logging.getLogger(module)
    
    @contextmanager
    def trace(self, operation: str):
        """Trace an operation"""
        span = TraceSpan(
            module=self.module,
            operation=operation,
            start_time=datetime.now()
        )
        self.logger.debug(f"[START] {operation}")
        
        try:
            yield span
            span.status = "success"
        except Exception as e:
            span.status = "error"
            span.error = str(e)
            self.logger.error(f"[ERROR] {operation}: {e}")
            raise
        finally:
            span.end_time = datetime.now()
            duration = (span.end_time - span.start_time).total_seconds() * 1000
            if span.status == "success":
                self.logger.debug(f"[DONE] {operation} ({duration:.1f}ms)")
            self._spans.append(span)


# Performance metrics (Phase 0.25)
from .metrics import (
    PerformanceMetrics,
    LatencyHistogram,
    get_metrics,
    set_metrics,
)

# PerformanceSLO from config Import（Uniquedefine）
from ..config import PerformanceSLO

__all__ = [
    # Logging
    'setup_logging',
    'get_logger',
    'LOG_DIR',
    # Tracing
    'ModuleTracer',
    'TraceSpan',
    'get_langsmith_tracer',
    # Metrics (Phase 0.25)
    'PerformanceMetrics',
    'PerformanceSLO',
    'LatencyHistogram',
    'get_metrics',
    'set_metrics',
]
