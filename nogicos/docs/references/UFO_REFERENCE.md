# Microsoft UFO 参考文档

> 源码地址: https://github.com/microsoft/UFO
> 最后更新: 2025/01/07

---

## 概述

### 项目定位

UFO (UI-Focused Agent) 是微软研究院开发的 Windows GUI 智能自动化框架，采用双层 Agent 架构（HostAgent + AppAgent），支持 GUI 和 API 混合执行。

### 核心架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           UFO 架构                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                         ┌─────────────────┐                                 │
│                         │   User Request  │                                 │
│                         └────────┬────────┘                                 │
│                                  │                                          │
│                                  ▼                                          │
│                         ┌─────────────────┐                                 │
│                         │   HostAgent     │ ← 桌面编排器                     │
│                         │  "what" & "when"│                                 │
│                         └────────┬────────┘                                 │
│                                  │                                          │
│                    ┌─────────────┼─────────────┐                            │
│                    │             │             │                            │
│                    ▼             ▼             ▼                            │
│            ┌───────────┐ ┌───────────┐ ┌───────────┐                       │
│            │ AppAgent  │ │ AppAgent  │ │ AppAgent  │ ← 应用执行器           │
│            │  (Word)   │ │  (Excel)  │ │ (Browser) │                       │
│            │"how"&"where"│ │          │ │           │                       │
│            └─────┬─────┘ └─────┬─────┘ └─────┬─────┘                       │
│                  │             │             │                              │
│                  ▼             ▼             ▼                              │
│            ┌─────────────────────────────────────────┐                      │
│            │          Hybrid Action Layer            │                      │
│            │   ┌─────────┐         ┌─────────┐      │                      │
│            │   │   GUI   │         │   API   │      │                      │
│            │   │(UIA/Win32)│       │ (WinCOM)│      │                      │
│            │   └─────────┘         └─────────┘      │                      │
│            └─────────────────────────────────────────┘                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 与 NogicOS 的关系

| UFO | NogicOS | 说明 |
|-----|---------|------|
| HostAgent + AppAgent | 可借鉴 | 双层架构设计 |
| 状态机 | 可借鉴 | 任务状态管理 |
| MCP 工具集成 | 可借鉴 | 工具注册机制 |
| UIA + Win32 | 可借鉴 | Windows 控制 |
| GUI 全局输入 | 需改进 | 加窗口隔离 |

---

## 核心代码

### 1. HostAgent (`host_agent.py`)

HostAgent 是桌面级别的编排器，负责理解用户请求、选择目标应用、创建和协调 AppAgent。

```python
# 源码位置: ufo/agents/agent/host_agent.py

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Union

from ufo.agents.agent.app_agent import AppAgent, OpenAIOperatorAgent
from ufo.agents.agent.basic import AgentRegistry, BasicAgent
from ufo.agents.memory.blackboard import Blackboard
from ufo.agents.processors.host_agent_processor import HostAgentProcessor
from ufo.agents.states.host_agent_state import ContinueHostAgentState, HostAgentStatus
from aip.messages import Command, MCPToolInfo
from ufo.module.context import Context, ContextNames
from ufo.prompter.agent_prompter import HostAgentPrompter


class RunningMode(str, Enum):
    """运行模式枚举"""
    NORMAL = "normal"
    BATCH_NORMAL = "batch_normal"
    FOLLOWER = "follower"
    NORMAL_OPERATOR = "normal_operator"
    BATCH_OPERATOR = "batch_normal_operator"


class AgentFactory:
    """
    工厂类：根据类型创建不同的 Agent
    """
    @staticmethod
    def create_agent(agent_type: str, *args, **kwargs) -> BasicAgent:
        if agent_type == "host":
            return HostAgent(*args, **kwargs)
        elif agent_type == "app":
            return AppAgent(*args, **kwargs)
        elif agent_type == "operator":
            return OpenAIOperatorAgent(*args, **kwargs)
        elif agent_type in AgentRegistry.list_agents():
            return AgentRegistry.get(agent_type)(*args, **kwargs)
        else:
            raise ValueError("Invalid agent type: {}".format(agent_type))


@AgentRegistry.register(agent_name="hostagent")
class HostAgent(BasicAgent):
    """
    HostAgent 是 AppAgents 的管理者
    职责：
    1. 解析用户请求
    2. 选择目标应用
    3. 创建和协调 AppAgent
    """

    def __init__(
        self,
        name: str,
        is_visual: bool,
        main_prompt: str,
        example_prompt: str,
        api_prompt: str,
    ) -> None:
        """
        初始化 HostAgent
        :param name: Agent 名称
        :param is_visual: 是否使用视觉模式
        :param main_prompt: 主提示词文件路径
        :param example_prompt: 示例提示词文件路径
        :param api_prompt: API 提示词文件路径
        """
        super().__init__(name=name)
        self.prompter = self.get_prompter(
            is_visual, main_prompt, example_prompt, api_prompt
        )
        self.offline_doc_retriever = None
        self.online_doc_retriever = None
        self.experience_retriever = None
        self.human_demonstration_retriever = None
        self.agent_factory = AgentFactory()
        self.appagent_dict = {}  # 存储所有 AppAgent
        self._active_appagent = None  # 当前活跃的 AppAgent
        self._blackboard = Blackboard()  # 共享黑板
        self.set_state(self.default_state)
        self._context_provision_executed = False

    @property
    def sub_agent_amount(self) -> int:
        """获取子 Agent 数量"""
        return len(self.appagent_dict)

    def get_active_appagent(self) -> AppAgent:
        """获取当前活跃的 AppAgent"""
        return self._active_appagent

    @property
    def blackboard(self) -> Blackboard:
        """获取共享黑板"""
        return self._blackboard

    def message_constructor(
        self,
        image_list: List[str],
        os_info: str,
        plan: List[str],
        prev_subtask: List[Dict[str, str]],
        request: str,
        blackboard_prompt: List[Dict[str, str]],
    ) -> List[Dict[str, Union[str, List[Dict[str, str]]]]]:
        """
        构建发送给 LLM 的消息
        :param image_list: 截图列表
        :param os_info: 操作系统信息
        :param plan: 执行计划
        :param prev_subtask: 之前的子任务
        :param request: 用户请求
        :param blackboard_prompt: 黑板提示
        :return: 消息列表
        """
        hostagent_prompt_system_message = self.prompter.system_prompt_construction()
        hostagent_prompt_user_message = self.prompter.user_content_construction(
            image_list=image_list,
            control_item=os_info,
            prev_subtask=prev_subtask,
            prev_plan=plan,
            user_request=request,
        )

        if blackboard_prompt:
            hostagent_prompt_user_message = (
                blackboard_prompt + hostagent_prompt_user_message
            )

        hostagent_prompt_message = self.prompter.prompt_construction(
            hostagent_prompt_system_message, hostagent_prompt_user_message
        )

        return hostagent_prompt_message

    async def process(self, context: Context) -> None:
        """
        处理 Agent 主循环
        :param context: 上下文
        """
        if not self._context_provision_executed:
            await self.context_provision(context=context)
            self._context_provision_executed = True
        
        self.processor = HostAgentProcessor(agent=self, global_context=context)
        await self.processor.process()

        # 同步状态
        self.status = self.processor.processing_context.get_local("status")
        self.logger.info(f"Host agent status updated to: {self.status}")

    async def context_provision(self, context: Context) -> None:
        """加载上下文（MCP 工具等）"""
        await self._load_mcp_context(context)

    async def _load_mcp_context(self, context: Context) -> None:
        """
        加载 MCP 工具信息
        """
        self.logger.info("Loading MCP tool information...")
        result = await context.command_dispatcher.execute_commands(
            [
                Command(
                    tool_name="list_tools",
                    parameters={"tool_type": "action"},
                    tool_type="action",
                )
            ]
        )

        tool_list = result[0].result if result else None
        tool_name_list = (
            [tool.get("tool_name") for tool in tool_list] if tool_list else []
        )
        self.logger.info(f"Loaded tool list: {tool_name_list} for the HostAgent.")

        tools_info = [MCPToolInfo(**tool) for tool in tool_list]
        self.prompter.create_api_prompt_template(tools=tools_info)

    def create_subagent(self, context: Optional["Context"] = None) -> None:
        """
        创建子 Agent（核心方法）
        根据上下文决定创建 AppAgent 还是 OperatorAgent
        :param context: 上下文
        """
        mode = RunningMode(context.get(ContextNames.MODE))

        assigned_third_party_agent = self.processor.processing_context.get_local(
            "assigned_third_party_agent"
        )
        
        if assigned_third_party_agent:
            # 创建第三方 Agent
            config = AgentConfigResolver.resolve_third_party_config(
                assigned_third_party_agent, mode
            )
        else:
            # 创建标准 AppAgent
            window_name = context.get(ContextNames.APPLICATION_PROCESS_NAME)
            root_name = context.get(ContextNames.APPLICATION_ROOT_NAME)

            if mode in {
                RunningMode.NORMAL,
                RunningMode.BATCH_NORMAL,
                RunningMode.FOLLOWER,
            }:
                config = AgentConfigResolver.resolve_app_agent_config(
                    root_name, window_name, mode
                )
            elif mode in {RunningMode.NORMAL_OPERATOR, RunningMode.BATCH_OPERATOR}:
                config = AgentConfigResolver.resolve_operator_agent_config(
                    root_name, window_name, mode
                )
            else:
                raise ValueError(f"Unsupported mode: {mode}")

        agent_name = config.get("name")
        agent_type = config.get("agent_type")
        process_name = config.get("process_name")

        self.logger.info(f"Creating sub agent with config: {config}")

        # 使用工厂创建 Agent
        app_agent = self.agent_factory.create_agent(**config)
        self.appagent_dict[agent_name] = app_agent
        app_agent.host = self  # 设置父 Agent
        self._active_appagent = app_agent

        self.logger.info(
            f"Created sub agent: {agent_name} with type {agent_type}"
        )

        return app_agent

    @property
    def status_manager(self) -> HostAgentStatus:
        """获取状态管理器"""
        return HostAgentStatus

    @property
    def default_state(self) -> ContinueHostAgentState:
        """获取默认状态"""
        return ContinueHostAgentState()
```

#### 关键点说明

1. **双层架构**: HostAgent 管理多个 AppAgent
2. **工厂模式**: `AgentFactory` 根据类型创建不同 Agent
3. **黑板模式**: `Blackboard` 用于 Agent 间共享信息
4. **MCP 集成**: 动态加载工具列表
5. **状态机**: `HostAgentStatus` 管理状态转换

---

### 2. AppAgent (`app_agent.py`)

AppAgent 是应用级别的执行器，负责在特定应用内执行操作。

```python
# 源码位置: ufo/agents/agent/app_agent.py

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple, Union

from ufo.agents.agent.basic import AgentRegistry, BasicAgent
from ufo.agents.memory.blackboard import Blackboard
from ufo.agents.processors.app_agent_processor import AppAgentProcessor
from ufo.agents.processors.core.processor_framework import ProcessorTemplate
from ufo.agents.processors.schemas.response_schema import AppAgentResponse
from ufo.agents.states.app_agent_state import AppAgentStatus, ContinueAppAgentState
from aip.messages import Command, MCPToolInfo
from ufo.module import interactor
from ufo.module.context import Context, ContextNames
from ufo.prompter.agent_prompter import AppAgentPrompter


@AgentRegistry.register(agent_name="appagent", processor_cls=AppAgentProcessor)
class AppAgent(BasicAgent):
    """
    AppAgent 管理与特定应用的交互
    """

    def __init__(
        self,
        name: str,
        process_name: str,
        app_root_name: str,
        is_visual: bool,
        main_prompt: str,
        example_prompt: str,
        skip_prompter: bool = False,
        mode: str = "normal",
    ) -> None:
        """
        初始化 AppAgent
        :param name: Agent 名称
        :param process_name: 应用进程名
        :param app_root_name: 应用根名称
        :param is_visual: 是否使用视觉模式
        :param main_prompt: 主提示词文件路径
        :param example_prompt: 示例提示词文件路径
        :param skip_prompter: 是否跳过提示词初始化
        :param mode: 运行模式
        """
        super().__init__(name=name)
        if not skip_prompter:
            self.prompter = self.get_prompter(is_visual, main_prompt, example_prompt)
        self._process_name = process_name
        self._app_root_name = app_root_name
        self.offline_doc_retriever = None
        self.online_doc_retriever = None
        self.experience_retriever = None
        self.human_demonstration_retriever = None

        self._mode = mode
        self.set_state(self.default_state)
        self._context_provision_executed = False
        self.logger = logging.getLogger(__name__)
        self._processor: Optional[AppAgentProcessor] = None

    def message_constructor(
        self,
        dynamic_examples: str,
        dynamic_knowledge: str,
        image_list: List,
        control_info: str,
        prev_subtask: List[Dict[str, str]],
        plan: List[str],
        request: str,
        subtask: str,
        current_application: str,
        host_message: List[str],
        blackboard_prompt: List[Dict[str, str]],
        last_success_actions: List[Dict[str, Any]],
        include_last_screenshot: bool,
    ) -> List[Dict[str, Union[str, List[Dict[str, str]]]]]:
        """
        构建 AppAgent 的提示消息
        :param dynamic_examples: 动态示例（来自自我演示和人工演示）
        :param dynamic_knowledge: 动态知识（来自外部知识库）
        :param image_list: 截图列表
        :param control_info: 控件信息
        :param plan: 执行计划
        :param request: 用户请求
        :param subtask: 当前子任务
        :param current_application: 当前应用名称
        :param host_message: 来自 HostAgent 的消息
        :param blackboard_prompt: 黑板提示
        :param last_success_actions: 上次成功的操作列表
        :param include_last_screenshot: 是否包含上次截图
        :return: 提示消息
        """
        appagent_prompt_system_message = self.prompter.system_prompt_construction(
            dynamic_examples
        )

        appagent_prompt_user_message = self.prompter.user_content_construction(
            image_list=image_list,
            control_item=control_info,
            prev_subtask=prev_subtask,
            prev_plan=plan,
            user_request=request,
            subtask=subtask,
            current_application=current_application,
            host_message=host_message,
            retrieved_docs=dynamic_knowledge,
            last_success_actions=last_success_actions,
            include_last_screenshot=include_last_screenshot,
        )

        if blackboard_prompt:
            appagent_prompt_user_message = (
                blackboard_prompt + appagent_prompt_user_message
            )

        appagent_prompt_message = self.prompter.prompt_construction(
            appagent_prompt_system_message, appagent_prompt_user_message
        )

        return appagent_prompt_message

    async def process(self, context: Context) -> None:
        """
        处理 Agent 主循环
        :param context: 上下文
        """
        if not self._context_provision_executed:
            await self.context_provision(context=context)
            self._context_provision_executed = True

        if not self._processor_cls:
            raise ValueError(f"{self.__class__.__name__} has no processor assigned.")

        self.processor: ProcessorTemplate = self._processor_cls(
            agent=self, global_context=context
        )
        await self.processor.process()

        self.status = self.processor.processing_context.get_local("status")

    def process_confirmation(self) -> bool:
        """
        处理用户确认（敏感操作）
        :return: 是否确认
        """
        action = self.processor.actions
        control_text = self.processor.control_text

        decision = interactor.sensitive_step_asker(action, control_text)

        if not decision:
            console.print("❌ The user has canceled the action.", style="red")

        return decision

    @property
    def status_manager(self) -> AppAgentStatus:
        """获取状态管理器"""
        return AppAgentStatus

    @property
    def mode(self) -> str:
        """获取运行模式"""
        return self._mode

    def build_offline_docs_retriever(self) -> None:
        """构建离线文档检索器"""
        self.offline_doc_retriever = self.retriever_factory.create_retriever(
            "offline", self._app_root_name
        )

    def build_experience_retriever(self, db_path: str) -> None:
        """构建经验检索器"""
        self.experience_retriever = self.retriever_factory.create_retriever(
            "experience", db_path
        )

    async def context_provision(
        self, request: str = "", context: Context = None
    ) -> None:
        """
        为 AppAgent 提供上下文
        :param request: 请求（用于 Bing 搜索检索器）
        """
        ufo_config = get_ufo_config()

        # 加载离线文档索引器
        if ufo_config.rag.offline_docs:
            console.print(
                f"📚 Loading offline help document indexer for {self._process_name}...",
                style="magenta",
            )
            self.build_offline_docs_retriever()

        # 加载在线搜索索引器
        if ufo_config.rag.online_search and request:
            console.print("🔍 Creating a Bing search indexer...", style="magenta")
            self.build_online_search_retriever(
                request, ufo_config.rag.online_search_topk
            )

        # 加载经验索引器
        if ufo_config.rag.experience:
            console.print("📖 Creating an experience indexer...", style="magenta")
            experience_path = ufo_config.rag.experience_saved_path
            db_path = os.path.join(experience_path, "experience_db")
            self.build_experience_retriever(db_path)

        # 加载演示索引器
        if ufo_config.rag.demonstration:
            console.print("🎬 Creating an demonstration indexer...", style="magenta")
            demonstration_path = ufo_config.rag.demonstration_saved_path
            db_path = os.path.join(demonstration_path, "demonstration_db")
            self.build_human_demonstration_retriever(db_path)

        await self._load_mcp_context(context)

    async def _load_mcp_context(self, context: Context) -> None:
        """
        加载 MCP 工具信息
        """
        self.logger.info("Loading MCP tool information...")
        result = await context.command_dispatcher.execute_commands(
            [
                Command(
                    tool_name="list_tools",
                    parameters={"tool_type": "action"},
                    tool_type="action",
                )
            ]
        )

        tool_list = result[0].result if result else None
        tool_name_list = (
            [tool.get("tool_name") for tool in tool_list] if tool_list else []
        )
        self.logger.info(
            f"Loaded tool list: {tool_name_list} for the application {self._process_name}."
        )

        tools_info = [MCPToolInfo(**tool) for tool in tool_list]

        # 更新上下文中的工具信息
        context.update_dict(ContextNames.TOOL_INFO, {self._name: tools_info})
        self.prompter.create_api_prompt_template(tools=tools_info)

    @property
    def default_state(self) -> ContinueAppAgentState:
        """获取默认状态"""
        return ContinueAppAgentState()
```

#### 关键点说明

1. **应用绑定**: `_process_name`, `_app_root_name`
2. **RAG 检索**: 支持离线文档、在线搜索、经验、演示
3. **敏感操作确认**: `process_confirmation()` 
4. **MCP 工具加载**: 动态获取可用工具
5. **状态机**: `AppAgentStatus` 管理状态

---

### 3. 状态机设计

```python
# UFO 状态机设计模式

from enum import Enum
from abc import ABC, abstractmethod

class AgentState(ABC):
    """Agent 状态基类"""
    
    @abstractmethod
    def handle(self, agent, context) -> 'AgentState':
        """处理当前状态，返回下一个状态"""
        pass

class HostAgentStatus(Enum):
    """HostAgent 状态枚举"""
    CONTINUE = "continue"       # 继续执行
    FINISH = "finish"           # 完成
    FAIL = "fail"               # 失败
    PENDING = "pending"         # 等待用户输入
    CONFIRM = "confirm"         # 等待确认

class AppAgentStatus(Enum):
    """AppAgent 状态枚举"""
    CONTINUE = "continue"       # 继续执行
    FINISH = "finish"           # 完成当前子任务
    ERROR = "error"             # 错误
    PENDING = "pending"         # 等待
    SCREENSHOT = "screenshot"   # 需要截图

class ContinueHostAgentState(AgentState):
    """继续执行状态"""
    
    def handle(self, agent, context) -> AgentState:
        # 1. 截图
        # 2. 调用 LLM
        # 3. 解析响应
        # 4. 根据响应决定下一个状态
        
        if response.status == "finish":
            return FinishHostAgentState()
        elif response.status == "pending":
            return PendingHostAgentState()
        else:
            return ContinueHostAgentState()
```

---

## 架构分析

### 优点

1. **双层架构**: HostAgent + AppAgent 职责分离
2. **Windows 原生**: 使用 UIA 和 Win32 API
3. **混合执行**: GUI + API 动态选择
4. **RAG 增强**: 支持经验检索和文档检索
5. **MCP 集成**: 标准化工具注册

### 限制

1. **全局输入**: `click_input`, `type_keys` 会移动物理鼠标
2. **无窗口隔离**: 不能在后台操作窗口
3. **复杂度高**: 代码量大，学习曲线陡

### 我们可以借鉴什么

| 模块 | 借鉴程度 | 说明 |
|------|---------|------|
| HostAgent + AppAgent | 完全借鉴 | 双层架构 |
| 状态机 | 完全借鉴 | CONTINUE/FINISH/PENDING |
| AgentFactory | 完全借鉴 | 工厂模式 |
| Blackboard | 部分借鉴 | Agent 间通信 |
| MCP 集成 | 完全借鉴 | 工具注册 |
| UIA 控件检测 | 部分借鉴 | 需要改进 |
| RAG 检索 | 可选借鉴 | 增强型功能 |

---

## NogicOS 适配建议

### 可以直接复用的部分

1. **双层 Agent 架构**

```python
# NogicOS 实现
class NogicOSHostAgent:
    """桌面编排器"""
    
    def __init__(self):
        self.app_agents = {}  # hwnd -> AppAgent
        self.active_agent = None
        self.blackboard = Blackboard()
    
    async def process(self, request: str, context: Context):
        # 1. 理解用户请求
        # 2. 选择目标应用/窗口
        # 3. 创建或获取 AppAgent
        # 4. 委派任务
        pass
    
    def create_app_agent(self, hwnd: int, app_info: dict) -> 'NogicOSAppAgent':
        agent = NogicOSAppAgent(
            hwnd=hwnd,
            process_name=app_info['process_name'],
            app_name=app_info['app_name'],
            host=self
        )
        self.app_agents[hwnd] = agent
        return agent


class NogicOSAppAgent:
    """应用执行器"""
    
    def __init__(self, hwnd: int, process_name: str, app_name: str, host: NogicOSHostAgent):
        self.hwnd = hwnd
        self.process_name = process_name
        self.app_name = app_name
        self.host = host
        self.state = ContinueState()
    
    async def process(self, subtask: str, context: Context):
        # 1. 截图（窗口级别）
        # 2. 调用 LLM
        # 3. 执行操作
        # 4. 验证结果
        pass
```

2. **状态机**

```python
class AgentStatus(Enum):
    IDLE = "idle"           # 空闲
    ACTIVE = "active"       # 执行中
    PENDING = "pending"     # 等待用户
    CONFIRM = "confirm"     # 等待确认
    PAUSED = "paused"       # 已暂停
    COMPLETED = "completed" # 完成
    FAILED = "failed"       # 失败
```

3. **工厂模式**

```python
class AgentFactory:
    @staticmethod
    def create_agent(agent_type: str, **kwargs):
        if agent_type == "host":
            return NogicOSHostAgent(**kwargs)
        elif agent_type == "app":
            return NogicOSAppAgent(**kwargs)
        elif agent_type == "browser":
            return BrowserAppAgent(**kwargs)  # CDP 专用
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
```

### 需要修改的部分

1. **窗口隔离**
   - UFO 使用全局输入
   - NogicOS 需要添加 `hwnd` 参数
   - 使用 PostMessage/CDP 代替物理输入

2. **截图机制**
   - UFO 全屏截图
   - NogicOS 窗口级别截图

3. **MCP 工具**
   - UFO 的 MCP 工具需要适配 NogicOS 的输入方式

### 完全不能用的部分

1. **UIA 全局输入** - `click_input`, `type_keys`
2. **Win32 backend** - UFO 已弃用
3. **复杂的 RAG 系统** - Demo 阶段不需要

---

## 参考检索索引

| 需要实现的功能 | 参考代码 | 关键类/方法 |
|--------------|---------|------------|
| 双层 Agent | `host_agent.py`, `app_agent.py` | `HostAgent`, `AppAgent` |
| 状态机 | `host_agent_state.py`, `app_agent_state.py` | `HostAgentStatus`, `AppAgentStatus` |
| Agent 工厂 | `host_agent.py` | `AgentFactory` |
| 子 Agent 创建 | `host_agent.py` | `create_subagent()` |
| MCP 工具加载 | `app_agent.py` | `_load_mcp_context()` |
| 敏感操作确认 | `app_agent.py` | `process_confirmation()` |
| 黑板通信 | `blackboard.py` | `Blackboard` |
