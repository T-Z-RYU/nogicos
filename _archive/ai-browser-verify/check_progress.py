"""
检查 benchmark_generalization.py 的运行进度
"""
import os
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

LOG_FILE = os.path.join(os.path.dirname(__file__), "benchmark_log.txt")
ERROR_FILE = os.path.join(os.path.dirname(__file__), "benchmark_error.txt")

def check_progress():
    print("=" * 60)
    print("  泛化测试进度检查")
    print("=" * 60)
    
    # 检查日志文件
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        
        # 统计进度
        websites_started = content.count("开始测试:")
        websites_done = content.count("结果摘要 ---")
        
        print(f"\n进度: {websites_done}/6 个网站完成")
        
        # 检查是否有错误
        if "错误" in content or "Error" in content:
            print("状态: 运行中（有一些警告/错误）")
        elif "测试完成" in content:
            print("状态: 已完成！")
        else:
            print("状态: 运行中...")
        
        # 显示最后 30 行
        lines = content.strip().split('\n')
        print(f"\n最近日志（最后 30 行）:")
        print("-" * 60)
        for line in lines[-30:]:
            print(line)
    else:
        print("日志文件不存在，测试可能还没开始或已被清理")
    
    # 检查错误日志
    if os.path.exists(ERROR_FILE):
        with open(ERROR_FILE, "r", encoding="utf-8", errors="replace") as f:
            error_content = f.read().strip()
        if error_content:
            print(f"\n错误日志:")
            print("-" * 60)
            print(error_content[-2000:])  # 最后 2000 字符

if __name__ == "__main__":
    check_progress()
