# -*- coding: utf-8 -*-
"""
NogicOS Smart Search - Cursor 风格的smartSearch
Implement 2次 LLM 调用的High效Search流程
"""

import os
import json
import time
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

import aiohttp
import anthropic

from engine.observability import get_logger

logger = get_logger("smart_search")


class SmartSearch:
    """
    Cursor 风格的smartSearch
    
    流程:
    0. Intent Detection - JudgeYesNo需要Search (Optional，FastJudge)
    1. Query Optimization - LLM 优化UserInput为Search query
    2. Tavily Search - 调用 API GetResult
    3. Result Synthesis - LLM 整合Result并生成回答
    
    调用精确度：
    - 需要Search: 时效性问题、事实Query、最NewInfo
    - 不需要Search: 代码问题、数学计算、通用知识、闲聊
    """
    
    # forcenotSearch's Pattern (mostHighPrioritylevel)
    FORCE_NO_SEARCH = [
        "这段代码", "这个File", "这个Function", "这个Class",
        "帮我Write", "帮我Implement", "帮我修", "帮我debug",
    ]
    
    # NeedSearch's Pattern (HighPrioritylevel)
    SEARCH_PATTERNS = [
        # timeeffectproperty
        "最New", "2025", "2024", "今Day", "最近", "现在",
        # factual query (generalconcept)
        "Yes什么意思", "有哪些", "区别", "对比", "how用",
        # explicitSearch
        "Search", "查一Down", "找一Down", "看看",
        # product/company/concept
        "YC", "Cursor", "OpenAI", "Anthropic", "Google",
        "量Child", "AI", "人工smart", "机器学习", "区块链",
    ]
    
    # Not NeedSearch's Pattern (LowPrioritylevel)
    NO_SEARCH_PATTERNS = [
        # coderelatedOff
        "Write代码", "Write一个", "Implement一个", "Function", "class ", "def ", "import ",
        "debug", "Repair", "报错", "error", "bug", "代码",
        # math calculation
        "计算一Down", "等于多少", "加减乘除",
        # idlechat
        "你好", "谢谢", "再见", "帮帮我", "可以吗",
    ]
    
    def __init__(self):
        # Get API keys
        self.tavily_api_key = os.environ.get("TAVILY_API_KEY")
        self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
        
        if not self.tavily_api_key:
            try:
                from api_keys import TAVILY_API_KEY
                self.tavily_api_key = TAVILY_API_KEY
            except ImportError:
                pass
        
        if not self.anthropic_api_key:
            try:
                from api_keys import ANTHROPIC_API_KEY
                self.anthropic_api_key = ANTHROPIC_API_KEY
            except ImportError:
                pass
        
        # with Cursor keeponecause，use Opus 4.5 to ensure quality
        self.optimizer_model = "claude-opus-4-5-20250514"  # qualityPriority
        self.client = anthropic.AsyncAnthropic(api_key=self.anthropic_api_key) if self.anthropic_api_key else None
    
    def should_search(self, user_input: str) -> tuple[bool, str]:
        """
        FastJudgeYesNo需要Search（无 LLM 调用，基于Rule）
        
        Priority级：强制不Search > Search模式 > 不Search模式 > DefaultRule
        
        Return: (YesNoSearch, 原因)
        """
        input_lower = user_input.lower()
        
        # 0. mostHighPrioritylevel：forcenotSearch（codeUpDowntextrelatedOff）
        for pattern in self.FORCE_NO_SEARCH:
            if pattern.lower() in input_lower:
                return False, f"代码UpDown文: {pattern}"
        
        # 1. CheckYesNoexplicitNeedSearch
        for pattern in self.SEARCH_PATTERNS:
            if pattern.lower() in input_lower:
                return True, f"MatchSearch模式: {pattern}"
        
        # 2. CheckYesNoexplicitNot NeedSearch
        for pattern in self.NO_SEARCH_PATTERNS:
            if pattern.lower() in input_lower:
                return False, f"Match不Search模式: {pattern}"
        
        # 3. DefaultRule：questionorShorttext -> Search
        if "?" in user_input or "？" in user_input:
            return True, "疑问句，DefaultSearch"
        
        if len(user_input) < 30:
            return True, "短Query，DefaultSearch"
        
        return False, "长文本且无SearchKey词，Default不Search"
        
    async def optimize_query(self, user_input: str) -> str:
        """
        Step 1: 用 LLM 将UserInput优化为Search query
        
        Target:
        - 提取Key词
        - AddTime限定 (如 2025)
        - 扩展同义词
        - 移除Invalid词
        
        耗时Target: < 1Second
        """
        if not self.client:
            logger.warning("No Anthropic client, returning original query")
            return user_input
        
        # extremesimple prompt addspeedGeneration
        prompt = f"""Convert to search query. Output ONLY the query, no explanation.
If time-sensitive, add "2025". Use English keywords if helpful.

Input: {user_input}
Query:"""

        try:
            start = time.time()
            response = await self.client.messages.create(
                model=self.optimizer_model,
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}]
            )
            optimized = response.content[0].text.strip()
            logger.info(f"[QueryOptimize] {time.time()-start:.2f}s: '{user_input}' → '{optimized}'")
            return optimized
        except Exception as e:
            logger.error(f"Query optimization failed: {e}")
            return user_input
    
    async def tavily_search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Step 2: 调用 Tavily API Search
        
        特性:
        - auto_parameters: Auto优化SearchArgument
        - include_answer: Get AI 生成的答案
        
        耗时Target: 0.5-1.5Second
        """
        if not self.tavily_api_key:
            return {"error": "TAVILY_API_KEY not configured"}
        
        try:
            start = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": self.tavily_api_key,
                        "query": query,
                        "max_results": max_results,
                        "include_answer": True,
                        "include_raw_content": False,
                        "search_depth": "basic",  # basic moreFast
                    },
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    logger.info(f"[TavilySearch] {time.time()-start:.2f}s: {len(data.get('results', []))} results")
                    return data
        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            return {"error": str(e)}
    
    async def synthesize_results(
        self, 
        user_input: str, 
        search_results: Dict[str, Any]
    ) -> str:
        """
        Step 3: 用 LLM 整合SearchResult
        
        Target:
        - 简洁回答User问题
        - 提供来Source引用
        - 突出KeyInfo
        
        耗时Target: 1-2Second
        """
        if not self.client:
            # None LLM timeReturnOriginalResult
            answer = search_results.get("answer", "")
            results = search_results.get("results", [])
            
            output = answer + "\n\n**来Source:**\n"
            for i, r in enumerate(results[:3], 1):
                output += f"{i}. [{r.get('title', 'Link')}]({r.get('url', '')})\n"
            return output
        
        # build conciseUpDowntext
        tavily_answer = search_results.get("answer", "")
        results = search_results.get("results", [])
        
        # onlytakeBefore3aResult，eachonlytake100Character
        context_parts = [f"AI摘要: {tavily_answer}"]
        for i, r in enumerate(results[:3], 1):
            context_parts.append(f"{i}. {r.get('title', '')} - {r.get('content', '')[:100]}")
        context = "\n".join(context_parts)
        
        # extremesimple prompt - forceMediumtext
        prompt = f"""Root据SearchResult用Medium文简洁回答。LastTail附来Source链接。

问题: {user_input}
{context}
回答:"""

        try:
            start = time.time()
            response = await self.client.messages.create(
                model=self.optimizer_model,
                max_tokens=300,  # LimitOutputLengthaddspeed
                messages=[{"role": "user", "content": prompt}]
            )
            synthesized = response.content[0].text.strip()
            logger.info(f"[Synthesize] {time.time()-start:.2f}s")
            return synthesized
        except Exception as e:
            logger.error(f"Result synthesis failed: {e}")
            # Fallback to raw answer
            return search_results.get("answer", f"SearchComplete，但整合Failed: {e}")
    
    async def search(
        self, 
        user_input: str, 
        max_results: int = 5,
        force_search: bool = False  # forceSearch，SkipJudge
    ) -> Dict[str, Any]:
        """
        完整的smartSearch流程
        
        Return:
        {
            "success": bool,
            "should_search": bool,  # YesNoExecuteSearch
            "skip_reason": str,     # IfSkip，originalbecauseYeswhat
            "answer": str,          # integrated answer
            "sources": list,        # fromSourceList
            "timing": {...}
        }
        """
        total_start = time.time()
        timing = {}
        
        # Step 0: JudgeYesNoNeedSearch
        if not force_search:
            should, reason = self.should_search(user_input)
            if not should:
                timing["total_ms"] = (time.time() - total_start) * 1000
                return {
                    "success": True,
                    "should_search": False,
                    "skip_reason": reason,
                    "answer": None,
                    "sources": [],
                    "timing": timing
                }
        
        try:
            # Step 1: Optimization Query
            step1_start = time.time()
            optimized_query = await self.optimize_query(user_input)
            timing["optimize_query_ms"] = (time.time() - step1_start) * 1000
            
            # Step 2: Tavily Search
            step2_start = time.time()
            search_results = await self.tavily_search(optimized_query, max_results)
            timing["search_ms"] = (time.time() - step2_start) * 1000
            
            if "error" in search_results:
                return {
                    "success": False,
                    "error": search_results["error"],
                    "timing": timing
                }
            
            # Step 3: integrateResult
            step3_start = time.time()
            final_answer = await self.synthesize_results(user_input, search_results)
            timing["synthesize_ms"] = (time.time() - step3_start) * 1000
            
            timing["total_ms"] = (time.time() - total_start) * 1000
            
            # ExtractionfromSource
            sources = []
            for r in search_results.get("results", [])[:5]:
                sources.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": r.get("content", "")[:150]
                })
            
            return {
                "success": True,
                "should_search": True,
                "query": user_input,
                "optimized_query": optimized_query,
                "answer": final_answer,
                "tavily_answer": search_results.get("answer", ""),
                "sources": sources,
                "timing": timing
            }
            
        except Exception as e:
            timing["total_ms"] = (time.time() - total_start) * 1000
            logger.error(f"Smart search failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timing": timing
            }


# Singleton instance
_smart_search: Optional[SmartSearch] = None

def get_smart_search() -> SmartSearch:
    global _smart_search
    if _smart_search is None:
        _smart_search = SmartSearch()
    return _smart_search


async def smart_search(query: str, max_results: int = 5, force_search: bool = False) -> Dict[str, Any]:
    """Convenience function for smart search"""
    return await get_smart_search().search(query, max_results, force_search)


# CLI for testing
if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from api_keys import setup_env
    setup_env()
    
    async def test():
        searcher = SmartSearch()
        
        test_queries = [
            "AI 最New进展",
            "Cursor IDE how用",
            "今DayDay气",
        ]
        
        for q in test_queries:
            print(f"\n{'='*60}")
            print(f"Query: {q}")
            print('='*60)
            
            result = await searcher.search(q)
            
            if result["success"]:
                print(f"\n📝 优化After Query: {result['optimized_query']}")
                print(f"\n📊 回答:\n{result['answer']}")
                print(f"\n⏱️ 耗时:")
                for k, v in result["timing"].items():
                    print(f"   {k}: {v:.0f}ms")
            else:
                print(f"❌ Failed: {result.get('error')}")
    
    asyncio.run(test())

