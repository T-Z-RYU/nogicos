#!/usr/bin/env python3
"""
Test可视化面板的AnimationEffect
Running：python test_visualization.py
确保Before端On发Service器已Running
"""

import asyncio
import random
from engine.server.websocket import get_server, start_server


async def demo_cursor_animation():
    """Demo光标MoveAnimation"""
    server = get_server()
    
    print("[Demo] 光标MoveAnimation")
    
    # move to severalRandomPosition
    positions = [
        (60, 80),    # LeftUpLocale
        (200, 150),  # Middle
        (150, 280),  # BottomButtonLocale
        (280, 100),  # Rightside
    ]
    
    for x, y in positions:
        await server.viz_cursor_move(x, y, duration=0.6)
        await asyncio.sleep(0.8)
    
    print("[Demo] 光标MoveComplete")


async def demo_click_animation():
    """Demo点击Animation"""
    server = get_server()
    
    print("[Demo] 点击Animation")
    
    # MovetoTargetandClick
    await server.viz_cursor_move(160, 320, duration=0.5)
    await asyncio.sleep(0.6)
    await server.viz_cursor_click()
    await asyncio.sleep(0.5)
    
    print("[Demo] 点击Complete")


async def demo_typing_animation():
    """DemoInputAnimation"""
    server = get_server()
    
    print("[Demo] InputAnimation")
    
    # MovetoInputboxandBeginInput
    await server.viz_cursor_move(200, 200, duration=0.5)
    await asyncio.sleep(0.6)
    await server.viz_cursor_click()
    await asyncio.sleep(0.3)
    await server.viz_cursor_type()
    await asyncio.sleep(3)  # simulateInput 3 Second
    await server.viz_cursor_stop_type()
    
    print("[Demo] InputComplete")


async def demo_highlight_animation():
    """Demo元素High亮"""
    server = get_server()
    
    print("[Demo] 元素High亮")
    
    # HighbrightoneasimulateButton
    await server.viz_highlight(138, 310, 85, 40, label="Commit按钮")
    await asyncio.sleep(2)
    await server.viz_highlight_hide()
    
    print("[Demo] High亮Complete")


async def demo_glow_states():
    """Demo屏幕光效State"""
    server = get_server()
    
    print("[Demo] 屏幕光效")
    
    states = ["low", "medium", "high", "success", "error", "off"]
    
    for state in states:
        print(f"  光效: {state}")
        await server.viz_screen_glow(state)
        await asyncio.sleep(1)
    
    await server.viz_screen_glow_stop()
    print("[Demo] 光效Complete")


async def demo_task_flow():
    """Demo完整任务流程"""
    server = get_server()
    
    print("[Demo] 完整任务流程")
    
    # 1. TaskBegin
    print("  [1/6] 任务Begin")
    await server.viz_task_start(max_steps=4, url="https://nogicos.ai/demo")
    await asyncio.sleep(0.5)
    
    # 2. Step 1：Movecursor
    print("  [2/6] 步骤 1 Begin")
    await server.viz_step_start(0)
    await server.viz_screen_glow("medium")
    await server.viz_cursor_move(80, 120, duration=0.5)
    await asyncio.sleep(0.7)
    await server.viz_highlight(60, 100, 100, 50, label="Target元素")
    await asyncio.sleep(0.5)
    await server.viz_step_complete(0, success=True)
    
    # 3. Step 2：Click
    print("  [3/6] 步骤 2 Begin")
    await server.viz_step_start(1)
    await server.viz_cursor_move(110, 125, duration=0.4)
    await asyncio.sleep(0.5)
    await server.viz_cursor_click()
    await asyncio.sleep(0.5)
    await server.viz_highlight_hide()
    await server.viz_step_complete(1, success=True)
    
    # 4. Step 3：Input
    print("  [4/6] 步骤 3 Begin")
    await server.viz_step_start(2)
    await server.viz_cursor_move(180, 220, duration=0.5)
    await asyncio.sleep(0.6)
    await server.viz_highlight(130, 200, 150, 40, label="Input框")
    await asyncio.sleep(0.3)
    await server.viz_cursor_click()
    await asyncio.sleep(0.3)
    await server.viz_cursor_type()
    await asyncio.sleep(2)
    await server.viz_cursor_stop_type()
    await server.viz_highlight_hide()
    await server.viz_step_complete(2, success=True)
    
    # 5. Step 4：Complete
    print("  [5/6] 步骤 4 Begin")
    await server.viz_step_start(3)
    await server.viz_cursor_move(160, 320, duration=0.5)
    await asyncio.sleep(0.6)
    await server.viz_highlight(135, 305, 85, 35, label="Confirm")
    await asyncio.sleep(0.3)
    await server.viz_cursor_click()
    await asyncio.sleep(0.5)
    await server.viz_highlight_hide()
    await server.viz_step_complete(3, success=True)
    
    # 6. TaskComplete
    print("  [6/6] 任务Complete")
    await server.viz_task_complete()
    await asyncio.sleep(2)
    await server.viz_screen_glow_stop()
    
    print("[Demo] 任务流程Complete")


async def main():
    """主Function：StartService器并RunningDemo"""
    print("=" * 50)
    print("NogicOS 可视化面板Test")
    print("=" * 50)
    print()
    print("确保Before端On发Service器已Running:")
    print("  cd nogicos/nogicos-ui && npm run dev")
    print()
    print("然AftervisitBefore端页面观看AnimationEffect")
    print()
    
    # Start WebSocket Serviceer
    server = await start_server()
    print(f"WebSocket server running at ws://{server.host}:{server.port}")
    
    # WaitClientConnect
    print("\nWaitBefore端Connect...")
    
    for i in range(30):  # mostWait 30 Second
        await asyncio.sleep(1)
        if server.client_count > 0:
            print(f"已Connect {server.client_count} 个Client")
            break
    else:
        print("没有ClientConnect，Exit")
        await server.stop()
        return
    
    # RunningDemo
    print("\n" + "=" * 50)
    print("BeginDemo")
    print("=" * 50)
    
    demos = [
        ("光标Move", demo_cursor_animation),
        ("点击Effect", demo_click_animation),
        ("InputEffect", demo_typing_animation),
        ("元素High亮", demo_highlight_animation),
        ("屏幕光效", demo_glow_states),
        ("完整流程", demo_task_flow),
    ]
    
    for i, (name, demo_fn) in enumerate(demos, 1):
        print(f"\n--- Demo {i}/{len(demos)}: {name} ---")
        await demo_fn()
        await asyncio.sleep(1)
    
    print("\n" + "=" * 50)
    print("所有DemoComplete!")
    print("=" * 50)
    
    # keepServiceerRunning
    print("\n按 Ctrl+C Exit...")
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n正在Close...")
    finally:
        await server.stop()
        print("Complete")


if __name__ == "__main__":
    asyncio.run(main())

