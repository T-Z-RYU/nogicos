"""
NogicOS Performance指标收集
====================

用于 SLO Monitor和Alert。

指标Class型:
1. Delayed分布 (Histogram) - 计算分位数
2. 计数器 (Counter) - 累计Statistics
3. 仪Table盘 (Gauge) - 瞬时值

参考:
- Prometheus 指标模型
- OpenTelemetry Metrics
"""

import time
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any, TYPE_CHECKING
from collections import deque
from enum import Enum
import asyncio

if TYPE_CHECKING:
    from ..config import PerformanceSLO

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """指标Class型"""
    HISTOGRAM = "histogram"
    COUNTER = "counter"
    GAUGE = "gauge"


@dataclass
class LatencyHistogram:
    """
    Delayed直方Graph - 计算分位数
    
    Usage滑动WindowSave最近 N 个Sample
    """
    
    name: str
    window_size: int = 100  # SwipeWindowSize
    _samples: deque = field(default_factory=lambda: deque(maxlen=100))
    
    def __post_init__(self):
        self._samples = deque(maxlen=self.window_size)
    
    def record(self, duration_ms: float):
        """记录一个DelayedSample"""
        self._samples.append(duration_ms)
    
    def percentile(self, p: float) -> float:
        """
        计算分位数
        
        Args:
            p: 分位数 (0-100)，如 50 Table示 P50
            
        Returns:
            分位数值
        """
        if not self._samples:
            return 0
        sorted_samples = sorted(self._samples)
        idx = int(len(sorted_samples) * p / 100)
        return sorted_samples[min(idx, len(sorted_samples) - 1)]
    
    @property
    def p50(self) -> float:
        """P50 (Medium位数)"""
        return self.percentile(50)
    
    @property
    def p90(self) -> float:
        """P90"""
        return self.percentile(90)
    
    @property
    def p99(self) -> float:
        """P99"""
        return self.percentile(99)
    
    @property
    def avg(self) -> float:
        """Average值"""
        return sum(self._samples) / len(self._samples) if self._samples else 0
    
    @property
    def min(self) -> float:
        """Min值"""
        return min(self._samples) if self._samples else 0
    
    @property
    def max(self) -> float:
        """Max值"""
        return max(self._samples) if self._samples else 0
    
    @property
    def count(self) -> int:
        """SampleCount"""
        return len(self._samples)
    
    def to_dict(self) -> dict:
        """Export为Dict"""
        return {
            "name": self.name,
            "count": self.count,
            "p50": self.p50,
            "p90": self.p90,
            "p99": self.p99,
            "avg": self.avg,
            "min": self.min,
            "max": self.max,
        }


class PerformanceMetrics:
    """
    Performance指标收集器
    
    UsageExample:
    ```python
    metrics = get_metrics()
    
    # RecordToolCallDelayed
    with metrics.measure_latency("tool", "window_click"):
        await execute_tool(...)
    
    # OrUsageAsyncUpDowntext
    async with metrics.measure_latency("llm", "claude_call"):
        response = await call_claude(...)
    
    # Check SLO
    violations = metrics.check_slo(slo_config)
    ```
    """
    
    def __init__(self):
        # Delayedmetric
        self._tool_latencies: Dict[str, LatencyHistogram] = {}
        self._llm_latency = LatencyHistogram("llm_response")
        self._screenshot_latency = LatencyHistogram("screenshot")
        
        # Counter
        self._tool_calls = 0
        self._tool_errors = 0
        self._tool_retries = 0
        self._tasks_completed = 0
        self._tasks_failed = 0
        
        # EventbusStatistics
        self._events_processed = 0
        self._events_dropped = 0
        
        # resourceSourceUsage
        self._peak_memory_mb = 0
        self._current_memory_mb = 0
        
        # IterateStatistics
        self._total_iterations = 0
        
        # SLO violationCallback
        self._slo_violation_callbacks: List[Callable] = []
        
        # StartTime
        self._start_time = time.time()
    
    def measure_latency(self, category: str, name: str) -> "LatencyMeasurer":
        """
        CreateDelayed测量UpDown文管理器
        
        Args:
            category: 分Class ("tool", "llm", "screenshot")
            name: 具体名称
            
        Returns:
            UpDown文管理器
        """
        return LatencyMeasurer(self, category, name)
    
    def record_tool_call(
        self, 
        tool_name: str, 
        duration_ms: float, 
        success: bool, 
        retried: bool = False
    ):
        """
        记录Tool调用
        
        Args:
            tool_name: Tool名称
            duration_ms: ExecuteTime (ms)
            success: YesNoSuccess
            retried: YesNoRetry过
        """
        # Delayed
        if tool_name not in self._tool_latencies:
            self._tool_latencies[tool_name] = LatencyHistogram(f"tool_{tool_name}")
        self._tool_latencies[tool_name].record(duration_ms)
        
        # Count
        self._tool_calls += 1
        if not success:
            self._tool_errors += 1
        if retried:
            self._tool_retries += 1
    
    def record_llm_call(self, duration_ms: float):
        """记录 LLM 调用"""
        self._llm_latency.record(duration_ms)
    
    def record_screenshot(self, duration_ms: float):
        """记录截Graph操作"""
        self._screenshot_latency.record(duration_ms)
    
    def record_task_result(self, success: bool):
        """记录任务Result"""
        if success:
            self._tasks_completed += 1
        else:
            self._tasks_failed += 1
    
    def record_iteration(self):
        """记录一次Iterate"""
        self._total_iterations += 1
    
    def record_event_stats(self, processed: int, dropped: int):
        """记录EventStatistics"""
        self._events_processed = processed
        self._events_dropped = dropped
    
    def record_memory_usage(self, memory_mb: float):
        """记录Inner存Usage"""
        self._current_memory_mb = memory_mb
        self._peak_memory_mb = max(self._peak_memory_mb, memory_mb)
    
    def check_slo(self, slo: "PerformanceSLO") -> Dict[str, bool]:
        """
        Check SLO YesNoFull足
        
        Args:
            slo: SLO Config
            
        Returns:
            Dict[metric_name, is_passing]
        """
        results = {}
        
        # Delayed SLO
        for tool_name, hist in self._tool_latencies.items():
            if hist.count > 0:
                results[f"{tool_name}_p50"] = hist.p50 <= slo.tool_execution_p50_ms
                results[f"{tool_name}_p99"] = hist.p99 <= slo.tool_execution_p99_ms
        
        if self._llm_latency.count > 0:
            results["llm_p50"] = self._llm_latency.p50 <= slo.llm_response_p50_ms
            results["llm_p99"] = self._llm_latency.p99 <= slo.llm_response_p99_ms
        
        if self._screenshot_latency.count > 0:
            results["screenshot"] = self._screenshot_latency.p50 <= slo.screenshot_capture_ms
        
        # canrelyproperty SLO
        total_tasks = self._tasks_completed + self._tasks_failed
        if total_tasks > 0:
            success_rate = self._tasks_completed / total_tasks
            results["task_success_rate"] = success_rate >= slo.task_success_rate
        
        if self._tool_calls > 0:
            retry_rate = self._tool_retries / self._tool_calls
            results["tool_retry_rate"] = retry_rate <= slo.tool_retry_rate
        
        # EventDiscardrate
        total_events = self._events_processed + self._events_dropped
        if total_events > 0:
            drop_rate = self._events_dropped / total_events
            results["event_drop_rate"] = drop_rate <= slo.event_drop_rate
        
        # resourceSource SLO
        results["memory_usage"] = self._current_memory_mb <= slo.max_memory_mb
        
        # CheckviolationandCallback
        violations = [k for k, v in results.items() if not v]
        if violations:
            for callback in self._slo_violation_callbacks:
                try:
                    callback(violations)
                except Exception as e:
                    logger.error(f"SLO violation callback error: {e}")
        
        return results
    
    def on_slo_violation(self, callback: Callable[[List[str]], None]):
        """Register SLO 违规Callback"""
        self._slo_violation_callbacks.append(callback)
    
    def get_summary(self) -> dict:
        """Get指标摘要"""
        uptime = time.time() - self._start_time
        
        return {
            "uptime_seconds": uptime,
            "tool_calls": self._tool_calls,
            "tool_errors": self._tool_errors,
            "tool_error_rate": self._tool_errors / max(1, self._tool_calls),
            "tool_retries": self._tool_retries,
            "tool_retry_rate": self._tool_retries / max(1, self._tool_calls),
            "tasks_completed": self._tasks_completed,
            "tasks_failed": self._tasks_failed,
            "task_success_rate": self._tasks_completed / max(1, self._tasks_completed + self._tasks_failed),
            "total_iterations": self._total_iterations,
            "llm_latency": self._llm_latency.to_dict(),
            "screenshot_latency": self._screenshot_latency.to_dict(),
            "tool_latencies": {
                name: h.to_dict()
                for name, h in self._tool_latencies.items()
            },
            "events_processed": self._events_processed,
            "events_dropped": self._events_dropped,
            "current_memory_mb": self._current_memory_mb,
            "peak_memory_mb": self._peak_memory_mb,
        }
    
    def reset(self):
        """Reset所有指标"""
        self._tool_latencies.clear()
        self._llm_latency = LatencyHistogram("llm_response")
        self._screenshot_latency = LatencyHistogram("screenshot")
        self._tool_calls = 0
        self._tool_errors = 0
        self._tool_retries = 0
        self._tasks_completed = 0
        self._tasks_failed = 0
        self._events_processed = 0
        self._events_dropped = 0
        self._total_iterations = 0
        self._start_time = time.time()


class LatencyMeasurer:
    """
    Delayed测量UpDown文管理器
    
    支持Sync和AsyncUsage
    """
    
    def __init__(self, metrics: PerformanceMetrics, category: str, name: str):
        self.metrics = metrics
        self.category = category
        self.name = name
        self.start_time: Optional[float] = None
        self.duration_ms: float = 0
    
    def __enter__(self) -> "LatencyMeasurer":
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.duration_ms = (time.perf_counter() - self.start_time) * 1000
        self._record(exc_type is None)
    
    async def __aenter__(self) -> "LatencyMeasurer":
        self.start_time = time.perf_counter()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.duration_ms = (time.perf_counter() - self.start_time) * 1000
        self._record(exc_type is None)
    
    def _record(self, success: bool):
        """记录测量Result"""
        if self.category == "tool":
            self.metrics.record_tool_call(self.name, self.duration_ms, success)
        elif self.category == "llm":
            self.metrics.record_llm_call(self.duration_ms)
        elif self.category == "screenshot":
            self.metrics.record_screenshot(self.duration_ms)


# ========== SingletonPattern ==========

_metrics_instance: Optional[PerformanceMetrics] = None


def get_metrics() -> PerformanceMetrics:
    """GetGlobal指标Instance（Singleton）"""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = PerformanceMetrics()
    return _metrics_instance


def set_metrics(metrics: PerformanceMetrics):
    """SetGlobal指标Instance（用于Test）"""
    global _metrics_instance
    _metrics_instance = metrics
