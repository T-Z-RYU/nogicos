"""
NogicOS OCR Extractor - 文本识别
================================

从截GraphMedium提取文本，支持多种 OCR After端：
1. Windows OCR (Inner置，无需额Outer依赖)
2. Tesseract OCR (需要安装)
3. EasyOCR (需要安装，支持多语言)

Phase 5c Implement
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
import logging
import base64
from io import BytesIO

logger = logging.getLogger(__name__)

# tryImportvarious OCR Afterend
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    Image = None

try:
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False
    pytesseract = None

try:
    import easyocr
    HAS_EASYOCR = True
except ImportError:
    HAS_EASYOCR = False
    easyocr = None

# Windows OCR - Need winsdk and numpy
HAS_WINDOWS_OCR = False
HAS_NUMPY = False
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    np = None

try:
    import asyncio
    import sys
    if sys.platform == 'win32' and HAS_NUMPY:
        # Windows Runtime OCR - Need winsdk + numpy
        try:
            from winsdk.windows.media.ocr import OcrEngine
            from winsdk.windows.globalization import Language
            HAS_WINDOWS_OCR = True
        except ImportError:
            pass
except Exception:
    pass


# ========== Datastructure ==========

@dataclass
class TextRegion:
    """
    识别到的文本区域
    
    Package含文本Inner容和PositionInfo
    """
    text: str
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    confidence: float = 1.0
    language: Optional[str] = None
    
    @property
    def center(self) -> Tuple[int, int]:
        """区域Medium心点"""
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) // 2, (y1 + y2) // 2)
    
    @property
    def width(self) -> int:
        return self.bbox[2] - self.bbox[0]
    
    @property
    def height(self) -> int:
        return self.bbox[3] - self.bbox[1]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "bbox": self.bbox,
            "center": self.center,
            "confidence": self.confidence,
            "language": self.language,
        }


@dataclass
class OCRResult:
    """
    OCR 识别Result
    """
    full_text: str
    regions: List[TextRegion] = field(default_factory=list)
    language: Optional[str] = None
    engine: str = "unknown"
    processing_time_ms: float = 0.0
    
    @property
    def has_text(self) -> bool:
        return bool(self.full_text.strip())
    
    @property
    def word_count(self) -> int:
        return len(self.full_text.split())
    
    def find_text(self, pattern: str, case_sensitive: bool = False) -> List[TextRegion]:
        """
        FindPackage含特定文本的区域
        
        Args:
            pattern: 要Find的文本
            case_sensitive: YesNo区分SizeWrite
            
        Returns:
            Match的 TextRegion List
        """
        results = []
        for region in self.regions:
            text = region.text
            search_pattern = pattern
            
            if not case_sensitive:
                text = text.lower()
                search_pattern = pattern.lower()
            
            if search_pattern in text:
                results.append(region)
        
        return results
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "full_text": self.full_text,
            "regions": [r.to_dict() for r in self.regions],
            "language": self.language,
            "engine": self.engine,
            "word_count": self.word_count,
        }


# ========== OCR Extractioner ==========

class OCRExtractor:
    """
    OCR 文本提取器
    
    AutoSelect最佳Available的 OCR After端
    
    UsageExample:
    ```python
    extractor = OCRExtractor()
    result = await extractor.extract(image_b64)
    print(result.full_text)
    ```
    """
    
    def __init__(
        self,
        preferred_engine: Optional[str] = None,
        languages: Optional[List[str]] = None,
    ):
        """
        Initialize OCR 提取器
        
        Args:
            preferred_engine: First选引擎 ("windows", "tesseract", "easyocr")
            languages: 支持的语言List (如 ["en", "zh"])
        """
        self.languages = languages or ["en", "zh"]
        self._engine_name = "none"
        
        # Selectengine
        if preferred_engine:
            self._engine_name = preferred_engine
        else:
            # AutoSelect
            if HAS_WINDOWS_OCR:
                self._engine_name = "windows"
            elif HAS_EASYOCR:
                self._engine_name = "easyocr"
            elif HAS_TESSERACT:
                self._engine_name = "tesseract"
            else:
                self._engine_name = "fallback"
        
        # Initialize EasyOCR reader（IfUsage）
        self._easyocr_reader = None
        if self._engine_name == "easyocr" and HAS_EASYOCR:
            try:
                self._easyocr_reader = easyocr.Reader(self.languages)
            except Exception as e:
                logger.warning(f"Failed to initialize EasyOCR: {e}")
                self._engine_name = "tesseract" if HAS_TESSERACT else "fallback"
        
        logger.info(f"OCRExtractor initialized with engine: {self._engine_name}")
    
    async def extract(
        self,
        image_b64: str,
        detect_regions: bool = True,
    ) -> OCRResult:
        """
        从Graph片Medium提取文本
        
        Args:
            image_b64: Base64 编码的Graph片
            detect_regions: YesNo检测文本区域
            
        Returns:
            OCRResult
        """
        import time
        start_time = time.time()
        
        if not HAS_PIL:
            return OCRResult(
                full_text="",
                engine="error",
                processing_time_ms=0,
            )
        
        try:
            # DecodeGraphpiece
            image_data = base64.b64decode(image_b64)
            image = Image.open(BytesIO(image_data))
            
            # RootdataengineSelectHandleMethod
            if self._engine_name == "windows":
                result = await self._extract_windows(image, detect_regions)
            elif self._engine_name == "easyocr":
                result = await self._extract_easyocr(image, detect_regions)
            elif self._engine_name == "tesseract":
                result = await self._extract_tesseract(image, detect_regions)
            else:
                result = self._extract_fallback(image)
            
            result.processing_time_ms = (time.time() - start_time) * 1000
            return result
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return OCRResult(
                full_text="",
                engine="error",
                processing_time_ms=(time.time() - start_time) * 1000,
            )
    
    async def _extract_windows(
        self,
        image: "Image.Image",
        detect_regions: bool,
    ) -> OCRResult:
        """
        Usage Windows OCR (Windows 10+ Inner置)
        
        需要安装 winsdk Package: pip install winsdk
        """
        if not HAS_WINDOWS_OCR:
            logger.debug("Windows OCR not available, falling back")
            if HAS_TESSERACT:
                return await self._extract_tesseract(image, detect_regions)
            return self._extract_fallback(image)
        
        try:
            from winsdk.windows.media.ocr import OcrEngine
            from winsdk.windows.globalization import Language
            from winsdk.windows.graphics.imaging import (
                SoftwareBitmap, BitmapPixelFormat, BitmapAlphaMode
            )
            from winsdk.windows.storage.streams import (
                DataWriter, InMemoryRandomAccessStream
            )
            import numpy as np
            
            # 1. Get OCR engine
            # tryMediumtext，thenAfterenglishtext
            engine = None
            for lang_tag in ["zh-Hans-CN", "zh-CN", "en-US", "en"]:
                try:
                    language = Language(lang_tag)
                    if OcrEngine.is_language_supported(language):
                        engine = OcrEngine.try_create_from_language(language)
                        if engine:
                            logger.debug(f"Using Windows OCR with language: {lang_tag}")
                            break
                except Exception:
                    continue
            
            if not engine:
                # UsageUserDefaultLanguage
                engine = OcrEngine.try_create_from_user_profile_languages()
            
            if not engine:
                logger.warning("Failed to create Windows OCR engine")
                if HAS_TESSERACT:
                    return await self._extract_tesseract(image, detect_regions)
                return self._extract_fallback(image)
            
            # 2. ConvertGraphpiecefor SoftwareBitmap
            # firstConvertfor BGRA Format's  numpy Array
            if image.mode != "RGBA":
                image = image.convert("RGBA")
            
            # PIL RGBA -> Windows BGRA
            img_array = np.array(image)
            # RGBA -> BGRA
            img_bgra = img_array[:, :, [2, 1, 0, 3]].copy()
            
            width, height = image.size
            
            # Create SoftwareBitmap
            bitmap = SoftwareBitmap(
                BitmapPixelFormat.BGRA8,
                width,
                height,
                BitmapAlphaMode.PREMULTIPLIED
            )
            
            # WritePixelData
            bitmap.copy_from_buffer(img_bgra.tobytes())
            
            # 3. Execute OCR
            ocr_result = await engine.recognize_async(bitmap)
            
            # 4. ParseResult
            full_text = ocr_result.text
            regions = []
            
            if detect_regions:
                for line in ocr_result.lines:
                    for word in line.words:
                        bbox = word.bounding_rect
                        regions.append(TextRegion(
                            text=word.text,
                            bbox=(
                                int(bbox.x),
                                int(bbox.y),
                                int(bbox.x + bbox.width),
                                int(bbox.y + bbox.height)
                            ),
                            confidence=1.0,  # Windows OCR notmentionprovideconfidence
                        ))
            
            return OCRResult(
                full_text=full_text,
                regions=regions,
                engine="windows",
            )
            
        except Exception as e:
            logger.warning(f"Windows OCR failed: {e}")
            if HAS_TESSERACT:
                return await self._extract_tesseract(image, detect_regions)
            return self._extract_fallback(image)
    
    async def _extract_easyocr(
        self,
        image: "Image.Image",
        detect_regions: bool,
    ) -> OCRResult:
        """Usage EasyOCR"""
        if not self._easyocr_reader:
            return self._extract_fallback(image)
        
        import numpy as np
        
        # Convertfor numpy Array
        image_np = np.array(image)
        
        # Execute OCR
        results = self._easyocr_reader.readtext(image_np)
        
        # ParseResult
        regions = []
        full_text_parts = []
        
        for bbox, text, conf in results:
            # EasyOCR bbox Format: [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]
            x_coords = [p[0] for p in bbox]
            y_coords = [p[1] for p in bbox]
            x1, x2 = int(min(x_coords)), int(max(x_coords))
            y1, y2 = int(min(y_coords)), int(max(y_coords))
            
            regions.append(TextRegion(
                text=text,
                bbox=(x1, y1, x2, y2),
                confidence=conf,
            ))
            full_text_parts.append(text)
        
        return OCRResult(
            full_text=" ".join(full_text_parts),
            regions=regions if detect_regions else [],
            engine="easyocr",
        )
    
    async def _extract_tesseract(
        self,
        image: "Image.Image",
        detect_regions: bool,
    ) -> OCRResult:
        """Usage Tesseract OCR"""
        if not HAS_TESSERACT:
            return self._extract_fallback(image)
        
        # simpletextExtraction
        full_text = pytesseract.image_to_string(image)
        
        regions = []
        if detect_regions:
            # GetdetailedInfo
            try:
                data = pytesseract.image_to_data(
                    image, 
                    output_type=pytesseract.Output.DICT
                )
                
                for i, text in enumerate(data['text']):
                    if text.strip():
                        conf = float(data['conf'][i])
                        if conf > 0:  # FilterInvalidResult
                            x = data['left'][i]
                            y = data['top'][i]
                            w = data['width'][i]
                            h = data['height'][i]
                            
                            regions.append(TextRegion(
                                text=text,
                                bbox=(x, y, x + w, y + h),
                                confidence=conf / 100.0,
                            ))
            except Exception as e:
                logger.warning(f"Failed to get region data: {e}")
        
        return OCRResult(
            full_text=full_text.strip(),
            regions=regions,
            engine="tesseract",
        )
    
    def _extract_fallback(self, image: "Image.Image") -> OCRResult:
        """回退方案：ReturnEmptyResult"""
        logger.warning("No OCR engine available")
        return OCRResult(
            full_text="",
            regions=[],
            engine="none",
        )
    
    @property
    def engine_name(self) -> str:
        """当BeforeUsage的引擎名称"""
        return self._engine_name
    
    @property
    def is_available(self) -> bool:
        """OCR YesNoAvailable"""
        return self._engine_name != "none" and self._engine_name != "fallback"


# ========== GlobalInstance ==========

_default_extractor: Optional[OCRExtractor] = None


def get_ocr_extractor(
    preferred_engine: Optional[str] = None,
) -> OCRExtractor:
    """
    GetGlobal OCR 提取器
    
    Args:
        preferred_engine: First选引擎
        
    Returns:
        OCRExtractor Instance
    """
    global _default_extractor
    
    if _default_extractor is None:
        _default_extractor = OCRExtractor(preferred_engine)
    
    return _default_extractor
