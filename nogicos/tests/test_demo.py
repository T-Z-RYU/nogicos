#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NogicOS Demo Test Script

Quick test to verify the YC Demo functionality works correctly.
Run this before recording the demo video.

Usage:
    python test_demo.py
"""

import asyncio
import json
import httpx
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))


async def test_health():
    """Test server health endpoint"""
    print("\n🏥 Testing health endpoint...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8080/health")
            data = response.json()
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Engine: {'✅' if data.get('engine') else '❌'}")
            return data.get('status') == 'healthy'
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False


async def test_yc_demo():
    """Test YC Demo task execution"""
    print("\n🎯 Testing YC Demo task...")
    
    task_data = {
        "task": "Analyze YC AI companies and find application best practices",
        "url": "https://www.ycombinator.com/companies",
        "mode": "agent",
        "use_cdp": False  # Use mock for testing
    }
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            print(f"   Sending request: {task_data['task'][:50]}...")
            response = await client.post(
                "http://localhost:8080/execute",
                json=task_data
            )
            data = response.json()
            
            print(f"\n   📊 Results:")
            print(f"   - Success: {'✅' if data.get('success') else '❌'}")
            print(f"   - Path: {data.get('path', 'unknown')}")
            print(f"   - Time: {data.get('time_seconds', 0):.2f}s")
            print(f"   - Steps: {data.get('steps', 0)}")
            print(f"   - Confidence: {data.get('confidence', 0):.0%}")
            
            if data.get('result'):
                print(f"\n   💡 Result: {data['result'][:200]}...")
            
            if data.get('error'):
                print(f"\n   ❌ Error: {data['error']}")
            
            return data.get('success', False)
            
        except httpx.TimeoutException:
            print("   ⏱️ Request timed out (this may be expected for long tasks)")
            return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False


async def test_tool_system():
    """Test Tool system (file operations)"""
    print("\n🔧 Testing Tool system...")
    
    # Import and test tool dispatcher
    try:
        from engine.tools import get_dispatcher
        
        dispatcher = get_dispatcher()
        print(f"   Dispatcher initialized: ✅")
        
        # Note: Full tool testing requires Electron connection
        print(f"   (Full tool testing requires running Electron client)")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


async def check_files_created():
    """Check if demo output files were created"""
    print("\n📁 Checking output files...")
    
    output_dir = os.path.expanduser("~/yc_research")
    expected_files = ["raw_data.json", "analysis.md", "recommendations.md"]
    
    found_count = 0
    for filename in expected_files:
        filepath = os.path.join(output_dir, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"   ✅ {filename} ({size} bytes)")
            found_count += 1
        else:
            print(f"   ⏳ {filename} (not created yet)")
    
    return found_count == len(expected_files)


async def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 NogicOS Demo Test Suite")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Health check
    results["health"] = await test_health()
    
    if not results["health"]:
        print("\n⚠️  Server not running. Start with: python hive_server.py")
        print("=" * 60)
        return
    
    # Test 2: Tool system
    results["tools"] = await test_tool_system()
    
    # Test 3: YC Demo
    results["yc_demo"] = await test_yc_demo()
    
    # Test 4: Check output files
    results["files"] = await check_files_created()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests passed! Ready for demo recording.")
    else:
        print("⚠️  Some tests failed. Check the issues above.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())



