# -*- coding: utf-8 -*-
"""
Desktop MCP 交互式测试脚本
运行: python test_interactive.py
"""
import time
import json
import pyautogui
import pyperclip
from pywinauto import Desktop, Application

pyautogui.FAILSAFE = True  # 鼠标移到左上角可中断

def list_windows():
    """列出所有窗口"""
    desktop = Desktop(backend="uia")
    windows = []
    for w in desktop.windows():
        try:
            title = w.window_text()
            if title and len(title) > 1:
                rect = w.rectangle()
                windows.append({
                    "title": title[:50],
                    "pos": f"({rect.left}, {rect.top})",
                    "size": f"{rect.width()}x{rect.height()}"
                })
        except:
            pass
    return windows[:15]

def open_app(name):
    """通过开始菜单打开应用"""
    pyautogui.press('win')
    time.sleep(0.5)
    pyautogui.typewrite(name, interval=0.05)
    time.sleep(0.8)
    pyautogui.press('enter')
    time.sleep(2)
    return f"Opened {name}"

def click(x, y):
    """点击指定坐标"""
    pyautogui.click(x, y)
    return f"Clicked ({x}, {y})"

def type_text(text):
    """输入文字（支持中文）"""
    if any(ord(c) > 127 for c in text):
        pyperclip.copy(text)
        pyautogui.hotkey('ctrl', 'v')
    else:
        pyautogui.typewrite(text, interval=0.03)
    return f"Typed: {text}"

def hotkey(*keys):
    """按组合键"""
    pyautogui.hotkey(*keys)
    return f"Pressed: {'+'.join(keys)}"

def screenshot(filename="test_screenshot.png"):
    """截图保存"""
    img = pyautogui.screenshot()
    img.save(filename)
    return f"Saved to {filename}"

def send_to_app(app_name, message):
    """发送消息到指定应用（WhatsApp/微信等）"""
    # 打开应用
    open_app(app_name)
    time.sleep(2)
    
    # 找窗口
    desktop = Desktop(backend="uia")
    target = None
    for w in desktop.windows():
        if app_name.lower() in w.window_text().lower():
            rect = w.rectangle()
            if rect.width() > 100:
                target = rect
                break
    
    if not target:
        return f"Window not found: {app_name}"
    
    # 点击输入框（窗口底部中间）
    x = target.left + int(target.width() * 0.7)
    y = target.bottom - 40
    click(x, y)
    time.sleep(0.3)
    
    # 输入并发送
    type_text(message)
    time.sleep(0.2)
    hotkey('enter')
    
    return f"Sent '{message}' to {app_name}"

# ============================================================
# 交互式菜单
# ============================================================

def main():
    print("\n" + "="*50)
    print("  Desktop MCP Interactive Tester")
    print("="*50)
    
    while True:
        print("\n[Commands]")
        print("  1. list      - List all windows")
        print("  2. open X    - Open app (e.g. 'open notepad')")
        print("  3. click X Y - Click at coordinates")
        print("  4. type X    - Type text")
        print("  5. key X Y   - Press hotkey (e.g. 'key ctrl s')")
        print("  6. shot      - Take screenshot")
        print("  7. send APP MSG - Send message to app")
        print("  8. quit      - Exit")
        print("-"*50)
        
        cmd = input("> ").strip().lower()
        
        try:
            if cmd == "list" or cmd == "1":
                windows = list_windows()
                for i, w in enumerate(windows):
                    print(f"  {i+1}. {w['title']} | {w['pos']} | {w['size']}")
            
            elif cmd.startswith("open ") or cmd.startswith("2 "):
                name = cmd.split(" ", 1)[1]
                print(open_app(name))
            
            elif cmd.startswith("click ") or cmd.startswith("3 "):
                parts = cmd.split()
                x, y = int(parts[1]), int(parts[2])
                print(click(x, y))
            
            elif cmd.startswith("type ") or cmd.startswith("4 "):
                text = cmd.split(" ", 1)[1]
                print(type_text(text))
            
            elif cmd.startswith("key ") or cmd.startswith("5 "):
                keys = cmd.split()[1:]
                print(hotkey(*keys))
            
            elif cmd == "shot" or cmd == "6":
                print(screenshot())
            
            elif cmd.startswith("send ") or cmd.startswith("7 "):
                parts = cmd.split(" ", 2)
                app, msg = parts[1], parts[2]
                print(send_to_app(app, msg))
            
            elif cmd == "quit" or cmd == "8" or cmd == "q":
                print("Bye!")
                break
            
            else:
                print("Unknown command")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
