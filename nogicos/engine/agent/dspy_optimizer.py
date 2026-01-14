# -*- coding: utf-8 -*-
"""
DSPy Optimizer - Automatic Prompt Optimization for NogicOS

This module uses DSPy to automatically optimize prompts and improve
agent task completion rates. Instead of manually tuning prompts,
DSPy learns from examples and automatically improves.

Key Features:
- Automatic prompt optimization (MIPROv2)
- Task classification with DSPy signatures
- Self-improving task routing
- Evaluation-driven optimization

Usage:
    from engine.agent.dspy_optimizer import (
        DSPyClassifier,
        optimize_classifier,
        get_optimized_classifier,
    )
    
    # Use optimized classifier
    classifier = get_optimized_classifier()
    result = classifier(task="Open浏览器visit google.com")
"""

import os
import json
from typing import Optional, List, Dict, Any, Literal
from dataclasses import dataclass
from pathlib import Path

from ..observability import get_logger
logger = get_logger("dspy_optimizer")

# DSPy imports (optional)
try:
    import dspy
    from dspy import Signature, InputField, OutputField, Predict, ChainOfThought
    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False
    dspy = None
    Signature = object
    InputField = OutputField = Predict = ChainOfThought = None
    logger.warning("[DSPy] Not installed. Run: pip install dspy-ai")

# Config
try:
    from config import DSPY_ENABLED, DSPY_CACHE_DIR, LANGSMITH_API_KEY, ANTHROPIC_API_KEY
except ImportError:
    DSPY_ENABLED = False
    DSPY_CACHE_DIR = "./data/dspy_cache"
    LANGSMITH_API_KEY = ""
    ANTHROPIC_API_KEY = ""

# Import existing API key if not in config
if not ANTHROPIC_API_KEY:
    try:
        from api_keys import ANTHROPIC_API_KEY
    except ImportError:
        pass


# ===========================================
# DSPy Signatures (Task Definitions)
# ===========================================

if DSPY_AVAILABLE:
    class TaskClassificationSignature(Signature):
        """Classify a user task into browser, local, or mixed category."""
        
        task: str = InputField(desc="The user's task or request in natural language")
        
        task_type: Literal["browser", "local", "mixed"] = OutputField(
            desc="The task type: 'browser' for web tasks, 'local' for file/shell tasks, 'mixed' for both"
        )
        complexity: Literal["simple", "moderate", "complex"] = OutputField(
            desc="The task complexity: 'simple' (1 step), 'moderate' (2-3 steps), 'complex' (4+ steps)"
        )
        reasoning: str = OutputField(
            desc="Brief explanation of why this classification was chosen (in Chinese)"
        )
    
    
    class TaskPlanningSignature(Signature):
        """Generate a step-by-step plan for a complex task."""
        
        task: str = InputField(desc="The user's task to accomplish")
        available_tools: str = InputField(desc="List of available tools and their descriptions")
        
        steps: str = OutputField(
            desc="Step-by-step plan as a numbered list (e.g., '1. Do X\\n2. Do Y')"
        )
        estimated_iterations: int = OutputField(
            desc="Estimated number of tool calls needed"
        )
    
    
    class AnswerExtractionSignature(Signature):
        """Extract the final answer from tool execution results."""
        
        task: str = InputField(desc="The original user task")
        tool_outputs: str = InputField(desc="Combined outputs from tool executions")
        
        answer: str = OutputField(desc="The extracted answer to the user's question")
        confidence: float = OutputField(
            desc="Confidence score from 0.0 to 1.0 that the answer is correct"
        )


# ===========================================
# DSPy Modules (Trainable Components)
# ===========================================

@dataclass
class ClassificationResult:
    """Result from DSPy classifier."""
    task_type: str
    complexity: str
    reasoning: str
    confidence: float = 1.0


class DSPyClassifier:
    """
    DSPy-powered task classifier with automatic prompt optimization.
    
    This classifier can be trained on examples to improve accuracy
    using DSPy's automatic optimization (MIPROv2).
    """
    
    def __init__(self, model: str = "anthropic/claude-sonnet-4-20250514"):
        """
        Initialize DSPy classifier.
        
        Args:
            model: LiteLLM model string (e.g., "anthropic/claude-3-5-sonnet-20241022")
        """
        if not DSPY_AVAILABLE:
            raise ImportError("DSPy not installed. Run: pip install dspy-ai")
        
        self.model = model
        self._configured = False
        
        # Initialize predictor (will be optimized later)
        self.predictor = ChainOfThought(TaskClassificationSignature)
        
        # Cache path for optimized module
        self.cache_path = Path(DSPY_CACHE_DIR) / "classifier_optimized.json"
        
        # Try to load optimized version
        self._load_optimized()
    
    def _ensure_configured(self):
        """Ensure DSPy is configured with LM."""
        if self._configured:
            return
        
        # Get API key
        api_key = ANTHROPIC_API_KEY or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.warning("[DSPy] No Anthropic API key found, using default")
        
        # Configure DSPy with Anthropic
        lm = dspy.LM(self.model, api_key=api_key)
        dspy.configure(lm=lm)
        
        self._configured = True
        logger.info(f"[DSPy] Configured with model: {self.model}")
    
    def _load_optimized(self) -> bool:
        """Load optimized predictor from cache if available."""
        if not self.cache_path.exists():
            return False
        
        try:
            self.predictor.load(str(self.cache_path))
            logger.info(f"[DSPy] Loaded optimized classifier from {self.cache_path}")
            return True
        except Exception as e:
            logger.warning(f"[DSPy] Failed to load optimized classifier: {e}")
            return False
    
    def __call__(self, task: str) -> ClassificationResult:
        """
        Classify a task.
        
        Args:
            task: User's task description
            
        Returns:
            ClassificationResult with task_type, complexity, and reasoning
        """
        self._ensure_configured()
        
        try:
            result = self.predictor(task=task)
            
            return ClassificationResult(
                task_type=result.task_type,
                complexity=result.complexity,
                reasoning=result.reasoning,
                confidence=1.0,  # DSPy doesn't provide confidence, assume high
            )
        except Exception as e:
            logger.error(f"[DSPy] Classification failed: {e}")
            # Fallback to rule-based
            return ClassificationResult(
                task_type="local",
                complexity="simple",
                reasoning=f"DSPy error: {e}, defaulting to local",
                confidence=0.3,
            )
    
    def save_optimized(self):
        """Save optimized predictor to cache."""
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            self.predictor.save(str(self.cache_path))
            logger.info(f"[DSPy] Saved optimized classifier to {self.cache_path}")
        except Exception as e:
            logger.error(f"[DSPy] Failed to save optimized classifier: {e}")


# ===========================================
# Training Data & Optimization
# ===========================================

# Training examples for classifier optimization
CLASSIFIER_TRAINSET = [
    # Browser tasks
    {"task": "Open google.com Search Python 教程", "task_type": "browser", "complexity": "simple"},
    {"task": "visit GitHub Down载最New版本的 React", "task_type": "browser", "complexity": "moderate"},
    {"task": "Login淘宝账号，Search手机壳，加入购物车", "task_type": "browser", "complexity": "complex"},
    {"task": "在 YouTube Search AI 视频并播放", "task_type": "browser", "complexity": "simple"},
    {"task": "Openwebpage https://example.com", "task_type": "browser", "complexity": "simple"},
    
    # Local tasks
    {"task": "Create一个NewFile test.py", "task_type": "local", "complexity": "simple"},
    {"task": "帮我看看当BeforeDirectory有什么File", "task_type": "local", "complexity": "simple"},
    {"task": "把桌面Up的File整理到 Documents File夹", "task_type": "local", "complexity": "moderate"},
    {"task": "Running pip install requests", "task_type": "local", "complexity": "simple"},
    {"task": "Read config.json FileInner容", "task_type": "local", "complexity": "simple"},
    {"task": "把所有 .txt FileMove到 backup File夹", "task_type": "local", "complexity": "moderate"},
    {"task": "Create项目Directory结构，Package含 src、tests、docs File夹", "task_type": "local", "complexity": "moderate"},
    
    # Mixed tasks
    {"task": "从 GitHub Down载项目，然After在本地Running", "task_type": "mixed", "complexity": "complex"},
    {"task": "Login网站然AfterDown载报TableSave到桌面", "task_type": "mixed", "complexity": "complex"},
    {"task": "Search网Up的代码Example，Save到本地File", "task_type": "mixed", "complexity": "moderate"},
    {"task": "从webpage抓取数据，HandleAfterSave到 CSV File", "task_type": "mixed", "complexity": "complex"},
]


def create_training_examples() -> List:
    """Create DSPy Example objects from training data."""
    if not DSPY_AVAILABLE:
        return []
    
    examples = []
    for item in CLASSIFIER_TRAINSET:
        ex = dspy.Example(
            task=item["task"],
            task_type=item["task_type"],
            complexity=item["complexity"],
            reasoning="",  # Will be generated during training
        ).with_inputs("task")
        examples.append(ex)
    
    return examples


def classifier_metric(example, prediction, trace=None) -> float:
    """
    Evaluation metric for classifier optimization.
    
    Returns 1.0 if both task_type and complexity match exactly.
    """
    type_match = prediction.task_type == example.task_type
    complexity_match = prediction.complexity == example.complexity
    
    if type_match and complexity_match:
        return 1.0
    elif type_match:
        return 0.5  # Partial credit for correct type
    else:
        return 0.0


def optimize_classifier(
    classifier: DSPyClassifier,
    num_threads: int = 4,
    auto: str = "light",
) -> DSPyClassifier:
    """
    Optimize the classifier using DSPy MIPROv2.
    
    Args:
        classifier: The classifier to optimize
        num_threads: Number of parallel threads for optimization
        auto: Optimization level ("light", "medium", "heavy")
        
    Returns:
        Optimized classifier
    """
    if not DSPY_AVAILABLE:
        logger.warning("[DSPy] Not available, skipping optimization")
        return classifier
    
    logger.info(f"[DSPy] Starting classifier optimization (auto={auto})")
    
    # Create training set
    trainset = create_training_examples()
    if not trainset:
        logger.warning("[DSPy] No training examples, skipping optimization")
        return classifier
    
    # Ensure configured
    classifier._ensure_configured()
    
    try:
        # Use MIPROv2 optimizer
        optimizer = dspy.MIPROv2(
            metric=classifier_metric,
            auto=auto,
            num_threads=num_threads,
        )
        
        # Optimize (disable permission prompt for non-interactive execution)
        optimized_predictor = optimizer.compile(
            classifier.predictor,
            trainset=trainset,
            requires_permission_to_run=False,  # Skip confirmation prompt
        )
        
        # Update classifier
        classifier.predictor = optimized_predictor
        classifier.save_optimized()
        
        logger.info("[DSPy] Classifier optimization complete!")
        return classifier
        
    except Exception as e:
        logger.error(f"[DSPy] Optimization failed: {e}")
        return classifier


# ===========================================
# Global Instance & Convenience Functions
# ===========================================

_optimized_classifier: Optional[DSPyClassifier] = None


def get_optimized_classifier() -> Optional[DSPyClassifier]:
    """
    Get the global optimized classifier instance.
    
    Returns None if DSPy is not available or not enabled.
    """
    global _optimized_classifier
    
    if not DSPY_AVAILABLE or not DSPY_ENABLED:
        return None
    
    if _optimized_classifier is None:
        try:
            _optimized_classifier = DSPyClassifier()
            logger.info("[DSPy] Global classifier initialized")
        except Exception as e:
            logger.error(f"[DSPy] Failed to create classifier: {e}")
            return None
    
    return _optimized_classifier


def dspy_classify(task: str) -> Optional[ClassificationResult]:
    """
    Convenience function to classify a task with DSPy.
    
    Falls back to None if DSPy is not available.
    
    Args:
        task: User's task description
        
    Returns:
        ClassificationResult or None if DSPy unavailable
    """
    classifier = get_optimized_classifier()
    if classifier is None:
        return None
    
    return classifier(task)


# ===========================================
# CLI for Training
# ===========================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="DSPy Classifier Optimizer")
    parser.add_argument("--optimize", action="store_true", help="Run optimization")
    parser.add_argument("--test", action="store_true", help="Test classifier")
    parser.add_argument("--auto", default="light", choices=["light", "medium", "heavy"],
                        help="Optimization level")
    args = parser.parse_args()
    
    if not DSPY_AVAILABLE:
        print("DSPy not installed. Run: pip install dspy-ai")
        exit(1)
    
    classifier = DSPyClassifier()
    
    if args.optimize:
        print(f"Starting optimization (auto={args.auto})...")
        classifier = optimize_classifier(classifier, auto=args.auto)
        print("Optimization complete!")
    
    if args.test or not args.optimize:
        print("\nTesting classifier...")
        test_tasks = [
            "Open google.com Search Python 教程",
            "Create一个NewFile test.py",
            "从 GitHub Down载项目然After本地Running",
            "帮我看看桌面有什么File",
        ]
        
        for task in test_tasks:
            result = classifier(task)
            print(f"\n任务: {task}")
            print(f"  Class型: {result.task_type}")
            print(f"  复杂度: {result.complexity}")
            print(f"  推理: {result.reasoning}")

