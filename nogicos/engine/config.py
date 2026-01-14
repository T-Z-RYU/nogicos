"""
NogicOS Config管理
================

集Medium管理所有ConfigArgument，支持EnvironmentVariable覆盖。

Package含:
- AgentConfig: Agent ExecuteArgument
- PerformanceSLO: PerformanceService水平Target
- SecurityConfig: Security相OffConfig

参考:
- 12-Factor App Config管理
- ByteBot ExecuteArgument
"""

import os
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


# ========== Performance SLO ==========

@dataclass
class PerformanceSLO:
    """
    PerformanceService水平Target (Service Level Objectives)
    
    定义SystemPerformance的量化指标，用于Monitor和Alert
    """
    
    # ========== Delayed SLO ==========
    tool_execution_p50_ms: int = 200       # ToolExecute P50 Delayed
    tool_execution_p99_ms: int = 2000      # ToolExecute P99 Delayed
    llm_response_p50_ms: int = 3000        # LLM Response P50 Delayed
    llm_response_p99_ms: int = 15000       # LLM Response P99 Delayed
    screenshot_capture_ms: int = 500       # captureGraphCatchDelayed
    
    # ========== throughputamount SLO ==========
    max_concurrent_tasks: int = 3          # MaxConcurrentTasknumber
    tool_calls_per_minute: int = 60        # eachMinuteToolCallnumber
    iterations_per_task: int = 20          # eachTaskMaxIteratenumber
    
    # ========== resourceSource SLO ==========
    max_memory_mb: int = 500               # MaxInnerstoreUsage
    max_cpu_percent: int = 30              # Max CPU Usagerate
    max_screenshot_cache_mb: int = 50      # captureGraphCacheUplimit
    
    # ========== canrelyproperty SLO ==========
    task_success_rate: float = 0.85        # TaskSuccessrate >= 85%
    tool_retry_rate: float = 0.10          # ToolRetryrate <= 10%
    event_drop_rate: float = 0.01          # EventDiscardrate <= 1%


# ========== SecurityConfig ==========

@dataclass
class SecurityConfig:
    """Security相OffConfig"""
    
    # sensitiveToolList（NeedUserConfirm）
    sensitive_tools: List[str] = field(default_factory=lambda: [
        "delete_file",
        "send_message", 
        "window_type",
        "execute_command",
        "modify_system_settings",
    ])
    
    # YesNoforceConfirmsensitiveAction
    require_confirm_for_sensitive: bool = True
    
    # Prompt injectDetection
    enable_prompt_injection_detection: bool = True
    
    # sensitiveDataPattern（regexTablereachstyle）
    sensitive_data_patterns: List[str] = field(default_factory=lambda: [
        r"\b\d{16}\b",                    # trustusecard number
        r"\b\d{3}-\d{2}-\d{4}\b",         # SSN
        r"password\s*[:=]\s*\S+",         # Password
        r"api[_-]?key\s*[:=]\s*\S+",      # API Key
    ])
    
    # MaxAllow's ToolArgumentLength
    max_tool_param_length: int = 10000


# ========== Agent Config ==========

@dataclass
class AgentConfig:
    """
    Agent Config - 支持EnvironmentVariable覆盖
    
    UsageExample:
    ```python
    # fromEnvironmentVariableLoad
    config = AgentConfig.from_env()
    
    # VerifyConfig
    errors = config.validate()
    if errors:
        raise ValueError(f"Config errors: {errors}")
    ```
    """
    
    # ========== ExecuteArgument ==========
    screenshot_delay_ms: int = 750
    context_compression_threshold: float = 0.75
    max_iterations: int = 20
    iteration_timeout_s: int = 120
    
    # ========== API Argument ==========
    claude_model: str = "claude-sonnet-4-20250514"
    claude_timeout_s: int = 60
    max_retries: int = 3
    retry_delay_s: float = 1.0
    
    # ========== ConcurrentArgument ==========
    max_concurrent_tasks: int = 3
    max_api_concurrency: int = 2
    
    # ========== Persistence ==========
    db_path: str = "nogicos_tasks.db"
    checkpoint_interval: int = 5  # each N timeIterateSaveCheckPoint
    
    # ========== Performance ==========
    slo: PerformanceSLO = field(default_factory=PerformanceSLO)
    enable_performance_monitoring: bool = True
    metrics_export_interval_s: int = 60
    
    # ========== Security ==========
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    # ========== functionOnOff (Feature Flags) ==========
    enable_dual_agent: bool = False       # Enabledoublelayer Agent
    enable_incremental_checkpoint: bool = True  # EnableincreaseamountCheckPoint
    enable_backpressure_bus: bool = False  # EnablebackpressureEventbus
    enable_prompt_caching: bool = True    # Enable Prompt Caching
    
    @classmethod
    def from_env(cls) -> "AgentConfig":
        """
        从EnvironmentVariableLoadConfig
        
        EnvironmentVariable命名Rule: NOGICOS_<FIELD_NAME>
        """
        return cls(
            # ExecuteArgument
            screenshot_delay_ms=int(os.getenv("NOGICOS_SCREENSHOT_DELAY", 750)),
            context_compression_threshold=float(os.getenv("NOGICOS_COMPRESSION_THRESHOLD", 0.75)),
            max_iterations=int(os.getenv("NOGICOS_MAX_ITERATIONS", 20)),
            iteration_timeout_s=int(os.getenv("NOGICOS_ITERATION_TIMEOUT", 120)),
            
            # API Argument
            claude_model=os.getenv("NOGICOS_MODEL", "claude-sonnet-4-20250514"),
            claude_timeout_s=int(os.getenv("NOGICOS_CLAUDE_TIMEOUT", 60)),
            max_retries=int(os.getenv("NOGICOS_MAX_RETRIES", 3)),
            
            # ConcurrentArgument
            max_concurrent_tasks=int(os.getenv("NOGICOS_MAX_TASKS", 3)),
            max_api_concurrency=int(os.getenv("NOGICOS_MAX_API_CONCURRENCY", 2)),
            
            # Persistence
            db_path=os.getenv("NOGICOS_DB_PATH", "nogicos_tasks.db"),
            checkpoint_interval=int(os.getenv("NOGICOS_CHECKPOINT_INTERVAL", 5)),
            
            # Performance
            enable_performance_monitoring=os.getenv("NOGICOS_ENABLE_METRICS", "true").lower() == "true",
            
            # functionOnOff
            enable_dual_agent=os.getenv("NOGICOS_DUAL_AGENT", "false").lower() == "true",
            enable_incremental_checkpoint=os.getenv("NOGICOS_INCREMENTAL_CHECKPOINT", "true").lower() == "true",
            enable_backpressure_bus=os.getenv("NOGICOS_BACKPRESSURE_BUS", "false").lower() == "true",
            enable_prompt_caching=os.getenv("NOGICOS_PROMPT_CACHING", "true").lower() == "true",
        )
    
    def validate(self) -> List[str]:
        """
        VerifyConfig合法性
        
        Returns:
            ErrorMessageList，EmptyListTable示Verify通过
        """
        errors = []
        
        if self.max_iterations < 1:
            errors.append("max_iterations must be >= 1")
        
        if not (0 < self.context_compression_threshold < 1):
            errors.append("context_compression_threshold must be in (0, 1)")
        
        if self.max_concurrent_tasks < 1:
            errors.append("max_concurrent_tasks must be >= 1")
        
        if self.screenshot_delay_ms < 0:
            errors.append("screenshot_delay_ms must be >= 0")
        
        if self.claude_timeout_s < 1:
            errors.append("claude_timeout_s must be >= 1")
        
        if self.checkpoint_interval < 1:
            errors.append("checkpoint_interval must be >= 1")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Export为Dict"""
        return {
            "screenshot_delay_ms": self.screenshot_delay_ms,
            "context_compression_threshold": self.context_compression_threshold,
            "max_iterations": self.max_iterations,
            "iteration_timeout_s": self.iteration_timeout_s,
            "claude_model": self.claude_model,
            "claude_timeout_s": self.claude_timeout_s,
            "max_retries": self.max_retries,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "max_api_concurrency": self.max_api_concurrency,
            "db_path": self.db_path,
            "checkpoint_interval": self.checkpoint_interval,
            "enable_performance_monitoring": self.enable_performance_monitoring,
            "enable_dual_agent": self.enable_dual_agent,
            "enable_incremental_checkpoint": self.enable_incremental_checkpoint,
            "enable_backpressure_bus": self.enable_backpressure_bus,
            "enable_prompt_caching": self.enable_prompt_caching,
        }


# ========== SingletonPattern ==========

_default_config: Optional[AgentConfig] = None


def get_config() -> AgentConfig:
    """GetDefaultConfig（Singleton）"""
    global _default_config
    if _default_config is None:
        _default_config = AgentConfig.from_env()
        
        # VerifyConfig
        errors = _default_config.validate()
        if errors:
            logger.warning(f"Config validation warnings: {errors}")
    
    return _default_config


def set_config(config: AgentConfig):
    """SetDefaultConfig（用于Test）"""
    global _default_config
    _default_config = config


def reload_config():
    """重NewLoadConfig"""
    global _default_config
    _default_config = AgentConfig.from_env()
    logger.info("Config reloaded from environment")
