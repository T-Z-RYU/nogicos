# -*- coding: utf-8 -*-
"""
NogicOS Health Checks - V2
"""

import asyncio
import os
import sys
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class HealthResult:
    """Health check result"""
    module: str
    status: str  # healthy, unhealthy, degraded
    latency_ms: float = 0.0
    error: Optional[str] = None


class HealthChecker:
    """System health checker"""
    
    async def check_all(self) -> dict:
        """Check all modules"""
        results = {
            "agent": await self.check_agent(),
            "tools": await self.check_tools(),
            "websocket": await self.check_websocket(),
        }
        
        statuses = [r.status for r in results.values()]
        if all(s == "healthy" for s in statuses):
            overall = "healthy"
        elif any(s == "unhealthy" for s in statuses):
            overall = "unhealthy"
        else:
            overall = "degraded"
        
        return {
            "overall": overall,
            "modules": {k: {"status": v.status, "error": v.error} for k, v in results.items()},
        }
    
    async def check_agent(self) -> HealthResult:
        """Check agent module"""
        start = time.time()
        try:
            from engine.agent.react_agent import ReActAgent
            
            # Check API key (try api_keys.py first)
            api_key = None
            try:
                import api_keys
                api_key = api_keys.ANTHROPIC_API_KEY
            except (ImportError, AttributeError):
                api_key = os.environ.get("ANTHROPIC_API_KEY")
            
            if not api_key:
                return HealthResult("agent", "degraded", error="No API key")
            
            return HealthResult("agent", "healthy", (time.time() - start) * 1000)
        except Exception as e:
            return HealthResult("agent", "unhealthy", error=str(e))
    
    async def check_tools(self) -> HealthResult:
        """Check tools module"""
        start = time.time()
        try:
            from engine.tools import create_full_registry
            registry = create_full_registry()
            tool_count = len(registry.to_anthropic_format())
            
            if tool_count == 0:
                return HealthResult("tools", "degraded", error="No tools registered")
            
            return HealthResult("tools", "healthy", (time.time() - start) * 1000)
        except Exception as e:
            return HealthResult("tools", "unhealthy", error=str(e))
    
    async def check_websocket(self) -> HealthResult:
        """Check websocket module"""
        start = time.time()
        try:
            from engine.server.websocket import StatusServer
            return HealthResult("websocket", "healthy", (time.time() - start) * 1000)
        except Exception as e:
            return HealthResult("websocket", "unhealthy", error=str(e))


async def check_all() -> dict:
    """Convenience function"""
    return await HealthChecker().check_all()


def main():
    """CLI entry point"""
    # Add to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    # Load API keys
    try:
        from api_keys import setup_env
        setup_env()
    except ImportError:
        pass
    
    print("=" * 50)
    print("NogicOS Health Check - V2")
    print("=" * 50)
    
    results = asyncio.run(check_all())
    
    print(f"\nOverall: {results['overall'].upper()}")
    print("-" * 50)
    
    for module, data in results["modules"].items():
        icon = "OK" if data["status"] == "healthy" else "WARN" if data["status"] == "degraded" else "FAIL"
        print(f"[{icon}] {module}: {data['status']}")
        if data.get("error"):
            print(f"      Error: {data['error']}")


if __name__ == "__main__":
    main()
