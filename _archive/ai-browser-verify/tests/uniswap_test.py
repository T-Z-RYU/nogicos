"""
Uniswap (Web3) 场景测试
"""
import asyncio
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import config, TEST_SCENARIOS
from run_verify import TechVerifier


async def test_uniswap():
    """测试 Uniswap 场景"""
    verifier = TechVerifier()
    
    print("=" * 60)
    print("Uniswap (Web3) 场景测试")
    print("=" * 60)
    
    scenario = "uniswap"
    tasks = TEST_SCENARIOS[scenario]["tasks"]
    
    for task in tasks:
        print(f"\n任务: {task}")
        print("-" * 40)
        
        # 无知识库 - 使用主模型
        result = await verifier.test_basic_execution(
            scenario=scenario,
            task=task,
            model=config.main_model
        )
        verifier.add_result(result)
        
        # 有知识库
        kb_path = verifier.knowledge_base_dir / f"{scenario}_kb"
        result = await verifier.test_with_knowledge_base(
            scenario=scenario,
            task=task,
            model=config.main_model,
            knowledge_base_path=str(kb_path)
        )
        verifier.add_result(result)
    
    # 生成报告
    verifier.generate_report()


async def test_uniswap_learning():
    """测试 Uniswap 学习能力"""
    verifier = TechVerifier()
    
    print("=" * 60)
    print("Uniswap 学习测试")
    print("=" * 60)
    
    # 学习 Uniswap 操作
    kb_path = await verifier.explore_and_learn(
        scenario="uniswap",
        model=config.main_model,
        iterations=30
    )
    
    if kb_path:
        print(f"\n知识库路径: {kb_path}")
        print("学习完成！可以使用 test_uniswap() 测试效果")
    else:
        print("\n学习失败，请检查环境配置")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--learn":
        asyncio.run(test_uniswap_learning())
    else:
        asyncio.run(test_uniswap())
