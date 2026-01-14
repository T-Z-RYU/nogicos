# -*- coding: utf-8 -*-
"""
Prometheus Metrics for NogicOS Agent

Provides metrics collection for:
- Request counts and rates
- Latency histograms
- Success/failure rates
- Tool usage statistics
- Resource utilization
"""

from typing import Optional
import time
from contextlib import contextmanager

try:
    from prometheus_client import (
        Counter,
        Histogram,
        Gauge,
        Summary,
        CollectorRegistry,
        generate_latest,
        CONTENT_TYPE_LATEST,
        make_asgi_app,
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    print("[Warning] prometheus-client not installed. Run: pip install prometheus-client")


# Singleton metrics instance
_metrics_instance = None


class AgentMetrics:
    """
    Prometheus metrics collection for NogicOS Agent.
    
    Usage:
        metrics = AgentMetrics()
        
        # Record a request
        with metrics.track_request("browser_task"):
            result = await agent.run(task)
        
        # Record tool usage
        metrics.record_tool_call("read_file", success=True, duration=0.5)
    """
    
    # Histogram buckets for latency (in seconds)
    LATENCY_BUCKETS = (0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0)
    
    def __init__(self, registry: Optional["CollectorRegistry"] = None):
        if not PROMETHEUS_AVAILABLE:
            self._enabled = False
            return
        
        self._enabled = True
        self.registry = registry or CollectorRegistry()
        
        # Request metrics
        self.requests_total = Counter(
            "nogicos_agent_requests_total",
            "Total number of agent requests",
            ["task_type", "status"],
            registry=self.registry,
        )
        
        self.request_latency = Histogram(
            "nogicos_agent_request_latency_seconds",
            "Request latency in seconds",
            ["task_type"],
            buckets=self.LATENCY_BUCKETS,
            registry=self.registry,
        )
        
        self.request_in_progress = Gauge(
            "nogicos_agent_requests_in_progress",
            "Number of requests currently being processed",
            registry=self.registry,
        )
        
        # Success rate gauge (updated periodically)
        self.success_rate = Gauge(
            "nogicos_agent_success_rate",
            "Current success rate (0.0 to 1.0)",
            ["task_type"],
            registry=self.registry,
        )
        
        # Tool metrics
        self.tool_calls_total = Counter(
            "nogicos_agent_tool_calls_total",
            "Total number of tool calls",
            ["tool_name", "status"],
            registry=self.registry,
        )
        
        self.tool_latency = Histogram(
            "nogicos_agent_tool_latency_seconds",
            "Tool call latency in seconds",
            ["tool_name"],
            buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
            registry=self.registry,
        )
        
        # Iteration metrics
        self.iterations_total = Counter(
            "nogicos_agent_iterations_total",
            "Total number of agent iterations",
            registry=self.registry,
        )
        
        self.iterations_per_task = Histogram(
            "nogicos_agent_iterations_per_task",
            "Number of iterations per task",
            buckets=(1, 2, 3, 5, 7, 10, 15, 20),
            registry=self.registry,
        )
        
        # Error metrics
        self.errors_total = Counter(
            "nogicos_agent_errors_total",
            "Total number of errors",
            ["error_type"],
            registry=self.registry,
        )
        
        # Resource metrics
        self.browser_sessions_active = Gauge(
            "nogicos_agent_browser_sessions_active",
            "Number of active browser sessions",
            registry=self.registry,
        )
        
        self.memory_usage_bytes = Gauge(
            "nogicos_agent_memory_usage_bytes",
            "Current memory usage in bytes",
            registry=self.registry,
        )
        
        # Internal tracking for success rate calculation
        self._request_counts = {}
        self._success_counts = {}
    
    @contextmanager
    def track_request(self, task_type: str = "unknown"):
        """
        Context manager to track a request's metrics.
        
        Example:
            with metrics.track_request("browser"):
                result = await agent.run(task)
        """
        if not self._enabled:
            yield
            return
        
        self.request_in_progress.inc()
        start_time = time.time()
        success = True
        
        try:
            yield
        except Exception:
            success = False
            raise
        finally:
            duration = time.time() - start_time
            status = "success" if success else "failure"
            
            self.requests_total.labels(task_type=task_type, status=status).inc()
            self.request_latency.labels(task_type=task_type).observe(duration)
            self.request_in_progress.dec()
            
            # Update success rate tracking
            self._request_counts[task_type] = self._request_counts.get(task_type, 0) + 1
            if success:
                self._success_counts[task_type] = self._success_counts.get(task_type, 0) + 1
            
            # Update success rate gauge
            total = self._request_counts[task_type]
            successes = self._success_counts.get(task_type, 0)
            self.success_rate.labels(task_type=task_type).set(successes / total if total > 0 else 0)
    
    def record_request(
        self,
        task_type: str,
        success: bool,
        duration_seconds: float,
        iterations: int = 1,
    ):
        """Record metrics for a completed request"""
        if not self._enabled:
            return
        
        status = "success" if success else "failure"
        self.requests_total.labels(task_type=task_type, status=status).inc()
        self.request_latency.labels(task_type=task_type).observe(duration_seconds)
        self.iterations_total.inc(iterations)
        self.iterations_per_task.observe(iterations)
        
        # Update success rate
        self._request_counts[task_type] = self._request_counts.get(task_type, 0) + 1
        if success:
            self._success_counts[task_type] = self._success_counts.get(task_type, 0) + 1
        
        total = self._request_counts[task_type]
        successes = self._success_counts.get(task_type, 0)
        self.success_rate.labels(task_type=task_type).set(successes / total if total > 0 else 0)
    
    def record_tool_call(
        self,
        tool_name: str,
        success: bool,
        duration_seconds: float,
    ):
        """Record metrics for a tool call"""
        if not self._enabled:
            return
        
        status = "success" if success else "failure"
        self.tool_calls_total.labels(tool_name=tool_name, status=status).inc()
        self.tool_latency.labels(tool_name=tool_name).observe(duration_seconds)
    
    def record_error(self, error_type: str):
        """Record an error"""
        if not self._enabled:
            return
        
        self.errors_total.labels(error_type=error_type).inc()
    
    def set_browser_sessions(self, count: int):
        """Set the number of active browser sessions"""
        if not self._enabled:
            return
        
        self.browser_sessions_active.set(count)
    
    def update_memory_usage(self):
        """Update memory usage metric from psutil"""
        if not self._enabled:
            return
        
        try:
            import psutil
            process = psutil.Process()
            self.memory_usage_bytes.set(process.memory_info().rss)
        except:
            pass
    
    def get_metrics_output(self) -> bytes:
        """Generate Prometheus metrics output"""
        if not self._enabled:
            return b"# Prometheus metrics not available\n"
        
        return generate_latest(self.registry)
    
    def get_content_type(self) -> str:
        """Get the content type for Prometheus metrics"""
        if not self._enabled:
            return "text/plain"
        
        return CONTENT_TYPE_LATEST
    
    def create_asgi_app(self):
        """Create an ASGI app for serving metrics (for FastAPI mount)"""
        if not self._enabled:
            return None
        
        return make_asgi_app(registry=self.registry)


def get_metrics() -> Optional[AgentMetrics]:
    """Get the singleton metrics instance. Returns None if prometheus is not available."""
    global _metrics_instance
    if not PROMETHEUS_AVAILABLE:
        return None
    if _metrics_instance is None:
        _metrics_instance = AgentMetrics()
    return _metrics_instance


# FastAPI integration helper
def setup_metrics_endpoint(app, path: str = "/metrics"):
    """
    Setup Prometheus metrics endpoint for FastAPI app.
    
    Example:
        from fastapi import FastAPI
        from monitoring.prometheus.metrics import setup_metrics_endpoint
        
        app = FastAPI()
        setup_metrics_endpoint(app)
    """
    if not PROMETHEUS_AVAILABLE:
        print("[Warning] Prometheus not available, metrics endpoint not created")
        return
    
    metrics = get_metrics()
    metrics_app = metrics.create_asgi_app()
    
    if metrics_app:
        app.mount(path, metrics_app)
        print(f"[Prometheus] Metrics endpoint mounted at {path}")

