# NogicOS

> **Workspace AI connects your tabs, files, and apps**
> 
> The AI that connects your browser tabs, local files, and desktop apps as one unified workspace.

---

## What is NogicOS?

NogicOS is a **Workspace AI** that connects your tabs, files, and apps into one unified context.

**The Problem:**
- ChatGPT only sees what you paste
- Claude only sees what you upload
- Cursor only sees your code
- ramAIn automates messaging (WhatsApp/Email)

**Our Solution:**
NogicOS connects your entire work environment—tabs, files, and apps—and takes action directly in it. We focus on research, analysis, and document integration, not communication automation.

---

## Key Features

### 🔗 Connecting
- **Tabs**: Browse the web, extract data (Playwright)
- **Files**: Read and write local files
- **Apps**: Understand desktop state, window management

### 🧠 Understanding
- AI understands your work context
- No copy-paste needed
- Cross-app intelligence

### ⚡ Acting
- Think → Act → Observe → Repeat
- Direct task execution
- Auto-retry on failures

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Electron Client                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Chat UI    │  │  AI Panel   │  │  Status Bar │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└───────────────────────────┬─────────────────────────────────┘
                            │ WebSocket + HTTP
┌───────────────────────────▼─────────────────────────────────┐
│                    Python Backend                            │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                    ReAct Agent                       │    │
│  │           Think → Act → Observe → Repeat            │    │
│  └─────────────────────────────────────────────────────┘    │
│                            │                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │Browser Tools │  │ Local Tools  │  │Desktop Tools │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Anthropic API key

### Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Electron dependencies
cd client && npm install && cd ..

# Set up API keys
cp api_keys.example.py api_keys.py
# Edit api_keys.py with your Anthropic API key
```

### Running

```bash
# Start backend
python hive_server.py

# In another terminal, start frontend
cd nogicos-ui && npm run dev
```

---

## Available Tools

### Browser Tools
| Tool | Description |
|------|-------------|
| `browser_navigate` | Navigate to URL |
| `browser_click` | Click element |
| `browser_type` | Type text |
| `browser_scroll` | Scroll page |
| `browser_screenshot` | Take screenshot |
| `browser_extract` | Extract page content |

### Local Tools
| Tool | Description |
|------|-------------|
| `read_file` | Read file content |
| `write_file` | Write to file |
| `list_directory` | List directory |
| `create_directory` | Create folder |
| `move_file` | Move/rename file |
| `shell_execute` | Run shell command |
| `glob_search` | Search by pattern |
| `grep_search` | Search contents |

---

## Example Tasks

```
"Analyze this competitor's website and save key features to Excel"
→ Agent opens website → extracts data → creates Excel file

"Organize my desktop by file type"
→ Agent lists files → categorizes → creates folders → moves files

"Find all TODO comments in this project"
→ Agent searches files → aggregates results → generates report
```

---

## Project Structure

```
nogicos/
├── hive_server.py           # Backend entry point
├── engine/
│   ├── agent/               # ReAct Agent + Planner
│   ├── tools/               # Browser/Local/Desktop tools
│   ├── knowledge/           # Knowledge Store
│   └── server/              # WebSocket service
├── client/                  # Electron client
├── nogicos-ui/              # React frontend
├── PRODUCT_SPEC.md          # Product specification
├── ARCHITECTURE.md          # Technical architecture
├── PITCH_CONTEXT.md         # Team pitch context
└── CHANGELOG.md             # Version history
```

---

## Documentation

- [PRODUCT_SPEC.md](./PRODUCT_SPEC.md) - Product definition and standards
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Technical architecture details
- [PITCH_CONTEXT.md](./PITCH_CONTEXT.md) - Pitch and collaboration guide
- [CHANGELOG.md](./CHANGELOG.md) - Version history

---

## Tech Stack

- **Frontend**: Electron + React + Tailwind
- **Backend**: Python + FastAPI + WebSocket
- **AI**: Claude 3.5 Sonnet + ReAct Loop
- **Browser**: Playwright
- **Design**: Vision Pro inspired glassmorphism

---

## License

MIT License

---

## Team

Building the AI work partner for everyone.
