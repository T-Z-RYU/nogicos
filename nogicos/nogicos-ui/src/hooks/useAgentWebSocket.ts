/**
 * Agent WebSocket Hook
 * Phase 7: Agent 专用 WebSocket 通信
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import type {
  AgentStatus,
  AgentProgress,
  AgentEvent,
  AgentError,
  AgentTask,
} from '@/types/agent';
import type { SensitiveAction } from '@/types/sensitive-action';

// Agent API Classtypedefine
interface AgentAPIType {
  onAgentEvent: (callback: (event: AgentEvent) => void) => () => void;
  onBatchEvents?: (callback: (events: AgentEvent[]) => void) => () => void;
  startTask: (task: string, targetHwnds: number[]) => Promise<{ taskId: string }>;
  stopTask: (taskId: string) => Promise<void>;
  resumeTask: (taskId: string) => Promise<void>;
  confirmSensitiveAction: (taskId: string, actionId: string, approved: boolean) => Promise<void>;
}

// Agent State
interface AgentState {
  status: AgentStatus;
  progress: AgentProgress | null;
  currentTask: AgentTask | null;
  pendingAction: SensitiveAction | null;
  error: AgentError | null;
}

// initialState
const initialState: AgentState = {
  status: 'idle',
  progress: null,
  currentTask: null,
  pendingAction: null,
  error: null,
};

// Toast Classtype
type AgentToastItem = { id: string; message: string; timestamp: number };

// Hook ReturnClasstype
interface UseAgentWebSocketReturn {
  state: AgentState;
  isConnected: boolean;
  toastQueue: AgentToastItem[];
  // Taskcontrol
  startTask: (task: string, targetHwnds: number[]) => Promise<string | null>;
  stopTask: () => void;
  resumeTask: () => void;
  // sensitiveAction
  confirmAction: (actionId: string, approved: boolean) => void;
  // State
  clearError: () => void;
  clearToasts: () => void;
  dismissToast: (id: string) => void;
}

/**
 * Agent WebSocket Hook
 * 通过 Electron IPC 与 Agent After端通信
 */
export function useAgentWebSocket(): UseAgentWebSocketReturn {
  const [state, setState] = useState<AgentState>(initialState);
  const [isConnected, setIsConnected] = useState(false);
  const currentTaskIdRef = useRef<string | null>(null);
  const unsubscribeRef = useRef<(() => void) | null>(null);

  // Get agentAPI
  const getAgentAPI = useCallback(() => {
    if (typeof window !== 'undefined' && (window as Window & { agentAPI?: AgentAPIType }).agentAPI) {
      return (window as Window & { agentAPI?: AgentAPIType }).agentAPI;
    }
    return null;
  }, []);

  // Toast Queue（forDisplayNone hwnd Action's Tip）
  const [toastQueue, setToastQueue] = useState<AgentToastItem[]>([]);

  // Handle Agent Event
  const handleAgentEvent = useCallback((event: AgentEvent) => {
    switch (event.type) {
      case 'status':
        setState((prev) => ({
          ...prev,
          status: event.data as AgentStatus,
          error: null,
        }));
        break;

      case 'progress':
        setState((prev) => ({
          ...prev,
          progress: event.data as AgentProgress,
        }));
        break;

      case 'confirm':
        setState((prev) => ({
          ...prev,
          status: 'confirm',
          pendingAction: event.data as SensitiveAction,
        }));
        break;

      case 'error':
        setState((prev) => ({
          ...prev,
          status: 'failed',
          error: event.data as AgentError,
        }));
        break;

      case 'complete':
        setState((prev) => ({
          ...prev,
          status: 'completed',
          pendingAction: null,
        }));
        currentTaskIdRef.current = null;
        break;

      case 'tool':
        // ToolExecuteEvent，AvailableatDisplaywhenBeforeAction
        setState((prev) => ({
          ...prev,
          status: 'executing',
        }));
        break;

      case 'toast': {
        // None hwnd Action's  toast Tip
        const toastData = event.data as { message: string; tool_name: string; timestamp: number };
        if (toastData?.message) {
          const toastId = `${toastData.timestamp}-${Math.random().toString(36).slice(2)}`;
          setToastQueue((prev) => [...prev, { id: toastId, message: toastData.message, timestamp: toastData.timestamp }]);
          // 3SecondAfterAutoRemove
          setTimeout(() => {
            setToastQueue((prev) => prev.filter((t) => t.id !== toastId));
          }, 3000);
        }
        break;
      }
    }
  }, []);

  // Subscribe Agent Event（singleandBatch）
  useEffect(() => {
    const api = getAgentAPI();
    if (!api) {
      console.warn('[useAgentWebSocket] agentAPI not available');
      return;
    }

    // SubscribesingleEvent
    const unsubscribeSingle = api.onAgentEvent(handleAgentEvent);
    
    // SubscribeBatchEvent（high frequency event optimization，withFault-tolerant）
    let unsubscribeBatch: (() => void) | null = null;
    if (api.onBatchEvents) {
      unsubscribeBatch = api.onBatchEvents((events: AgentEvent[]) => {
        // handle each itemBatchEvent，singleitemFailednotaffectOther
        events.forEach((event, index) => {
          try {
            handleAgentEvent(event);
          } catch (error) {
            console.error(`[useAgentWebSocket] Batch event #${index} processing failed:`, error);
          }
        });
      });
    }
    
    unsubscribeRef.current = () => {
      unsubscribeSingle();
      unsubscribeBatch?.();
    };
    setIsConnected(true);

    return () => {
      if (unsubscribeRef.current) {
        unsubscribeRef.current();
        unsubscribeRef.current = null;
      }
      setIsConnected(false);
    };
  }, [getAgentAPI, handleAgentEvent]);

  // StartTask
  const startTask = useCallback(
    async (task: string, targetHwnds: number[]): Promise<string | null> => {
      const api = getAgentAPI();
      if (!api) {
        console.error('[useAgentWebSocket] agentAPI not available');
        return null;
      }

      try {
        setState((prev) => ({
          ...prev,
          status: 'queued',
          error: null,
        }));

        const result = await api.startTask(task, targetHwnds);
        currentTaskIdRef.current = result.taskId;

        setState((prev) => ({
          ...prev,
          status: 'thinking',
          currentTask: {
            id: result.taskId,
            task_text: task,
            status: 'thinking',
            progress: {
              iteration: 0,
              maxIterations: 10,
              toolCalls: 0,
              currentWindow: '',
            },
            targetHwnds,
            createdAt: Date.now(),
            updatedAt: Date.now(),
          },
        }));

        return result.taskId;
      } catch (error) {
        console.error('[useAgentWebSocket] startTask error:', error);
        setState((prev) => ({
          ...prev,
          status: 'failed',
          error: {
            type: 'unknown',
            message: error instanceof Error ? error.message : 'Failed to start task',
            recoverable: true,
          },
        }));
        return null;
      }
    },
    [getAgentAPI]
  );

  // StopTask
  const stopTask = useCallback(() => {
    const api = getAgentAPI();
    const taskId = currentTaskIdRef.current;
    if (!api || !taskId) return;

    api.stopTask(taskId).then(() => {
      setState((prev) => ({
        ...prev,
        status: 'idle',
        pendingAction: null,
      }));
      currentTaskIdRef.current = null;
    });
  }, [getAgentAPI]);

  // ResumeTask
  const resumeTask = useCallback(() => {
    const api = getAgentAPI();
    const taskId = currentTaskIdRef.current;
    if (!api || !taskId) return;

    api.resumeTask(taskId).then(() => {
      setState((prev) => ({
        ...prev,
        status: 'recovering',
        error: null,
      }));
    });
  }, [getAgentAPI]);

  // ConfirmsensitiveAction
  const confirmAction = useCallback(
    (actionId: string, approved: boolean) => {
      const api = getAgentAPI();
      const taskId = currentTaskIdRef.current;
      if (!api || !taskId) return;

      api.confirmSensitiveAction(taskId, actionId, approved).then(() => {
        setState((prev) => ({
          ...prev,
          status: approved ? 'executing' : 'paused',
          pendingAction: null,
        }));
      });
    },
    [getAgentAPI]
  );

  // ClearError
  const clearError = useCallback(() => {
    setState((prev) => ({
      ...prev,
      error: null,
    }));
  }, []);

  // Clearall toast
  const clearToasts = useCallback(() => {
    setToastQueue([]);
  }, []);

  // Removesingleitem toast
  const dismissToast = useCallback((id: string) => {
    setToastQueue((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return {
    state,
    isConnected,
    toastQueue,
    startTask,
    stopTask,
    resumeTask,
    confirmAction,
    clearError,
    clearToasts,
    dismissToast,
  };
}
