import { useEffect, useRef, useState, useCallback } from 'react';

export type ConnectionState = 'connecting' | 'connected' | 'disconnected' | 'reconnecting';

interface UseWebSocketOptions {
  url: string;
  onMessage?: (data: unknown) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  heartbeatInterval?: number; // ms
  reconnectDelay?: number; // ms, initial delay
  maxReconnectDelay?: number; // ms
  maxReconnectAttempts?: number;
}

interface UseWebSocketReturn {
  state: ConnectionState;
  send: (data: unknown) => void;
  reconnect: () => void;
  disconnect: () => void;
}

/**
 * useWebSocket - Robust WebSocket hook with heartbeat and auto-reconnect
 * 
 * Features:
 * - Automatic reconnection with exponential backoff
 * - Ping/pong heartbeat to detect dead connections
 * - Connection state management
 * - Graceful cleanup
 */
export function useWebSocket({
  url,
  onMessage,
  onConnect,
  onDisconnect,
  heartbeatInterval = 30000, // 30 seconds
  reconnectDelay = 2000, // Start with 2 seconds (reduced frequency)
  maxReconnectDelay = 15000, // Max 15 seconds
  maxReconnectAttempts = 20, // Limit attempts to avoid resource exhaustion
}: UseWebSocketOptions): UseWebSocketReturn {
  const [state, setState] = useState<ConnectionState>('disconnected');
  
  const wsRef = useRef<WebSocket | null>(null);
  const heartbeatTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const currentDelayRef = useRef(reconnectDelay);
  const isMountedRef = useRef(true);
  const shouldReconnectRef = useRef(true);
  // Unique instance ID to prevent cleanup race conditions
  const instanceIdRef = useRef(Math.random().toString(36).slice(2));

  // Cleanup timers
  const clearTimers = useCallback(() => {
    if (heartbeatTimerRef.current) {
      clearInterval(heartbeatTimerRef.current);
      heartbeatTimerRef.current = null;
    }
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
  }, []);

  // Start heartbeat
  const startHeartbeat = useCallback(() => {
    if (heartbeatTimerRef.current) {
      clearInterval(heartbeatTimerRef.current);
    }
    
    heartbeatTimerRef.current = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        try {
          wsRef.current.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }));
        } catch {
          // Heartbeat failed silently
        }
      }
    }, heartbeatInterval);
  }, [heartbeatInterval]);

  // Connect to WebSocket
  const connect = useCallback(() => {
    const currentInstanceId = instanceIdRef.current;
    
    // Don't connect if already connecting/connected or unmounted
    if (!isMountedRef.current || !shouldReconnectRef.current) return;
    if (wsRef.current?.readyState === WebSocket.OPEN || 
        wsRef.current?.readyState === WebSocket.CONNECTING) {
      return;
    }
    
    // Clear any existing WebSocket first
    if (wsRef.current) {
      try {
        wsRef.current.close();
      } catch {
        // Ignore close errors
      }
      wsRef.current = null;
    }

    setState('connecting');
    
    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        // Check if this is still the current instance
        if (!isMountedRef.current || currentInstanceId !== instanceIdRef.current) {
          ws.close();
          return;
        }
        
        setState('connected');
        reconnectAttemptsRef.current = 0;
        currentDelayRef.current = reconnectDelay;
        
        startHeartbeat();
        onConnect?.();
      };

      ws.onclose = () => {
        // Only handle close for current instance
        if (!isMountedRef.current || currentInstanceId !== instanceIdRef.current) return;
        
        clearTimers();
        wsRef.current = null;
        setState('disconnected');
        onDisconnect?.();
        
        // Auto-reconnect with exponential backoff
        if (shouldReconnectRef.current && 
            reconnectAttemptsRef.current < maxReconnectAttempts) {
          setState('reconnecting');
          
          const delay = currentDelayRef.current;
          
          reconnectTimerRef.current = setTimeout(() => {
            reconnectAttemptsRef.current++;
            currentDelayRef.current = Math.min(
              currentDelayRef.current * 1.5,
              maxReconnectDelay
            );
            connect();
          }, delay);
        }
      };

      ws.onerror = () => {
        // Don't close here - let onclose handle reconnection
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // Handle pong internally
          if (data.type === 'pong') {
            return;
          }
          
          onMessage?.(data);
        } catch {
          // Failed to parse message
        }
      };
    } catch {
      setState('disconnected');
    }
  }, [url, reconnectDelay, maxReconnectDelay, maxReconnectAttempts, startHeartbeat, clearTimers, onConnect, onDisconnect, onMessage]);

  // Send message
  const send = useCallback((data: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      try {
        wsRef.current.send(JSON.stringify(data));
      } catch {
        // Failed to send
      }
    }
  }, []);

  // Manual reconnect
  const reconnect = useCallback(() => {
    shouldReconnectRef.current = true;
    reconnectAttemptsRef.current = 0;
    currentDelayRef.current = reconnectDelay;
    
    if (wsRef.current) {
      wsRef.current.close();
    } else {
      connect();
    }
  }, [connect, reconnectDelay]);

  // Manual disconnect
  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false;
    clearTimers();
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setState('disconnected');
  }, [clearTimers]);

  // Initial connection
  useEffect(() => {
    isMountedRef.current = true;
    shouldReconnectRef.current = true;
    connect();

    return () => {
      // Generate new instance ID to invalidate any pending operations
      instanceIdRef.current = Math.random().toString(36).slice(2);
      
      isMountedRef.current = false;
      shouldReconnectRef.current = false;
      clearTimers();
      
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url]); // Only reconnect when URL changes

  return { state, send, reconnect, disconnect };
}

