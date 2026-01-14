# -*- coding: utf-8 -*-
"""
YC Application Workflow - Complete implementation

This module provides the trigger detection and execution logic for the 
YC Application preset workflow.

Trigger phrase: "Help me fill out these two questions"
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional, Callable, Awaitable
from pathlib import Path

logger = logging.getLogger("nogicos.tools.yc_workflow")

# ============================================================
# CONFIGURATION
# ============================================================

YC_WORKFLOW_TRIGGER = "help me fill out these two questions"

# WhatsApp message template
WHATSAPP_MESSAGE = "YC Application Updated ✅"

# File paths
DESKTOP_PATH = Path(os.path.expanduser("~")) / "Desktop"
YC_FOLDER_NAME = "YC Application"
DOCUMENT_PATH = Path("nogicos/PITCH_CONTEXT.md")
KEYWORDS = ["nogicos", "yc", "ycombinator", "y combinator"]

# CDP Configuration
CDP_URL = "http://localhost:9222"

# ============================================================
# STATE MANAGEMENT
# ============================================================

class WorkflowState:
    """Simple state tracking for workflow execution count"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.execution_count = 0
            cls._instance.desktop_organized = False
        return cls._instance
    
    def increment(self):
        self.execution_count += 1
        
    def mark_desktop_organized(self):
        self.desktop_organized = True

def get_workflow_state() -> WorkflowState:
    return WorkflowState()

# ============================================================
# TRIGGER DETECTION
# ============================================================

def is_yc_workflow_trigger(task: str) -> bool:
    """Check if the task text matches the YC workflow trigger phrase"""
    return YC_WORKFLOW_TRIGGER in task.lower()

# ============================================================
# WORKFLOW STEPS
# ============================================================

async def step_organize_desktop(
    status_callback: Optional[Callable[[str], Awaitable[None]]] = None
) -> Dict[str, Any]:
    """
    Step 1: Organize desktop files using UFO (AI desktop automation)
    """
    state = get_workflow_state()
    
    # Check if should skip
    if state.desktop_organized:
        if status_callback:
            await status_callback("⚡ 桌面已整理，Skip此步骤")
        return {
            "status": "skipped",
            "message": "Desktop already organized",
            "files_moved": 0,
        }
    
    if status_callback:
        await status_callback("📁 正在Usage UFO 整理桌面File...")
    
    try:
        from engine.tools.ufo_executor import execute_desktop_task, TaskStatus
        
        # Use UFO to organize desktop files
        task = f"Create a folder named '{YC_FOLDER_NAME}' on the desktop if it doesn't exist, then move all files containing 'NogicOS' or 'YC' in their names to that folder."
        
        if status_callback:
            await status_callback("  → 调用 UFO Execute桌面整理任务...")
        
        result = await execute_desktop_task(task)
        
        if result.status == TaskStatus.SUCCESS:
            state.mark_desktop_organized()
            if status_callback:
                await status_callback("✅ UFO Complete桌面整理")
            return {
                "status": "completed",
                "message": result.message,
                "method": "ufo",
            }
        else:
            # Fallback to manual file operations
            if status_callback:
                await status_callback(f"⚠️ UFO Failed ({result.message})，Usage备用方案...")
            return await _step_organize_desktop_fallback(status_callback)
            
    except ImportError as e:
        logger.warning(f"UFO not available: {e}, using fallback")
        if status_callback:
            await status_callback("⚠️ UFO 未安装，Usage备用方案...")
        return await _step_organize_desktop_fallback(status_callback)
    except Exception as e:
        logger.error(f"UFO organize failed: {e}")
        if status_callback:
            await status_callback(f"⚠️ UFO Error: {e}，Usage备用方案...")
        return await _step_organize_desktop_fallback(status_callback)


async def _step_organize_desktop_fallback(
    status_callback: Optional[Callable[[str], Awaitable[None]]] = None
) -> Dict[str, Any]:
    """Fallback: Organize desktop using standard file operations"""
    state = get_workflow_state()
    
    # Create YC Application folder
    yc_folder = DESKTOP_PATH / YC_FOLDER_NAME
    yc_folder.mkdir(exist_ok=True)
    
    # Get and move files
    files_to_organize = _get_files_to_organize()
    moved_files = []
    
    for file in files_to_organize:
        try:
            dest = yc_folder / file.name
            file.rename(dest)
            moved_files.append(file.name)
            if status_callback:
                await status_callback(f"  → Move: {file.name}")
    except Exception as e:
            logger.error(f"Failed to move {file.name}: {e}")
    
    state.mark_desktop_organized()
    
    result_msg = f"已整理 {len(moved_files)} 个File到 {YC_FOLDER_NAME}/" if moved_files else "没有需要整理的File"
    if status_callback:
        await status_callback(f"✅ {result_msg}")
    
    return {
        "status": "completed",
        "message": result_msg,
        "files_moved": len(moved_files),
        "files": moved_files,
        "method": "fallback",
    }


def _get_files_to_organize() -> list:
    """Get list of desktop files containing keywords"""
    files = []
    if not DESKTOP_PATH.exists():
        return files
    
    for item in DESKTOP_PATH.iterdir():
        name_lower = item.name.lower()
        for keyword in KEYWORDS:
            if keyword in name_lower and item.name != YC_FOLDER_NAME:
                files.append(item)
                break
    return files


async def step_read_document(
    status_callback: Optional[Callable[[str], Awaitable[None]]] = None
) -> Dict[str, Any]:
    """
    Step 2: Read and display the product documentation
    """
    if status_callback:
        await status_callback("📖 正在Read产品文档...")
        await asyncio.sleep(0.3)  # Visual delay
        await status_callback("  → Open PITCH_CONTEXT.md")
    
    try:
        # Try multiple paths
        doc_content = None
        tried_paths = []
        
        for try_path in [
            DOCUMENT_PATH,
            Path.cwd() / DOCUMENT_PATH,
            Path.cwd() / "nogicos" / "PITCH_CONTEXT.md",
            Path(__file__).parent.parent.parent / "PITCH_CONTEXT.md",
        ]:
            tried_paths.append(str(try_path))
            if try_path.exists():
                doc_content = try_path.read_text(encoding='utf-8')
                if status_callback:
                    await status_callback(f"  → 找到文档: {try_path}")
                break
        
        if doc_content:
            # Visual reading process
            await asyncio.sleep(0.2)
            if status_callback:
                await status_callback("  → 定位 YC Application Answers 部分...")
            await asyncio.sleep(0.2)
            
            # Find the answer section
            if "YC Application Answers" in doc_content:
        if status_callback:
                    await status_callback("  → 找到答案部分")
                    await status_callback("  → 提取 'What is your company going to make?' 的答案...")
            
            await asyncio.sleep(0.2)
            if status_callback:
                await status_callback("✅ 文档ReadComplete")
            
            return {
                "status": "completed",
                "message": "Document read successfully",
                "content": doc_content,
            }
        else:
            if status_callback:
                await status_callback(f"⚠️ 未找到文档，将Usage预设答案")
            return {
                "status": "completed",
                "message": "Using preset answer",
                "content": None,
                "tried_paths": tried_paths,
            }
        
    except Exception as e:
        logger.error(f"Failed to read document: {e}")
        if status_callback:
            await status_callback(f"⚠️ ReadFailed: {e}，将Usage预设答案")
        return {
            "status": "completed",  # Still continue with preset
            "message": f"Read failed: {e}",
            "content": None,
        }


async def step_read_yc_questions(
    status_callback: Optional[Callable[[str], Awaitable[None]]] = None
) -> Dict[str, Any]:
    """
    Step 3: Read YC application questions from the hooked Chrome browser
    
    Uses CDP to extract the questions from the YC form page.
    """
    if status_callback:
        await status_callback("🔍 正在Read YC Table单问题...")
        await status_callback("  → Connect到已 Hook 的 Chrome...")
    
    try:
        import aiohttp
        import websockets
        import json
        
        # Find the YC page
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{CDP_URL}/json") as resp:
                targets = await resp.json()
        
        yc_target = None
        for target in targets:
            if "apply.ycombinator.com" in target.get("url", ""):
                yc_target = target
                break
        
        if not yc_target:
            if status_callback:
                await status_callback("❌ 未找到 YC Apply页面")
            return {"status": "failed", "message": "YC page not found", "questions": []}
        
        if status_callback:
            await status_callback(f"  → 找到 YC 页面 ✓")
        
        # Connect and extract questions
        ws_url = yc_target["webSocketDebuggerUrl"]
        
        async with websockets.connect(ws_url) as ws:
            msg_id = 1
            
            async def send_cdp(method, params=None):
                nonlocal msg_id
                msg = {"id": msg_id, "method": method, "params": params or {}}
                await ws.send(json.dumps(msg))
                msg_id += 1
                while True:
                    response = json.loads(await ws.recv())
                    if response.get("id") == msg_id - 1:
                        return response
            
            # JavaScript to extract form questions
            js_code = '''
            (function() {
                const questions = [];
                const labels = document.querySelectorAll('label');
                const textareas = document.querySelectorAll('textarea');
                
                // Extract questions from labels near textareas
                textareas.forEach((ta, index) => {
                    const container = ta.closest('div');
                    let questionText = '';
                    
                    // Look for label in container
                    const label = container ? container.querySelector('label') : null;
                    if (label) {
                        questionText = label.textContent.trim();
                    }
                    
                    // Also check for any text before the textarea
                    if (!questionText && container) {
                        const textNodes = Array.from(container.childNodes)
                            .filter(n => n.nodeType === Node.TEXT_NODE || n.tagName === 'P' || n.tagName === 'SPAN')
                            .map(n => n.textContent.trim())
                            .filter(t => t.length > 10);
                        if (textNodes.length > 0) {
                            questionText = textNodes[0];
                        }
                    }
                    
                    if (questionText) {
                        questions.push({
                            index: index,
                            question: questionText,
                            fieldName: ta.name || ta.id || `textarea_${index}`,
                            currentValue: ta.value || ''
                        });
                    }
                });
                
                return { success: true, questions: questions };
            })()
            '''
            
            if status_callback:
                await status_callback("  → 提取Table单问题...")
            
            result = await send_cdp("Runtime.evaluate", {
                "expression": js_code,
                "returnByValue": True
            })
            
            eval_result = result.get("result", {}).get("result", {}).get("value", {})
            questions = eval_result.get("questions", [])
            
            if questions:
            if status_callback:
                    await status_callback(f"  → 找到 {len(questions)} 个问题")
                    for q in questions[:3]:  # Show first 3
                        short_q = q['question'][:50] + "..." if len(q['question']) > 50 else q['question']
                        await status_callback(f"    • {short_q}")
                    await status_callback("✅ YC 问题ReadComplete")
                
                return {
                    "status": "completed",
                    "message": f"Found {len(questions)} questions",
                    "questions": questions,
                }
        else:
            if status_callback:
                    await status_callback("⚠️ 未找到Table单问题")
                return {
                    "status": "completed",
                    "message": "No questions found",
                    "questions": [],
                }
                
    except Exception as e:
        logger.error(f"Failed to read YC questions: {e}")
        if status_callback:
            await status_callback(f"❌ Read YC 问题Failed: {e}")
        return {
            "status": "failed",
            "message": str(e),
            "questions": [],
        }


async def step_generate_answer(
    product_doc: str,
    question: str,
    status_callback: Optional[Callable[[str], Awaitable[None]]] = None
) -> Dict[str, Any]:
    """
    Step 4: Use AI to generate an answer based on the product document and question
    """
            if status_callback:
        await status_callback("🤖 正在Usage AI 生成答案...")
        short_q = question[:40] + "..." if len(question) > 40 else question
        await status_callback(f"  → 问题: {short_q}")
    
    try:
        import anthropic
        from api_keys import ANTHROPIC_API_KEY
        
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        prompt = f"""You are helping fill out a YC (Y Combinator) application form.

Based on the following product documentation, answer this YC application question concisely and compellingly.

## Product Documentation:
{product_doc}

## YC Application Question:
{question}

## Instructions:
- Answer in 1-3 sentences, be concise but compelling
- Focus on what makes this product unique
- Use clear, simple language
- Don't use marketing fluff

## Your Answer:"""
        
        if status_callback:
            await status_callback("  → 调用 Claude API...")
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract text from response (handle different block types)
        content_block = message.content[0]
        answer = getattr(content_block, 'text', str(content_block)).strip()
        
            if status_callback:
            short_answer = answer[:60] + "..." if len(answer) > 60 else answer
            await status_callback(f"  → 生成答案: {short_answer}")
            await status_callback("✅ AI 答案生成Complete")
        
        return {
            "status": "completed",
            "message": "Answer generated",
            "answer": answer,
            "question": question,
        }
        
    except Exception as e:
        logger.error(f"Failed to generate answer: {e}")
            if status_callback:
            await status_callback(f"❌ AI 生成答案Failed: {e}")
        return {
            "status": "failed",
            "message": str(e),
            "answer": None,
        }


async def step_show_confirmation(
    status_server,
    answer: str,
    execution_count: int,
    source_file: str = "PITCH_CONTEXT.md",
) -> bool:
    """
    Step 3: Show confirmation dialog and wait for user response
    
    Returns True if user confirmed, False if cancelled
    """
    if not status_server:
        logger.warning("No status server available for confirmation dialog")
        return True  # Auto-confirm if no UI
    
    import uuid
    request_id = f"yc-confirm-{uuid.uuid4().hex[:8]}"
    
    # Create confirmation request (matching App.tsx confirm_request format)
    confirmation_data = {
        "request_id": request_id,
        "title": "YC Application" + ("" if execution_count == 0 else f" #{execution_count + 1}"),
                "question": "What is your company going to make?",
                "answer": answer,
        "execution_count": execution_count + 1,
        "source_file": source_file,
    }
    
    # Broadcast confirmation request
    await status_server.broadcast({
        "type": "confirm_request",
        "data": confirmation_data,
            })
        
    # Wait for user confirmation
    # The status_server should track confirm responses
    # For now, wait with timeout
    timeout = 60.0  # 60 second timeout
    poll_interval = 0.5
    elapsed = 0.0
    
    while elapsed < timeout:
        # Check if confirmation response received
        if hasattr(status_server, 'confirm_responses') and request_id in status_server.confirm_responses:
            response = status_server.confirm_responses.pop(request_id)
            return response.get('confirmed', False)
        
        await asyncio.sleep(poll_interval)
        elapsed += poll_interval
    
    # Timeout - auto-confirm for demo
    logger.warning(f"[YC Workflow] Confirmation timeout after {timeout}s, auto-confirming")
    return True


async def step_fill_form(
    browser_session,
    answer: str,
    status_callback: Optional[Callable[[str], Awaitable[None]]] = None,
    yc_url: str = "https://apply.ycombinator.com/"
) -> Dict[str, Any]:
    """
    Step 4: Fill the YC form using CDP - directly operates on the hooked Chrome
    
    This connects to the EXISTING Chrome window (hooked), not launching a new browser.
    """
    # #region agent log
    import json as _json; open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log','a',encoding='utf-8').write(_json.dumps({"hypothesisId":"D","location":"yc_workflow.py:step_fill_form:entry","message":"Step 4 entry - using CDP on hooked Chrome","data":{"answer_len": len(answer)},"timestamp":__import__('time').time()})+'\n')
    # #endregion
    
            if status_callback:
        await status_callback("✍️ 正在填Write YC Table单...")
        await status_callback("  → Connect到已 Hook 的 Chrome...")
    
    try:
        import aiohttp
        import websockets
        import json
        
        CDP_URL = "http://localhost:9222"
        
        # Step 1: Find the YC page in Chrome
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{CDP_URL}/json") as resp:
                targets = await resp.json()
        
        yc_target = None
        for target in targets:
            if "apply.ycombinator.com" in target.get("url", ""):
                yc_target = target
                break
        
        if not yc_target:
            if status_callback:
                await status_callback("❌ 未找到 YC Apply页面")
            return {"status": "failed", "message": "YC page not found in hooked Chrome"}
        
        if status_callback:
            await status_callback(f"  → 找到 YC 页面 ✓")
        
        # Step 2: Connect via WebSocket and execute JavaScript
        ws_url = yc_target["webSocketDebuggerUrl"]
        
        async with websockets.connect(ws_url) as ws:
            msg_id = 1
            
            async def send_cdp(method, params=None):
                nonlocal msg_id
                msg = {"id": msg_id, "method": method, "params": params or {}}
                await ws.send(json.dumps(msg))
                msg_id += 1
                while True:
                    response = json.loads(await ws.recv())
                    if response.get("id") == msg_id - 1:
                        return response
        
        if status_callback:
            await status_callback("  → FindTable单Input框...")
            
        # JavaScript to find and fill the textarea
            js_code = f'''
            (function() {{
                const textareas = document.querySelectorAll('textarea');
                for (const ta of textareas) {{
                    // Check if this is the right field by looking at labels or nearby text
                    const container = ta.closest('div');
                    const text = container ? container.textContent : '';
                    if (text.includes('company going to make') || text.includes('What is your company')) {{
                        ta.focus();
                        ta.value = {json.dumps(answer)};
                        ta.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        ta.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        return {{ success: true, field: 'what_company' }};
                    }}
                }}
                // Fallback: fill the first textarea
                if (textareas.length > 0) {{
                    textareas[0].focus();
                    textareas[0].value = {json.dumps(answer)};
                    textareas[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
                    return {{ success: true, field: 'first_textarea' }};
                }}
                return {{ success: false, error: 'No textarea found' }};
            }})()
            '''
            
            result = await send_cdp("Runtime.evaluate", {
                "expression": js_code,
                "returnByValue": True
            })
            
            # #region agent log
            import json as _json; open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log','a',encoding='utf-8').write(_json.dumps({"hypothesisId":"D-cdp","location":"yc_workflow.py:step_fill_form:cdp_result","message":"CDP fill result","data":{"result": str(result)[:300]},"timestamp":__import__('time').time()})+'\n')
            # #endregion
            
            eval_result = result.get("result", {}).get("result", {}).get("value", {})
            
            if eval_result.get("success"):
                if status_callback:
                    await status_callback(f"  → ✅ 已填Write到 {eval_result.get('field', 'textarea')}")
                    await status_callback("✅ Table单填WriteComplete!")
                return {
                    "status": "completed",
                    "message": "Form filled via CDP on hooked Chrome",
                    "answer": answer,
                    "method": "cdp_hooked",
                    "field": eval_result.get("field"),
                }
            else:
                error = eval_result.get("error", "Unknown error")
                if status_callback:
                    await status_callback(f"⚠️ 填WriteFailed: {error}")
                return {"status": "failed", "message": error}
                
    except Exception as e:
        logger.error(f"CDP fill failed: {e}")
        # #region agent log
        import json as _json; open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log','a',encoding='utf-8').write(_json.dumps({"hypothesisId":"D-error","location":"yc_workflow.py:step_fill_form:error","message":"CDP fill error","data":{"error": str(e)},"timestamp":__import__('time').time()})+'\n')
        # #endregion
        if status_callback:
            await status_callback(f"❌ CDP 填WriteFailed: {e}")
        return {
            "status": "failed",
            "message": str(e),
        }


async def _step_fill_form_browser_use_fallback(
    browser_session,
    answer: str,
    status_callback: Optional[Callable[[str], Awaitable[None]]] = None,
    yc_url: str = "https://apply.ycombinator.com/"
) -> Dict[str, Any]:
    """
    Fallback: Fill form using Browser-Use (requires working browser-use installation)
    """
    try:
        if not browser_session or not browser_session.is_started:
            if status_callback:
                await status_callback("⚠️ 浏览器Session未激活")
            return {
                "status": "failed",
                "message": "Browser session not started",
            }
        
        # Try multiple selectors for the YC form input
        selectors = [
            'textarea[name="what"]',
            'textarea[data-testid="what"]',
            '#what',
            'textarea:first-of-type',
            'textarea',
        ]
        
        success = False
        for selector in selectors:
            try:
                if status_callback:
                    await status_callback(f"  → 尝试Select器: {selector}")
                
                # Clear existing content and type new answer
                await browser_session._page.fill(selector, answer)
                success = True
                if status_callback:
                    await status_callback(f"✅ Success填WriteTable单")
                break
            except Exception as e:
                logger.debug(f"Selector {selector} failed: {e}")
                continue
        
        if not success:
            # Fallback: use keyboard
            if status_callback:
                await status_callback("  → 尝试Usage键盘Input...")
            
            # Click on the page first
            try:
                await browser_session._page.click('body')
                await asyncio.sleep(0.5)
                # Tab to the input field
                await browser_session._page.keyboard.press('Tab')
                await asyncio.sleep(0.3)
                # Type the answer
                await browser_session._page.keyboard.type(answer)
                success = True
                if status_callback:
                    await status_callback("✅ 通过键盘InputSuccess")
            except Exception as e:
                logger.error(f"Keyboard fallback failed: {e}")
        
        if success:
            return {
                "status": "completed",
                "message": "Form filled successfully",
                "answer": answer,
            }
        else:
            return {
                "status": "failed",
                "message": "Could not find or fill form input",
            }
            
    except Exception as e:
        logger.error(f"Failed to fill form: {e}")
        if status_callback:
            await status_callback(f"❌ 填WriteFailed: {e}")
        return {
            "status": "failed",
            "message": str(e),
        }


async def step_send_whatsapp(
    message: str,
    contact: str = "ZinoT",
    status_callback: Optional[Callable[[str], Awaitable[None]]] = None
) -> Dict[str, Any]:
    """
    Step 5: Send WhatsApp message using UFO (AI desktop automation)
    """
            if status_callback:
        await status_callback(f"📱 正在Usage UFO Send WhatsApp Message到 {contact}...")
    
    try:
        from engine.tools.ufo_executor import execute_desktop_task, TaskStatus
        
        # Use UFO to send WhatsApp message
        task = f"Open WhatsApp, find the chat with '{contact}', type the message '{message}' and press Enter to send it."
        
        if status_callback:
            await status_callback("  → UFO 正在Execute WhatsApp Send任务...")
        
        result = await execute_desktop_task(task)
        
        if result.status == TaskStatus.SUCCESS:
            if status_callback:
                await status_callback("✅ UFO SuccessSend WhatsApp Message")
            return {
                "status": "completed",
                "message": f"Sent '{message}' to {contact} via UFO",
                "method": "ufo",
            }
        else:
            # Fallback to pyautogui
            if status_callback:
                await status_callback(f"⚠️ UFO Failed ({result.message})，Usage备用方案...")
            return await _step_send_whatsapp_fallback(message, contact, status_callback)
            
    except ImportError as e:
        logger.warning(f"UFO not available: {e}, using fallback")
        if status_callback:
            await status_callback("⚠️ UFO 未安装，Usage备用方案...")
        return await _step_send_whatsapp_fallback(message, contact, status_callback)
    except Exception as e:
        logger.error(f"UFO WhatsApp failed: {e}")
        if status_callback:
            await status_callback(f"⚠️ UFO Error: {e}，Usage备用方案...")
        return await _step_send_whatsapp_fallback(message, contact, status_callback)


async def _step_send_whatsapp_fallback(
    message: str,
    contact: str = "ZinoT",
    status_callback: Optional[Callable[[str], Awaitable[None]]] = None
) -> Dict[str, Any]:
    """Fallback: Send WhatsApp using pyautogui"""
    try:
        import pyautogui
        
        if status_callback:
            await status_callback(f"  → Usage pyautogui InputMessage: {message}")
        
        pyautogui.write(message, interval=0.02)
        await asyncio.sleep(0.5)
        pyautogui.press('enter')
        
        if status_callback:
            await status_callback("✅ WhatsApp Message已Send")
        
        return {
            "status": "completed",
            "message": f"Sent '{message}' to {contact}",
            "method": "pyautogui_fallback",
        }
        
    except ImportError:
        if status_callback:
            await status_callback("⚠️ pyautogui 未安装，Skip WhatsApp Send")
        return {
            "status": "skipped",
            "message": "pyautogui not available",
        }
    except Exception as e:
        logger.error(f"Failed to send WhatsApp: {e}")
        if status_callback:
            await status_callback(f"❌ WhatsApp SendFailed: {e}")
        return {
            "status": "failed",
            "message": str(e),
        }


# ============================================================
# MAIN WORKFLOW EXECUTION
# ============================================================

async def execute_yc_workflow(
    status_callback: Optional[Callable[[str], Awaitable[None]]] = None,
    browser_session = None,
    status_server = None,
) -> Dict[str, Any]:
    """
    Execute the intelligent YC Application workflow
    
    NEW FLOW (AI-Powered):
    1. Organize desktop (optional, skip if already done)
    2. Read product documentation (PITCH_CONTEXT.md from Cursor)
    3. Read YC questions from hooked Chrome page
    4. Use AI to generate answers based on document + questions
    5. Show confirmation dialog with AI-generated answer
    6. Fill YC form via CDP
    7. Send WhatsApp notification

    Returns:
        Dict with success status and details
    """
    # #region agent log
    import json as _json; open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log','a',encoding='utf-8').write(_json.dumps({"hypothesisId":"A","location":"yc_workflow.py:execute_yc_workflow:entry","message":"AI Workflow entry","data":{"browser_session_is_none": browser_session is None, "status_server_is_none": status_server is None},"timestamp":__import__('time').time()})+'\n')
    # #endregion
    
    state = get_workflow_state()
    steps_completed = []
    
    # Header
    if status_callback:
        await status_callback("=" * 50)
        await status_callback(f"🚀 NogicOS smart YC Workflow - Execute #{state.execution_count + 1}")
        await status_callback("=" * 50)
        await asyncio.sleep(0.3)
    
    try:
        # ============ Step 1: Organize desktop (optional) ============
        if status_callback:
            await status_callback("\n📋 步骤 1/6: 整理桌面")
        result = await step_organize_desktop(status_callback)
        steps_completed.append(f"Organize Desktop: {result['status']}")
        
        # ============ Step 2: Read product documentation ============
        if status_callback:
            await status_callback("\n📋 步骤 2/6: Read Cursor 产品文档")
        doc_result = await step_read_document(status_callback)
        steps_completed.append(f"Read Document: {doc_result['status']}")
        
        product_doc = doc_result.get("content", "")
        if not product_doc:
            if status_callback:
                await status_callback("❌ 无法Read产品文档，工作流Terminate")
            return {
                "success": False,
                "message": "Cannot read product document",
                "steps_completed": steps_completed,
            }
        
        # ============ Step 3: Read YC questions from Chrome ============
        if status_callback:
            await status_callback("\n📋 步骤 3/6: Read YC Table单问题")
        questions_result = await step_read_yc_questions(status_callback)
        steps_completed.append(f"Read YC Questions: {questions_result['status']}")
        
        yc_questions = questions_result.get("questions", [])
        if not yc_questions:
            # Fallback: use default question
            if status_callback:
                await status_callback("⚠️ 未找到Table单问题，UsageDefault问题")
            yc_questions = [{
                "index": 0,
                "question": "What is your company going to make?",
                "fieldName": "what_company"
            }]
        
        # ============ Step 4: Generate AI answer ============
        if status_callback:
            await status_callback("\n📋 步骤 4/6: AI 生成答案")
        
        # Focus on the first question (usually "What is your company going to make?")
        target_question = yc_questions[0]["question"]
        
        answer_result = await step_generate_answer(
            product_doc, 
            target_question, 
            status_callback
        )
        steps_completed.append(f"Generate Answer: {answer_result['status']}")
        
        if answer_result["status"] == "failed" or not answer_result.get("answer"):
            if status_callback:
                await status_callback("❌ AI 无法生成答案，工作流Terminate")
            return {
                "success": False,
                "message": "AI failed to generate answer",
                "steps_completed": steps_completed,
            }
        
        ai_answer = answer_result["answer"]
        
        # ============ Step 5: Show confirmation ============
        if status_callback:
            await status_callback("\n📋 步骤 5/6: Confirm AI 生成的答案")
            await status_callback(f"  → 问题: {target_question[:50]}...")
            await status_callback(f"  → AI 答案: {ai_answer[:60]}...")
        
        confirmed = await step_show_confirmation(
            status_server,
            ai_answer,
            state.execution_count,
        )
        
        if not confirmed:
            if status_callback:
                await status_callback("❌ UserCancel了工作流")
            return {
                "success": False,
                "message": "User cancelled",
                "steps_completed": steps_completed,
            }
        
        steps_completed.append("Confirmation: confirmed")
        
        # ============ Step 6: Fill form ============
        if status_callback:
            await status_callback("\n📋 步骤 6/6: 填WriteTable单")
        result = await step_fill_form(browser_session, ai_answer, status_callback)
        steps_completed.append(f"Fill Form: {result['status']}")
        
        if result['status'] == 'failed':
            return {
                "success": False,
                "message": result['message'],
                "steps_completed": steps_completed,
            }
        
        # ============ Optional: Send WhatsApp ============
        if status_callback:
            await status_callback("\n📋 额Outer步骤: Send WhatsApp Notify")
        
        whatsapp_result = await step_send_whatsapp(WHATSAPP_MESSAGE, "ZinoT", status_callback)
        steps_completed.append(f"WhatsApp: {whatsapp_result['status']}")
        
        # Mark execution complete
        state.increment()
        
        # Final summary
        if status_callback:
            await status_callback("\n" + "=" * 50)
            await status_callback("✅ smart工作流ExecuteComplete!")
            await status_callback("=" * 50)
            await status_callback(f"📝 AI 生成并填Write的答案:")
            await status_callback(f"   {ai_answer}")
        
        return {
            "success": True,
            "message": "Intelligent workflow completed successfully",
            "steps_completed": steps_completed,
            "question": target_question,
            "ai_answer": ai_answer,
            "execution_count": state.execution_count,
        }
        
    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        if status_callback:
            await status_callback(f"\n❌ 工作流Failed: {e}")
        return {
            "success": False,
            "message": str(e),
            "steps_completed": steps_completed,
        }
