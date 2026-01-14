# -*- coding: utf-8 -*-
"""
Messaging Tools - WhatsApp and other messaging platforms

Tools for sending messages through desktop messaging apps.
Uses pyautogui + pyperclip for desktop automation.
"""

import time
import logging
from typing import Optional

logger = logging.getLogger("nogicos.tools.messaging")

# ============================================================================
# Import dependencies
# ============================================================================

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    pyautogui = None

try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False
    pyperclip = None


def register_messaging_tools(registry):
    """
    Register messaging tools to the registry.
    
    Args:
        registry: ToolRegistry instance
    """
    from .base import ToolCategory
    
    # ========================================================================
    # WhatsApp Tools
    # ========================================================================
    
    @registry.action(
        description="""Send a WhatsApp message to a contact.

This tool:
1. Opens WhatsApp via Start menu
2. Uses pywinauto to locate the WhatsApp window precisely
3. Clicks in the message input and sends the message

Requirements:
- WhatsApp Desktop must be installed
- The contact chat must be visible in the chat list
- Supports Chinese and other Unicode characters

Example: send_whatsapp(contact="ZinoT", message="你好")""",
        category=ToolCategory.LOCAL,
    )
    async def send_whatsapp(
        contact: str,
        message: str,
        wait_for_app: float = 3.0,
    ) -> str:
        """
        Send a WhatsApp message to a specific contact.
        
        Args:
            contact: Contact name (must be visible in chat list or searchable)
            message: Message text to send (supports Chinese/Unicode)
            wait_for_app: Seconds to wait for WhatsApp to open
            
        Returns:
            Success or error message
        """
        if not PYAUTOGUI_AVAILABLE:
            return "Error: pyautogui not installed. Run: pip install pyautogui"
        if not PYPERCLIP_AVAILABLE:
            return "Error: pyperclip not installed. Run: pip install pyperclip"
        
        try:
            # Import pywinauto for window detection
            try:
                from pywinauto import Desktop
            except ImportError:
                return "Error: pywinauto not installed. Run: pip install pywinauto"
            
            # Step 1: Check if WhatsApp is already open
            logger.info("[WhatsApp] Checking if WhatsApp is already open...")
            desktop = Desktop(backend='uia')
            whatsapp = None
            all_windows = []
            for win in desktop.windows():
                title = win.window_text()
                all_windows.append(title)
                if 'WhatsApp' in title:
                    whatsapp = win
                    break
            
            # #region agent log H6
            import json as _json; open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log','a',encoding='utf-8').write(_json.dumps({"hypothesisId":"H6","location":"messaging.py:find_window","message":"Window search result","data":{"found":bool(whatsapp),"all_windows":all_windows[:10],"whatsapp_title":whatsapp.window_text() if whatsapp else None},"timestamp":__import__('time').time()})+'\n')
            # #endregion
            
            # Only open WhatsApp if not already running
            if not whatsapp:
                logger.info(f"[WhatsApp] WhatsApp not open, launching...")
                pyautogui.press('win')
                time.sleep(0.5)
                pyautogui.typewrite('WhatsApp', interval=0.05)
                time.sleep(1)
                pyautogui.press('enter')
                time.sleep(wait_for_app)
                
                # Find the window again
                for win in desktop.windows():
                    title = win.window_text()
                    if 'WhatsApp' in title:
                        whatsapp = win
                        break
            else:
                logger.info(f"[WhatsApp] WhatsApp already open, using existing window")
            
            if not whatsapp:
                return "Error: WhatsApp window not found. Make sure WhatsApp is installed."
            
            rect = whatsapp.rectangle()
            
            # #region agent log H7
            open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log','a',encoding='utf-8').write(_json.dumps({"hypothesisId":"H7","location":"messaging.py:window_rect","message":"Window rectangle","data":{"left":rect.left,"top":rect.top,"right":rect.right,"bottom":rect.bottom,"width":rect.width(),"height":rect.height(),"is_minimized":whatsapp.is_minimized() if hasattr(whatsapp,'is_minimized') else 'unknown'},"timestamp":__import__('time').time()})+'\n')
            # #endregion
            
            logger.info(f"[WhatsApp] Window at ({rect.left},{rect.top}) {rect.width()}x{rect.height()}")
            
            # Bring WhatsApp to focus
            whatsapp.set_focus()
            time.sleep(0.5)
            
            # Step 2: Search and navigate to the contact
            logger.info(f"[WhatsApp] Searching for contact: {contact}")
            # #region agent log H8
            open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log','a',encoding='utf-8').write(_json.dumps({"hypothesisId":"H8","location":"messaging.py:search_contact","message":"Searching for contact","data":{"contact":contact},"timestamp":__import__('time').time()})+'\n')
            # #endregion
            
            # Press Ctrl+F to open search
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(0.5)
            
            # Type contact name using clipboard for Unicode support
            pyperclip.copy(contact)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(1)
            
            # Press Enter to select the contact
            pyautogui.press('enter')
            time.sleep(0.5)
            
            # Step 3: Click in message input area (bottom center of window)
            # Re-get the rect since window might have resized
            rect = whatsapp.rectangle()
            input_x = rect.left + int(rect.width() * 0.5)
            input_y = rect.bottom - 30
            
            logger.info(f"[WhatsApp] Clicking input at ({input_x}, {input_y})")
            pyautogui.click(input_x, input_y)
            time.sleep(0.5)
            
            # Step 4: Type message using clipboard (for Unicode support)
            logger.info(f"[WhatsApp] Typing message: {message[:30]}...")
            pyperclip.copy(message)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.3)
            
            # Step 5: Send message
            pyautogui.press('enter')
            
            logger.info(f"[WhatsApp] Message sent to {contact}")
            return f"Successfully sent WhatsApp message to {contact}: {message}"
            
        except Exception as e:
            logger.error(f"[WhatsApp] Error: {e}")
            return f"Error sending WhatsApp message: {str(e)}"
    
    @registry.action(
        description="""Open WhatsApp and optionally navigate to a specific contact's chat.

This tool:
1. Opens WhatsApp via Start menu
2. If contact is specified, searches and opens their chat

Use this when you need to:
- Just open WhatsApp without sending a message
- Prepare to send multiple messages to same contact

Example: open_whatsapp(contact="ZinoT")""",
        category=ToolCategory.LOCAL,
    )
    async def open_whatsapp(
        contact: Optional[str] = None,
        wait_for_app: float = 2.0,
    ) -> str:
        """
        Open WhatsApp and optionally navigate to a contact's chat.
        
        Args:
            contact: Optional contact name to open chat with
            wait_for_app: Seconds to wait for WhatsApp to open
            
        Returns:
            Success or error message
        """
        if not PYAUTOGUI_AVAILABLE:
            return "Error: pyautogui not installed"
        
        try:
            # Open WhatsApp via Start menu
            logger.info("[WhatsApp] Opening WhatsApp")
            pyautogui.press('win')
            time.sleep(0.5)
            pyautogui.typewrite('WhatsApp', interval=0.05)
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(wait_for_app)
            
            if contact:
                # Search for contact
                logger.info(f"[WhatsApp] Navigating to contact: {contact}")
                pyautogui.hotkey('ctrl', 'f')
                time.sleep(0.3)
                
                is_ascii = all(ord(c) < 128 for c in contact)
                if is_ascii:
                    pyautogui.typewrite(contact, interval=0.05)
                else:
                    if PYPERCLIP_AVAILABLE:
                        pyperclip.copy(contact)
                        pyautogui.hotkey('ctrl', 'v')
                    else:
                        return "Error: pyperclip needed for non-ASCII contact names"
                
                time.sleep(1)
                pyautogui.press('enter')
                time.sleep(0.5)
                
                return f"WhatsApp opened with chat: {contact}"
            
            return "WhatsApp opened successfully"
            
        except Exception as e:
            logger.error(f"[WhatsApp] Error: {e}")
            return f"Error opening WhatsApp: {str(e)}"
    
    logger.info("[Messaging] WhatsApp tools registered")
