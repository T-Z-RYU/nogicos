# -*- coding: utf-8 -*-
"""
NogicOS Form Workflow - smartTable单填Write工作流

模拟 Cursor + Playwright MCP 的完整流程：
1. Read产品文档
2. Get页面快照
3. AnalyzeEmpty白Field
4. Root据文档生成答案
5. DisplayConfirm对话框
6. 填WriteTable单
"""

import asyncio
import logging
import os
from typing import Dict, Any, Optional, List, Callable, Awaitable
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class FormWorkflowContext:
    """工作流UpDown文"""
    document_path: str = ""
    document_content: str = ""
    page_url: str = ""
    page_title: str = ""
    empty_fields: List[Dict[str, Any]] = field(default_factory=list)
    generated_answers: Dict[str, str] = field(default_factory=dict)  # field_label -> answer
    confirmed: bool = False
    filled_count: int = 0
    execution_count: int = 1  # Executecount（1 = Firsttime，2+ = Aftercontinued）
    
    # CallbackFunction
    on_status_update: Optional[Callable[[str], Awaitable[None]]] = None
    # ConfirmCallback：(title, question, answer, execution_count, source_file) -> bool
    on_confirm_request: Optional[Callable[[str, str, str, int, str], Awaitable[bool]]] = None


class FormWorkflow:
    """
    smartTable单填Write工作流
    
    完全复刻 Cursor + Playwright MCP 的流程
    """
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self._playwright_executor = None
    
    async def _get_executor(self):
        """Get Playwright Execute器"""
        if self._playwright_executor is None:
            from .playwright_executor import get_playwright_executor
            self._playwright_executor = get_playwright_executor()
        return self._playwright_executor
    
    async def _send_status(self, ctx: FormWorkflowContext, message: str):
        """SendStateUpdate"""
        logger.info(f"[FormWorkflow] {message}")
        if ctx.on_status_update:
            await ctx.on_status_update(message)
    
    async def _request_confirm(
        self, 
        ctx: FormWorkflowContext, 
        title: str, 
        question: str, 
        answer: str
    ) -> bool:
        """RequestUserConfirm"""
        if ctx.on_confirm_request:
            return await ctx.on_confirm_request(
                title, 
                question, 
                answer, 
                ctx.execution_count, 
                ctx.document_path
            )
        return True  # DefaultConfirm
    
    async def step_read_document(self, ctx: FormWorkflowContext) -> bool:
        """
        步骤 1: Read产品文档
        """
        await self._send_status(ctx, f"📖 正在Read产品文档: {ctx.document_path}")
        
        try:
            # BuildCompletePath
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            full_path = os.path.join(base_path, ctx.document_path)
            
            if not os.path.exists(full_path):
                # tryOtherPath
                full_path = ctx.document_path
            
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    ctx.document_content = f.read()
                
                await self._send_status(ctx, f"   └── ReadComplete，共 {len(ctx.document_content)} Character")
                await self._send_status(ctx, f"   └── 文档Class型: 产品说明文档")
                return True
            else:
                await self._send_status(ctx, f"   └── ❌ File不存在: {full_path}")
                return False
                
        except Exception as e:
            await self._send_status(ctx, f"   └── ❌ ReadFailed: {e}")
            return False
    
    async def step_get_page_snapshot(self, ctx: FormWorkflowContext) -> bool:
        """
        步骤 2: Get页面快照
        """
        await self._send_status(ctx, "🌐 正在Connect浏览器...")
        
        # #region agent log
        import json as _json
        with open(r"c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log", "a") as _f:
            _f.write(_json.dumps({"location":"form_workflow.py:step_get_page_snapshot","message":"step started","data":{},"timestamp":__import__("time").time()*1000,"hypothesisId":"A"}) + "\n")
        # #endregion
        
        try:
            executor = await self._get_executor()
            
            # #region agent log
            with open(r"c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log", "a") as _f:
                _f.write(_json.dumps({"location":"form_workflow.py:step_get_page_snapshot","message":"got executor","data":{"connected":executor._connected},"timestamp":__import__("time").time()*1000,"hypothesisId":"A"}) + "\n")
            # #endregion
            
            # Connectto Chrome
            if not executor._connected:
                success = await executor.connect()
                # #region agent log
                with open(r"c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log", "a") as _f:
                    _f.write(_json.dumps({"location":"form_workflow.py:step_get_page_snapshot","message":"connect result","data":{"success":success},"timestamp":__import__("time").time()*1000,"hypothesisId":"A"}) + "\n")
                # #endregion
                if not success:
                    await self._send_status(ctx, "   └── ❌ 无法Connect到 Chrome (需要 CDP Port)")
                    return False
            
            await self._send_status(ctx, "   └── ✅ 已Connect到 Chrome")
            
            # get snapshot
            snapshot = await executor.get_snapshot()
            # #region agent log
            with open(r"c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log", "a") as _f:
                _f.write(_json.dumps({"location":"form_workflow.py:step_get_page_snapshot","message":"snapshot result","data":{"has_snapshot":snapshot is not None,"url":snapshot.url if snapshot else None},"timestamp":__import__("time").time()*1000,"hypothesisId":"D"}) + "\n")
            # #endregion
            if snapshot:
                ctx.page_url = snapshot.url
                ctx.page_title = snapshot.title
                await self._send_status(ctx, f"   └── 页面: {snapshot.title}")
                await self._send_status(ctx, f"   └── URL: {snapshot.url}")
                return True
            else:
                await self._send_status(ctx, "   └── ❌ 无法Get页面快照")
                return False
                
        except Exception as e:
            # #region agent log
            with open(r"c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log", "a") as _f:
                _f.write(_json.dumps({"location":"form_workflow.py:step_get_page_snapshot","message":"exception","data":{"error":str(e),"error_type":type(e).__name__},"timestamp":__import__("time").time()*1000,"hypothesisId":"A"}) + "\n")
            # #endregion
            await self._send_status(ctx, f"   └── ❌ ConnectFailed: {e}")
            return False
    
    async def step_find_empty_fields(self, ctx: FormWorkflowContext) -> bool:
        """
        步骤 3: FindEmpty白Field
        """
        await self._send_status(ctx, "🔍 正在analyze form...")
        
        try:
            executor = await self._get_executor()
            empty_fields = await executor.find_empty_fields()
            
            ctx.empty_fields = empty_fields
            
            if empty_fields:
                await self._send_status(ctx, f"   └── 找到 {len(empty_fields)} 个Empty白Field:")
                for i, field in enumerate(empty_fields[:3]):  # onlyDisplayBefore 3 a
                    label = field.get('label', '未知Field')[:50]
                    await self._send_status(ctx, f"      {i+1}. {label}")
                if len(empty_fields) > 3:
                    await self._send_status(ctx, f"      ... 还有 {len(empty_fields) - 3} 个Field")
                return True
            else:
                await self._send_status(ctx, "   └── ✅ 所有Field已填WriteComplete")
                return True
                
        except Exception as e:
            await self._send_status(ctx, f"   └── ❌ AnalyzeFailed: {e}")
            return False
    
    async def step_generate_answers(self, ctx: FormWorkflowContext) -> bool:
        """
        步骤 4: Root据文档生成答案
        """
        if not ctx.empty_fields:
            return True
        
        await self._send_status(ctx, "🤔 正在Root据产品文档生成答案...")
        
        try:
            for field in ctx.empty_fields:
                label = field.get('label', '')
                
                # Usage LLM GenerationAnswer
                answer = await self._generate_answer_for_field(
                    ctx.document_content, 
                    label
                )
                
                if answer:
                    ctx.generated_answers[label] = answer
                    short_answer = answer[:50] + "..." if len(answer) > 50 else answer
                    await self._send_status(ctx, f"   └── {label[:30]}: {short_answer}")
            
            return bool(ctx.generated_answers)
            
        except Exception as e:
            await self._send_status(ctx, f"   └── ❌ 生成Failed: {e}")
            return False
    
    async def _generate_answer_for_field(self, document: str, field_label: str) -> str:
        """Usage LLM 生成答案"""
        if not self.llm_client:
            # no LLM，Usagesimple's RuleMatch
            return self._simple_answer_generation(document, field_label)
        
        try:
            # Usage Anthropic API
            prompt = f"""Based on the following product document, generate a concise answer for the form field.

Product Document:
{document[:3000]}

Form Field: {field_label}

Requirements:
- Be concise and professional
- Focus on the product's key features and value proposition
- If the field asks "What is your company going to make?", describe the product clearly

Generate ONLY the answer, no explanation:"""

            response = self.llm_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            logger.error(f"[FormWorkflow] LLM generation failed: {e}")
            return self._simple_answer_generation(document, field_label)
    
    def _simple_answer_generation(self, document: str, field_label: str) -> str:
        """简单的RuleMatch生成答案"""
        label_lower = field_label.lower()
        
        if "company" in label_lower and "make" in label_lower:
            # Extractionproductdescribe
            lines = document.split('\n')
            for line in lines:
                if 'NogicOS' in line and len(line) > 50:
                    return line.strip().strip('>').strip()
            
            # DefaultAnswer
            return "NogicOS is the first AI that can see your browser, local files, and desktop apps simultaneously. It's a desktop AI assistant for knowledge workers that reads your complete work environment and takes direct action."
        
        return ""
    
    async def step_confirm(self, ctx: FormWorkflowContext) -> bool:
        """
        步骤 5: DisplayConfirm对话框
        """
        if not ctx.generated_answers:
            return True
        
        await self._send_status(ctx, "⏸️ WaitUserConfirm...")
        
        # BuildConfirmInnercontent
        for label, answer in ctx.generated_answers.items():
            confirmed = await self._request_confirm(
                ctx,
                title="Confirm填WriteTable单",
                question=label,
                answer=answer
            )
            
            if not confirmed:
                await self._send_status(ctx, f"   └── ❌ UserCancel了: {label[:30]}")
                return False
            
            await self._send_status(ctx, f"   └── ✅ Confirm: {label[:30]}")
        
        ctx.confirmed = True
        return True
    
    async def step_fill_form(self, ctx: FormWorkflowContext) -> bool:
        """
        步骤 6: 填WriteTable单
        """
        if not ctx.confirmed or not ctx.generated_answers:
            return False
        
        await self._send_status(ctx, "✏️ 正在填WriteTable单...")
        
        try:
            executor = await self._get_executor()
            
            for label, answer in ctx.generated_answers.items():
                success = await executor.fill_field_by_label(label, answer)
                
                if success:
                    ctx.filled_count += 1
                    await self._send_status(ctx, f"   └── ✅ 已填Write: {label[:30]}")
                else:
                    await self._send_status(ctx, f"   └── ⚠️ 无法填Write: {label[:30]}")
            
            return ctx.filled_count > 0
            
        except Exception as e:
            await self._send_status(ctx, f"   └── ❌ 填WriteFailed: {e}")
            return False
    
    async def run(
        self, 
        document_path: str,
        on_status: Optional[Callable[[str], Awaitable[None]]] = None,
        on_confirm: Optional[Callable[[str, str, str, int, str], Awaitable[bool]]] = None,
        execution_count: int = 1,
    ) -> Dict[str, Any]:
        """
        Running完整工作流
        
        Args:
            document_path: 产品文档Path
            on_status: StateUpdateCallback
            on_confirm: ConfirmRequestCallback (title, question, answer, execution_count, source_file) -> bool
            execution_count: Execute次数（1 = First次，2+ = Aftercontinued）
            
        Returns:
            工作流Result
        """
        ctx = FormWorkflowContext(
            document_path=document_path,
            on_status_update=on_status,
            on_confirm_request=on_confirm,
            execution_count=execution_count,
        )
        
        steps = [
            ("Read文档", self.step_read_document),
            ("Connect浏览器", self.step_get_page_snapshot),
            ("analyze form", self.step_find_empty_fields),
            ("生成答案", self.step_generate_answers),
            ("Confirm填Write", self.step_confirm),
            ("填WriteTable单", self.step_fill_form),
        ]
        
        for step_name, step_func in steps:
            await self._send_status(ctx, f"\n{'='*40}")
            await self._send_status(ctx, f"步骤: {step_name}")
            await self._send_status(ctx, f"{'='*40}")
            
            success = await step_func(ctx)
            
            if not success and step_name not in ["analyze form"]:  # AllownoEmptywhiteField
                return {
                    "success": False,
                    "failed_step": step_name,
                    "filled_count": ctx.filled_count,
                }
        
        return {
            "success": True,
            "filled_count": ctx.filled_count,
            "answers": ctx.generated_answers,
        }


def register_form_workflow_tools(registry):
    """RegisterTable单工作流Tool"""
    from .base import ToolCategory
    
    def get_status_server():
        """Get StatusServer Instance"""
        try:
            # from hive_server ModuleGetGlobal engine Instance
            import sys
            if 'hive_server' in sys.modules:
                hive_server = sys.modules['hive_server']
                engine = getattr(hive_server, 'engine', None)
                if engine and hasattr(engine, 'status_server'):
                    return engine.status_server
        except Exception as e:
            logger.warning(f"[FormWorkflow] Failed to get status_server: {e}")
        return None
    
    @registry.action(
        description="""Run the complete form filling workflow (like Cursor + Playwright MCP).
        
This workflow:
1. Read the product document
2. Connect to Chrome via Hook (CDP)
3. Get page snapshot and find empty form fields
4. Generate answers based on the document using AI
5. Show confirmation dialog (wait for user to confirm)
6. Fill the form with confirmed answers

Args:
    document_path: Path to the product document (e.g. 'nogicos/PITCH_CONTEXT.md')
    
Returns:
    Result with success status, filled fields count, and generated answers""",
        category=ToolCategory.LOCAL,
    )
    async def run_form_workflow(document_path: str) -> Dict[str, Any]:
        """Run the form filling workflow"""
        workflow = FormWorkflow()
        server = get_status_server()
        
        # Status callback - send to WebSocket
        async def send_status(msg: str):
            logger.info(f"[FormWorkflow] {msg}")
            if server:
                await server.broadcast_workflow_status(msg)
        
        # Confirmation callback - use WebSocket dialog
        async def request_confirm(
            title: str, 
            question: str, 
            answer: str, 
            execution_count: int = 1, 
            source_file: str = ""
        ) -> bool:
            if server:
                # Use WebSocket confirmation dialog
                return await server.request_confirmation(
                    title, 
                    question, 
                    answer,
                    execution_count=execution_count,
                    source_file=source_file
                )
            else:
                # Fallback: auto-confirm if no server
                logger.warning("[FormWorkflow] No status server, auto-confirming")
                return True
        
        result = await workflow.run(
            document_path=document_path,
            on_status=send_status,
            on_confirm=request_confirm,
        )
        
        return result
    
    logger.info("[FormWorkflow] Form workflow tools registered")


# Test
async def test_workflow():
    """Test工作流"""
    workflow = FormWorkflow()
    
    async def print_status(msg: str):
        print(msg)
    
    async def auto_confirm(title: str, question: str, answer: str) -> bool:
        print(f"\n{'='*50}")
        print(f"ConfirmRequest: {title}")
        print(f"问题: {question}")
        print(f"答案: {answer}")
        print(f"{'='*50}")
        return True
    
    result = await workflow.run(
        document_path="nogicos/PITCH_CONTEXT.md",
        on_status=print_status,
        on_confirm=auto_confirm,
    )
    
    print(f"\nResult: {result}")


if __name__ == "__main__":
    asyncio.run(test_workflow())
