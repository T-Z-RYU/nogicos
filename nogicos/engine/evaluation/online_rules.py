# -*- coding: utf-8 -*-
"""
NogicOS Online Monitoring Rules - Phase 8.4

LangSmith Online Evaluation Rules Config，用于实时Monitor Agent Running质量。

这些Rule会在 LangSmith Dashboard MediumConfig，Implement：
- 实时Alert (Alerts)
- 人工审核标记 (Review Flags)
- AutoEvaluateTrigger (Auto Evaluation)

Usage:
    from engine.evaluation.online_rules import (
        ONLINE_RULES,
        get_alert_rules,
        get_review_rules,
        get_critical_rules,
    )

Config方式：
    在 LangSmith Dashboard → Project → Rules MediumManualConfig，
    或Usage LangSmith API Auto化Config。

Reference:
    https://docs.smith.langchain.com/evaluation/how_to_guides/online_evaluation

================================================================================
Field依赖说明（IMPORTANT）
================================================================================

本FileMedium的RuleCondition依赖以DownField，需确保Evaluate流水线正确Write：

1. run.outputs.* Field（由 HostAgent Write）:
   - run.outputs.iterations: Iterate次数
   - run.outputs.success: 任务YesNoSuccess
   - run.outputs.tool_calls: Tool调用List
   
   WritePosition: HostAgent._get_task_result() Return值

2. feedback.* Field（由Evaluate器Write）:
   - feedback.latency         <- latency_evaluator (key="latency")
   - feedback.error_rate      <- error_rate_evaluator (key="error_rate")
   - feedback.token_count     <- token_count_evaluator (key="token_count")
   - feedback.ttft            <- ttft_evaluator (key="ttft")
   - feedback.hallucination   <- hallucination_evaluator (key="hallucination")
   - feedback.task_completion_llm <- task_completion_llm_evaluator (key="task_completion_llm")
   - feedback.content_richness <- content_richness_evaluator (key="content_richness")
   - feedback.window_isolation <- window_isolation_evaluator (key="window_isolation")
   - feedback.agent_handoff   <- agent_handoff_evaluator (key="agent_handoff")
   - feedback.multi_agent_efficiency <- multi_agent_efficiency_evaluator (key="multi_agent_efficiency")
   - feedback.set_task_status <- set_task_status_evaluator (key="set_task_status")
   
   Write方式: Evaluate器Return {"key": "xxx", "score": 0.x, "comment": "..."} 
             LangSmith Auto将其Write feedback.{key}

3. VerifyRuleYesNo生效:
   - 在 LangSmith Dashboard view Runs，Confirm feedback Field已Write
   - Usage run_evaluation.py TriggerEvaluate，Check feedback YesNo正确
   
================================================================================
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

from engine.observability import get_logger

logger = get_logger("online_rules")


class RuleType(Enum):
    """RuleClass型"""
    ALERT = "alert"           # AlertRule（TriggerNotify）
    REVIEW = "review"         # reviewRule（Markmanualreview）
    EVALUATION = "evaluation" # EvaluateRule（TriggerAutoEvaluate）


class Severity(Enum):
    """严重程度"""
    CRITICAL = "critical"  # severe - ImmediateNotify
    HIGH = "high"          # High - handle ASAPHandle
    MEDIUM = "medium"      # Medium - needs attention
    LOW = "low"            # Low - InfoRecord


@dataclass
class OnlineRule:
    """
    在线MonitorRule定义
    
    Attributes:
        name: Rule名称
        description: Rule描述
        rule_type: RuleClass型
        severity: 严重程度
        condition: TriggerCondition（LangSmith Table达式）
        action: Trigger时的动作
        evaluator: Off联的Evaluate器（如果YesEvaluateRule）
        notification_channels: notification channelList
        enabled: YesNoEnable
    """
    name: str
    description: str
    rule_type: RuleType
    severity: Severity
    condition: str
    action: str
    evaluator: Optional[str] = None
    notification_channels: List[str] = field(default_factory=list)
    enabled: bool = True
    
    def to_langsmith_config(self) -> Dict[str, Any]:
        """Convert为 LangSmith API 格式"""
        return {
            "name": self.name,
            "description": self.description,
            "type": self.rule_type.value,
            "severity": self.severity.value,
            "condition": self.condition,
            "action": self.action,
            "evaluator": self.evaluator,
            "notification_channels": self.notification_channels,
            "enabled": self.enabled,
        }


# ===========================================
# AlertRule (Alerts) - PerformanceandErrorMonitor
# ===========================================
# NOTE: ConditionUsage LangSmith ActualSupport's FieldPath
# - run.outputs.* : Agent Output's Field（by HostAgent Write）
# - run.inputs.* : TaskInput
# - run.error : RunningError
# - feedback.* : EvaluateerFeedback（by evaluator Write）

LATENCY_ALERT = OnlineRule(
    name="high_latency_alert",
    description="检测HighDelayed任务（> 30s），TriggerAlert",
    rule_type=RuleType.ALERT,
    severity=Severity.HIGH,
    # Usage feedback.latency by latency_evaluator Write
    condition="feedback.latency < 0.2",  # score < 0.2 Tableshow > 30s
    action="Send notification to Slack channel #agent-alerts",
    evaluator="latency_evaluator",
    notification_channels=["slack:agent-alerts", "email:oncall"],
    enabled=True,
)

ERROR_RATE_ALERT = OnlineRule(
    name="error_rate_alert",
    description="检测HighError率（> 30%），TriggerAlert",
    rule_type=RuleType.ALERT,
    severity=Severity.CRITICAL,
    # Usage feedback.error_rate by error_rate_evaluator Write
    condition="feedback.error_rate < 0.5",  # score < 0.5 table shows significantError
    action="Send immediate notification + create incident",
    evaluator="error_rate_evaluator",
    notification_channels=["slack:agent-alerts", "pagerduty"],
    enabled=True,
)

ITERATION_LIMIT_ALERT = OnlineRule(
    name="iteration_limit_alert",
    description="检测接近IterateUp限（> 40/50），预警",
    rule_type=RuleType.ALERT,
    severity=Severity.MEDIUM,
    # Usage run.outputs.iterations by HostAgent Write
    condition="run.outputs.iterations > 40",
    action="Send warning notification",
    notification_channels=["slack:agent-monitoring"],
    enabled=True,
)

TOKEN_OVERUSE_ALERT = OnlineRule(
    name="token_overuse_alert",
    description="检测 token Usage过量（> 100k），成本预警",
    rule_type=RuleType.ALERT,
    severity=Severity.MEDIUM,
    # Usage feedback.token_count by token_count_evaluator Write
    condition="feedback.token_count < 0.4",  # score < 0.4 Tableshow > 5000 tokens
    action="Send cost warning notification",
    evaluator="token_count_evaluator",
    notification_channels=["email:billing"],
    enabled=True,
)


# ===========================================
# reviewRule (Review Flags) - qualityreviewMark
# ===========================================

HALLUCINATION_REVIEW = OnlineRule(
    name="hallucination_review",
    description="幻觉检测评分Low时标记人工审核",
    rule_type=RuleType.REVIEW,
    severity=Severity.HIGH,
    condition="feedback.hallucination < 0.5",
    action="Flag for human review",
    evaluator="hallucination_evaluator",
    enabled=True,
)

LOW_COMPLETION_REVIEW = OnlineRule(
    name="low_completion_review",
    description="任务Complete度Low时标记审核",
    rule_type=RuleType.REVIEW,
    severity=Severity.MEDIUM,
    condition="feedback.task_completion_llm < 0.5",
    action="Flag for review with context",
    evaluator="task_completion_llm_evaluator",
    enabled=True,
)

NEEDS_HELP_REVIEW = OnlineRule(
    name="needs_help_review",
    description="Agent Requesthelp时标记审核",
    rule_type=RuleType.REVIEW,
    severity=Severity.LOW,
    # set_task_status EvaluateerwillDetection needs_help State，minutenumber 0.8 Tableshow needs_help
    condition="feedback.set_task_status >= 0.7 AND feedback.set_task_status <= 0.85",
    action="Flag for review - check if help request is valid",
    evaluator="set_task_status_evaluator",
    enabled=True,
)


# ===========================================
# Agent ArchitecturespecialuseRule (Phase 8)
# ===========================================

WINDOW_ISOLATION_CRITICAL = OnlineRule(
    name="window_isolation_critical",
    description="Window隔离违规（跨Window污染），严重Alert",
    rule_type=RuleType.ALERT,
    severity=Severity.CRITICAL,
    condition="feedback.window_isolation < 0.3",
    action="Immediate alert - potential data leakage between windows",
    evaluator="window_isolation_evaluator",
    notification_channels=["slack:agent-alerts", "pagerduty"],
    enabled=True,
)

HANDOFF_FAILURE_ALERT = OnlineRule(
    name="handoff_failure_alert",
    description="Agent handoff Failed率High，Alert",
    rule_type=RuleType.ALERT,
    severity=Severity.HIGH,
    condition="feedback.agent_handoff < 0.5",
    action="Alert - AppAgent scheduling issues",
    evaluator="agent_handoff_evaluator",
    notification_channels=["slack:agent-monitoring"],
    enabled=True,
)

INEFFICIENT_EXECUTION_REVIEW = OnlineRule(
    name="inefficient_execution_review",
    description="多 Agent 协作效率Low时标记审核",
    rule_type=RuleType.REVIEW,
    severity=Severity.MEDIUM,
    condition="feedback.multi_agent_efficiency < 0.5",
    action="Flag for optimization review",
    evaluator="multi_agent_efficiency_evaluator",
    enabled=True,
)

TASK_STATUS_MISSING_ALERT = OnlineRule(
    name="task_status_missing_alert",
    description="任务未正确SetState，可能Yes bug",
    rule_type=RuleType.ALERT,
    severity=Severity.MEDIUM,
    condition="feedback.set_task_status < 0.3",
    action="Alert - task termination issue",
    evaluator="set_task_status_evaluator",
    notification_channels=["slack:agent-monitoring"],
    enabled=True,
)


# ===========================================
# UX relatedOffRule
# ===========================================

SLOW_TTFT_REVIEW = OnlineRule(
    name="slow_ttft_review",
    description="First Token Time过长（> 3s），影响User体验",
    rule_type=RuleType.REVIEW,
    severity=Severity.MEDIUM,
    # Usage feedback.ttft by ttft_evaluator Write，score < 0.5 Tableshow > 2s
    condition="feedback.ttft < 0.5",
    action="Flag for UX optimization review",
    evaluator="ttft_evaluator",
    enabled=True,
)

LOW_CONTENT_RICHNESS_REVIEW = OnlineRule(
    name="low_content_richness_review",
    description="ResponseInner容不够丰富，可能需要改进 prompt",
    rule_type=RuleType.REVIEW,
    severity=Severity.LOW,
    # Repair：add parenthesesensure OR logiccorrect
    condition="feedback.content_richness < 0.5 AND (run.inputs.task CONTAINS 'Write' OR run.inputs.task CONTAINS 'code')",
    action="Flag for prompt improvement review",
    evaluator="content_richness_evaluator",
    enabled=True,
)


# ===========================================
# RuleSet
# ===========================================

ONLINE_RULES: Dict[str, OnlineRule] = {
    # AlertRule
    "latency_alert": LATENCY_ALERT,
    "error_rate_alert": ERROR_RATE_ALERT,
    "iteration_limit_alert": ITERATION_LIMIT_ALERT,
    "token_overuse_alert": TOKEN_OVERUSE_ALERT,
    
    # reviewRule
    "hallucination_review": HALLUCINATION_REVIEW,
    "low_completion_review": LOW_COMPLETION_REVIEW,
    "needs_help_review": NEEDS_HELP_REVIEW,
    
    # Agent ArchitectureRule (Phase 8)
    "window_isolation_critical": WINDOW_ISOLATION_CRITICAL,
    "handoff_failure_alert": HANDOFF_FAILURE_ALERT,
    "inefficient_execution_review": INEFFICIENT_EXECUTION_REVIEW,
    "task_status_missing_alert": TASK_STATUS_MISSING_ALERT,
    
    # UX Rule
    "slow_ttft_review": SLOW_TTFT_REVIEW,
    "low_content_richness_review": LOW_CONTENT_RICHNESS_REVIEW,
}


# ===========================================
# HelperFunction
# ===========================================

def get_alert_rules() -> List[OnlineRule]:
    """Get所有AlertRule"""
    return [rule for rule in ONLINE_RULES.values() if rule.rule_type == RuleType.ALERT]


def get_review_rules() -> List[OnlineRule]:
    """Get所有审核Rule"""
    return [rule for rule in ONLINE_RULES.values() if rule.rule_type == RuleType.REVIEW]


def get_critical_rules() -> List[OnlineRule]:
    """Get所有严重级别Rule"""
    return [rule for rule in ONLINE_RULES.values() if rule.severity == Severity.CRITICAL]


def get_agent_architecture_rules() -> List[OnlineRule]:
    """Get Agent 架构相OffRule (Phase 8)"""
    agent_rules = [
        "window_isolation_critical",
        "handoff_failure_alert",
        "inefficient_execution_review",
        "task_status_missing_alert",
    ]
    return [ONLINE_RULES[name] for name in agent_rules if name in ONLINE_RULES]


def get_rules_by_evaluator(evaluator_name: str) -> List[OnlineRule]:
    """Root据Evaluate器名称GetOff联Rule"""
    return [
        rule for rule in ONLINE_RULES.values()
        if rule.evaluator and evaluator_name in rule.evaluator
    ]


def export_rules_for_langsmith() -> List[Dict[str, Any]]:
    """Export所有Rule为 LangSmith API 格式"""
    return [rule.to_langsmith_config() for rule in ONLINE_RULES.values() if rule.enabled]


def get_notification_summary() -> Dict[str, List[str]]:
    """Getnotification channel汇总"""
    summary: Dict[str, List[str]] = {}
    for rule in ONLINE_RULES.values():
        for channel in rule.notification_channels:
            if channel not in summary:
                summary[channel] = []
            summary[channel].append(rule.name)
    return summary


# ===========================================
# RuleConfigVerify
# ===========================================

def validate_rules() -> List[str]:
    """
    VerifyRuleConfigYesNo完整
    
    Returns:
        VerifyErrorList，EmptyListTable示全部通过
    """
    errors = []
    
    for name, rule in ONLINE_RULES.items():
        # CheckRequiredField
        if not rule.name:
            errors.append(f"Rule '{name}' missing name")
        if not rule.condition:
            errors.append(f"Rule '{name}' missing condition")
        if not rule.action:
            errors.append(f"Rule '{name}' missing action")
        
        # CheckEvaluateRuleYesNohaveOffconnectEvaluateer
        if rule.rule_type == RuleType.EVALUATION and not rule.evaluator:
            errors.append(f"Evaluation rule '{name}' missing evaluator")
        
        # ChecksevereAlertYesNohavenotification channel
        if rule.severity == Severity.CRITICAL and not rule.notification_channels:
            errors.append(f"Critical rule '{name}' has no notification channels")
    
    if errors:
        for error in errors:
            logger.warning(f"[OnlineRules] Validation: {error}")
    else:
        logger.info(f"[OnlineRules] All {len(ONLINE_RULES)} rules validated successfully")
    
    return errors


# ModuleLoadtimeVerify
_validation_errors = validate_rules()
