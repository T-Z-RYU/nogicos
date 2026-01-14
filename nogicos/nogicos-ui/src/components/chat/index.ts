/**
 * Chat Components
 * 
 * Multiple chat interface styles:
 * - Minimal: 极致克制，纯黑白灰 (Recommended)
 * - System: System级 AI Tool界面
 * - Premium: Linear/Raycast-grade refined interface
 * - Cursor: Cursor IDE-style interface
 */

// Minimal Design (Recommended) - minimal
export { MinimalChatArea } from './MinimalChatArea';

// System Design - SystemlevelTool
export { SystemChatArea } from './SystemChatArea';

// Premium Design
export { PremiumChatArea } from './PremiumChatArea';
export { PremiumMessage } from './PremiumMessage';

// Cursor-Style (Legacy)
export { CursorChatArea } from './CursorChatArea';
export { Message } from './Message';
export { StreamingText } from './StreamingText';
export { ThinkingBlock } from './ThinkingBlock';
export { CodeBlock } from './CodeBlock';

// Mode System (Cursor-style Agent/Ask/Plan)
export { ModeSelector, ModeIndicator, type AgentMode } from './ModeSelector';
export { PlanEditor, type EditablePlan, type PlanStep } from './PlanEditor';

