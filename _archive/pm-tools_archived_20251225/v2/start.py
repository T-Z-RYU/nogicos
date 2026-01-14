#!/usr/bin/env python3
"""
PM Tool v2 - 一键启动脚本
同时启动 FastAPI 后端和 Next.js 前端
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

# 项目路径
PROJECT_ROOT = Path(__file__).parent
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"

# 进程列表
processes = []


def start_backend():
    """启动 FastAPI 后端"""
    print("🚀 启动 FastAPI 后端 (http://localhost:8000)...")
    
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        cwd=BACKEND_DIR,
        env=env,
        # Windows 下不能使用 preexec_fn
    )
    processes.append(("Backend", process))
    return process


def start_frontend():
    """启动 Next.js 前端"""
    print("🚀 启动 Next.js 前端 (http://localhost:3001)...")
    
    # Windows 使用 npm.cmd
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    
    process = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=FRONTEND_DIR,
        shell=(sys.platform == "win32"),
    )
    processes.append(("Frontend", process))
    return process


def cleanup(signum=None, frame=None):
    """清理所有进程"""
    print("\n🛑 正在关闭服务...")
    
    for name, process in processes:
        if process.poll() is None:  # 进程还在运行
            print(f"   关闭 {name}...")
            if sys.platform == "win32":
                process.terminate()
            else:
                process.send_signal(signal.SIGTERM)
    
    # 等待进程结束
    for name, process in processes:
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
    
    print("✅ 所有服务已关闭")
    sys.exit(0)


def main():
    """主函数"""
    print("=" * 50)
    print("PM Tool v2 - 现代化竞品截图分析工具")
    print("=" * 50)
    print()
    
    # 检查目录
    if not BACKEND_DIR.exists():
        print(f"❌ 后端目录不存在: {BACKEND_DIR}")
        sys.exit(1)
    
    if not FRONTEND_DIR.exists():
        print(f"❌ 前端目录不存在: {FRONTEND_DIR}")
        sys.exit(1)
    
    # 注册信号处理
    signal.signal(signal.SIGINT, cleanup)
    if sys.platform != "win32":
        signal.signal(signal.SIGTERM, cleanup)
    
    try:
        # 启动后端
        backend = start_backend()
        time.sleep(2)  # 等待后端启动
        
        # 启动前端
        frontend = start_frontend()
        
        print()
        print("=" * 50)
        print("✅ 服务已启动!")
        print()
        print("   📡 后端 API:  http://localhost:8000")
        print("   📡 API 文档:  http://localhost:8000/docs")
        print("   🌐 前端页面:  http://localhost:3001")
        print()
        print("   按 Ctrl+C 停止所有服务")
        print("=" * 50)
        
        # 等待进程
        while True:
            # 检查进程状态
            for name, process in processes:
                if process.poll() is not None:
                    print(f"⚠️  {name} 意外退出 (code: {process.returncode})")
            time.sleep(1)
            
    except KeyboardInterrupt:
        cleanup()


if __name__ == "__main__":
    main()


