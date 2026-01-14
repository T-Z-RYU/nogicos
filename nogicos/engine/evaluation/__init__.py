# -*- coding: utf-8 -*-
"""
NogicOS Evaluation Module

Provides:
- LangSmith dataset management
- Custom evaluators for agent tasks
- Automated evaluation pipeline
- Agent architecture evaluators (Phase 8)
- Online monitoring rules (Phase 8)
"""

# appearhaveEvaluateer
from .evaluators import (
    # RuleEvaluateer
    latency_evaluator,
    token_count_evaluator,
    tool_call_count_evaluator,
    error_rate_evaluator,
    # UX Evaluateer
    ttft_evaluator,
    follow_up_evaluator,
    content_richness_evaluator,
    # LLM Evaluateer
    task_completion_llm_evaluator,
    tool_selection_llm_evaluator,
    correctness_evaluator,
    hallucination_evaluator,
    conciseness_evaluator,
    # Compatpropertyothername
    task_completion_evaluator,
    tool_selection_evaluator,
    response_quality_evaluator,
    # Evaluateergroup
    get_rule_evaluators,
    get_llm_evaluators,
    get_ux_evaluators,
    get_all_evaluators,
    get_fast_evaluators,
    get_quality_evaluators,
    get_essential_evaluators,
)

# Phase 8: Newincrease Agent ArchitectureEvaluateer
from .agent_evaluators import (
    agent_handoff_evaluator,
    window_isolation_evaluator,
    set_task_status_evaluator,
    multi_agent_efficiency_evaluator,
    get_agent_evaluators,
    get_agent_core_evaluators,
    get_agent_quality_evaluators,
)

# Phase 8: OnlineMonitorRule
from .online_rules import (
    ONLINE_RULES,
    OnlineRule,
    RuleType,
    Severity,
    get_alert_rules,
    get_review_rules,
    get_critical_rules,
    get_agent_architecture_rules,
    export_rules_for_langsmith,
)

# Datasetmanage
from .dataset_manager import (
    DatasetManager,
    create_dataset_from_runs,
    add_example_to_dataset,
)

__all__ = [
    # === RuleEvaluateer（objective metrics） ===
    "latency_evaluator",
    "token_count_evaluator",
    "tool_call_count_evaluator",
    "error_rate_evaluator",
    
    # === UX Evaluateer ===
    "ttft_evaluator",
    "follow_up_evaluator",
    "content_richness_evaluator",
    
    # === LLM Evaluateer（semantic understanding） ===
    "task_completion_llm_evaluator",
    "tool_selection_llm_evaluator",
    "correctness_evaluator",
    "hallucination_evaluator",
    "conciseness_evaluator",
    
    # === Compatpropertyothername ===
    "task_completion_evaluator",
    "tool_selection_evaluator",
    "response_quality_evaluator",
    
    # === EvaluateergroupFunction ===
    "get_rule_evaluators",
    "get_llm_evaluators",
    "get_ux_evaluators",
    "get_all_evaluators",
    "get_fast_evaluators",
    "get_quality_evaluators",
    "get_essential_evaluators",
    
    # === Phase 8: Agent ArchitectureEvaluateer ===
    "agent_handoff_evaluator",
    "window_isolation_evaluator",
    "set_task_status_evaluator",
    "multi_agent_efficiency_evaluator",
    "get_agent_evaluators",
    "get_agent_core_evaluators",
    "get_agent_quality_evaluators",
    
    # === Phase 8: OnlineMonitorRule ===
    "ONLINE_RULES",
    "OnlineRule",
    "RuleType",
    "Severity",
    "get_alert_rules",
    "get_review_rules",
    "get_critical_rules",
    "get_agent_architecture_rules",
    "export_rules_for_langsmith",
    
    # === Datasetmanage ===
    "DatasetManager",
    "create_dataset_from_runs",
    "add_example_to_dataset",
]

