# -*- coding: utf-8 -*-
"""Send WhatsApp message script"""
import time
import pyautogui
import pyperclip

def send_whatsapp_message(message: str, x: int = 1240, y: int = 757):
    """Click input box, type message, press enter to send"""
    # Click input box
    pyautogui.click(x, y)
    time.sleep(0.3)
    
    # Use clipboard for Chinese text
    pyperclip.copy(message)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.3)
    
    # Press enter to send
    pyautogui.press('enter')
    print("Message sent!")

if __name__ == "__main__":
    # Message to send
    msg = "\u725b\u903c"  # "牛逼" in unicode escape
    send_whatsapp_message(msg)
