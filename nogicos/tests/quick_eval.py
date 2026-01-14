"""Quick evaluation script for NogicOS optimizations"""
import asyncio
import httpx
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

async def quick_eval():
    url = 'http://localhost:8080/api/chat'
    
    test_cases = [
        ('你好', 'TTFT'),
        ('帮我整理一Down', 'Follow-up'),
        ('Write一个快排算法', 'Code'),
    ]
    
    results = []
    
    for prompt, test_type in test_cases:
        print(f'Testing: {test_type}')
        
        start = time.time()
        ttft = None
        response_text = ''
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    'POST', url,
                    json={'messages': [{'role': 'user', 'content': prompt}], 'session_id': f'eval_{int(time.time())}'},
                    headers={'Accept': 'text/event-stream'}
                ) as response:
                    async for line in response.aiter_lines():
                        if line.startswith('data: '):
                            try:
                                data = json.loads(line[6:])
                                if data.get('type') == 'text-delta':
                                    if ttft is None:
                                        ttft = time.time() - start
                                    response_text += data.get('delta', '')
                            except:
                                pass
        except Exception as e:
            print(f'  Error: {e}')
            ttft = 999
        
        total = time.time() - start
        has_questions = any(x in response_text for x in ['?', '？', '请告诉', '什么', '哪', '希望'])
        has_code = '```' in response_text or 'def ' in response_text or 'function' in response_text
        
        result = {'type': test_type, 'ttft': ttft, 'total': total, 'has_questions': has_questions, 'has_code': has_code, 'response': response_text[:200]}
        results.append(result)
        
        ttft_str = f"{ttft:.2f}s" if ttft is not None else "N/A"
        total_str = f"{total:.2f}s" if total is not None else "N/A"
        print(f'  TTFT: {ttft_str} | Total: {total_str} | Len: {len(response_text)}')
        print(f'  Preview: {response_text[:100]}...')
    
    print()
    print('=' * 50)
    print('EVALUATION RESULTS')
    print('=' * 50)
    
    avg_ttft = sum(r['ttft'] or 0 for r in results) / len(results)
    ttft_pass = 'PASS' if avg_ttft < 1 else 'FAIL'
    print(f'[{ttft_pass}] Avg TTFT: {avg_ttft:.2f}s (target < 1s)')
    
    follow_up_pass = 'PASS' if results[1]['has_questions'] else 'FAIL'
    print(f'[{follow_up_pass}] Follow-up questions: {results[1]["has_questions"]}')
    
    code_pass = 'PASS' if results[2]['has_code'] else 'FAIL'
    print(f'[{code_pass}] Code generation: {results[2]["has_code"]}')
    
    # Overall
    passed = sum(1 for x in [ttft_pass, follow_up_pass, code_pass] if x == 'PASS')
    print()
    print(f'Overall: {passed}/3 tests passed')

if __name__ == '__main__':
    asyncio.run(quick_eval())

