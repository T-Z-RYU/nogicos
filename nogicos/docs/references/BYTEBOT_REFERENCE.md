# ByteBot 参考文档

> 源码地址: https://github.com/bytebot-ai/bytebot
> 最后更新: 2025/01/07

---

## 概述

### 项目定位

ByteBot 是一个 AI 驱动的桌面自动化系统，运行在虚拟 Ubuntu 桌面环境中，通过 LLM 理解用户指令并执行桌面操作。

### 核心架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ByteBot 架构                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐       │
│  │  Web Interface  │────→│  Agent Service  │────→│ Desktop Container│       │
│  │   (Next.js)     │     │   (NestJS)      │     │  (Ubuntu + XFCE) │       │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘       │
│         │                        │                        │                 │
│         │                        │                        │                 │
│         ▼                        ▼                        ▼                 │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐       │
│  │   Task Queue    │     │  LLM Provider   │     │    bytebotd     │       │
│  │  (PostgreSQL)   │     │ (Claude/GPT/etc)│     │  (nut-tree/js)  │       │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 与 NogicOS 的关系

| ByteBot | NogicOS | 说明 |
|---------|---------|------|
| 虚拟 Linux 环境 | 原生 Windows 环境 | 底层执行完全不同 |
| Agent 循环 | 可借鉴 | 核心逻辑可复用 |
| 工具定义规范 | 可借鉴 | Tool Schema 可复用 |
| System Prompt | 可借鉴 | 需要适配 Windows |
| bytebotd (nut-tree) | 需要替换 | 用 koffi + Windows API |

---

## 核心代码

### 1. Agent 主循环 (`agent.processor.ts`)

这是 ByteBot 最核心的代码，定义了 Agent 如何处理任务。

```typescript
// 源码位置: packages/bytebot-agent/src/agent/agent.processor.ts

import { TasksService } from '../tasks/tasks.service';
import { MessagesService } from '../messages/messages.service';
import { Injectable, Logger } from '@nestjs/common';
import {
  Message,
  Role,
  Task,
  TaskPriority,
  TaskStatus,
  TaskType,
} from '@prisma/client';
import { AnthropicService } from '../anthropic/anthropic.service';
import {
  isComputerToolUseContentBlock,
  isSetTaskStatusToolUseBlock,
  isCreateTaskToolUseBlock,
  SetTaskStatusToolUseBlock,
} from '@bytebot/shared';

import {
  MessageContentBlock,
  MessageContentType,
  ToolResultContentBlock,
  TextContentBlock,
} from '@bytebot/shared';
import { InputCaptureService } from './input-capture.service';
import { OnEvent } from '@nestjs/event-emitter';
import { OpenAIService } from '../openai/openai.service';
import { GoogleService } from '../google/google.service';
import {
  BytebotAgentModel,
  BytebotAgentService,
  BytebotAgentResponse,
} from './agent.types';
import {
  AGENT_SYSTEM_PROMPT,
  SUMMARIZATION_SYSTEM_PROMPT,
} from './agent.constants';
import { SummariesService } from '../summaries/summaries.service';
import { handleComputerToolUse } from './agent.computer-use';
import { ProxyService } from '../proxy/proxy.service';

@Injectable()
export class AgentProcessor {
  private readonly logger = new Logger(AgentProcessor.name);
  private currentTaskId: string | null = null;
  private isProcessing = false;
  private abortController: AbortController | null = null;
  private services: Record<string, BytebotAgentService> = {};

  constructor(
    private readonly tasksService: TasksService,
    private readonly messagesService: MessagesService,
    private readonly summariesService: SummariesService,
    private readonly anthropicService: AnthropicService,
    private readonly openaiService: OpenAIService,
    private readonly googleService: GoogleService,
    private readonly proxyService: ProxyService,
    private readonly inputCaptureService: InputCaptureService,
  ) {
    this.services = {
      anthropic: this.anthropicService,
      openai: this.openaiService,
      google: this.googleService,
      proxy: this.proxyService,
    };
    this.logger.log('AgentProcessor initialized');
  }

  /**
   * Check if the processor is currently processing a task
   */
  isRunning(): boolean {
    return this.isProcessing;
  }

  /**
   * Get the current task ID being processed
   */
  getCurrentTaskId(): string | null {
    return this.currentTaskId;
  }

  @OnEvent('task.takeover')
  handleTaskTakeover({ taskId }: { taskId: string }) {
    this.logger.log(`Task takeover event received for task ID: ${taskId}`);

    // If the agent is still processing this task, abort any in-flight operations
    if (this.currentTaskId === taskId && this.isProcessing) {
      this.abortController?.abort();
    }

    // Always start capturing user input so that emitted actions are received
    this.inputCaptureService.start(taskId);
  }

  @OnEvent('task.resume')
  handleTaskResume({ taskId }: { taskId: string }) {
    if (this.currentTaskId === taskId && this.isProcessing) {
      this.logger.log(`Task resume event received for task ID: ${taskId}`);
      this.abortController = new AbortController();

      void this.runIteration(taskId);
    }
  }

  @OnEvent('task.cancel')
  async handleTaskCancel({ taskId }: { taskId: string }) {
    this.logger.log(`Task cancel event received for task ID: ${taskId}`);

    await this.stopProcessing();
  }

  processTask(taskId: string) {
    this.logger.log(`Starting processing for task ID: ${taskId}`);

    if (this.isProcessing) {
      this.logger.warn('AgentProcessor is already processing another task');
      return;
    }

    this.isProcessing = true;
    this.currentTaskId = taskId;
    this.abortController = new AbortController();

    // Kick off the first iteration without blocking the caller
    void this.runIteration(taskId);
  }

  /**
   * ========================================
   * 核心方法: runIteration
   * ========================================
   * 这是 Agent 的主循环，每次迭代：
   * 1. 获取任务状态
   * 2. 构建上下文（历史消息 + 摘要）
   * 3. 调用 LLM 获取下一步操作
   * 4. 执行工具调用
   * 5. 保存结果
   * 6. 调度下一次迭代
   */
  private async runIteration(taskId: string): Promise<void> {
    if (!this.isProcessing) {
      return;
    }

    try {
      // 1. 获取任务状态
      const task: Task = await this.tasksService.findById(taskId);

      if (task.status !== TaskStatus.RUNNING) {
        this.logger.log(
          `Task processing completed for task ID: ${taskId} with status: ${task.status}`,
        );
        this.isProcessing = false;
        this.currentTaskId = null;
        return;
      }

      this.logger.log(`Processing iteration for task ID: ${taskId}`);

      // 刷新 abort controller
      this.abortController = new AbortController();

      // 2. 构建上下文：最新摘要 + 未摘要的消息
      const latestSummary = await this.summariesService.findLatest(taskId);
      const unsummarizedMessages =
        await this.messagesService.findUnsummarized(taskId);
      const messages = [
        ...(latestSummary
          ? [
              {
                id: '',
                createdAt: new Date(),
                updatedAt: new Date(),
                taskId,
                summaryId: null,
                role: Role.USER,
                content: [
                  {
                    type: MessageContentType.Text,
                    text: latestSummary.content,
                  },
                ],
              },
            ]
          : []),
        ...unsummarizedMessages,
      ];
      this.logger.debug(
        `Sending ${messages.length} messages to LLM for processing`,
      );

      // 3. 调用 LLM
      const model = task.model as unknown as BytebotAgentModel;
      let agentResponse: BytebotAgentResponse;

      const service = this.services[model.provider];
      if (!service) {
        this.logger.warn(
          `No service found for model provider: ${model.provider}`,
        );
        await this.tasksService.update(taskId, {
          status: TaskStatus.FAILED,
        });
        this.isProcessing = false;
        this.currentTaskId = null;
        return;
      }

      agentResponse = await service.generateMessage(
        AGENT_SYSTEM_PROMPT,
        messages,
        model.name,
        true,
        this.abortController.signal,
      );

      const messageContentBlocks = agentResponse.contentBlocks;

      this.logger.debug(
        `Received ${messageContentBlocks.length} content blocks from LLM`,
      );

      if (messageContentBlocks.length === 0) {
        this.logger.warn(
          `Task ID: ${taskId} received no content blocks from LLM, marking as failed`,
        );
        await this.tasksService.update(taskId, {
          status: TaskStatus.FAILED,
        });
        this.isProcessing = false;
        this.currentTaskId = null;
        return;
      }

      // 4. 保存 LLM 响应
      await this.messagesService.create({
        content: messageContentBlocks,
        role: Role.ASSISTANT,
        taskId,
      });

      // 5. 检查是否需要摘要（Token 使用超过 75%）
      const contextWindow = model.contextWindow || 200000;
      const contextThreshold = contextWindow * 0.75;
      const shouldSummarize =
        agentResponse.tokenUsage.totalTokens >= contextThreshold;

      if (shouldSummarize) {
        // ... 摘要逻辑 ...
      }

      // 6. 执行工具调用
      const generatedToolResults: ToolResultContentBlock[] = [];
      let setTaskStatusToolUseBlock: SetTaskStatusToolUseBlock | null = null;

      for (const block of messageContentBlocks) {
        // 处理 Computer Tool 调用
        if (isComputerToolUseContentBlock(block)) {
          const result = await handleComputerToolUse(block, this.logger);
          generatedToolResults.push(result);
        }

        // 处理创建子任务
        if (isCreateTaskToolUseBlock(block)) {
          const type = block.input.type?.toUpperCase() as TaskType;
          const priority = block.input.priority?.toUpperCase() as TaskPriority;

          await this.tasksService.create({
            description: block.input.description,
            type,
            createdBy: Role.ASSISTANT,
            ...(block.input.scheduledFor && {
              scheduledFor: new Date(block.input.scheduledFor),
            }),
            model: task.model,
            priority,
          });

          generatedToolResults.push({
            type: MessageContentType.ToolResult,
            tool_use_id: block.id,
            content: [
              {
                type: MessageContentType.Text,
                text: 'The task has been created',
              },
            ],
          });
        }

        // 处理设置任务状态
        if (isSetTaskStatusToolUseBlock(block)) {
          setTaskStatusToolUseBlock = block;

          generatedToolResults.push({
            type: MessageContentType.ToolResult,
            tool_use_id: block.id,
            is_error: block.input.status === 'failed',
            content: [
              {
                type: MessageContentType.Text,
                text: block.input.description,
              },
            ],
          });
        }
      }

      // 7. 保存工具执行结果
      if (generatedToolResults.length > 0) {
        await this.messagesService.create({
          content: generatedToolResults,
          role: Role.USER,
          taskId,
        });
      }

      // 8. 更新任务状态
      if (setTaskStatusToolUseBlock) {
        switch (setTaskStatusToolUseBlock.input.status) {
          case 'completed':
            await this.tasksService.update(taskId, {
              status: TaskStatus.COMPLETED,
              completedAt: new Date(),
            });
            break;
          case 'needs_help':
            await this.tasksService.update(taskId, {
              status: TaskStatus.NEEDS_HELP,
            });
            break;
        }
      }

      // 9. 调度下一次迭代
      if (this.isProcessing) {
        setImmediate(() => this.runIteration(taskId));
      }
    } catch (error: any) {
      if (error?.name === 'BytebotAgentInterrupt') {
        this.logger.warn(`Processing aborted for task ID: ${taskId}`);
      } else {
        this.logger.error(
          `Error during task processing iteration for task ID: ${taskId} - ${error.message}`,
          error.stack,
        );
        await this.tasksService.update(taskId, {
          status: TaskStatus.FAILED,
        });
        this.isProcessing = false;
        this.currentTaskId = null;
      }
    }
  }

  async stopProcessing(): Promise<void> {
    if (!this.isProcessing) {
      return;
    }

    this.logger.log(`Stopping execution of task ${this.currentTaskId}`);

    // Signal any in-flight async operations to abort
    this.abortController?.abort();

    await this.inputCaptureService.stop();

    this.isProcessing = false;
    this.currentTaskId = null;
  }
}
```

#### 关键点说明

1. **状态管理**: `isProcessing`, `currentTaskId`, `abortController`
2. **事件驱动**: 使用 `@OnEvent` 装饰器处理 takeover/resume/cancel
3. **异步迭代**: 使用 `setImmediate` 非阻塞调度下一次迭代
4. **上下文压缩**: Token 超过 75% 时自动生成摘要
5. **多 LLM 支持**: 通过 `services` Map 支持 Anthropic/OpenAI/Google

---

### 2. 工具定义 (`agent.tools.ts`)

```typescript
// 源码位置: packages/bytebot-agent/src/agent/agent.tools.ts

/**
 * Common schema definitions for reuse
 */
const coordinateSchema = {
  type: 'object' as const,
  properties: {
    x: {
      type: 'number' as const,
      description: 'The x-coordinate',
    },
    y: {
      type: 'number' as const,
      description: 'The y-coordinate',
    },
  },
  required: ['x', 'y'],
};

const holdKeysSchema = {
  type: 'array' as const,
  items: { type: 'string' as const },
  description: 'Optional array of keys to hold during the action',
  nullable: true,
};

const buttonSchema = {
  type: 'string' as const,
  enum: ['left', 'right', 'middle'],
  description: 'The mouse button',
};

/**
 * Tool definitions for mouse actions
 */
export const _moveMouseTool = {
  name: 'computer_move_mouse',
  description: 'Moves the mouse cursor to the specified coordinates',
  input_schema: {
    type: 'object' as const,
    properties: {
      coordinates: {
        ...coordinateSchema,
        description: 'Target coordinates for mouse movement',
      },
    },
    required: ['coordinates'],
  },
};

export const _clickMouseTool = {
  name: 'computer_click_mouse',
  description:
    'Performs a mouse click at the specified coordinates or current position',
  input_schema: {
    type: 'object' as const,
    properties: {
      coordinates: {
        ...coordinateSchema,
        description:
          'Optional click coordinates (defaults to current position)',
        nullable: true,
      },
      button: buttonSchema,
      holdKeys: holdKeysSchema,
      clickCount: {
        type: 'integer' as const,
        description: 'Number of clicks to perform (e.g., 2 for double-click)',
        default: 1,
      },
    },
    required: ['button', 'clickCount'],
  },
};

export const _typeTextTool = {
  name: 'computer_type_text',
  description:
    'Types a string of text character by character. Use this tool for strings less than 25 characters, or passwords/sensitive form fields.',
  input_schema: {
    type: 'object' as const,
    properties: {
      text: {
        type: 'string' as const,
        description: 'The text string to type',
      },
      delay: {
        type: 'number' as const,
        description: 'Optional delay in milliseconds between characters',
        nullable: true,
      },
      isSensitive: {
        type: 'boolean' as const,
        description: 'Flag to indicate sensitive information',
        nullable: true,
      },
    },
    required: ['text'],
  },
};

export const _screenshotTool = {
  name: 'computer_screenshot',
  description: 'Captures a screenshot of the current screen',
  input_schema: {
    type: 'object' as const,
    properties: {},
  },
};

export const _setTaskStatusTool = {
  name: 'set_task_status',
  description: 'Sets the status of the current task',
  input_schema: {
    type: 'object' as const,
    properties: {
      status: {
        type: 'string' as const,
        enum: ['completed', 'needs_help'],
        description: 'The status of the task',
      },
      description: {
        type: 'string' as const,
        description:
          'If the task is completed, a summary of the task. If the task needs help, a description of the issue or clarification needed.',
      },
    },
    required: ['status', 'description'],
  },
};

/**
 * Export all tools as an array
 */
export const agentTools = [
  _moveMouseTool,
  _traceMouseTool,
  _clickMouseTool,
  _pressMouseTool,
  _dragMouseTool,
  _scrollTool,
  _typeKeysTool,
  _pressKeysTool,
  _typeTextTool,
  _pasteTextTool,
  _waitTool,
  _screenshotTool,
  _applicationTool,
  _cursorPositionTool,
  _setTaskStatusTool,
  _createTaskTool,
  _readFileTool,
];
```

#### 关键点说明

1. **Schema 复用**: `coordinateSchema`, `holdKeysSchema`, `buttonSchema`
2. **17 个工具**: 鼠标(6) + 键盘(4) + 实用(4) + 任务(3)
3. **敏感信息标记**: `isSensitive` 字段

---

### 3. System Prompt (`agent.constants.ts`)

```typescript
// 源码位置: packages/bytebot-agent/src/agent/agent.constants.ts

export const AGENT_SYSTEM_PROMPT = `
You are **Bytebot**, a highly-reliable AI engineer operating a virtual computer whose display measures 1280 x 960 pixels.

────────────────────────
CORE WORKING PRINCIPLES
────────────────────────
1. **Observe First** - *Always* invoke \`computer_screenshot\` before your first action **and** whenever the UI may have changed.
2. **Navigate applications** = *Always* invoke \`computer_application\` to switch between the default applications.
3. **Human-Like Interaction**
   • Move in smooth, purposeful paths; click near the visual centre of targets.
   • Double-click desktop icons to open them.
4. **Valid Keys Only** - Use **exactly** the identifiers listed in **VALID KEYS** below.
5. **Verify Every Step** - After each action:
   a. Take another screenshot.
   b. Confirm the expected state before continuing.
6. **Efficiency & Clarity** - Combine related key presses; prefer scrolling or dragging over many small moves.
7. **Stay Within Scope** - Do nothing the user didn't request.
8. **Security** - If you see sensitive information, do not repeat it in conversation.
9. **Consistency & Persistence** - Even if the task is repetitive, do not end the task until the user's goal is completely met.

────────────────────────
TASK LIFECYCLE TEMPLATE
────────────────────────
1. **Prepare** - Initial screenshot → plan → estimate scope if possible.
2. **Execute Loop** - For each sub-goal: Screenshot → Think → Act → Verify.
3. **Batch Loop** - For repetitive tasks:
   • While items remain:
     - Process batch of 10-20 items
     - Update progress counter
     - Check for stop conditions
4. **Ask for Help** - If you need clarification:
   \`\`\`json
   { "name": "set_task_status", "input": { "status": "needs_help", "description": "..." } }
   \`\`\`
5. **Terminate** - ONLY ONCE THE USER'S GOAL IS COMPLETELY MET:
   \`\`\`json
   { "name": "set_task_status", "input": { "status": "completed", "description": "..." } }
   \`\`\`

Remember: **accuracy over speed, clarity and consistency over cleverness**.
`;
```

#### 关键点说明

1. **Observe-Act-Verify 循环**: 每次操作前截图，操作后验证
2. **任务生命周期**: Prepare → Execute Loop → Terminate
3. **安全机制**: 敏感信息不重复
4. **批量处理**: 10-20 个一批

---

### 4. 工具执行 (`agent.computer-use.ts`)

```typescript
// 源码位置: packages/bytebot-agent/src/agent/agent.computer-use.ts

const BYTEBOT_DESKTOP_BASE_URL = process.env.BYTEBOT_DESKTOP_BASE_URL as string;

export async function handleComputerToolUse(
  block: ComputerToolUseContentBlock,
  logger: Logger,
): Promise<ToolResultContentBlock> {
  logger.debug(
    `Handling computer tool use: ${block.name}, tool_use_id: ${block.id}`,
  );

  if (isScreenshotToolUseBlock(block)) {
    const image = await screenshot();
    return {
      type: MessageContentType.ToolResult,
      tool_use_id: block.id,
      content: [
        {
          type: MessageContentType.Image,
          source: {
            data: image,
            media_type: 'image/png',
            type: 'base64',
          },
        },
      ],
    };
  }

  // ... 其他工具处理 ...

  // 执行操作后等待 750ms，然后截图返回
  const delayMs = 750;
  await new Promise((resolve) => setTimeout(resolve, delayMs));
  const image = await screenshot();

  return {
    type: MessageContentType.ToolResult,
    tool_use_id: block.id,
    content: [
      { type: MessageContentType.Text, text: 'Tool executed successfully' },
      {
        type: MessageContentType.Image,
        source: { data: image, media_type: 'image/png', type: 'base64' },
      },
    ],
  };
}

// 所有操作通过 HTTP 调用 bytebotd 服务
async function clickMouse(input: {
  coordinates?: Coordinates;
  button: Button;
  holdKeys?: string[];
  clickCount: number;
}): Promise<void> {
  const { coordinates, button, holdKeys, clickCount } = input;

  await fetch(`${BYTEBOT_DESKTOP_BASE_URL}/computer-use`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      action: 'click_mouse',
      coordinates,
      button,
      holdKeys: holdKeys && holdKeys.length > 0 ? holdKeys : undefined,
      clickCount,
    }),
  });
}
```

#### 关键点说明

1. **HTTP API 调用**: 所有操作发送到 `bytebotd` 服务
2. **750ms 等待**: 操作后等待 UI 稳定
3. **自动截图**: 每次操作后返回截图供 LLM 验证

---

## 架构分析

### 优点

1. **清晰的分层**: Agent Service ↔ Desktop Service 分离
2. **多 LLM 支持**: 抽象的 `BytebotAgentService` 接口
3. **上下文管理**: 自动摘要压缩，保持上下文窗口
4. **任务管理**: 支持子任务、定时任务
5. **用户接管**: takeover/resume 机制

### 限制

1. **虚拟环境依赖**: 必须运行在 Docker 容器里
2. **全局输入**: 没有窗口隔离能力
3. **Linux Only**: bytebotd 只支持 Linux

### 我们可以借鉴什么

| 模块 | 借鉴程度 | 说明 |
|------|---------|------|
| Agent 循环 | 完全借鉴 | `runIteration` 模式 |
| 工具定义 | 完全借鉴 | Schema 格式 |
| System Prompt | 部分借鉴 | 需要适配 Windows |
| 上下文压缩 | 完全借鉴 | 摘要机制 |
| 任务状态 | 完全借鉴 | completed/needs_help |
| HTTP API | 不借鉴 | 我们用 IPC |
| bytebotd | 不借鉴 | 我们用 koffi + Windows API |

---

## NogicOS 适配建议

### 可以直接复用的部分

1. **Agent 循环架构**

```python
# NogicOS 实现
class AgentProcessor:
    async def run_iteration(self, task_id: str):
        # 1. 检查任务状态
        task = await self.tasks_service.find_by_id(task_id)
        if task.status != TaskStatus.RUNNING:
            return
        
        # 2. 构建上下文
        messages = await self.build_context(task_id)
        
        # 3. 调用 LLM
        response = await self.llm_service.generate(
            system_prompt=AGENT_SYSTEM_PROMPT,
            messages=messages
        )
        
        # 4. 执行工具
        results = await self.execute_tools(response.tool_calls)
        
        # 5. 保存结果
        await self.messages_service.create(results)
        
        # 6. 调度下一次
        if self.is_processing:
            asyncio.create_task(self.run_iteration(task_id))
```

2. **工具定义格式**

```python
# NogicOS 工具定义
TOOLS = [
    {
        "name": "computer_click",
        "description": "在指定位置点击",
        "input_schema": {
            "type": "object",
            "properties": {
                "hwnd": {"type": "integer", "description": "目标窗口句柄"},
                "x": {"type": "integer"},
                "y": {"type": "integer"},
                "button": {"type": "string", "enum": ["left", "right"]},
            },
            "required": ["hwnd", "x", "y"]
        }
    }
]
```

3. **任务状态机**

```python
class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    NEEDS_HELP = "needs_help"
    FAILED = "failed"
```

### 需要修改的部分

1. **System Prompt**
   - 移除 Linux 特定内容
   - 添加 Windows 应用列表
   - 添加窗口隔离说明

2. **工具执行**
   - HTTP → IPC (Electron ↔ Python)
   - bytebotd → koffi + Windows API

3. **截图机制**
   - 全屏截图 → 窗口截图
   - 使用 `hwnd` 指定目标窗口

### 完全不能用的部分

1. **bytebotd 服务** - Linux Only
2. **nut-tree/js** - 不支持窗口隔离
3. **Docker 容器化** - 我们是原生 Windows

---

## 参考检索索引

| 需要实现的功能 | 参考代码 | 行号范围 |
|--------------|---------|---------|
| Agent 主循环 | `agent.processor.ts` | `runIteration()` |
| 工具定义 | `agent.tools.ts` | `agentTools` |
| System Prompt | `agent.constants.ts` | `AGENT_SYSTEM_PROMPT` |
| 工具执行 | `agent.computer-use.ts` | `handleComputerToolUse()` |
| 任务状态 | `agent.processor.ts` | `setTaskStatusToolUseBlock` |
| 上下文压缩 | `agent.processor.ts` | `shouldSummarize` |
