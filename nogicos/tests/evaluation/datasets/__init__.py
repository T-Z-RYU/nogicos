# -*- coding: utf-8 -*-
"""
Evaluation Datasets Module
"""

import json
from pathlib import Path

DATASETS_DIR = Path(__file__).parent


def load_golden_dataset():
    """Load the golden dataset for evaluation"""
    path = DATASETS_DIR / "golden_dataset.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_dataset(name: str):
    """Load a named dataset"""
    path = DATASETS_DIR / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {name}")
    
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)



