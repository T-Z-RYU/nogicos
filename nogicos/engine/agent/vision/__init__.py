"""
NogicOS Vision Enhancement Layer - Phase 5c
=============================================

视觉增强层，提升 Agent 的视觉理解能力：
1. OCR 文本识别 - 从截GraphMedium提取文本
2. UI 元素检测 - 识别按钮、Input框等
3. 结构化描述 - 将视觉Info转为结构化数据

Component:
- VisionEnhancer: 主入口，组合各种增强能力
- OCRExtractor: 文本识别
- UIDetector: UI 元素检测（Optional，依赖额Outer模型）
"""

from .enhancer import (
    VisionEnhancer,
    EnhancedScreenshot,
    UIElement,
    get_vision_enhancer,
)

from .ocr import (
    OCRExtractor,
    OCRResult,
    TextRegion,
    get_ocr_extractor,
)

__all__ = [
    # Enhancer
    'VisionEnhancer',
    'EnhancedScreenshot',
    'UIElement',
    'get_vision_enhancer',
    # OCR
    'OCRExtractor',
    'OCRResult',
    'TextRegion',
    'get_ocr_extractor',
]
