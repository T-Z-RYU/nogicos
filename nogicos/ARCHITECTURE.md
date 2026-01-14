# NogicOS Architecture

## Overview

NogicOS is an AI assistant that works across your browser, files, and desktop as one unified workspace.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Electron Client                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Webview   │  │  AI Panel   │  │  Status Bar │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└───────────────────────────┬─────────────────────────────────┘
                            │ WebSocket + HTTP
┌───────────────────────────▼─────────────────────────────────┐
│                    Python Backend                            │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                   HiveEngine                         │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │    │
│  │  │  Router  │─▶│  Agent   │─▶│ Knowledge Store  │   │    │
│  │  └──────────┘  └──────────┘  └──────────────────┘   │    │
│  └─────────────────────────────────────────────────────┘    │
│                            │                                 │
│  ┌─────────────────────────▼─────────────────────────────┐  │
│  │              Browser Control (CDP)                     │  │
│  │  Navigation │ Click │ Type │ Screenshot │ A11y Tree   │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. ReAct Agent
State machine-based AI agent:
- `observe` → Capture page state (screenshot + accessibility tree)
- `think` → LLM reasoning and action planning
- `act` → Execute browser actions via CDP
- `terminate` → Return result

### 2. Knowledge Store
Stores and retrieves context:
- Semantic memory for relevant context retrieval
- Session history persistence

### 3. CDP Bridge
Chrome DevTools Protocol integration for browser control:
- Direct control of Electron BrowserView
- No external browser dependency
- Real-time action execution

## Data Flow

```
User Task → ReAct Agent → Tool Execution → Result
```

## UI Architecture

### Parallel Streaming

NogicOS UI 支持多 session 并行 streaming，切换 session 不会中断 AI 回复：

```
┌─────────────────────────────────────────────────────────┐
│                      App.tsx                             │
│  ┌─────────────────────────────────────────────────┐    │
│  │           activeSessions: Set<string>            │    │
│  │  - session-1 (visible)                           │    │
│  │  - session-2 (hidden, streaming in background)   │    │
│  │  - session-3 (hidden)                            │    │
│  └─────────────────────────────────────────────────┘    │
│                         │                                │
│    ┌────────────────────┼────────────────────┐          │
│    ▼                    ▼                    ▼          │
│  MinimalChatArea    MinimalChatArea    MinimalChatArea  │
│  (display: flex)    (display: none)    (display: none)  │
│  useChat instance   useChat instance   useChat instance │
└─────────────────────────────────────────────────────────┘
```

**关键设计**：
- 每个 session 渲染独立的 `MinimalChatArea` 组件
- 使用 CSS `display: none/flex` 控制可见性
- 每个组件有独立的 `useChat` 实例，streaming 互不影响
- 切换只改变显示，不销毁组件

### Session Persistence

```
Frontend State          Backend API              SQLite
─────────────────      ─────────────           ─────────
chatSessions (Map) ←→  /v2/sessions   ←→     sessions.db
currentUnsavedSession  /v2/sessions/:id
persistedSessions      
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/execute` | POST | Execute AI task |
| `/v2/chat` | POST | Vercel AI SDK streaming chat |
| `/v2/sessions` | GET | List all sessions |
| `/v2/sessions/:id` | GET | Get session detail |
| `/v2/sessions/:id` | POST | Save session |
| `/v2/sessions/:id` | DELETE | Delete session |
| `/stats` | GET | Knowledge base statistics |
| `/health` | GET | Health check |

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DEFAULT_MODEL` | claude-opus-4-5 | LLM model |
| `HTTP_PORT` | 8080 | API server port |
| `WS_PORT` | 8765 | WebSocket port |
