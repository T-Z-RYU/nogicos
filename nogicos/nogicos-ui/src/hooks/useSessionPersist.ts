/**
 * useSessionPersist Hook
 * 
 * 封装After端 Session 持久化 API
 * 对接 /v2/sessions 端点
 */

import { useState, useCallback, useEffect } from 'react';

const API_URL = 'http://localhost:8080';

// Types
export interface SessionSummary {
  id: string;
  title: string;
  preview: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface SessionDetail {
  id: string;
  title: string;
  history: Message[];
  preferences: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  tool_calls?: unknown[];
  timestamp?: string;
}

interface UseSessionPersistOptions {
  autoLoad?: boolean;
  onError?: (error: Error) => void;
}

export function useSessionPersist(options: UseSessionPersistOptions = {}) {
  const { autoLoad = true, onError } = options;
  
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  // HandleError
  const handleError = useCallback((e: unknown) => {
    const err = e instanceof Error ? e : new Error(String(e));
    setError(err);
    onError?.(err);
    console.error('[SessionPersist] Error:', err);
  }, [onError]);

  // Load Session List
  const loadSessions = useCallback(async (limit = 20, offset = 0) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(
        `${API_URL}/v2/sessions?limit=${limit}&offset=${offset}`
      );
      
      if (!response.ok) {
        throw new Error(`Failed to load sessions: ${response.status}`);
      }
      
      const data = await response.json();

      // [P1 FIX] Enhanced data validation with type guards
      if (!data || typeof data !== 'object') {
        throw new Error('Invalid response format');
      }

      const rawSessions = Array.isArray(data.sessions) ? data.sessions : [];

      // ConvertforBeforeendFormat with validation
      const formattedSessions: SessionSummary[] = rawSessions
        .filter((s: unknown): s is Record<string, unknown> =>
          s !== null && typeof s === 'object' && 'id' in s && typeof (s as Record<string, unknown>).id === 'string'
        )
        .map((s: Record<string, unknown>) => ({
          id: String(s.id),
          title: typeof s.title === 'string' ? s.title : 'Untitled',
          preview: typeof s.preview === 'string' ? s.preview : '',
          message_count: typeof s.message_count === 'number' ? s.message_count : 0,
          created_at: typeof s.created_at === 'string' ? s.created_at : new Date().toISOString(),
          updated_at: typeof s.updated_at === 'string' ? s.updated_at : new Date().toISOString(),
        }));

      setSessions(formattedSessions);
      return formattedSessions;
    } catch (e) {
      handleError(e);
      return [];
    } finally {
      setIsLoading(false);
    }
  }, [handleError]);

  // Loadsingle Session Detail（PackagecontainHistoryMessage）
  const loadSession = useCallback(async (sessionId: string): Promise<SessionDetail | null> => {
    try {
      const response = await fetch(`${API_URL}/v2/sessions/${sessionId}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          return null; // Session Not Exists
        }
        throw new Error(`Failed to load session: ${response.status}`);
      }
      
      const data = await response.json();

      // [P1 FIX] Validate response structure
      if (!data || typeof data !== 'object' || typeof data.id !== 'string') {
        throw new Error('Invalid session data format');
      }

      // [P1 FIX] Validate history array
      const history = Array.isArray(data.history)
        ? data.history.filter((m: unknown): m is Message => {
            if (m === null || typeof m !== 'object') return false;
            const msg = m as Record<string, unknown>;
            return (
              'role' in msg && typeof msg.role === 'string' &&
              ['user', 'assistant', 'system'].includes(msg.role) &&
              'content' in msg && typeof msg.content === 'string'
            );
          })
        : [];

      return {
        id: data.id,
        title: typeof data.title === 'string' ? data.title : 'Untitled',
        history,
        preferences: typeof data.preferences === 'object' && data.preferences !== null ? data.preferences : {},
        created_at: typeof data.created_at === 'string' ? data.created_at : new Date().toISOString(),
        updated_at: typeof data.updated_at === 'string' ? data.updated_at : new Date().toISOString(),
      };
    } catch (e) {
      handleError(e);
      return null;
    }
  }, [handleError]);

  // Save Session
  const saveSession = useCallback(async (
    sessionId: string,
    history: Message[],
    title?: string,
    preferences?: Record<string, unknown>
  ) => {
    try {
      const response = await fetch(`${API_URL}/v2/sessions/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          history,
          title,
          preferences,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Failed to save session: ${response.status}`);
      }
      
      const result = await response.json();
      
      // Updatelocal sessions List
      setSessions(prev => {
        const exists = prev.find(s => s.id === sessionId);
        if (exists) {
          return prev.map(s => s.id === sessionId ? {
            ...s,
            title: title || s.title,
            message_count: history.length,
            updated_at: new Date().toISOString(),
          } : s);
        }
        // New Session，AddtoListOnHead
        return [{
          id: sessionId,
          title: title || 'New Session',
          preview: history[0]?.content?.slice(0, 50) || '',
          message_count: history.length,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        }, ...prev];
      });
      
      return result;
    } catch (e) {
      handleError(e);
      return null;
    }
  }, [handleError]);

  // Delete Session
  const deleteSession = useCallback(async (sessionId: string) => {
    try {
      const response = await fetch(`${API_URL}/v2/sessions/${sessionId}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        throw new Error(`Failed to delete session: ${response.status}`);
      }
      
      // fromlocalListRemove
      setSessions(prev => prev.filter(s => s.id !== sessionId));
      return true;
    } catch (e) {
      handleError(e);
      return false;
    }
  }, [handleError]);

  // AutoLoad
  useEffect(() => {
    if (autoLoad) {
      loadSessions();
    }
  }, [autoLoad, loadSessions]);

  return {
    // State
    sessions,
    isLoading,
    error,
    
    // Actions
    loadSessions,
    loadSession,
    saveSession,
    deleteSession,
    
    // Helpers
    refreshSessions: () => loadSessions(),
  };
}

export default useSessionPersist;

