# Anthropic Computer Use 参考文档

> 源码地址: https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo
> 最后更新: 2025/01/07

---

## 概述

### 项目定位

Anthropic Computer Use Demo 是 Claude 官方的桌面控制演示项目，运行在 Docker 容器化的 Ubuntu 桌面环境中，通过 xdotool 执行鼠标键盘操作。

### 核心架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Anthropic Computer Use 架构                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐         ┌─────────────────┐                           │
│  │   Streamlit UI  │────────→│  Sampling Loop  │                           │
│  │   (Web 界面)     │         │   (Agent 循环)   │                           │
│  └─────────────────┘         └────────┬────────┘                           │
│                                       │                                     │
│                                       ▼                                     │
│                         ┌─────────────────────────┐                        │
│                         │     Tool Collection     │                        │
│                         │  ┌─────┐ ┌─────┐ ┌────┐ │                        │
│                         │  │Comp-│ │Bash │ │Edit│ │                        │
│                         │  │uter │ │Tool │ │Tool│ │                        │
│                         │  └──┬──┘ └──┬──┘ └──┬─┘ │                        │
│                         └─────┼───────┼───────┼───┘                        │
│                               │       │       │                             │
│                               ▼       ▼       ▼                             │
│                         ┌─────────────────────────┐                        │
│                         │     Ubuntu Desktop      │                        │
│                         │   (Docker Container)    │                        │
│                         │   xdotool, scrot, etc   │                        │
│                         └─────────────────────────┘                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 与 NogicOS 的关系

| Anthropic | NogicOS | 说明 |
|-----------|---------|------|
| Docker Ubuntu | 原生 Windows | 底层不同 |
| xdotool | koffi + Windows API | 执行层替换 |
| sampling_loop | 可借鉴 | 核心循环 |
| ComputerTool | 可借鉴 | 工具设计 |
| 坐标缩放 | 可借鉴 | DPI 处理 |

---

## 核心代码

### 1. Agent 循环 (`loop.py`)

这是 Anthropic 官方的 Agent 采样循环实现。

```python
# 源码位置: computer-use-demo/computer_use_demo/loop.py

"""
Agentic sampling loop that calls the Claude API and local implementation 
of anthropic-defined computer use tools.
"""

import platform
from collections.abc import Callable
from datetime import datetime
from enum import StrEnum
from typing import Any, cast

import httpx
from anthropic import (
    Anthropic,
    AnthropicBedrock,
    AnthropicVertex,
    APIError,
    APIResponseValidationError,
    APIStatusError,
)
from anthropic.types.beta import (
    BetaCacheControlEphemeralParam,
    BetaContentBlockParam,
    BetaImageBlockParam,
    BetaMessage,
    BetaMessageParam,
    BetaTextBlock,
    BetaTextBlockParam,
    BetaToolResultBlockParam,
    BetaToolUseBlockParam,
)

from .tools import (
    TOOL_GROUPS_BY_VERSION,
    ToolCollection,
    ToolResult,
    ToolVersion,
)

PROMPT_CACHING_BETA_FLAG = "prompt-caching-2024-07-31"


class APIProvider(StrEnum):
    ANTHROPIC = "anthropic"
    BEDROCK = "bedrock"
    VERTEX = "vertex"


# 系统提示词
SYSTEM_PROMPT = f"""<SYSTEM_CAPABILITY>
* You are utilising an Ubuntu virtual machine using {platform.machine()} architecture with internet access.
* You can feel free to install Ubuntu applications with your bash tool. Use curl instead of wget.
* To open firefox, please just click on the firefox icon. Note, firefox-esr is what is installed on your system.
* Using bash tool you can start GUI applications, but you need to set export DISPLAY=:1 and use a subshell.
* When using your bash tool with commands that are expected to output very large quantities of text, redirect into a tmp file.
* When viewing a page it can be helpful to zoom out so that you can see everything on the page.
* When using your computer function calls, they take a while to run. Where possible, try to chain multiple calls into one request.
* The current date is {datetime.today().strftime("%A, %B %-d, %Y")}.
</SYSTEM_CAPABILITY>

<IMPORTANT>
* When using Firefox, if a startup wizard appears, IGNORE IT. Do not even click "skip this step".
* If the item you are looking at is a pdf, use curl to download and pdftotext to convert.
</IMPORTANT>"""


async def sampling_loop(
    *,
    model: str,
    provider: APIProvider,
    system_prompt_suffix: str,
    messages: list[BetaMessageParam],
    output_callback: Callable[[BetaContentBlockParam], None],
    tool_output_callback: Callable[[ToolResult, str], None],
    api_response_callback: Callable[
        [httpx.Request, httpx.Response | object | None, Exception | None], None
    ],
    api_key: str,
    only_n_most_recent_images: int | None = None,
    max_tokens: int = 4096,
    tool_version: ToolVersion,
    thinking_budget: int | None = None,
    token_efficient_tools_beta: bool = False,
):
    """
    ========================================
    核心方法: sampling_loop
    ========================================
    Agent 采样循环，用于 assistant/tool 交互
    
    流程：
    1. 初始化工具集合
    2. 构建系统提示
    3. 循环调用 Claude API
    4. 解析响应，执行工具
    5. 将工具结果添加到消息
    6. 重复直到没有工具调用
    """
    # 初始化工具集合
    tool_group = TOOL_GROUPS_BY_VERSION[tool_version]
    tool_collection = ToolCollection(*(ToolCls() for ToolCls in tool_group.tools))
    
    # 构建系统提示
    system = BetaTextBlockParam(
        type="text",
        text=f"{SYSTEM_PROMPT}{' ' + system_prompt_suffix if system_prompt_suffix else ''}",
    )

    # 主循环
    while True:
        enable_prompt_caching = False
        betas = [tool_group.beta_flag] if tool_group.beta_flag else []
        
        if token_efficient_tools_beta:
            betas.append("token-efficient-tools-2025-02-19")
        
        image_truncation_threshold = only_n_most_recent_images or 0
        
        # 根据 provider 初始化客户端
        if provider == APIProvider.ANTHROPIC:
            client = Anthropic(api_key=api_key, max_retries=4)
            enable_prompt_caching = True
        elif provider == APIProvider.VERTEX:
            client = AnthropicVertex()
        elif provider == APIProvider.BEDROCK:
            client = AnthropicBedrock()

        # Prompt Caching 设置
        if enable_prompt_caching:
            betas.append(PROMPT_CACHING_BETA_FLAG)
            _inject_prompt_caching(messages)
            only_n_most_recent_images = 0
            system["cache_control"] = {"type": "ephemeral"}

        # 图片截断（保留最近 N 张）
        if only_n_most_recent_images:
            _maybe_filter_to_n_most_recent_images(
                messages,
                only_n_most_recent_images,
                min_removal_threshold=image_truncation_threshold,
            )
        
        # Thinking 模式
        extra_body = {}
        if thinking_budget:
            extra_body = {
                "thinking": {"type": "enabled", "budget_tokens": thinking_budget}
            }

        # ========== 调用 Claude API ==========
        try:
            raw_response = client.beta.messages.with_raw_response.create(
                max_tokens=max_tokens,
                messages=messages,
                model=model,
                system=[system],
                tools=tool_collection.to_params(),
                betas=betas,
                extra_body=extra_body,
            )
        except (APIStatusError, APIResponseValidationError) as e:
            api_response_callback(e.request, e.response, e)
            return messages
        except APIError as e:
            api_response_callback(e.request, e.body, e)
            return messages

        api_response_callback(
            raw_response.http_response.request, raw_response.http_response, None
        )

        response = raw_response.parse()

        # ========== 解析响应 ==========
        response_params = _response_to_params(response)
        messages.append({
            "role": "assistant",
            "content": response_params,
        })

        # ========== 执行工具调用 ==========
        tool_result_content: list[BetaToolResultBlockParam] = []
        for content_block in response_params:
            output_callback(content_block)
            
            if (
                isinstance(content_block, dict)
                and content_block.get("type") == "tool_use"
            ):
                # 类型收窄
                tool_use_block = cast(BetaToolUseBlockParam, content_block)
                
                # 执行工具
                result = await tool_collection.run(
                    name=tool_use_block["name"],
                    tool_input=cast(dict[str, Any], tool_use_block.get("input", {})),
                )
                
                # 构建工具结果
                tool_result_content.append(
                    _make_api_tool_result(result, tool_use_block["id"])
                )
                tool_output_callback(result, tool_use_block["id"])

        # ========== 循环终止条件 ==========
        # 如果没有工具调用，结束循环
        if not tool_result_content:
            return messages

        # 将工具结果添加到消息
        messages.append({"content": tool_result_content, "role": "user"})


def _make_api_tool_result(
    result: ToolResult, tool_use_id: str
) -> BetaToolResultBlockParam:
    """
    将 ToolResult 转换为 API 格式的 ToolResultBlockParam
    """
    tool_result_content: list[BetaTextBlockParam | BetaImageBlockParam] | str = []
    is_error = False
    
    if result.error:
        is_error = True
        tool_result_content = _maybe_prepend_system_tool_result(result, result.error)
    else:
        if result.output:
            tool_result_content.append({
                "type": "text",
                "text": _maybe_prepend_system_tool_result(result, result.output),
            })
        if result.base64_image:
            tool_result_content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": result.base64_image,
                },
            })
    
    return {
        "type": "tool_result",
        "content": tool_result_content,
        "tool_use_id": tool_use_id,
        "is_error": is_error,
    }
```

#### 关键点说明

1. **循环终止条件**: 当 Claude 不再调用任何工具时，循环结束
2. **图片管理**: `only_n_most_recent_images` 控制保留的截图数量
3. **Prompt Caching**: 启用缓存减少 API 成本
4. **多 Provider 支持**: Anthropic、Vertex、Bedrock
5. **Thinking 模式**: 支持 Claude 的思考 token

---

### 2. ComputerTool (`computer.py`)

这是 Anthropic 定义的 Computer Use 工具实现。

```python
# 源码位置: computer-use-demo/computer_use_demo/tools/computer.py

import asyncio
import base64
import os
import shlex
import shutil
from enum import StrEnum
from pathlib import Path
from typing import Literal, TypedDict, cast, get_args
from uuid import uuid4

from anthropic.types.beta import BetaToolComputerUse20241022Param, BetaToolUnionParam

from .base import BaseAnthropicTool, ToolError, ToolResult
from .run import run

OUTPUT_DIR = "/tmp/outputs"

TYPING_DELAY_MS = 12
TYPING_GROUP_SIZE = 50

# 支持的操作（2024.10.22 版本）
Action_20241022 = Literal[
    "key",              # 按键
    "type",             # 输入文字
    "mouse_move",       # 移动鼠标
    "left_click",       # 左键点击
    "left_click_drag",  # 左键拖拽
    "right_click",      # 右键点击
    "middle_click",     # 中键点击
    "double_click",     # 双击
    "screenshot",       # 截图
    "cursor_position",  # 获取光标位置
]

# 支持的操作（2025.01.24 版本，增加更多）
Action_20250124 = (
    Action_20241022
    | Literal[
        "left_mouse_down",  # 鼠标按下
        "left_mouse_up",    # 鼠标抬起
        "scroll",           # 滚动
        "hold_key",         # 长按按键
        "wait",             # 等待
        "triple_click",     # 三击
    ]
)

ScrollDirection = Literal["up", "down", "left", "right"]


class Resolution(TypedDict):
    width: int
    height: int


# 最大缩放目标（超过这个分辨率会缩小）
MAX_SCALING_TARGETS: dict[str, Resolution] = {
    "XGA": Resolution(width=1024, height=768),    # 4:3
    "WXGA": Resolution(width=1280, height=800),   # 16:10
    "FWXGA": Resolution(width=1366, height=768),  # ~16:9
}

# 鼠标按钮映射
CLICK_BUTTONS = {
    "left_click": 1,
    "right_click": 3,
    "middle_click": 2,
    "double_click": "--repeat 2 --delay 10 1",
    "triple_click": "--repeat 3 --delay 10 1",
}


class ScalingSource(StrEnum):
    COMPUTER = "computer"  # 屏幕 → API
    API = "api"            # API → 屏幕


class ComputerToolOptions(TypedDict):
    display_height_px: int
    display_width_px: int
    display_number: int | None


class BaseComputerTool:
    """
    允许 Agent 与屏幕、键盘、鼠标交互的工具
    参数由 Anthropic 定义，不可编辑
    """

    name: Literal["computer"] = "computer"
    width: int
    height: int
    display_num: int | None

    _screenshot_delay = 2.0      # 截图前等待时间
    _scaling_enabled = True       # 是否启用坐标缩放

    @property
    def options(self) -> ComputerToolOptions:
        """获取工具选项（会自动缩放分辨率）"""
        width, height = self.scale_coordinates(
            ScalingSource.COMPUTER, self.width, self.height
        )
        return {
            "display_width_px": width,
            "display_height_px": height,
            "display_number": self.display_num,
        }

    def __init__(self):
        super().__init__()

        self.width = int(os.getenv("WIDTH") or 0)
        self.height = int(os.getenv("HEIGHT") or 0)
        assert self.width and self.height, "WIDTH, HEIGHT must be set"
        
        if (display_num := os.getenv("DISPLAY_NUM")) is not None:
            self.display_num = int(display_num)
            self._display_prefix = f"DISPLAY=:{self.display_num} "
        else:
            self.display_num = None
            self._display_prefix = ""

        self.xdotool = f"{self._display_prefix}xdotool"

    async def __call__(
        self,
        *,
        action: Action_20241022,
        text: str | None = None,
        coordinate: tuple[int, int] | None = None,
        start_coordinate: tuple[int, int] | None = None,
        **kwargs,
    ):
        """
        ========================================
        核心方法: __call__
        ========================================
        根据 action 类型执行不同操作
        """
        
        # ---------- 鼠标移动和拖拽 ----------
        if action in ("mouse_move", "left_click_drag"):
            if coordinate is None:
                raise ToolError(f"coordinate is required for {action}")
            if text is not None:
                raise ToolError(f"text is not accepted for {action}")

            if action == "left_click_drag":
                if start_coordinate is None:
                    raise ToolError(f"start_coordinate is required for {action}")
                start_x, start_y = self.validate_and_get_coordinates(start_coordinate)
                end_x, end_y = self.validate_and_get_coordinates(coordinate)
                command_parts = [
                    self.xdotool,
                    f"mousemove --sync {start_x} {start_y} mousedown 1 "
                    f"mousemove --sync {end_x} {end_y} mouseup 1",
                ]
                return await self.shell(" ".join(command_parts))
            
            elif action == "mouse_move":
                x, y = self.validate_and_get_coordinates(coordinate)
                command_parts = [self.xdotool, f"mousemove --sync {x} {y}"]
                return await self.shell(" ".join(command_parts))

        # ---------- 键盘操作 ----------
        if action in ("key", "type"):
            if text is None:
                raise ToolError(f"text is required for {action}")
            if coordinate is not None:
                raise ToolError(f"coordinate is not accepted for {action}")
            if not isinstance(text, str):
                raise ToolError(output=f"{text} must be a string")

            if action == "key":
                # 按键（如 Return, ctrl+c）
                command_parts = [self.xdotool, f"key -- {text}"]
                return await self.shell(" ".join(command_parts))
            
            elif action == "type":
                # 输入文字（分块处理）
                results: list[ToolResult] = []
                for chunk in chunks(text, TYPING_GROUP_SIZE):
                    command_parts = [
                        self.xdotool,
                        f"type --delay {TYPING_DELAY_MS} -- {shlex.quote(chunk)}",
                    ]
                    results.append(
                        await self.shell(" ".join(command_parts), take_screenshot=False)
                    )
                screenshot_base64 = (await self.screenshot()).base64_image
                return ToolResult(
                    output="".join(result.output or "" for result in results),
                    error="".join(result.error or "" for result in results),
                    base64_image=screenshot_base64,
                )

        # ---------- 点击和截图 ----------
        if action in (
            "left_click",
            "right_click",
            "double_click",
            "middle_click",
            "screenshot",
            "cursor_position",
        ):
            if text is not None:
                raise ToolError(f"text is not accepted for {action}")
            if coordinate is not None:
                raise ToolError(f"coordinate is not accepted for {action}")

            if action == "screenshot":
                return await self.screenshot()
            
            elif action == "cursor_position":
                command_parts = [self.xdotool, "getmouselocation --shell"]
                result = await self.shell(
                    " ".join(command_parts),
                    take_screenshot=False,
                )
                output = result.output or ""
                x, y = self.scale_coordinates(
                    ScalingSource.COMPUTER,
                    int(output.split("X=")[1].split("\n")[0]),
                    int(output.split("Y=")[1].split("\n")[0]),
                )
                return result.replace(output=f"X={x},Y={y}")
            
            else:
                # 点击
                command_parts = [self.xdotool, f"click {CLICK_BUTTONS[action]}"]
                return await self.shell(" ".join(command_parts))

        raise ToolError(f"Invalid action: {action}")

    def validate_and_get_coordinates(
        self, coordinate: tuple[int, int] | None = None
    ):
        """验证并转换坐标"""
        if not isinstance(coordinate, list) or len(coordinate) != 2:
            raise ToolError(f"{coordinate} must be a tuple of length 2")
        if not all(isinstance(i, int) and i >= 0 for i in coordinate):
            raise ToolError(f"{coordinate} must be a tuple of non-negative ints")

        return self.scale_coordinates(ScalingSource.API, coordinate[0], coordinate[1])

    async def screenshot(self):
        """截图并返回 base64 编码的图片"""
        output_dir = Path(OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / f"screenshot_{uuid4().hex}.png"

        # 优先使用 gnome-screenshot，回退到 scrot
        if shutil.which("gnome-screenshot"):
            screenshot_cmd = f"{self._display_prefix}gnome-screenshot -f {path} -p"
        else:
            screenshot_cmd = f"{self._display_prefix}scrot -p {path}"

        result = await self.shell(screenshot_cmd, take_screenshot=False)
        
        # 如果启用缩放，缩小图片
        if self._scaling_enabled:
            x, y = self.scale_coordinates(
                ScalingSource.COMPUTER, self.width, self.height
            )
            await self.shell(
                f"convert {path} -resize {x}x{y}! {path}", take_screenshot=False
            )

        if path.exists():
            return result.replace(
                base64_image=base64.b64encode(path.read_bytes()).decode()
            )
        raise ToolError(f"Failed to take screenshot: {result.error}")

    async def shell(self, command: str, take_screenshot=True) -> ToolResult:
        """执行 shell 命令并返回结果"""
        _, stdout, stderr = await run(command)
        base64_image = None

        if take_screenshot:
            # 等待 UI 稳定后截图
            await asyncio.sleep(self._screenshot_delay)
            base64_image = (await self.screenshot()).base64_image

        return ToolResult(output=stdout, error=stderr, base64_image=base64_image)

    def scale_coordinates(self, source: ScalingSource, x: int, y: int):
        """
        ========================================
        坐标缩放
        ========================================
        将坐标在屏幕空间和 API 空间之间转换
        """
        if not self._scaling_enabled:
            return x, y
        
        ratio = self.width / self.height
        target_dimension = None
        
        for dimension in MAX_SCALING_TARGETS.values():
            # 允许一些宽高比误差
            if abs(dimension["width"] / dimension["height"] - ratio) < 0.02:
                if dimension["width"] < self.width:
                    target_dimension = dimension
                break
        
        if target_dimension is None:
            return x, y
        
        # 缩放因子（应该 < 1）
        x_scaling_factor = target_dimension["width"] / self.width
        y_scaling_factor = target_dimension["height"] / self.height
        
        if source == ScalingSource.API:
            # API → 屏幕：放大
            if x > self.width or y > self.height:
                raise ToolError(f"Coordinates {x}, {y} are out of bounds")
            return round(x / x_scaling_factor), round(y / y_scaling_factor)
        
        # 屏幕 → API：缩小
        return round(x * x_scaling_factor), round(y * y_scaling_factor)
```

#### 关键点说明

1. **xdotool**: Linux 下的鼠标键盘模拟工具
2. **坐标缩放**: 自动将大分辨率缩放到标准分辨率
3. **截图延迟**: 操作后等待 2 秒让 UI 稳定
4. **分块输入**: 长文本分成 50 字符的块输入
5. **多种操作**: 支持点击、拖拽、输入、截图等

---

### 3. ToolResult 和 ToolCollection

```python
# 源码位置: computer-use-demo/computer_use_demo/tools/base.py

from dataclasses import dataclass, field, replace
from typing import Any

from anthropic.types.beta import BetaToolUnionParam


class ToolError(Exception):
    """工具执行错误"""
    def __init__(self, message: str):
        self.message = message


@dataclass(kw_only=True, frozen=True)
class ToolResult:
    """
    工具执行结果
    """
    output: str | None = None       # 文本输出
    error: str | None = None        # 错误信息
    base64_image: str | None = None # 截图（base64）
    system: str | None = None       # 系统信息

    def __bool__(self):
        return any([self.output, self.error, self.base64_image])

    def replace(self, **kwargs):
        """创建一个新的 ToolResult，替换指定字段"""
        return replace(self, **kwargs)


class BaseAnthropicTool:
    """Anthropic 工具基类"""
    
    name: str
    api_type: str

    def to_params(self) -> BetaToolUnionParam:
        """转换为 API 参数"""
        raise NotImplementedError

    async def __call__(self, **kwargs) -> ToolResult:
        """执行工具"""
        raise NotImplementedError


@dataclass
class ToolCollection:
    """
    工具集合，用于管理和执行多个工具
    """
    tools: tuple[BaseAnthropicTool, ...] = field(default_factory=tuple)

    def __init__(self, *tools: BaseAnthropicTool):
        self.tools = tools
        self._tools_map = {tool.name: tool for tool in tools}

    def to_params(self) -> list[BetaToolUnionParam]:
        """转换为 API 参数列表"""
        return [tool.to_params() for tool in self.tools]

    async def run(self, *, name: str, tool_input: dict[str, Any]) -> ToolResult:
        """
        根据名称执行工具
        """
        tool = self._tools_map.get(name)
        if tool is None:
            return ToolResult(error=f"Tool {name} not found")
        
        try:
            return await tool(**tool_input)
        except ToolError as e:
            return ToolResult(error=e.message)
```

---

## 架构分析

### 优点

1. **简洁清晰**: 代码结构简单，易于理解
2. **官方标准**: Anthropic 定义的标准工具格式
3. **坐标缩放**: 内置 DPI 处理
4. **操作丰富**: 支持多种鼠标键盘操作
5. **自动截图**: 每次操作后自动截图

### 限制

1. **Linux Only**: 依赖 xdotool、gnome-screenshot
2. **全局输入**: 没有窗口隔离
3. **固定延迟**: 2 秒截图延迟可能太长
4. **单线程**: 不支持并行操作

### 我们可以借鉴什么

| 模块 | 借鉴程度 | 说明 |
|------|---------|------|
| sampling_loop | 完全借鉴 | 循环结构 |
| ToolResult | 完全借鉴 | 结果格式 |
| 坐标缩放 | 完全借鉴 | DPI 处理 |
| Action 枚举 | 部分借鉴 | 需要增加 hwnd |
| xdotool | 不借鉴 | 用 Windows API |

---

## NogicOS 适配建议

### 可以直接复用的部分

1. **ToolResult 结构**

```python
# NogicOS 实现
@dataclass(kw_only=True, frozen=True)
class ToolResult:
    output: str | None = None
    error: str | None = None
    base64_image: str | None = None
    hwnd: int | None = None  # 新增：目标窗口
    
    def __bool__(self):
        return any([self.output, self.error, self.base64_image])
```

2. **Agent 循环结构**

```python
async def sampling_loop(
    messages: list[dict],
    tools: ToolCollection,
    model: str = "claude-sonnet-4-20250514",
) -> list[dict]:
    """NogicOS Agent 采样循环"""
    
    while True:
        # 调用 Claude
        response = await client.messages.create(
            model=model,
            messages=messages,
            tools=tools.to_params(),
        )
        
        messages.append({"role": "assistant", "content": response.content})
        
        # 执行工具
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = await tools.run(
                    name=block.name,
                    tool_input=block.input
                )
                tool_results.append(_make_tool_result(result, block.id))
        
        # 如果没有工具调用，结束
        if not tool_results:
            return messages
        
        messages.append({"role": "user", "content": tool_results})
```

3. **坐标缩放**

```python
def scale_coordinates(
    source: str, 
    x: int, 
    y: int, 
    window_width: int, 
    window_height: int,
    target_width: int = 1280,
    target_height: int = 800,
) -> tuple[int, int]:
    """坐标缩放（窗口级别）"""
    x_factor = target_width / window_width
    y_factor = target_height / window_height
    
    if source == "api":
        # API → 窗口：放大
        return round(x / x_factor), round(y / y_factor)
    else:
        # 窗口 → API：缩小
        return round(x * x_factor), round(y * y_factor)
```

### 需要修改的部分

1. **窗口级操作**

```python
# Anthropic 原版（全局）
async def __call__(self, *, action: str, coordinate: tuple[int, int] | None = None):
    if action == "left_click":
        # 全局点击
        await self.shell(f"xdotool click 1")

# NogicOS 版本（窗口隔离）
async def __call__(
    self, 
    *, 
    action: str, 
    hwnd: int,  # 新增：目标窗口
    coordinate: tuple[int, int] | None = None
):
    if action == "left_click":
        # 窗口级点击
        await click_in_window(hwnd, coordinate[0], coordinate[1])
```

2. **截图机制**

```python
# Anthropic 原版（全屏）
async def screenshot(self):
    await run("gnome-screenshot -f /tmp/screenshot.png")

# NogicOS 版本（窗口级）
async def screenshot(self, hwnd: int):
    return await capture_window(hwnd)
```

### 完全不能用的部分

1. **xdotool** - Linux Only
2. **gnome-screenshot** - Linux Only
3. **全局输入** - 需要窗口隔离

---

## 参考检索索引

| 需要实现的功能 | 参考代码 | 关键函数/类 |
|--------------|---------|------------|
| Agent 循环 | `loop.py` | `sampling_loop()` |
| 工具集合 | `base.py` | `ToolCollection` |
| 工具结果 | `base.py` | `ToolResult` |
| 计算机工具 | `computer.py` | `ComputerTool20241022` |
| 坐标缩放 | `computer.py` | `scale_coordinates()` |
| 操作类型 | `computer.py` | `Action_20241022` |
| 截图 | `computer.py` | `screenshot()` |
| 输入文字 | `computer.py` | `type` action |
