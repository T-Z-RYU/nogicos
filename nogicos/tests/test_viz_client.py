#!/usr/bin/env python3
"""
通过 WebSocket ClientSend可视化Event到Before端
Connect到已Running的 hive_server.py
"""

import asyncio
import json
import sys

try:
    import websockets
except ImportError:
    print("请安装 websockets: pip install websockets")
    sys.exit(1)


async def send_event(ws, event_type: str, data: dict = None):
    """Send一个Event"""
    msg = {"type": event_type}
    if data:
        msg["data"] = data
    await ws.send(json.dumps(msg))
    print(f"  → Send: {event_type}")


async def run_demo():
    uri = "ws://localhost:8765"
    
    print("=" * 50)
    print("NogicOS 可视化Demo")
    print("=" * 50)
    print(f"\nConnect到 {uri}...")
    
    try:
        async with websockets.connect(uri) as ws:
            print("已Connect!\n")
            
            # WaitinitialStateMessage
            init_msg = await asyncio.wait_for(ws.recv(), timeout=2)
            print(f"收到初始State: {json.loads(init_msg).get('type', 'unknown')}")
            
            print("\n" + "-" * 40)
            print("BeginDemo - 观察Right侧可视化面板")
            print("-" * 40 + "\n")
            
            # Demo 1: TaskBegin
            print("[1] 任务Begin")
            await send_event(ws, "task_start", {"max_steps": 4, "url": "https://nogicos.ai/demo"})
            await asyncio.sleep(1)
            
            # Demo 2: Step 1 - Movecursor
            print("[2] 步骤 1: Move光标")
            await send_event(ws, "step_start", {"step": 0})
            await send_event(ws, "screen_glow", {"intensity": "medium"})
            await send_event(ws, "cursor_move", {"x": 80, "y": 100, "duration": 0.6})
            await asyncio.sleep(0.8)
            await send_event(ws, "highlight", {"rect": {"x": 60, "y": 80, "width": 100, "height": 50}, "label": "Target元素"})
            await asyncio.sleep(1)
            await send_event(ws, "step_complete", {"step": 0, "success": True})
            await asyncio.sleep(0.5)
            
            # Demo 3: Step 2 - Click
            print("[3] 步骤 2: 点击")
            await send_event(ws, "step_start", {"step": 1})
            await send_event(ws, "cursor_move", {"x": 110, "y": 105, "duration": 0.4})
            await asyncio.sleep(0.5)
            await send_event(ws, "cursor_click")
            await asyncio.sleep(0.5)
            await send_event(ws, "highlight_hide")
            await send_event(ws, "step_complete", {"step": 1, "success": True})
            await asyncio.sleep(0.5)
            
            # Demo 4: Step 3 - Input
            print("[4] 步骤 3: Input")
            await send_event(ws, "step_start", {"step": 2})
            await send_event(ws, "cursor_move", {"x": 180, "y": 180, "duration": 0.5})
            await asyncio.sleep(0.6)
            await send_event(ws, "highlight", {"rect": {"x": 130, "y": 160, "width": 150, "height": 40}, "label": "Input框"})
            await asyncio.sleep(0.3)
            await send_event(ws, "cursor_click")
            await asyncio.sleep(0.3)
            await send_event(ws, "cursor_type")
            await asyncio.sleep(2)
            await send_event(ws, "cursor_stop_type")
            await send_event(ws, "highlight_hide")
            await send_event(ws, "step_complete", {"step": 2, "success": True})
            await asyncio.sleep(0.5)
            
            # Demo 5: Step 4 - Confirm
            print("[5] 步骤 4: Confirm")
            await send_event(ws, "step_start", {"step": 3})
            await send_event(ws, "cursor_move", {"x": 160, "y": 280, "duration": 0.5})
            await asyncio.sleep(0.6)
            await send_event(ws, "highlight", {"rect": {"x": 135, "y": 265, "width": 85, "height": 35}, "label": "Confirm按钮"})
            await asyncio.sleep(0.3)
            await send_event(ws, "cursor_click")
            await asyncio.sleep(0.5)
            await send_event(ws, "highlight_hide")
            await send_event(ws, "step_complete", {"step": 3, "success": True})
            await asyncio.sleep(0.5)
            
            # Demo 6: TaskComplete
            print("[6] 任务Complete")
            await send_event(ws, "task_complete")
            await asyncio.sleep(2)
            await send_event(ws, "screen_glow_stop")
            
            print("\n" + "=" * 50)
            print("DemoComplete!")
            print("=" * 50)
            
    except ConnectionRefusedError:
        print("无法Connect到Service器。请确保 hive_server.py 正在Running。")
    except asyncio.TimeoutError:
        print("ConnectTimeout")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(run_demo())

