#!/usr/bin/env python3
"""
Desktop MCP Server - 让 Cursor 能操作 Windows 桌面应用
基于 Model Context Protocol (MCP) 标准

使用方法：
1. pip install pyautogui pywinauto pillow
2. 配置到 Cursor 的 mcp.json
3. 在 Cursor 中使用桌面工具
"""

import sys
import json
import base64
import subprocess
import time
from io import BytesIO
from typing import Any, Dict, List, Optional

# ============================================================
# 依赖检查
# ============================================================

try:
    import pyautogui
    pyautogui.FAILSAFE = True  # 鼠标移到左上角可中断
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    from pywinauto import Application, Desktop
    from pywinauto.findwindows import ElementNotFoundError
    PYWINAUTO_AVAILABLE = True
except ImportError:
    PYWINAUTO_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ============================================================
# MCP 协议处理
# ============================================================

class DesktopMCPServer:
    """桌面自动化 MCP 服务器"""
    
    def __init__(self):
        self.tools = self._register_tools()
    
    def _register_tools(self) -> List[Dict]:
        """注册所有可用工具"""
        tools = [
            {
                "name": "desktop_screenshot",
                "description": "截取整个屏幕或指定窗口的截图，返回 base64 编码的图片",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "window_title": {
                            "type": "string",
                            "description": "可选：指定窗口标题，不填则截取整个屏幕"
                        }
                    }
                }
            },
            {
                "name": "desktop_click",
                "description": "在屏幕指定坐标位置点击鼠标",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "x": {"type": "integer", "description": "X 坐标"},
                        "y": {"type": "integer", "description": "Y 坐标"},
                        "button": {
                            "type": "string",
                            "enum": ["left", "right", "middle"],
                            "description": "鼠标按钮，默认 left"
                        },
                        "clicks": {"type": "integer", "description": "点击次数，默认 1"}
                    },
                    "required": ["x", "y"]
                }
            },
            {
                "name": "desktop_type",
                "description": "在当前焦点位置输入文字",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "要输入的文字"},
                        "interval": {
                            "type": "number",
                            "description": "每个字符之间的间隔（秒），默认 0.05"
                        }
                    },
                    "required": ["text"]
                }
            },
            {
                "name": "desktop_hotkey",
                "description": "按下组合键，如 Ctrl+C, Alt+Tab",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "keys": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "按键列表，如 ['ctrl', 'c'] 表示 Ctrl+C"
                        }
                    },
                    "required": ["keys"]
                }
            },
            {
                "name": "desktop_open_app",
                "description": "通过开始菜单搜索并打开应用程序",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "app_name": {
                            "type": "string",
                            "description": "应用名称，如 'WhatsApp', 'Notepad', 'Chrome'"
                        }
                    },
                    "required": ["app_name"]
                }
            },
            {
                "name": "desktop_list_windows",
                "description": "列出当前所有打开的窗口",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "desktop_focus_window",
                "description": "聚焦到指定标题的窗口",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "window_title": {
                            "type": "string",
                            "description": "窗口标题（支持部分匹配）"
                        }
                    },
                    "required": ["window_title"]
                }
            },
            {
                "name": "desktop_window_click",
                "description": "在指定窗口中点击特定控件（通过控件名称或自动化 ID）",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "window_title": {
                            "type": "string",
                            "description": "窗口标题"
                        },
                        "control_name": {
                            "type": "string",
                            "description": "控件名称或文本"
                        },
                        "control_type": {
                            "type": "string",
                            "description": "控件类型，如 Button, Edit, Text"
                        }
                    },
                    "required": ["window_title", "control_name"]
                }
            },
            {
                "name": "desktop_window_type",
                "description": "在指定窗口的输入框中输入文字",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "window_title": {
                            "type": "string",
                            "description": "窗口标题"
                        },
                        "control_name": {
                            "type": "string",
                            "description": "输入框名称或自动化 ID"
                        },
                        "text": {
                            "type": "string",
                            "description": "要输入的文字"
                        }
                    },
                    "required": ["window_title", "text"]
                }
            }
        ]
        return tools
    
    # ============================================================
    # 工具实现
    # ============================================================
    
    def desktop_screenshot(self, window_title: Optional[str] = None) -> Dict:
        """截取屏幕截图"""
        if not PYAUTOGUI_AVAILABLE:
            return {"error": "pyautogui 未安装，请运行: pip install pyautogui"}
        
        try:
            if window_title and PYWINAUTO_AVAILABLE:
                # 截取特定窗口
                app = Application(backend="uia").connect(title_re=f".*{window_title}.*")
                window = app.top_window()
                rect = window.rectangle()
                screenshot = pyautogui.screenshot(region=(
                    rect.left, rect.top, 
                    rect.width(), rect.height()
                ))
            else:
                # 截取整个屏幕
                screenshot = pyautogui.screenshot()
            
            # 转换为 base64
            buffer = BytesIO()
            screenshot.save(buffer, format='PNG')
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return {
                "success": True,
                "width": screenshot.width,
                "height": screenshot.height,
                "image_base64": img_base64[:100] + "...(truncated)",  # 日志用
                "full_image": img_base64  # 完整图片
            }
        except Exception as e:
            return {"error": str(e)}
    
    def desktop_click(self, x: int, y: int, button: str = "left", clicks: int = 1) -> Dict:
        """点击屏幕指定位置"""
        if not PYAUTOGUI_AVAILABLE:
            return {"error": "pyautogui 未安装"}
        
        try:
            pyautogui.click(x, y, button=button, clicks=clicks)
            return {
                "success": True,
                "message": f"已在 ({x}, {y}) 点击 {button} 键 {clicks} 次"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def desktop_type(self, text: str, interval: float = 0.05) -> Dict:
        """输入文字"""
        if not PYAUTOGUI_AVAILABLE:
            return {"error": "pyautogui 未安装"}
        
        try:
            # 对于非 ASCII 字符，使用剪贴板
            if any(ord(c) > 127 for c in text):
                import pyperclip
                pyperclip.copy(text)
                pyautogui.hotkey('ctrl', 'v')
            else:
                pyautogui.typewrite(text, interval=interval)
            
            return {
                "success": True,
                "message": f"已输入: {text[:50]}{'...' if len(text) > 50 else ''}"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def desktop_hotkey(self, keys: List[str]) -> Dict:
        """按下组合键"""
        if not PYAUTOGUI_AVAILABLE:
            return {"error": "pyautogui 未安装"}
        
        try:
            pyautogui.hotkey(*keys)
            return {
                "success": True,
                "message": f"已按下组合键: {'+'.join(keys)}"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def desktop_open_app(self, app_name: str) -> Dict:
        """通过开始菜单打开应用"""
        if not PYAUTOGUI_AVAILABLE:
            return {"error": "pyautogui 未安装"}
        
        try:
            # 按 Win 键打开开始菜单
            pyautogui.press('win')
            time.sleep(0.5)
            
            # 输入应用名称
            pyautogui.typewrite(app_name, interval=0.05)
            time.sleep(0.8)
            
            # 按回车打开
            pyautogui.press('enter')
            
            return {
                "success": True,
                "message": f"已尝试打开应用: {app_name}"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def desktop_list_windows(self) -> Dict:
        """列出所有窗口"""
        if not PYWINAUTO_AVAILABLE:
            return {"error": "pywinauto 未安装，请运行: pip install pywinauto"}
        
        try:
            desktop = Desktop(backend="uia")
            windows = []
            
            for window in desktop.windows():
                try:
                    title = window.window_text()
                    if title:  # 只列出有标题的窗口
                        rect = window.rectangle()
                        windows.append({
                            "title": title,
                            "position": {"x": rect.left, "y": rect.top},
                            "size": {"width": rect.width(), "height": rect.height()}
                        })
                except:
                    pass
            
            return {
                "success": True,
                "count": len(windows),
                "windows": windows[:20]  # 最多返回 20 个
            }
        except Exception as e:
            return {"error": str(e)}
    
    def desktop_focus_window(self, window_title: str) -> Dict:
        """聚焦指定窗口"""
        if not PYWINAUTO_AVAILABLE:
            return {"error": "pywinauto 未安装"}
        
        try:
            app = Application(backend="uia").connect(title_re=f".*{window_title}.*")
            window = app.top_window()
            window.set_focus()
            
            return {
                "success": True,
                "message": f"已聚焦窗口: {window.window_text()}"
            }
        except ElementNotFoundError:
            return {"error": f"找不到标题包含 '{window_title}' 的窗口"}
        except Exception as e:
            return {"error": str(e)}
    
    def desktop_window_click(self, window_title: str, control_name: str, 
                             control_type: Optional[str] = None) -> Dict:
        """点击窗口中的控件"""
        if not PYWINAUTO_AVAILABLE:
            return {"error": "pywinauto 未安装"}
        
        try:
            app = Application(backend="uia").connect(title_re=f".*{window_title}.*")
            window = app.top_window()
            
            # 查找控件
            kwargs = {"title_re": f".*{control_name}.*"}
            if control_type:
                kwargs["control_type"] = control_type
            
            control = window.child_window(**kwargs)
            control.click_input()
            
            return {
                "success": True,
                "message": f"已点击控件: {control_name}"
            }
        except ElementNotFoundError:
            return {"error": f"找不到控件: {control_name}"}
        except Exception as e:
            return {"error": str(e)}
    
    def desktop_window_type(self, window_title: str, text: str, 
                            control_name: Optional[str] = None) -> Dict:
        """在窗口输入框中输入文字"""
        if not PYWINAUTO_AVAILABLE:
            return {"error": "pywinauto 未安装"}
        
        try:
            app = Application(backend="uia").connect(title_re=f".*{window_title}.*")
            window = app.top_window()
            
            if control_name:
                # 点击特定输入框
                control = window.child_window(title_re=f".*{control_name}.*")
                control.click_input()
            
            # 输入文字
            window.type_keys(text, with_spaces=True)
            
            return {
                "success": True,
                "message": f"已在窗口 '{window_title}' 输入文字"
            }
        except Exception as e:
            return {"error": str(e)}
    
    # ============================================================
    # MCP 协议处理
    # ============================================================
    
    def handle_request(self, request: Dict) -> Dict:
        """处理 MCP 请求"""
        method = request.get("method", "")
        request_id = request.get("id")
        params = request.get("params", {})
        
        if method == "initialize":
            return self._response(request_id, {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "desktop-mcp",
                    "version": "1.0.0"
                }
            })
        
        elif method == "tools/list":
            return self._response(request_id, {"tools": self.tools})
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            # 调用对应的工具方法
            tool_method = getattr(self, tool_name, None)
            if tool_method:
                result = tool_method(**arguments)
                return self._response(request_id, {
                    "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]
                })
            else:
                return self._error(request_id, -32601, f"Unknown tool: {tool_name}")
        
        elif method == "notifications/initialized":
            # 初始化完成通知，不需要响应
            return None
        
        else:
            return self._error(request_id, -32601, f"Unknown method: {method}")
    
    def _response(self, request_id: Any, result: Any) -> Dict:
        """构建成功响应"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
    
    def _error(self, request_id: Any, code: int, message: str) -> Dict:
        """构建错误响应"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": code, "message": message}
        }
    
    def run(self):
        """运行 MCP 服务器（stdio 模式）"""
        sys.stderr.write("Desktop MCP Server started\n")
        sys.stderr.flush()
        
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                request = json.loads(line)
                response = self.handle_request(request)
                
                if response:
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
                    
            except json.JSONDecodeError as e:
                sys.stderr.write(f"JSON decode error: {e}\n")
            except Exception as e:
                sys.stderr.write(f"Error: {e}\n")
                sys.stderr.flush()


# ============================================================
# 入口
# ============================================================

if __name__ == "__main__":
    server = DesktopMCPServer()
    server.run()
