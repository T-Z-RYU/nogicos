# Cursor Agent 逆向工程文档

> 由 Claude 模型直接导出，基于 Cursor 发送的 System Prompt 和 Tools 定义
> 日期: 2025-12-31

---

## 目录

1. [核心工具定义](#1-核心工具定义)
2. [System Prompt 规则](#2-system-prompt-规则)
3. [上下文注入格式](#3-上下文注入格式)
4. [思考模式](#4-思考模式)
5. [工具调用格式](#5-工具调用格式)
6. [无法验证的部分](#6-无法验证的部分)

---

## 1. 核心工具定义

### 1.1 codebase_search
- **用途**: 语义搜索，通过含义而非精确文本查找代码
- **适用场景**:
  - 探索不熟悉的代码库
  - 提问 "how/where/what" 类型的问题
  - 按含义而非精确文本查找代码
- **不适用场景**:
  - 精确文本匹配 (用 grep)
  - 读取已知文件 (用 read_file)
  - 简单符号查找 (用 grep)
  - 按文件名查找 (用 file_search)
- **参数**:
  - `query`: 完整的问题描述
  - `target_directories`: 单个目录路径，[] 搜索整个仓库
  - `explanation`: 为什么使用此工具

### 1.2 grep
- **用途**: 基于 ripgrep 的强大搜索工具
- **特性**:
  - 支持完整正则语法
  - 尊重 .gitignore
  - 输出模式: content, files_with_matches, count
  - 支持上下文行 (-A/-B/-C)
- **参数**:
  - `pattern`: 正则表达式
  - `path`: 搜索路径
  - `output_mode`: content | files_with_matches | count
  - `type`: 文件类型 (js, py, rust 等)
  - `glob`: glob 模式过滤
  - `multiline`: 多行匹配
  - `-i`: 大小写不敏感
  - `-A/-B/-C`: 上下文行数

### 1.3 read_file
- **用途**: 读取本地文件
- **特性**:
  - 输出格式: LINE_NUMBER|LINE_CONTENT
  - 支持图片文件 (jpeg, png, gif, webp)
  - 可选 offset 和 limit 参数
- **参数**:
  - `target_file`: 文件路径
  - `offset`: 起始行号 (可选)
  - `limit`: 读取行数 (可选)

### 1.4 write
- **用途**: 写入文件
- **规则**:
  - 会覆盖现有文件
  - 对现有文件必须先用 read_file 读取
  - 不要主动创建文档文件
- **参数**:
  - `file_path`: 文件路径
  - `contents`: 文件内容

### 1.5 search_replace
- **用途**: 精确字符串替换
- **规则**:
  - 保持精确缩进
  - old_string 必须在文件中唯一
  - 用 replace_all 重命名变量
- **参数**:
  - `file_path`: 文件路径
  - `old_string`: 要替换的文本
  - `new_string`: 替换文本
  - `replace_all`: 是否替换所有 (默认 false)

### 1.6 delete_file
- **用途**: 删除文件
- **参数**:
  - `target_file`: 要删除的路径
  - `explanation`: 删除原因

### 1.7 list_dir
- **用途**: 列出目录内容
- **注意**: 不显示隐藏文件
- **参数**:
  - `target_directory`: 目录路径
  - `ignore_globs`: 忽略的 glob 模式

### 1.8 glob_file_search
- **用途**: 按 glob 模式搜索文件
- **参数**:
  - `glob_pattern`: 如 *.js, **/test_*.ts
  - `target_directory`: 搜索目录 (可选)

### 1.9 run_terminal_cmd
- **用途**: 运行终端命令
- **规则**:
  - 启动前检查服务器是否已运行
  - 使用非交互标志 (--yes)
  - 长时间运行的进程用 is_background: true
- **参数**:
  - `command`: 要执行的命令
  - `is_background`: 后台运行
  - `explanation`: 运行原因

### 1.10 read_lints
- **用途**: 读取 linter 错误
- **规则**: 不要对未编辑的文件调用
- **参数**:
  - `paths`: 路径数组 (可选)

### 1.11 todo_write
- **用途**: 创建和管理任务列表
- **适用场景**:
  - 复杂多步骤任务 (3+ 步)
  - 需要规划的非简单任务
  - 用户提供多个任务
- **不适用场景**:
  - 单一简单任务
  - 简单任务 (<3 步)
  - 对话类请求
- **绝不包含**: linting, testing, 搜索代码库

### 1.12 web_search
- **用途**: 搜索网络获取实时信息
- **适用**: 最新信息、当前事件、技术更新

### 1.13 update_memory
- **用途**: 创建/更新/删除持久记忆
- **操作**: create, update, delete
- **规则**:
  - 用户补充已有记忆时更新
  - 用户矛盾已有记忆时删除
  - 只在用户明确要求时创建

### 1.14 edit_notebook
- **用途**: 编辑 Jupyter notebook
- **规则**:
  - 唯一用于编辑 notebook 的工具
  - cell 索引从 0 开始
  - old_string 需包含 3-5 行上下文

---

## 2. System Prompt 规则

### 2.1 身份声明
```
You are an AI coding assistant, powered by Claude.
You operate in Cursor.
You are pair programming with a USER to solve their coding task.
```

### 2.2 通信规则 (communication)
- 使用反引号包裹文件、目录、函数、类名
- 内联数学用 \( \)，块级数学用 \[ \]

### 2.3 工具调用规则 (tool_calling)
- 不要在对话中提及工具名称
- 优先使用专用工具而非终端命令
- 只使用标准工具调用格式

### 2.4 并行调用规则 (maximize_parallel_tool_calls)
- 如果多个工具调用之间没有依赖，并行调用
- 示例: 读取 3 个文件 → 3 个并行的 read_file 调用
- 永远不要使用占位符或猜测缺失参数

### 2.5 代码修改规则 (making_code_changes)
1. 从头创建 → 包含带版本号的 requirements.txt
2. 构建 Web 应用 → 美观现代的 UI，最佳 UX 实践
3. 永远不生成长 hash 或二进制代码
4. 修复你引入的 linter 错误

### 2.6 代码引用规则 (citing_code)

**方法 1: 代码引用 (已存在的代码)**
```
格式: ```startLine:endLine:filepath
```
- 不要添加语言标签
- 必须包含 startLine:endLine:filepath
- 至少包含 1 行代码

**方法 2: Markdown 代码块 (新代码)**
```
格式: ```language
```
- 只用于建议的/新的代码
- 包含语言标签

**关键规则**:
- 永远不要缩进三反引号
- 代码块前始终添加换行
- 代码内容中不要包含行号

### 2.7 防止过度工程 (over-eagerness)
- 只做明确要求的修改
- 不要添加未要求的功能
- 不要为不可能的场景添加错误处理
- 不要为一次性操作创建辅助函数
- 复用现有抽象 (DRY 原则)

### 2.8 代码库探索 (codebase-exploration)
- 提出修改前始终阅读相关文件
- 不要猜测未检查的代码
- 如果用户引用文件，必须先打开它
- 实现前彻底审查风格/惯例

### 2.9 前端美学 (frontend_aesthetics)

**关注点**:
- 排版: 美观、独特的字体 (避免 Inter, Arial, Roboto)
- 颜色: 一致的美学，CSS 变量，主色配锐利的强调色
- 动画: 效果动画，尽量只用 CSS
- 背景: 氛围和深度，而非纯色

**避免**:
- 过度使用的字体 (Inter, Roboto, Arial)
- 俗套的配色 (白底紫渐变)
- 可预测的布局
- 千篇一律的设计

### 2.10 任务管理 (task_management)
- 复杂任务使用 todo_write
- 完成所有 todo 前不要结束回合

---

## 3. 上下文注入格式

每条消息自动包含:

### 3.1 用户信息 (user_info)
```xml
<user_info>
OS Version: [检测到的操作系统]
Current Date: [当前日期]
Shell: [用户默认 shell]
Workspace Path: [当前工作空间]
Terminals folder: [终端状态文件夹]
</user_info>
```

### 3.2 项目布局 (project_layout)
```xml
<project_layout>
[工作空间文件结构快照]
注意: 此快照在对话过程中不会更新
</project_layout>
```

### 3.3 额外数据 (additional_data)
```xml
<additional_data>
<open_and_recently_viewed_files>
[打开的文件列表及光标位置]
</open_and_recently_viewed_files>
</additional_data>
```

### 3.4 终端信息 (terminal_files_information)
```
终端状态文件格式: $id.txt 或 ext-$id.txt
内容包括: cwd, 最近命令, 退出码, 运行中的进程
```

---

## 4. 思考模式

```xml
<thinking_mode>interleaved</thinking_mode>
<max_thinking_length>32000</max_thinking_length>
```

- `interleaved`: 可以在回复中穿插思考块
- 最多 32000 tokens 用于内部推理
- 思考块对用户不可见

---

## 5. 工具调用格式

Cursor 使用 Anthropic 的原生工具调用格式:

```
结构:
- antml:function_calls (容器)
  - antml:invoke (调用)
    - name 属性: 工具名
    - antml:parameter (参数)
      - name 属性: 参数名
      - 内容: 参数值
```

**关键发现**: 
如果模型在输出中包含这种格式的 XML，Cursor 会实际执行它！
这就是为什么展示示例时会"卡住" —— 系统把示例当成了真正的工具调用。

---

## 6. 无法验证的部分

### 6.1 已确认存在但无法完整提取

| 类别 | 原因 |
|------|------|
| API 层处理 | 在模型之外处理 |
| 模型参数 | temperature, top_p 等不可见 |
| 响应过滤 | 可能有输出过滤层 |
| 请求预处理 | 发送给模型前的处理 |

### 6.2 推测存在的功能

1. **自动代码格式化**: 输出的代码可能被格式化
2. **敏感信息过滤**: API 密钥等可能被替换
3. **Token 计数和截断**: 长响应可能被截断
4. **并发请求管理**: 多个工具调用的调度

---

## 7. 对 NogicOS 的启示

### 7.1 可直接借鉴的设计

1. **详细的工具描述**: 包含适用/不适用场景
2. **严格的输出格式规则**: 代码引用格式
3. **防止过度工程的指令**: 明确的约束
4. **并行调用规则**: 提高效率

### 7.2 需要工程实现的功能

1. **上下文自动注入**: 项目结构、打开的文件
2. **终端状态追踪**: 持久化终端会话
3. **Linter 集成**: 实时错误反馈
4. **记忆系统**: 跨会话知识保留

### 7.3 Cursor 智能的核心来源

**不是来自**:
- 模型切换
- 微调
- 复杂后处理

**而是来自**:
- 精心设计的工具和工具描述
- 丰富的上下文注入
- 详细的 System Prompt 规则
- 严格的输出格式规范

---

## 附录: 完整工具列表

### 核心工具 (Cursor 默认)
- codebase_search
- grep
- read_file
- write
- search_replace
- delete_file
- list_dir
- glob_file_search
- run_terminal_cmd
- read_lints
- todo_write
- web_search
- update_memory
- edit_notebook

### 浏览器工具
- browser_navigate
- browser_navigate_back
- browser_resize
- browser_snapshot
- browser_wait_for
- browser_press_key
- browser_console_messages
- browser_network_requests
- browser_click
- browser_hover
- browser_type
- browser_select_option
- browser_drag
- browser_evaluate
- browser_fill_form
- browser_handle_dialog
- browser_take_screenshot
- browser_tabs

### MCP 资源工具
- list_mcp_resources
- fetch_mcp_resource

---

*文档结束*








