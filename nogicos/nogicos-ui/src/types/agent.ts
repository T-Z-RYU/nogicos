/**
 * Agent Class型定义
 * Phase 7: 扩展StateSystem
 */

// 10 kinds of fine granularityState
export type AgentStatus =
  | 'idle'       // Emptyidle
  | 'queued'     // queued (waiting)（ConcurrentLimit）
  | 'thinking'   // AI thinkMedium
  | 'planning'   // GenerationExecuteplan
  | 'executing'  // ExecuteTool
  | 'verifying'  // captureGraphVerifyMedium
  | 'waiting'    // WaitWindowResponse
  | 'confirm'    // WaitUserConfirm
  | 'paused'     // UserPause
  | 'recovering' // fromErrorResume
  | 'completed'  // Complete
  | 'failed';    // Failed

// Agent progressInfo
export interface AgentProgress {
  iteration: number;        // whenBeforeIterate
  maxIterations: number;    // MaxIterate
  toolCalls: number;        // alreadyExecuteToolnumber
  currentWindow: string;    // whenBeforeActionWindow
  estimatedTime?: number;   // estimated remainingTime(Second)
}

// StateDisplayConfig
export interface StatusDisplay {
  icon: string;
  label: string;
  color: string;
  animation: AnimationType | null;
}

// AnimationClasstype
export type AnimationType =
  | 'pulse'
  | 'spin'
  | 'bounce'
  | 'blink'
  | 'scan'
  | 'shake'
  | 'check';

// Agent EventClasstype
export interface AgentEvent {
  type: 'status' | 'progress' | 'error' | 'confirm' | 'complete' | 'tool' | 'toast';
  taskId: string;
  data: unknown;
  timestamp: number;
}

// Agent ControllerInterface
export interface AgentController {
  startTask: (task: string, targetHwnds: number[]) => Promise<{ taskId: string }>;
  stopTask: (taskId: string) => Promise<void>;
  resumeTask: (taskId: string) => Promise<void>;
  emergencyStop: () => void;
  togglePause: () => void;
  confirmPendingAction: () => void;
  cycleActiveWindow: () => void;
}

// Agent TaskState
export interface AgentTask {
  id: string;
  task_text: string;
  status: AgentStatus;
  progress: AgentProgress;
  targetHwnds: number[];
  createdAt: number;
  updatedAt: number;
}

// ErrorClasstype
export type AgentErrorType =
  | 'api_timeout'
  | 'window_lost'
  | 'tool_failed'
  | 'emergency_stop'
  | 'connection_error'
  | 'unknown';

// ErrorInfo
export interface AgentError {
  type: AgentErrorType;
  message: string;
  detail?: string;
  recoverable: boolean;
}
