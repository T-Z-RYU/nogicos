# NogicOS Reference Library Index

This document provides a comprehensive index of open-source browser and AI agent projects referenced for NogicOS development.

## Project Categories

### 1. AI Browser Automation Projects

| Project | Stars | Language | Key Features | Reference Path |
|---------|-------|----------|--------------|----------------|
| **browser-use** | 52k+ | Python | Event-driven agent, robust tools system, detailed system prompts | `reference/browser-use/` |
| **Stagehand** | 15k+ | TypeScript | Computer Use Agent (CUA), multi-provider support, hybrid mode | `reference/stagehand/` |
| **LaVague** | 6k+ | Python | World Model + Action Engine architecture, multi-modal LLM | `reference/lavague/` |

### 2. Mature Browsers (Architecture Reference)

| Browser | Focus Area | Notes |
|---------|------------|-------|
| Chromium | Core architecture, rendering, CDP | Industry standard |
| Firefox | Privacy, web standards | Alternative approach |

### 3. Electron Browsers

| Project | Key Learning Points |
|---------|---------------------|
| BrowserOS | Custom Chromium, TypeScript extension system |
| Min | Lightweight, privacy-focused |

---

## Detailed Project Analysis

### browser-use (Python)

**Repository**: https://github.com/browser-use/browser-use

**Architecture Highlights**:
- Event-driven architecture with `BrowserSession` managing CDP connections
- `Agent` class orchestrates tasks with LLM-driven action loops
- Structured system prompts with XML tags for clarity
- Registry pattern for action management
- DOM serialization optimized for LLM consumption

**Key Files Downloaded**:
```
reference/browser-use/
├── agent/
│   ├── service.py          # Core Agent class
│   ├── views.py             # Data structures
│   ├── prompts.py           # Prompt management
│   └── system_prompts/      # System prompt templates
├── browser/
│   ├── session.py           # Browser session management
│   ├── profile.py           # Browser configuration
│   └── events.py            # Event definitions
├── tools/
│   ├── service.py           # Tools/Actions execution
│   └── registry/            # Action registry
└── dom/
    ├── service.py           # DOM extraction
    └── serializer/          # DOM serialization for LLM
```

**System Prompt Design**:
- Uses XML-like tags: `<user_request>`, `<browser_state>`, `<agent_history>`
- Clear separation of thinking, evaluation, memory, and action
- Flash mode for faster execution with simplified prompts
- Anthropic-specific prompt variants

---

### Stagehand (TypeScript)

**Repository**: https://github.com/browserbase/stagehand

**Architecture Highlights**:
- Three core operations: `act`, `extract`, `observe`
- Computer Use Agent (CUA) with multi-provider support
- Hybrid mode: combines screenshot vision with accessibility tree
- Strong typing with Zod schemas

**Key Files Downloaded**:
```
reference/stagehand/
├── cursorrules.md           # Usage patterns
├── lib/
│   ├── prompt.ts            # Prompt builders
│   ├── inference.ts         # LLM inference
│   └── v3/
│       └── agent/
│           ├── AgentClient.ts      # Agent interface
│           ├── AgentProvider.ts    # Provider factory
│           └── prompts/
│               └── agentSystemPrompt.ts  # Agent system prompt
```

**System Prompt Design**:
- XML structure with `<system>`, `<task>`, `<tools>`, `<strategy>`
- Mode-aware tools (hybrid vs DOM-only)
- Page understanding protocol with primary/secondary tools
- Roadblocks handling (captcha, popups)

---

### LaVague (Python)

**Repository**: https://github.com/lavague-ai/LaVague

**Architecture Highlights**:
- Two-tier architecture: World Model + Action Engine
- Multi-modal LLM for visual understanding
- Short-term memory for state management
- Multiple engines: Navigation, Python, Navigation Controls

**Key Files Downloaded**:
```
reference/lavague/
└── core/
    ├── agents.py            # WebAgent orchestrator
    └── world_model.py       # World Model with prompts
```

**System Prompt Design**:
- Engine-based routing: Navigation Engine, Python Engine, Navigation Controls
- Few-shot examples with detailed thought processes
- State representation in YAML format
- Tab management awareness

---

## Key Learnings for NogicOS

### 1. Agent Architecture Patterns

| Pattern | browser-use | Stagehand | LaVague | NogicOS Recommendation |
|---------|-------------|-----------|---------|------------------------|
| Core Loop | Event-driven | Step-based | Engine dispatch | Hybrid: Event + Step |
| State Management | History + State | Context | Short-term Memory | Unified State Store |
| Action Execution | Registry | Tools | Engine dispatch | Registry + CDP |

### 2. System Prompt Best Practices

1. **Structure**: Use XML tags for clear section separation
2. **Examples**: Include few-shot examples with reasoning
3. **State Representation**: Accessibility tree > raw HTML
4. **Memory**: Explicit evaluation of previous actions
5. **Modes**: Provide fast/detailed modes for different use cases

### 3. Tool/Action Design

1. **Atomic Actions**: Keep actions simple and single-purpose
2. **Fallback Strategies**: Handle failures gracefully
3. **Validation**: Verify action results before proceeding
4. **Coordination**: Use scrolling/viewport management

### 4. Performance Optimization

1. **DOM Serialization**: Paint-order filtering, interactive element prioritization
2. **Screenshot Compression**: JPEG for visual context
3. **Caching**: LRU cache for repeated operations
4. **Token Management**: Track and optimize token usage

---

## Usage in NogicOS Development

When implementing new features:

1. **Check Reference First**: Search this library for similar implementations
2. **Adapt, Don't Copy**: Understand the pattern, adapt to our architecture
3. **Document Learnings**: Update this index with new insights
4. **Test Thoroughly**: Reference implementations may have edge cases

---

## Quick Reference Commands

```bash
# Browse reference code
cd nogicos/reference/

# Search for patterns
grep -r "system prompt" reference/
grep -r "click" reference/browser-use/tools/

# Compare implementations
diff reference/browser-use/agent/service.py reference/lavague/core/agents.py
```

---

*Last Updated: 2024-12-27*

