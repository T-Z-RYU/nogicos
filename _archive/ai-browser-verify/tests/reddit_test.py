"""
Reddit 场景测试
"""
import asyncio
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import config, TEST_SCENARIOS
from run_verify import TechVerifier


async def test_reddit():
    """测试 Reddit 场景"""
    verifier = TechVerifier()
    
    print("=" * 60)
    print("Reddit 场景测试")
    print("=" * 60)
    
    scenario = "reddit"
    tasks = TEST_SCENARIOS[scenario]["tasks"]
    
    for task in tasks:
        print(f"\n任务: {task}")
        print("-" * 40)
        
        # 无知识库
        result = await verifier.test_basic_execution(
            scenario=scenario,
            task=task,
            model=config.fast_model
        )
        verifier.add_result(result)
        
        # 有知识库
        kb_path = verifier.knowledge_base_dir / f"{scenario}_kb"
        result = await verifier.test_with_knowledge_base(
            scenario=scenario,
            task=task,
            model=config.fast_model,
            knowledge_base_path=str(kb_path)
        )
        verifier.add_result(result)
    
    # 生成报告
    verifier.generate_report()


if __name__ == "__main__":
    asyncio.run(test_reddit())
