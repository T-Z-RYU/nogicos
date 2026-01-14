# -*- coding: utf-8 -*-
"""Send WhatsApp message - with contact search"""
import time
import pyautogui
import pyperclip

pyautogui.FAILSAFE = True

def send_message(message, contact="ZinoT"):
    """Send a message to a WhatsApp contact"""
    
    # Step 1: Open WhatsApp via Start menu
    print("Opening WhatsApp...")
    pyautogui.press('win')
    time.sleep(0.5)
    pyautogui.typewrite('WhatsApp', interval=0.05)
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(2.5)
    
    # Step 2: Search for contact using Ctrl+F
    print(f"Searching for contact: {contact}...")
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.5)
    
    # Type contact name
    if all(ord(c) < 128 for c in contact):
        pyautogui.typewrite(contact, interval=0.05)
    else:
        pyperclip.copy(contact)
        pyautogui.hotkey('ctrl', 'v')
    
    time.sleep(1)
    
    # Press Enter to select first result
    pyautogui.press('enter')
    time.sleep(0.8)
    
    # Step 3: Click in message input area
    screen_w, screen_h = pyautogui.size()
    input_x = int(screen_w * 0.75)
    input_y = int(screen_h * 0.9)
    
    print(f"Clicking input at ({input_x}, {input_y})")
    pyautogui.click(input_x, input_y)
    time.sleep(0.3)
    
    # Step 4: Type message using clipboard
    print(f"Typing: {message}")
    pyperclip.copy(message)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.3)
    
    # Step 5: Send
    pyautogui.press('enter')
    print("Message sent!")
    return True

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        contact = sys.argv[1]
        msg = sys.argv[2]
    elif len(sys.argv) == 2:
        contact = "ZinoT"
        msg = sys.argv[1]
    else:
        contact = "ZinoT"
        msg = "test from NogicOS"
    
    send_message(msg, contact)
