# -*- coding: utf-8 -*-
"""
NogicOS Monitoring Module

Provides Prometheus metrics collection and Grafana dashboard support.
"""

from .prometheus.metrics import AgentMetrics, get_metrics

__all__ = ["AgentMetrics", "get_metrics"]



