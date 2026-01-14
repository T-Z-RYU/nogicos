# -*- coding: utf-8 -*-
"""
Vision Tools - Phase C4

Claude Vision API integration for visual understanding.

Tools:
- C4.1: Claude Vision API integration
- C4.2: analyze_screenshot tool
- C4.3: Agent decision support
"""

# [Fix] Ensure user-installed packages can be found
import sys
import os
_user_site = os.path.expanduser("~\\AppData\\Roaming\\Python\\Python314\\site-packages")
if _user_site not in sys.path:
    sys.path.insert(0, _user_site)

import base64
import logging
from typing import Optional
from io import BytesIO

logger = logging.getLogger("nogicos.tools.vision")

# ============================================================================
# Anthropic Vision API (C4.1)
# ============================================================================

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None
    logger.warning("[Vision] anthropic not installed")

# PIL for image handling
try:
    from PIL import Image, ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None
    ImageGrab = None


class VisionAnalyzer:
    """
    Claude Vision API wrapper for screenshot analysis (C4.1).
    
    Uses Claude's multimodal capabilities to understand
    what's on screen and provide actionable insights.
    """
    
    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        """
        Initialize vision analyzer.
        
        Args:
            model: Claude model to use (must support vision)
        """
        self.model = model
        self.client = None
        
        if ANTHROPIC_AVAILABLE:
            # Try api_keys.py first, then environment variable
            api_key = None
            try:
                import api_keys
                api_key = api_keys.ANTHROPIC_API_KEY
            except (ImportError, AttributeError):
                api_key = os.environ.get("ANTHROPIC_API_KEY")
            
            if api_key:
                self.client = anthropic.Anthropic(api_key=api_key)
        
        if self.client:
            logger.info(f"[Vision] Initialized with model: {model}")
        else:
            logger.warning("[Vision] Client not available (check API key)")
    
    async def analyze_screenshot(
        self,
        image_b64: str,
        prompt: str = "Describe what you see on this screen.",
        max_tokens: int = 1024,
    ) -> str:
        """
        Analyze a screenshot using Claude Vision.
        
        Args:
            image_b64: Base64 encoded image (PNG or JPEG)
            prompt: Analysis prompt
            max_tokens: Maximum response tokens
            
        Returns:
            Analysis text
        """
        if not self.client:
            return "Error: Vision API not available"
        
        try:
            # Determine media type
            media_type = "image/png"
            if image_b64.startswith("/9j/"):  # JPEG magic bytes
                media_type = "image/jpeg"
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_b64,
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt,
                        }
                    ]
                }]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"[Vision] Analysis error: {e}")
            return f"Error analyzing screenshot: {str(e)}"
    
    async def find_element(
        self,
        image_b64: str,
        element_description: str,
    ) -> Optional[dict]:
        """
        Find UI element in screenshot (C4.3).
        
        Args:
            image_b64: Screenshot as base64
            element_description: Description of element to find
            
        Returns:
            Dict with 'found', 'x', 'y', 'description' or None
        """
        if not self.client:
            return None
        
        prompt = f"""Analyze this screenshot and find the UI element: "{element_description}"

If found, respond with ONLY JSON in this format:
{{"found": true, "x": <center_x>, "y": <center_y>, "description": "<brief description>"}}

If not found:
{{"found": false, "reason": "<why not found>"}}

Estimate coordinates as percentage of screen (0-100 for x and y)."""

        try:
            result = await self.analyze_screenshot(image_b64, prompt, max_tokens=256)
            
            # Parse JSON from response
            import json
            # Try to extract JSON from response
            if "{" in result and "}" in result:
                json_start = result.index("{")
                json_end = result.rindex("}") + 1
                json_str = result[json_start:json_end]
                return json.loads(json_str)
            
            return {"found": False, "reason": "Could not parse response"}
            
        except Exception as e:
            return {"found": False, "reason": str(e)}


def register_vision_tools(registry):
    """
    Register vision tools to the registry.
    
    Args:
        registry: ToolRegistry instance
    """
    from .base import ToolCategory
    
    # Shared analyzer instance
    analyzer = VisionAnalyzer()
    
    @registry.action(
        description="Analyze desktop screenshot with AI vision. Use 'prompt' or 'question' parameter.",
        category=ToolCategory.LOCAL,
    )
    async def desktop_analyze_screen(
        prompt: Optional[str] = None,
        question: Optional[str] = None,  # Alias for prompt
    ) -> str:
        """
        C4.2: Take screenshot and analyze with Claude Vision.
        
        Args:
            prompt: What to analyze/look for
            question: Alias for prompt
            
        Returns:
            AI analysis of the screen
        """
        # Handle parameter aliases
        actual_prompt = prompt or question or "Describe what you see on this screen, focusing on key UI elements and any text."
        
        if not PIL_AVAILABLE:
            return "Error: PIL not installed"
        
        if not analyzer.client:
            return "Error: Vision API not available"
        
        try:
            # Take screenshot
            screenshot = ImageGrab.grab()
            
            # Convert to base64
            buffer = BytesIO()
            screenshot.save(buffer, format='PNG')
            image_b64 = base64.b64encode(buffer.getvalue()).decode()
            
            # Analyze
            result = await analyzer.analyze_screenshot(image_b64, actual_prompt)
            return result
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    @registry.action(
        description="Find UI element on screen using AI vision. Pass the element description as 'element_description' parameter.",
        category=ToolCategory.LOCAL,
    )
    async def desktop_find_element(
        element_description: Optional[str] = None,
        # Common aliases AI might use
        title: Optional[str] = None,
        description: Optional[str] = None,
        element: Optional[str] = None,
        name: Optional[str] = None,
    ) -> str:
        """
        C4.3: Find UI element coordinates using vision.

        Args:
            element_description: Description of element to find
                (e.g., "the blue Submit button", "search box in top right")
            title: Alias for element_description
            description: Alias for element_description
            element: Alias for element_description
            name: Alias for element_description

        Returns:
            Element location or not found message
        """
        # Support multiple parameter names that AI might use
        actual_description = element_description or title or description or element or name
        if not actual_description:
            return "Error: Must provide element_description (or title/description/element/name)"
        element_description = actual_description

        if not PIL_AVAILABLE:
            return "Error: PIL not installed"
        
        if not analyzer.client:
            return "Error: Vision API not available"
        
        try:
            # Take screenshot
            screenshot = ImageGrab.grab()
            width, height = screenshot.size
            
            # Convert to base64
            buffer = BytesIO()
            screenshot.save(buffer, format='PNG')
            image_b64 = base64.b64encode(buffer.getvalue()).decode()
            
            # Find element
            result = await analyzer.find_element(image_b64, element_description)
            
            if result and result.get("found"):
                # Convert percentage to pixel coordinates
                x = int(result["x"] * width / 100)
                y = int(result["y"] * height / 100)
                return f"Found '{element_description}' at ({x}, {y}). Description: {result.get('description', 'N/A')}"
            else:
                reason = result.get("reason", "Unknown") if result else "Analysis failed"
                return f"Element not found: {reason}"
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    @registry.action(
        description="Click on UI element found by AI vision. Use 'element_description' parameter.",
        category=ToolCategory.LOCAL,
    )
    async def desktop_click_element(
        element_description: Optional[str] = None,
        # Common aliases AI might use
        title: Optional[str] = None,
        description: Optional[str] = None,
        element: Optional[str] = None,
        name: Optional[str] = None,
        target: Optional[str] = None,
    ) -> str:
        """
        Find element with vision and click on it.

        Args:
            element_description: Description of element to click
            title: Alias for element_description
            description: Alias for element_description
            element: Alias for element_description
            name: Alias for element_description
            target: Alias for element_description

        Returns:
            Click result message
        """
        # Support multiple parameter names
        actual_description = element_description or title or description or element or name or target
        if not actual_description:
            return "Error: Must provide element_description (or title/description/element/name/target)"
        element_description = actual_description

        if not PIL_AVAILABLE:
            return "Error: PIL not installed"
        
        if not analyzer.client:
            return "Error: Vision API not available"
        
        try:
            import pyautogui
        except ImportError:
            return "Error: pyautogui not installed"
        
        try:
            # Take screenshot
            screenshot = ImageGrab.grab()
            width, height = screenshot.size
            
            # Convert to base64
            buffer = BytesIO()
            screenshot.save(buffer, format='PNG')
            image_b64 = base64.b64encode(buffer.getvalue()).decode()
            
            # Find element
            result = await analyzer.find_element(image_b64, element_description)
            
            if result and result.get("found"):
                # Convert percentage to pixel coordinates
                x = int(result["x"] * width / 100)
                y = int(result["y"] * height / 100)
                
                # Click
                pyautogui.click(x, y)
                return f"Clicked '{element_description}' at ({x}, {y})"
            else:
                reason = result.get("reason", "Unknown") if result else "Analysis failed"
                return f"Cannot click - element not found: {reason}"
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    logger.info("[Vision] All vision tools registered")


# Global analyzer for direct use
_analyzer: Optional[VisionAnalyzer] = None


def get_analyzer() -> VisionAnalyzer:
    """Get or create global analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = VisionAnalyzer()
    return _analyzer

