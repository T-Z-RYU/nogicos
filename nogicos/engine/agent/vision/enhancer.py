"""
NogicOS Vision Enhancer - 视觉增强主Module
========================================

整合各种视觉增强能力，为 LLM 提供更丰富的视觉UpDown文：
1. OCR 文本提取 - 提取截GraphMedium的文本
2. UI 元素检测 - 识别按钮、Input框等（Optional）
3. 结构化描述生成 - 为截Graph生成结构化描述

Phase 5c Implement
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
import logging
import base64
from io import BytesIO

from .ocr import OCRExtractor, OCRResult, TextRegion, get_ocr_extractor

logger = logging.getLogger(__name__)

# PIL
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    Image = None


# ========== Datastructure ==========

@dataclass
class UIElement:
    """
    UI 元素
    
    Table示截GraphMedium识别到的 UI 元素
    """
    type: str  # "button", "input", "text", "link", "checkbox", "dropdown", etc.
    text: str
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    confidence: float = 1.0
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def center(self) -> Tuple[int, int]:
        """元素Medium心点"""
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) // 2, (y1 + y2) // 2)
    
    @property
    def clickable(self) -> bool:
        """YesNo可点击"""
        return self.type in ["button", "link", "checkbox", "radio", "dropdown"]
    
    @property
    def editable(self) -> bool:
        """YesNo可Edit"""
        return self.type in ["input", "textarea"]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "text": self.text,
            "bbox": self.bbox,
            "center": self.center,
            "confidence": self.confidence,
            "clickable": self.clickable,
            "editable": self.editable,
            "attributes": self.attributes,
        }


@dataclass
class EnhancedScreenshot:
    """
    增强截Graph
    
    Package含Original截Graph和提取的各种Info
    """
    # OriginalGraphpiece
    image_b64: str
    width: int
    height: int
    
    # OCR Result
    text_elements: List[TextRegion] = field(default_factory=list)
    full_text: str = ""
    
    # UI Elements（Optional）
    ui_elements: List[UIElement] = field(default_factory=list)
    
    # structureizedescribe
    description: str = ""
    
    # ScalingbecauseChild（IfGraphpiecebeResizeover）
    scale_factor: Tuple[float, float] = (1.0, 1.0)
    
    # elementData
    hwnd: Optional[int] = None
    window_title: Optional[str] = None
    
    def get_text_at(self, x: int, y: int, radius: int = 50) -> Optional[TextRegion]:
        """
        GetSpecifyPosition附近的文本
        
        Args:
            x: X Coordinate
            y: Y Coordinate
            radius: Search半径
            
        Returns:
            最近的 TextRegion，如果没有则Return None
        """
        closest = None
        min_distance = float('inf')
        
        for region in self.text_elements:
            cx, cy = region.center
            distance = ((cx - x) ** 2 + (cy - y) ** 2) ** 0.5
            
            if distance < min_distance and distance <= radius:
                min_distance = distance
                closest = region
        
        return closest
    
    def get_element_at(self, x: int, y: int) -> Optional[UIElement]:
        """
        GetSpecifyPosition的 UI 元素
        
        Args:
            x: X Coordinate
            y: Y Coordinate
            
        Returns:
            Package含该点的 UIElement，如果没有则Return None
        """
        for element in self.ui_elements:
            x1, y1, x2, y2 = element.bbox
            if x1 <= x <= x2 and y1 <= y <= y2:
                return element
        return None
    
    def find_text(self, pattern: str, case_sensitive: bool = False) -> List[TextRegion]:
        """Find文本"""
        results = []
        for region in self.text_elements:
            text = region.text
            search = pattern
            
            if not case_sensitive:
                text = text.lower()
                search = pattern.lower()
            
            if search in text:
                results.append(region)
        
        return results
    
    def find_elements_by_type(self, element_type: str) -> List[UIElement]:
        """按Class型Find UI 元素"""
        return [e for e in self.ui_elements if e.type == element_type]
    
    def to_context_string(self) -> str:
        """
        Convert为UpDown文Character串，用于Add到 LLM Message
        
        Returns:
            描述截GraphInner容的Character串
        """
        parts = []
        
        # basicallyInfo
        parts.append(f"Screenshot: {self.width}x{self.height}")
        if self.window_title:
            parts.append(f"Window: {self.window_title}")
        
        # describe
        if self.description:
            parts.append(f"\nDescription: {self.description}")
        
        # Visibletext
        if self.full_text:
            # TruncateoverLongtext
            text = self.full_text[:500]
            if len(self.full_text) > 500:
                text += "..."
            parts.append(f"\nVisible text: {text}")
        
        # UI ElementsSummary
        if self.ui_elements:
            element_summary = []
            buttons = self.find_elements_by_type("button")
            inputs = self.find_elements_by_type("input")
            links = self.find_elements_by_type("link")
            
            if buttons:
                button_texts = [b.text for b in buttons[:5]]
                element_summary.append(f"Buttons: {', '.join(button_texts)}")
            if inputs:
                input_texts = [i.text or i.attributes.get("placeholder", "input") for i in inputs[:3]]
                element_summary.append(f"Inputs: {', '.join(input_texts)}")
            if links:
                link_texts = [l.text for l in links[:5]]
                element_summary.append(f"Links: {', '.join(link_texts)}")
            
            if element_summary:
                parts.append(f"\nUI Elements: {'; '.join(element_summary)}")
        
        return "\n".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "width": self.width,
            "height": self.height,
            "text_elements": [t.to_dict() for t in self.text_elements],
            "full_text": self.full_text,
            "ui_elements": [e.to_dict() for e in self.ui_elements],
            "description": self.description,
            "hwnd": self.hwnd,
            "window_title": self.window_title,
        }


# ========== visualEnhancementer ==========

class VisionEnhancer:
    """
    视觉增强器
    
    组合各种视觉增强能力，生成增强截Graph
    
    UsageExample:
    ```python
    enhancer = VisionEnhancer()
    
    # EnhancementcaptureGraph
    enhanced = await enhancer.enhance(screenshot_b64, hwnd=12345)
    
    # GetUpDowntext
    context = enhanced.to_context_string()
    
    # Findspecifictext
    regions = enhanced.find_text("Submit")
    ```
    """
    
    def __init__(
        self,
        use_ocr: bool = True,
        use_ui_detection: bool = False,  # UI DetectionNeedquotaOutermodetype
        ocr_extractor: Optional[OCRExtractor] = None,
        generate_description: bool = True,
    ):
        """
        Initialize视觉增强器
        
        Args:
            use_ocr: YesNoUsage OCR
            use_ui_detection: YesNo检测 UI 元素（需要额Outer模型）
            ocr_extractor: OCR 提取器Instance
            generate_description: YesNo生成描述
        """
        self.use_ocr = use_ocr
        self.use_ui_detection = use_ui_detection
        self.generate_description = generate_description
        
        # OCR Extractioner
        self._ocr = ocr_extractor or (get_ocr_extractor() if use_ocr else None)
        
        logger.info(
            f"VisionEnhancer initialized: ocr={use_ocr}, ui_detection={use_ui_detection}"
        )
    
    async def enhance(
        self,
        screenshot_b64: str,
        hwnd: Optional[int] = None,
        window_title: Optional[str] = None,
    ) -> EnhancedScreenshot:
        """
        增强截Graph
        
        Args:
            screenshot_b64: Base64 编码的截Graph
            hwnd: Window句柄（Optional）
            window_title: Windowtitle（Optional）
            
        Returns:
            EnhancedScreenshot
        """
        # GetGraphpieceSize
        width, height = 0, 0
        if HAS_PIL:
            try:
                image_data = base64.b64decode(screenshot_b64)
                image = Image.open(BytesIO(image_data))
                width, height = image.size
            except Exception as e:
                logger.warning(f"Failed to get image size: {e}")
        
        # OCR Extraction
        text_elements = []
        full_text = ""
        if self.use_ocr and self._ocr:
            try:
                ocr_result = await self._ocr.extract(screenshot_b64, detect_regions=True)
                text_elements = ocr_result.regions
                full_text = ocr_result.full_text
            except Exception as e:
                logger.warning(f"OCR failed: {e}")
        
        # UI ElementsDetection（not yetImplement）
        ui_elements = []
        if self.use_ui_detection:
            ui_elements = await self._detect_ui_elements(screenshot_b64)
        
        # Generationdescribe
        description = ""
        if self.generate_description:
            description = self._generate_description(
                text_elements, ui_elements, width, height
            )
        
        return EnhancedScreenshot(
            image_b64=screenshot_b64,
            width=width,
            height=height,
            text_elements=text_elements,
            full_text=full_text,
            ui_elements=ui_elements,
            description=description,
            hwnd=hwnd,
            window_title=window_title,
        )
    
    async def _detect_ui_elements(
        self,
        screenshot_b64: str,
    ) -> List[UIElement]:
        """
        检测 UI 元素
        
        TODO: 可以Usage以DownMethodImplement:
        1. YOLO 模型检测 UI 元素
        2. Usage Claude Vision 识别
        3. 基于Rule的简单检测（颜色、形状）
        
        Args:
            screenshot_b64: 截Graph
            
        Returns:
            UIElement List
        """
        # not yetImplement
        return []
    
    def _generate_description(
        self,
        text_elements: List[TextRegion],
        ui_elements: List[UIElement],
        width: int,
        height: int,
    ) -> str:
        """
        生成截Graph描述
        
        Args:
            text_elements: 文本区域
            ui_elements: UI 元素
            width: Graph片Width
            height: Graph片Height
            
        Returns:
            描述文本
        """
        parts = []
        
        # Size
        if width and height:
            parts.append(f"Screen size: {width}x{height}")
        
        # textStatistics
        if text_elements:
            word_count = sum(len(t.text.split()) for t in text_elements)
            parts.append(f"Contains {len(text_elements)} text regions ({word_count} words)")
        else:
            parts.append("No readable text detected")
        
        # UI ElementsStatistics
        if ui_elements:
            type_counts = {}
            for e in ui_elements:
                type_counts[e.type] = type_counts.get(e.type, 0) + 1
            
            element_desc = ", ".join(f"{count} {typ}(s)" for typ, count in type_counts.items())
            parts.append(f"UI elements: {element_desc}")
        
        return ". ".join(parts)
    
    async def get_clickable_elements(
        self,
        screenshot_b64: str,
    ) -> List[Dict[str, Any]]:
        """
        Get可点击元素List
        
        Return所有可能可点击的元素及其Coordinate
        
        Args:
            screenshot_b64: 截Graph
            
        Returns:
            可点击元素List
        """
        enhanced = await self.enhance(screenshot_b64)
        
        results = []
        
        # from UI ElementsMediumExtraction
        for element in enhanced.ui_elements:
            if element.clickable:
                results.append({
                    "type": element.type,
                    "text": element.text,
                    "center": element.center,
                    "bbox": element.bbox,
                    "confidence": element.confidence,
                })
        
        # fromtextMediuminfer（Buttontextetc）
        button_keywords = ["submit", "ok", "cancel", "save", "delete", "confirm", "login", "sign"]
        for region in enhanced.text_elements:
            text_lower = region.text.lower()
            if any(kw in text_lower for kw in button_keywords):
                results.append({
                    "type": "potential_button",
                    "text": region.text,
                    "center": region.center,
                    "bbox": region.bbox,
                    "confidence": region.confidence * 0.7,  # decreaseLowconfidence
                })
        
        return results


# ========== GlobalInstance ==========

_default_enhancer: Optional[VisionEnhancer] = None


def get_vision_enhancer(
    use_ocr: bool = True,
    use_ui_detection: bool = False,
) -> VisionEnhancer:
    """
    GetGlobal视觉增强器
    
    Args:
        use_ocr: YesNoUsage OCR
        use_ui_detection: YesNo检测 UI 元素
        
    Returns:
        VisionEnhancer Instance
    """
    global _default_enhancer
    
    if _default_enhancer is None:
        _default_enhancer = VisionEnhancer(
            use_ocr=use_ocr,
            use_ui_detection=use_ui_detection,
        )
    
    return _default_enhancer
