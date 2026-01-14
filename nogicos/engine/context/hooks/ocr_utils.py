# -*- coding: utf-8 -*-
"""
OCR Utilities - 本地 OCR 支持

提供多种 OCR 引擎支持：
1. Windows OCR (Inner置)
2. pytesseract (跨Platform)
3. EasyOCR (AI-based)
"""

import asyncio
import logging
import sys
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class OCRResult:
    """OCR 识别Result"""
    text: str
    confidence: float = 0.0
    bbox: Optional[Tuple[int, int, int, int]] = None  # x, y, width, height


class OCREngine:
    """OCR 引擎基Class"""
    
    def __init__(self):
        self._available = False
    
    @property
    def available(self) -> bool:
        return self._available
    
    async def recognize(self, image_data: bytes) -> List[OCRResult]:
        """识别Graph像Medium的文字"""
        raise NotImplementedError


class WindowsOCR(OCREngine):
    """
    Windows Inner置 OCR
    
    Usage Windows.Media.Ocr 命名Empty间
    优点：无需安装额Outer依赖，速度快
    缺点：仅 Windows 10/11
    """
    
    def __init__(self):
        super().__init__()
        self._engine = None
        
        if sys.platform == "win32":
            try:
                # tryImport Windows OCR
                import winsdk.windows.media.ocr as ocr
                import winsdk.windows.graphics.imaging as imaging
                import winsdk.windows.storage.streams as streams
                
                self._ocr_module = ocr
                self._imaging_module = imaging
                self._streams_module = streams
                
                # CheckYesNohaveAvailable's  OCR engine
                # DefaultUsageUserLanguage
                self._engine = ocr.OcrEngine.try_create_from_user_profile_languages()
                self._available = self._engine is not None
                
                if self._available:
                    logger.info("[WindowsOCR] Engine initialized")
                else:
                    logger.warning("[WindowsOCR] No OCR language available")
                    
            except ImportError:
                logger.debug("[WindowsOCR] winsdk not available")
            except Exception as e:
                logger.debug(f"[WindowsOCR] Init failed: {e}")
    
    async def recognize(self, image_data: bytes) -> List[OCRResult]:
        """Usage Windows OCR 识别文字"""
        if not self._available or not self._engine:
            return []
        
        try:
            from io import BytesIO
            
            ocr = self._ocr_module
            imaging = self._imaging_module
            streams = self._streams_module
            
            # CreateInnerstorestream
            stream = streams.InMemoryRandomAccessStream()
            writer = streams.DataWriter(stream.get_output_stream_at(0))
            writer.write_bytes(list(image_data))
            await writer.store_async()
            
            # DecodeGraphlike
            stream.seek(0)
            decoder = await imaging.BitmapDecoder.create_async(stream)
            bitmap = await decoder.get_software_bitmap_async()
            
            # OCR Recognition
            result = await self._engine.recognize_async(bitmap)
            
            # ParseResult
            ocr_results = []
            for line in result.lines:
                ocr_results.append(OCRResult(
                    text=line.text,
                    confidence=0.9,  # Windows OCR notmentionprovideconfidence
                ))
            
            return ocr_results
            
        except Exception as e:
            logger.error(f"[WindowsOCR] Recognition failed: {e}")
            return []


class TesseractOCR(OCREngine):
    """
    Tesseract OCR
    
    Usage pytesseract + Tesseract-OCR
    优点：跨Platform，支持多语言
    缺点：需要安装 Tesseract
    """
    
    def __init__(self):
        super().__init__()
        
        try:
            import pytesseract
            from PIL import Image
            
            self._pytesseract = pytesseract
            self._Image = Image
            
            # Test Tesseract YesNoAvailable
            pytesseract.get_tesseract_version()
            self._available = True
            logger.info("[TesseractOCR] Engine initialized")
            
        except ImportError:
            logger.debug("[TesseractOCR] pytesseract not installed")
        except Exception as e:
            logger.debug(f"[TesseractOCR] Init failed: {e}")
    
    async def recognize(self, image_data: bytes) -> List[OCRResult]:
        """Usage Tesseract 识别文字"""
        if not self._available:
            return []
        
        try:
            from io import BytesIO
            
            # LoadGraphlike
            image = self._Image.open(BytesIO(image_data))
            
            # inThreadpoolMediumRunning OCR（avoidBlocked）
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._pytesseract.image_to_data(image, output_type=self._pytesseract.Output.DICT)
            )
            
            # ParseResult
            ocr_results = []
            n_boxes = len(result['text'])
            
            for i in range(n_boxes):
                text = result['text'][i].strip()
                conf = int(result['conf'][i])
                
                if text and conf > 30:  # FilterLowconfidence
                    ocr_results.append(OCRResult(
                        text=text,
                        confidence=conf / 100.0,
                        bbox=(
                            result['left'][i],
                            result['top'][i],
                            result['width'][i],
                            result['height'][i],
                        ),
                    ))
            
            return ocr_results
            
        except Exception as e:
            logger.error(f"[TesseractOCR] Recognition failed: {e}")
            return []


class ScreenshotOCR:
    """
    截Graph OCR 管理器
    
    AutoSelectAvailable的 OCR 引擎
    """
    
    def __init__(self):
        self._engines: List[OCREngine] = []
        
        # byPrioritylevelAddengine
        # 1. Windows OCR（mostFast）
        if sys.platform == "win32":
            win_ocr = WindowsOCR()
            if win_ocr.available:
                self._engines.append(win_ocr)
        
        # 2. Tesseract（crossPlatform）
        tesseract = TesseractOCR()
        if tesseract.available:
            self._engines.append(tesseract)
        
        if self._engines:
            logger.info(f"[ScreenshotOCR] {len(self._engines)} engine(s) available")
        else:
            logger.warning("[ScreenshotOCR] No OCR engine available")
    
    @property
    def available(self) -> bool:
        return len(self._engines) > 0
    
    async def recognize(self, image_data: bytes) -> List[OCRResult]:
        """
        识别Graph像Medium的文字
        
        AutoUsage第一个Available的引擎
        """
        for engine in self._engines:
            try:
                results = await engine.recognize(image_data)
                if results:
                    return results
            except Exception as e:
                logger.warning(f"[ScreenshotOCR] Engine failed: {e}")
                continue
        
        return []
    
    async def extract_url(self, screenshot_data: bytes, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[str]:
        """
        从截GraphMedium提取 URL
        
        Args:
            screenshot_data: 截Graph的二进制数据
            region: Optional的裁剪区域 (x, y, width, height)
        
        Returns:
            提取的 URL 或 None
        """
        import re
        
        # IfSpecifyLocale，ClippingGraphlike
        if region:
            try:
                from PIL import Image
                from io import BytesIO
                
                image = Image.open(BytesIO(screenshot_data))
                x, y, w, h = region
                cropped = image.crop((x, y, x + w, y + h))
                
                buffer = BytesIO()
                cropped.save(buffer, format='PNG')
                screenshot_data = buffer.getvalue()
            except Exception as e:
                logger.warning(f"[ScreenshotOCR] Failed to crop image: {e}")
        
        # OCR Recognition
        results = await self.recognize(screenshot_data)
        
        # Mergealltext
        full_text = " ".join(r.text for r in results)
        
        # URL regexMatch
        url_patterns = [
            r'https?://[^\s<>"{}|\\^`\[\]]+',  # Complete URL
            r'(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[^\s<>"{}|\\^`\[\]]*)?',  # domainname
        ]
        
        for pattern in url_patterns:
            matches = re.findall(pattern, full_text)
            if matches:
                url = matches[0]
                # Completion https://
                if not url.startswith('http'):
                    url = f"https://{url}"
                return url
        
        return None


# GlobalSingleton
_screenshot_ocr: Optional[ScreenshotOCR] = None


def get_screenshot_ocr() -> ScreenshotOCR:
    """Get ScreenshotOCR Singleton"""
    global _screenshot_ocr
    if _screenshot_ocr is None:
        _screenshot_ocr = ScreenshotOCR()
    return _screenshot_ocr


async def capture_and_ocr(hwnd: int = 0, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[str]:
    """
    便捷Function：截Graph并 OCR
    
    Args:
        hwnd: Window句柄，0 Table示全屏
        region: 裁剪区域
    
    Returns:
        OCR 识别的文本
    """
    try:
        import mss
        
        with mss.mss() as sct:
            if hwnd == 0:
                # FullscreencaptureGraph
                monitor = sct.monitors[1]  # mainDisplayer
            else:
                # TODO: GetWindowLocale
                monitor = sct.monitors[1]
            
            if region:
                monitor = {
                    "left": region[0],
                    "top": region[1],
                    "width": region[2],
                    "height": region[3],
                }
            
            screenshot = sct.grab(monitor)
            
            # Convertfor PNG
            from PIL import Image
            from io import BytesIO
            
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            image_data = buffer.getvalue()
        
        # OCR
        ocr = get_screenshot_ocr()
        results = await ocr.recognize(image_data)
        
        return " ".join(r.text for r in results)
        
    except Exception as e:
        logger.error(f"[capture_and_ocr] Failed: {e}")
        return None

