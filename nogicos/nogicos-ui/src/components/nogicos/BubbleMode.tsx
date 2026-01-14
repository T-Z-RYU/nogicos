/**
 * BubbleMode - Bubble-Native Mode Full Page
 * 
 * Fullscreen canvas + floating chat panel design
 * - Canvas fills screen: neural network connection visualization
 * - Floating chat panel: draggable, collapsible
 * - Bottom floating input bar
 */

import { useState, useCallback, useRef, useEffect, memo, useMemo } from 'react';
import type { KeyboardEvent } from 'react';
import { useChat } from '@ai-sdk/react';
import { DefaultChatTransport } from 'ai';
import { motion, AnimatePresence } from 'motion/react';
import { ArrowUp, Square, Zap, Crosshair } from 'lucide-react';
import { cn } from '@/lib/utils';
import { BubbleCanvas } from './BubbleCanvas';
import { FloatingChatPanel } from './FloatingChatPanel';
import { BubbleSidebar, type Session } from './BubbleSidebar';
import { ContextInsightPanel, type Suggestion } from './ContextInsightPanel';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { useWebSocket } from '@/hooks/useWebSocket';

// ============================================================================
// Types
// ============================================================================

interface WindowInfo {
  hwnd: number;
  title: string;
  app_name: string;
  app_display_name: string;
  icon_base64?: string;
  is_browser: boolean;
}

interface ConnectedApp extends WindowInfo {
  connected_at: string;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  toolInvocations?: ToolInvocation[];
  timestamp?: number;  // For sorting messages from different sources
}

interface ToolInvocation {
  toolCallId: string;
  toolName: string;
  args: Record<string, unknown>;
  state: 'partial-call' | 'call' | 'result';
  result?: unknown;
}

// WebSocket event-driven state types
interface DataFlow {
  sourceHwnd: number | null;
  targetHwnd: number | null;
  direction: 'in' | 'out';
  action?: string;
}

interface ThinkingStateInput {
  isThinking: boolean;
  content: string;
  durationMs?: number;
}

interface BubbleModeProps {
  apiUrl?: string;
  sessionId?: string;
  initialWindows?: WindowInfo[];
  onBack?: () => void;
  className?: string;
  // Session management
  sessions?: Session[];
  activeSessionId?: string;
  onNewSession?: () => void;
  onSelectSession?: (id: string) => void;
  onDeleteSession?: (id: string) => void;
  // 🔥 WebSocket Eventdriver's State（fromself App.tsx）
  dataFlow?: DataFlow;
  thinkingState?: ThinkingStateInput;
  connectedAppsFromParent?: ConnectedApp[];  // Connected apps from parent component
  onConnectedAppsChange?: (apps: ConnectedApp[]) => void;
}

// ============================================================================
// Constants
// ============================================================================

const SPRING = {
  gentle: { type: 'spring' as const, stiffness: 120, damping: 14 },
  snappy: { type: 'spring' as const, stiffness: 400, damping: 25 },
};

// ============================================================================
// 2026: View Transitions API support
// ============================================================================

/**
 * Usage View Transitions API ExecuteState变化
 * Auto回退到普通Update如果浏览器不支持
 */
async function withViewTransition(callback: () => void | Promise<void>): Promise<void> {
  // @ts-expect-error - View Transitions API class type definition not yet built-in
  if (document.startViewTransition) {
    // @ts-expect-error
    await document.startViewTransition(async () => {
      await callback();
    }).finished;
  } else {
    await callback();
  }
}

/**
 * 带有自定义Transition名称的 View Transition
 */
function setViewTransitionName(element: HTMLElement | null, name: string | null): void {
  if (element) {
    // @ts-expect-error - viewTransitionName YesNewProperty
    element.style.viewTransitionName = name || '';
  }
}

// ============================================================================
// Main BubbleMode Component
// ============================================================================

export const BubbleMode = memo(function BubbleMode({
  apiUrl = 'http://localhost:8080/api/chat',
  sessionId,
  initialWindows = [],
  onBack,
  className,
  // Session management with defaults
  sessions: propSessions,
  activeSessionId: propActiveSessionId,
  onNewSession: propOnNewSession,
  onSelectSession: propOnSelectSession,
  onDeleteSession: propOnDeleteSession,
  // 🔥 WebSocket Eventdriver's State（fromself App.tsx）
  dataFlow: wsDataFlow,
  thinkingState: wsThinkingState,
  connectedAppsFromParent,
  onConnectedAppsChange,
}: BubbleModeProps) {
  // Session state (use props or internal state)
  const [internalSessions, setInternalSessions] = useState<Session[]>([
    { id: '1', title: 'Current Session', preview: 'Active conversation...', timestamp: new Date() }
  ]);
  const [internalActiveSessionId, setInternalActiveSessionId] = useState('1');
  
  const sessions = propSessions ?? internalSessions;
  const activeSessionIdState = propActiveSessionId ?? internalActiveSessionId;
  
  const handleNewSession = useCallback(() => {
    if (propOnNewSession) {
      propOnNewSession();
    } else {
      const newId = Date.now().toString();
      setInternalSessions(prev => [
        { id: newId, title: `Session ${prev.length + 1}`, preview: 'New session...', timestamp: new Date() },
        ...prev
      ]);
      setInternalActiveSessionId(newId);
    }
  }, [propOnNewSession]);
  
  const handleSelectSession = useCallback((id: string) => {
    if (propOnSelectSession) {
      propOnSelectSession(id);
    } else {
      setInternalActiveSessionId(id);
    }
  }, [propOnSelectSession]);
  
  const handleDeleteSession = useCallback((id: string) => {
    if (propOnDeleteSession) {
      propOnDeleteSession(id);
    } else {
      setInternalSessions(prev => prev.filter(s => s.id !== id));
    }
  }, [propOnDeleteSession]);
  
  // App state
  const [availableWindows, setAvailableWindows] = useState<WindowInfo[]>(initialWindows);
  const [internalConnectedApps, setInternalConnectedApps] = useState<ConnectedApp[]>([]);
  
  // 🔥 PriorityUsageParentComponenttransmitenter's  connectedApps
  const connectedApps = connectedAppsFromParent ?? internalConnectedApps;
  const setConnectedApps = onConnectedAppsChange ?? setInternalConnectedApps;
  
  const [activeAppHwnd, setActiveAppHwnd] = useState<number | undefined>(undefined);
  const [aiState, setAiState] = useState<'idle' | 'thinking' | 'reading' | 'acting' | 'success'>('idle');
  
  // 2026 toplevel: OutputType semanticizeState (formoveeffect)
  type OutputType = 'idle' | 'observing' | 'analyzing' | 'planning' | 'writing' | 'sending' | 'waiting' | 'completed' | 'error';
  const [outputType, setOutputType] = useState<OutputType>('idle');
  const [targetHwnd, setTargetHwnd] = useState<number | null>(null);
  const [sourceHwnd, setSourceHwnd] = useState<number | null>(null);
  
  // ============================================================================
  // 🔥 WebSocket EventListen - directlyListenAfterendState，driver Canvas canvisualization
  // ============================================================================
  const connectedAppsRef = useRef(connectedApps);
  useEffect(() => { connectedAppsRef.current = connectedApps; }, [connectedApps]);
  
  const handleWsMessage = useCallback((data: unknown) => {
    // AfterendSendFormat: { type: "tool_start", data: { name: "xxx", id: "xxx" } }
    const msg = data as {
      type: string;
      data?: {
        name?: string;
        id?: string;
        status?: string;
      };
      tool_id?: string;
      tool_name?: string;
      result?: string;
      error?: string;
    };
    
    const apps = connectedAppsRef.current;
    
    // from data.name or tool_name GetToolname
    const toolNameFromMsg = msg.data?.name || msg.tool_name;
    const toolIdFromMsg = msg.data?.id || msg.tool_id;
    
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'BubbleMode.tsx:handleWsMessage',message:'H1: WS message received',data:{type:msg.type,tool_name:toolNameFromMsg,tool_id:toolIdFromMsg,appsCount:apps.length,rawData:msg.data},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H1'})}).catch(()=>{});
    // #endregion
    
    switch (msg.type) {
      case 'thinking_start':
        console.log('[BubbleMode] 🧠 Thinking started');
        setAiState('thinking');
        setOutputType('analyzing');
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'BubbleMode.tsx:thinking_start',message:'H3: State set to thinking',data:{aiState:'thinking',outputType:'analyzing'},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H3'})}).catch(()=>{});
        // #endregion
        break;
        
      case 'thinking_end':
        console.log('[BubbleMode] 🧠 Thinking ended');
        break;
        
      case 'tool_start':
        console.log('[BubbleMode] 🔧 Tool started:', toolNameFromMsg);
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'BubbleMode.tsx:tool_start:entry',message:'H2: tool_start received',data:{tool_name:toolNameFromMsg,appsCount:apps.length,appsNames:apps.map(a=>a.app_name)},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H2'})}).catch(()=>{});
        // #endregion
        
        if (toolNameFromMsg && apps.length > 0) {
          const toolName = toolNameFromMsg.toLowerCase();
          
          // JudgeActionClasstype
          const isReadOp = toolName.includes('read') || toolName.includes('get') || 
                          toolName.includes('list') || toolName.includes('search') ||
                          toolName.includes('snapshot') || toolName.includes('ocr');
          const isWriteOp = toolName.includes('write') || toolName.includes('click') ||
                          toolName.includes('type') || toolName.includes('fill') ||
                          toolName.includes('navigate');
          const isSendOp = toolName.includes('send') || toolName.includes('whatsapp') ||
                          toolName.includes('email') || toolName.includes('message');
          
          // RootdataToolnameinferTargetApply
          let targetApp = apps[0];
          
          if (toolName.includes('cursor') || toolName.includes('code') || toolName.includes('ide') || toolName.includes('read_file')) {
            targetApp = apps.find(a => a.app_name.toLowerCase().includes('cursor')) || targetApp;
          } else if (toolName.includes('chrome') || toolName.includes('browser') || toolName.includes('playwright') || toolName.includes('navigate') || toolName.includes('fill_form') || toolName.includes('click') || toolName.includes('type')) {
            targetApp = apps.find(a => a.app_name.toLowerCase().includes('chrome') || a.is_browser) || targetApp;
          } else if (toolName.includes('whatsapp')) {
            targetApp = apps.find(a => a.app_name.toLowerCase().includes('whatsapp')) || targetApp;
          }
          
          // #region agent log
          fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'BubbleMode.tsx:tool_start:classify',message:'H2: Operation classified',data:{toolName,isReadOp,isWriteOp,isSendOp,targetAppName:targetApp?.app_name,targetAppHwnd:targetApp?.hwnd},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H2'})}).catch(()=>{});
          // #endregion
          
          if (isReadOp) {
            setAiState('reading');
            setOutputType('observing');
            setSourceHwnd(targetApp.hwnd);
            setTargetHwnd(null);
            // #region agent log
            fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'BubbleMode.tsx:tool_start:setRead',message:'H3: State set to reading',data:{aiState:'reading',outputType:'observing',sourceHwnd:targetApp.hwnd},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H3'})}).catch(()=>{});
            // #endregion
          } else if (isSendOp) {
            setAiState('acting');
            setOutputType('sending');
            setSourceHwnd(null);
            setTargetHwnd(targetApp.hwnd);
            // #region agent log
            fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'BubbleMode.tsx:tool_start:setSend',message:'H3: State set to sending',data:{aiState:'acting',outputType:'sending',targetHwnd:targetApp.hwnd},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H3'})}).catch(()=>{});
            // #endregion
          } else if (isWriteOp) {
            setAiState('acting');
            setOutputType('writing');
            setSourceHwnd(null);
            setTargetHwnd(targetApp.hwnd);
            // #region agent log
            fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'BubbleMode.tsx:tool_start:setWrite',message:'H3: State set to writing',data:{aiState:'acting',outputType:'writing',targetHwnd:targetApp.hwnd},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H3'})}).catch(()=>{});
            // #endregion
          } else {
            setAiState('thinking');
            setOutputType('analyzing');
            // #region agent log
            fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'BubbleMode.tsx:tool_start:setDefault',message:'H3: State set to default analyzing',data:{aiState:'thinking',outputType:'analyzing'},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H3'})}).catch(()=>{});
            // #endregion
          }
        } else {
          // #region agent log
          fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'BubbleMode.tsx:tool_start:skip',message:'H2: tool_start skipped - no tool_name or no apps',data:{hasToolName:!!msg.tool_name,appsCount:apps.length},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H2'})}).catch(()=>{});
          // #endregion
        }
        break;
        
      case 'tool_result':
        console.log('[BubbleMode] 🔧 Tool completed:', msg.tool_id);
        break;
        
      case 'task_complete':
        console.log('[BubbleMode] ✅ Task complete');
        setAiState('success');
        setOutputType('completed');
        setTimeout(() => {
          setAiState('idle');
          setOutputType('idle');
          setSourceHwnd(null);
          setTargetHwnd(null);
        }, 2000);
        break;
        
      case 'task_error':
        console.log('[BubbleMode] ❌ Task error');
        setAiState('idle');
        setOutputType('error');
        setTimeout(() => {
          setOutputType('idle');
        }, 2000);
        break;
        
      case 'execution_complete':
        console.log('[BubbleMode] ✅ Execution complete');
        setAiState('success');
        setOutputType('completed');
        setTimeout(() => {
          setAiState('idle');
          setOutputType('idle');
          setSourceHwnd(null);
          setTargetHwnd(null);
        }, 2000);
        break;
    }
  }, []);
  
  // Connect WebSocket
  useWebSocket({
    url: 'ws://localhost:8765',
    onMessage: handleWsMessage,
    onConnect: () => {
      console.log('[BubbleMode] 🔌 WebSocket connected');
    },
    heartbeatInterval: 30000,
    reconnectDelay: 2000,
  });
  
  // Input state
  const [localInput, setLocalInput] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  
  // Drag connector state
  const [isDragging, setIsDragging] = useState(false);
  const windowsRef = useRef(availableWindows);
  useEffect(() => { windowsRef.current = availableWindows; }, [availableWindows]);
  
  // Context insight state - Level 3 Smartperception (SupportmultipleApplyCompose)
  const [insightApps, setInsightApps] = useState<Array<{
    hwnd: number;
    appName: string;
    appType: 'desktop' | 'browser' | 'ide';
  }>>([]);
  
  // YesNoDisplayComposeAnalyzePattern
  const isMultiAppInsight = insightApps.length > 1;
  
  // Chat transport
  const chatTransport = useMemo(() => new DefaultChatTransport({
    api: apiUrl,
    body: { 
      session_id: sessionId,
      connected_apps: connectedApps,
    },
  }), [apiUrl, sessionId, connectedApps]);
  
  // useChat hook (from @assistant-ui/react)
  const {
    messages,
    sendMessage,
    stop,
    status,
    error,
  } = useChat({
    id: `bubble-${sessionId}`,
    transport: chatTransport,
    onError: (err) => {
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'BubbleMode.tsx:onError',message:'H8: useChat error',data:{error:String(err),errorName:err?.name,errorMessage:err?.message,errorStack:err?.stack?.slice(0,500)},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H8'})}).catch(()=>{});
      // #endregion
      console.error('[BubbleMode] Chat error:', err);
      setAiState('idle');
    },
  });
  
  // Log error state changes
  useEffect(() => {
    if (error) {
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'BubbleMode.tsx:errorEffect',message:'H8: error state',data:{error:String(error),errorName:error?.name,errorMessage:error?.message},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H8'})}).catch(()=>{});
      // #endregion
    }
  }, [error]);
  
  // Track loading state - Repair：byat status notcanrely，UsageMessageInnercontentchangeDetection
  const statusBasedLoading = status === 'submitted' || status === 'streaming';
  
  // Usage ref trackMessageInnercontentLengthfromDetection AI YesNoinOutput
  const lastContentLenRef = useRef(0);
  const [isActuallyLoading, setIsActuallyLoading] = useState(false);
  
  // PollDetectionMessageInnercontentchange
  useEffect(() => {
    const checkInterval = setInterval(() => {
      if (!messages || messages.length === 0) return;
      
      const lastMsg = messages[messages.length - 1];
      if (lastMsg.role !== 'assistant') return;
      
      const content = (lastMsg as { content?: string })?.content || '';
      const currentLen = content.length;
      
      if (currentLen > lastContentLenRef.current) {
        // InnercontentinincreaseLong，AI currentlywork
        setIsActuallyLoading(true);
        lastContentLenRef.current = currentLen;
      } else if (currentLen === lastContentLenRef.current && isActuallyLoading) {
        // InnercontentStopincreaseLong，DelayedonePointagainMarkforComplete
        setTimeout(() => {
          if (lastContentLenRef.current === currentLen) {
            setIsActuallyLoading(false);
          }
        }, 500);
      }
    }, 100); // each 100ms Checkonce
    
    return () => clearInterval(checkInterval);
  }, [messages, isActuallyLoading]);
  
  // ComposetwokindDetectionway (for UI State)
  const isLoading = statusBasedLoading || isActuallyLoading;
  
  // Note: Canvas state now by WebSocket Eventdirectly driven (see above handleWsMessage）
  // isLoading onlyforInputboxDisableandStopButtonDisplay
  
  // RecordUponceMessageCountandInnercontentLength，forDetection AI YesNoinwork
  const prevMessagesRef = useRef<{ count: number; lastContentLen: number }>({ count: 0, lastContentLen: 0 });
  
  // 2026 toplevel: based on messagechangeDetection AI State（bypass unreliable's  status）
  useEffect(() => {
    // IfnoConnectanyApply，notSetTarget
    if (connectedApps.length === 0) {
      setTargetHwnd(null);
      setSourceHwnd(null);
      return;
    }
    
    if (!messages || messages.length === 0) return;
    
    const lastMsg = messages[messages.length - 1];
    const lastContent = (lastMsg as { content?: string })?.content || '';
    const currentCount = messages.length;
    const currentLen = lastContent.length;
    const prev = prevMessagesRef.current;
    
    // Detection AI YesNocurrentlyOutput：Messagenumberincreaseadd or mostAfteroneitemMessageInnercontentLengthincreaseadd
    const isAIWorking = lastMsg.role === 'assistant' && (
      currentCount > prev.count || 
      currentLen > prev.lastContentLen
    );
    
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'BubbleMode.tsx:outputTypeEffect:entry',message:'H6: Checking AI working state',data:{isAIWorking,currentCount,prevCount:prev.count,currentLen,prevLen:prev.lastContentLen,lastRole:lastMsg.role},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H6'})}).catch(()=>{});
    // #endregion
    
    // Update ref
    prevMessagesRef.current = { count: currentCount, lastContentLen: currentLen };
    
    // Smartinfer：based on messagechangeDetection AI YesNoinwork
    if (isAIWorking) {
      // AI currentlyworktime，based on messageInnercontentinferActionClasstype
      const lastMsg = messages?.[messages.length - 1];
      const lastContent = (lastMsg as { content?: string })?.content?.toLowerCase() || '';
      
      // CheckYesNohaveToolCall（AI SDK 5.0 Usage parts Format）
      const msgAny = lastMsg as { 
        parts?: Array<{
          type: string;
          toolCallId?: string;
          toolName?: string;
          args?: Record<string, unknown>;
          result?: unknown;
        }>;
      };
      
      let detectedOutputType: OutputType = 'analyzing';
      let detectedSourceHwnd: number | null = null;
      let detectedTargetHwnd: number | null = null;
      
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'BubbleMode.tsx:toolDetection:start',message:'H1: Checking message format for tools',data:{hasParts:!!msgAny.parts,partsCount:msgAny.parts?.length,partsTypes:msgAny.parts?.map(p=>p.type),hasToolInvocations:!!(lastMsg as {toolInvocations?:unknown[]}).toolInvocations,toolInvocationsCount:((lastMsg as {toolInvocations?:unknown[]}).toolInvocations || []).length,msgKeys:Object.keys(lastMsg || {}),connectedAppsHwnds:connectedApps.map(a=>({hwnd:a.hwnd,name:a.app_display_name}))},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H1'})}).catch(()=>{});
      // #endregion
      
      // alsoCheck toolInvocations Field（AI SDK maybeUsagethisField）
      const toolInvocations = (lastMsg as {toolInvocations?: Array<{toolName?:string;state?:string;args?:Record<string,unknown>}>}).toolInvocations;
      
      // Check parts Medium's ToolCall
      if (msgAny.parts && msgAny.parts.length > 0) {
        const toolParts = msgAny.parts.filter(p => p.type === 'tool-invocation' || p.type === 'tool-call');
        if (toolParts.length > 0) {
          const lastTool = toolParts[toolParts.length - 1];
          const toolName = lastTool.toolName?.toLowerCase() || '';
          
          // RootdataToolnameSet outputType
          if (toolName.includes('read') || toolName.includes('screen') || toolName.includes('snapshot') || toolName.includes('ocr') || toolName.includes('get')) {
            detectedOutputType = 'observing';
            detectedSourceHwnd = connectedApps[0].hwnd;
          } else if (toolName.includes('write') || toolName.includes('edit') || toolName.includes('type') || toolName.includes('fill') || toolName.includes('set')) {
            detectedOutputType = 'writing';
            detectedTargetHwnd = connectedApps[connectedApps.length > 1 ? 1 : 0].hwnd;
          } else if (toolName.includes('send') || toolName.includes('submit') || toolName.includes('whatsapp') || toolName.includes('email')) {
            detectedOutputType = 'sending';
            detectedTargetHwnd = connectedApps[connectedApps.length > 1 ? connectedApps.length - 1 : 0].hwnd;
          } else if (toolName.includes('click') || toolName.includes('navigate') || toolName.includes('browser')) {
            detectedOutputType = 'observing';
            detectedTargetHwnd = connectedApps[0].hwnd;
          } else {
            detectedOutputType = 'analyzing';
          }
          // #region agent log
          fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'BubbleMode.tsx:toolDetection:fromParts',message:'H1: Tool detected from parts',data:{toolName,detectedOutputType,detectedSourceHwnd,detectedTargetHwnd},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H1'})}).catch(()=>{});
          // #endregion
        }
      }
      
      // If parts noTool，Check toolInvocations Field（AI SDK 5.0 Format）
      if (detectedOutputType === 'analyzing' && toolInvocations && toolInvocations.length > 0) {
        const lastTool = toolInvocations[toolInvocations.length - 1];
        const toolName = lastTool.toolName?.toLowerCase() || '';
        
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'BubbleMode.tsx:toolDetection:fromInvocations',message:'H1: Checking toolInvocations',data:{toolName,state:lastTool.state,argsKeys:Object.keys(lastTool.args || {})},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H1'})}).catch(()=>{});
        // #endregion
        
        if (toolName.includes('read') || toolName.includes('screen') || toolName.includes('snapshot') || toolName.includes('ocr') || toolName.includes('get')) {
          detectedOutputType = 'observing';
          detectedSourceHwnd = connectedApps[0].hwnd;
        } else if (toolName.includes('write') || toolName.includes('edit') || toolName.includes('type') || toolName.includes('fill') || toolName.includes('set')) {
          detectedOutputType = 'writing';
          detectedTargetHwnd = connectedApps[connectedApps.length > 1 ? 1 : 0].hwnd;
        } else if (toolName.includes('send') || toolName.includes('submit') || toolName.includes('whatsapp') || toolName.includes('email')) {
          detectedOutputType = 'sending';
          detectedTargetHwnd = connectedApps[connectedApps.length > 1 ? connectedApps.length - 1 : 0].hwnd;
        } else if (toolName.includes('click') || toolName.includes('navigate') || toolName.includes('browser')) {
          detectedOutputType = 'observing';
          detectedTargetHwnd = connectedApps[0].hwnd;
        }
        
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'BubbleMode.tsx:toolDetection:invocationsResult',message:'H1: Tool detected from invocations',data:{toolName,detectedOutputType,detectedSourceHwnd,detectedTargetHwnd},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H1'})}).catch(()=>{});
        // #endregion
      }
      
      // 🔥 KeyRepair：fromMessageInnercontentMediumRecognitionConcrete's Applyname
      const findAppByName = (content: string): ConnectedApp | undefined => {
        const contentLower = content.toLowerCase();
        return connectedApps.find(app => {
          const appName = app.app_name.toLowerCase();
          const displayName = app.app_display_name.toLowerCase();
          // MatchApplyname（SupportMediumenglishtext）
          return contentLower.includes(appName) || 
                 contentLower.includes(displayName) ||
                 (appName.includes('cursor') && contentLower.includes('cursor')) ||
                 (appName.includes('chrome') && (contentLower.includes('chrome') || contentLower.includes('浏览器'))) ||
                 (appName.includes('whatsapp') && (contentLower.includes('whatsapp') || contentLower.includes('Message')));
        });
      };
      
      // if no tool detected，fromMessageInnercontentinfer（Enhancementkeyword matching + app name recognition）
      if (detectedOutputType === 'analyzing' && lastContent) {
        // 🔥 firsttryRecognitionMessageMediummentionto's ConcreteApply
        const mentionedApp = findAppByName(lastContent);
        
        // ReadClassKeyword
        if (lastContent.includes('Read') || lastContent.includes('Get') || lastContent.includes('view') || 
            lastContent.includes('截Graph') || lastContent.includes('扫描') || lastContent.includes('Analyze') ||
            lastContent.includes('Find') || lastContent.includes('Search') || lastContent.includes('浏览')) {
          detectedOutputType = 'observing';
          // 🔥 UsageMessageMediummentionto's Apply，andnotYesPinFirsta
          detectedSourceHwnd = mentionedApp?.hwnd || connectedApps[0].hwnd;
        // WriteClassKeyword
        } else if (lastContent.includes('Write') || lastContent.includes('Input') || lastContent.includes('填Write') || 
                   lastContent.includes('Modify') || lastContent.includes('Edit') || lastContent.includes('Update') ||
                   lastContent.includes('yc') || lastContent.includes('Apply')) {
          detectedOutputType = 'writing';
          // 🔥 UsageMessageMediummentionto's Apply
          detectedTargetHwnd = mentionedApp?.hwnd || connectedApps[connectedApps.length > 1 ? 1 : 0].hwnd;
        // SendClassKeyword (PrioritylevelmostHigh)
        } else if (lastContent.includes('Send') || lastContent.includes('Commit') || lastContent.includes('whatsapp') ||
                   lastContent.includes('Notify') || lastContent.includes('告知') || lastContent.includes('推送') ||
                   lastContent.includes('团队')) {
          detectedOutputType = 'sending';
          // Find WhatsApp Apply
          const waApp = connectedApps.find(a => 
            a.app_name.toLowerCase().includes('whatsapp') || 
            a.app_display_name.toLowerCase().includes('whatsapp')
          );
          detectedTargetHwnd = waApp?.hwnd || mentionedApp?.hwnd || connectedApps[connectedApps.length - 1].hwnd;
        } else if (mentionedApp) {
          // 🔥 even ifnoMatchtoactionKeyword，onlyneedmentiontoApplyname，thentoitsetfor source
          detectedOutputType = 'observing';
          detectedSourceHwnd = mentionedApp.hwnd;
        }
      }
      
      // default case：IfnoRecognitiontoConcreteApply，UsageFirsta
      if (detectedOutputType === 'analyzing' && connectedApps.length > 0 && !detectedSourceHwnd) {
        detectedSourceHwnd = connectedApps[0].hwnd;
      }
      
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'BubbleMode.tsx:outputTypeEffect:setting',message:'H2,H3: Setting outputType and hwnds',data:{detectedOutputType,detectedSourceHwnd,detectedTargetHwnd,firstConnectedHwnd:connectedApps[0]?.hwnd},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H2,H3'})}).catch(()=>{});
      // #endregion
      setOutputType(detectedOutputType);
      setSourceHwnd(detectedSourceHwnd);
      setTargetHwnd(detectedTargetHwnd);
    }
    // ready State's Handleinanother useEffect Medium
  }, [messages, connectedApps]);
  
  // Convert messages to ChatMessage format, memoized
  const chatMessages: ChatMessage[] = useMemo(() => {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'BubbleMode.tsx:chatMessages',message:'H2: Converting messages',data:{messagesCount:messages?.length || 0,messagesPreview:(messages || []).slice(0,2).map(m=>({id:m.id,role:m.role,hasContent:!!(m as {content?:string}).content,hasParts:!!((m as {parts?:unknown[]}).parts)}))},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H2'})}).catch(()=>{});
    // #endregion
    
    try {
      return (messages || []).map((msg, index) => {
        const msgAny = msg as { content?: string; parts?: Array<{ type: string; text?: string }> };
        let content = msgAny.content || '';
        
        if (!content && msgAny.parts) {
          content = msgAny.parts
            .filter(p => p && p.type === 'text')
            .map(p => p.text || '')
            .join('');
        }
        
        // #region agent log
        if (index < 3) {
          fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'BubbleMode.tsx:chatMessages:item',message:'H2: Message converted',data:{index,id:msg.id,role:msg.role,contentLength:content?.length,contentPreview:content?.slice(0,50)},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H2'})}).catch(()=>{});
        }
        // #endregion
        
        return {
          id: msg.id,
          role: msg.role as 'user' | 'assistant',
          content,
          // Note: Don't pass timestamp here - MessageBubble expects Date, we have number
        };
      });
    } catch (err) {
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'BubbleMode.tsx:chatMessages:error',message:'H2: Conversion error',data:{error:String(err)},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H2'})}).catch(()=>{});
      // #endregion
      return [];
    }
  }, [messages]);
  
  // Fetch available windows
  useEffect(() => {
    const fetchWindows = async () => {
      try {
        const response = await fetch('http://localhost:8080/api/windows');
        if (response.ok) {
          const data = await response.json();
          if (data.windows && data.windows.length > 0) {
            setAvailableWindows(data.windows);
          }
        }
      } catch (error) {
        console.error('Failed to fetch windows:', error);
      }
    };
    
    fetchWindows();
    const interval = setInterval(fetchWindows, 5000);
    return () => clearInterval(interval);
  }, []);
  
  // Handle connect app - Trigger Overlay specialeffect + Smartperception（SupportmultipleApplyCompose）
  const handleConnect = useCallback(async (window: WindowInfo) => {
    const newApp: ConnectedApp = {
      ...window,
      connected_at: new Date().toISOString(),
    };
    
    // UpdatealreadyConnectApplyList
    const updatedApps = [...connectedApps, newApp];
    setConnectedApps(updatedApps);
    setActiveAppHwnd(window.hwnd);
    
    // JudgeApplyClasstype
    const getAppType = (app: WindowInfo): 'desktop' | 'browser' | 'ide' => {
      const appNameLower = app.app_name.toLowerCase();
      if (app.is_browser) return 'browser';
      if (appNameLower.includes('cursor') || appNameLower.includes('code') || appNameLower.includes('idea')) return 'ide';
      return 'desktop';
    };
    
    // BuildallalreadyConnectApply's  insight List
    const allInsightApps = updatedApps.map(app => ({
      hwnd: app.hwnd,
      appName: app.app_display_name || app.app_name,
      appType: getAppType(app),
    }));
    
    // Update insightApps（TriggerComposeAnalyze）
    setInsightApps(allInsightApps);
    
    console.log('[BubbleMode] Connected apps count:', updatedApps.length, 
      updatedApps.length > 1 ? '(multi-app analysis mode)' : '(single-app mode)');
    
    // Trigger Overlay specialeffect（Ifin Electron EnvironmentMedium）
    if (typeof globalThis !== 'undefined' && (globalThis as Window & { electronAPI?: unknown }).electronAPI) {
      const electronAPI = (globalThis as Window & { 
        electronAPI: { 
          attachOverlay: (title: string, type: string) => Promise<unknown>;
          createMultiOverlay: (hwnd: number, type: string, title: string) => Promise<unknown>;
        } 
      }).electronAPI;
      
      try {
        // PriorityUsagemultipleWindow Overlay（SupportmultipleaApplymeanwhileDisplayBorder）
        await electronAPI.createMultiOverlay(
          window.hwnd,
          window.is_browser ? 'browser' : 'desktop',
          window.title
        );
        console.log('[BubbleMode] Overlay created for:', window.app_display_name);
      } catch (e) {
        console.warn('[BubbleMode] Failed to create overlay:', e);
        // FallbacktosingleWindow Overlay
        try {
          await electronAPI.attachOverlay(window.title, window.is_browser ? 'browser' : 'desktop');
        } catch (e2) {
          console.warn('[BubbleMode] Fallback overlay also failed:', e2);
        }
      }
    }
  }, [connectedApps]);
  
  // Handle disconnect app - Destroy Overlay + UpdateSmartperception
  const handleDisconnect = useCallback(async (hwnd: number) => {
    // UpdatealreadyConnectApplyList
    const remainingApps = connectedApps.filter(app => app.hwnd !== hwnd);
    setConnectedApps(remainingApps);
    
    if (activeAppHwnd === hwnd) {
      setActiveAppHwnd(undefined);
    }
    
    // AdaptiveUpdateSmartperceptionPanel
    const getAppType = (app: WindowInfo): 'desktop' | 'browser' | 'ide' => {
      const appNameLower = app.app_name.toLowerCase();
      if (app.is_browser) return 'browser';
      if (appNameLower.includes('cursor') || appNameLower.includes('code') || appNameLower.includes('idea')) return 'ide';
      return 'desktop';
    };
    
    if (remainingApps.length === 0) {
      // noApply，ClosePanel
      setInsightApps([]);
    } else {
      // UpdateforremainingApply's ComposeAnalyze
      setInsightApps(remainingApps.map(app => ({
        hwnd: app.hwnd,
        appName: app.app_display_name || app.app_name,
        appType: getAppType(app),
      })));
    }
    
    console.log('[BubbleMode] Disconnected, remaining apps:', remainingApps.length);
    
    // Destroy Overlay（Ifin Electron EnvironmentMedium）
    if (typeof globalThis !== 'undefined' && (globalThis as Window & { electronAPI?: unknown }).electronAPI) {
      const electronAPI = (globalThis as Window & { 
        electronAPI: { 
          destroyMultiOverlay: (hwnd: number) => Promise<unknown>;
          detachOverlay: () => Promise<unknown>;
        } 
      }).electronAPI;
      
      try {
        await electronAPI.destroyMultiOverlay(hwnd);
        console.log('[BubbleMode] Overlay destroyed for hwnd:', hwnd);
      } catch (e) {
        console.warn('[BubbleMode] Failed to destroy overlay:', e);
      }
    }
  }, [activeAppHwnd, connectedApps]);
  
  // Handle clicking already connected app (just focus it)
  const handleOpenLiveArea = useCallback((app: ConnectedApp) => {
    setActiveAppHwnd(app.hwnd);
  }, []);
  
  // Handle send message
  const handleSendMessage = useCallback(async (text: string) => {
    if (!text.trim()) return;
    
    setLocalInput('');
    setAiState('thinking');
    
    // passObjectFormat，with MinimalChatArea onecause
    await sendMessage({ text });
  }, [sendMessage]);
  
  // Handle form submit
  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    handleSendMessage(localInput);
  }, [handleSendMessage, localInput]);
  
  // Handle key down
  const handleKeyDown = useCallback((e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as unknown as React.FormEvent);
    }
  }, [handleSubmit]);
  
  // ============================================================================
  // Drag Connector Logic (reuse ConnectorPanel 's logic)
  // ============================================================================
  
  // BeginDrag
  const handleDragStart = useCallback(async (e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
    
    const electronAPI = (globalThis as Window & { 
      electronAPI?: { 
        startDragConnector?: () => Promise<{ success: boolean }>;
      } 
    }).electronAPI;
    
    if (electronAPI?.startDragConnector) {
      try {
        const result = await electronAPI.startDragConnector();
        console.log('[BubbleMode] Drag connector started:', result);
        if (!result?.success) {
          console.error('[BubbleMode] Failed to start drag connector');
          setIsDragging(false);
        }
      } catch (error) {
        console.error('[BubbleMode] Error starting drag connector:', error);
        setIsDragging(false);
      }
    } else {
      console.warn('[BubbleMode] electronAPI.startDragConnector not available');
      setIsDragging(false);
    }
  }, []);
  
  // HandleDragComplete - ConnectTargetWindow
  const connectTargetWindow = useCallback(async (target: { hwnd: number; title: string }) => {
    // firstRefreshWindowList
    try {
      const response = await fetch('http://localhost:8080/api/windows');
      if (response.ok) {
        const data = await response.json();
        if (data.windows) {
          setAvailableWindows(data.windows);
          windowsRef.current = data.windows;
        }
      }
    } catch (e) {
      console.warn('[BubbleMode] Failed to refresh windows:', e);
    }
    
    // FindTargetWindowInfo
    const currentWindows = windowsRef.current;
    let targetWindow = currentWindows.find(w => w.hwnd === target.hwnd);
    
    if (!targetWindow) {
      // IfWindowListinsideno，useReturn's InfoCreate
      targetWindow = {
        hwnd: target.hwnd,
        title: target.title,
        app_name: '',
        app_display_name: target.title.split(' - ').pop() || target.title,
        is_browser: false,
      };
    }
    
    // ConnectWindow
    await handleConnect(targetWindow);
    console.log('[BubbleMode] Connected via drag:', targetWindow.app_display_name);
  }, [handleConnect]);
  
  // ListenDragCompleteEvent（frommainProcessDetectiontoMouseRelease）
  useEffect(() => {
    const electronAPI = (globalThis as Window & { 
      electronAPI?: { 
        onDragConnectorComplete?: (callback: (target: { hwnd: number; title: string }) => void) => () => void;
      } 
    }).electronAPI;

    if (!electronAPI?.onDragConnectorComplete) {
      return;
    }
    
    const cleanup = electronAPI.onDragConnectorComplete(async (target) => {
      console.log('[BubbleMode] Drag complete from main process:', target);
      setIsDragging(false);

      if (target) {
        await connectTargetWindow(target);
      }
    });

    return cleanup;
  }, [connectTargetWindow]);
  
  // backup：Global mouseup Listen
  const isDraggingRef = useRef(isDragging);
  useEffect(() => { isDraggingRef.current = isDragging; }, [isDragging]);
  
  useEffect(() => {
    if (!isDragging) return;

    const handleGlobalMouseUp = async () => {
      if (!isDraggingRef.current) return;
      
      // DelayedExecute，letmainProcessfirstHandle
      setTimeout(async () => {
        if (isDraggingRef.current) {
          setIsDragging(false);
          
          const electronAPI = (globalThis as Window & { 
            electronAPI?: { 
              endDragConnector?: () => Promise<{ success: boolean; target: { hwnd: number; title: string } | null }>;
            } 
          }).electronAPI;

          if (electronAPI?.endDragConnector) {
            try {
              const result = await electronAPI.endDragConnector();
              if (result?.target) {
                await connectTargetWindow(result.target);
              }
            } catch (error) {
              console.error('[BubbleMode] Error ending drag:', error);
            }
          }
        }
      }, 100);
    };

    document.addEventListener('mouseup', handleGlobalMouseUp);
    return () => document.removeEventListener('mouseup', handleGlobalMouseUp);
  }, [isDragging, connectTargetWindow]);
  
  return (
    <div className={cn(
      "bubble-mode-container relative w-full h-full flex",
      "bg-[#0a0a0a]",
      className
    )}>
      {/* Left Sidebar */}
      <BubbleSidebar
        sessions={sessions}
        activeSessionId={activeSessionIdState}
        onNewSession={handleNewSession}
        onSelectSession={handleSelectSession}
        onDeleteSession={handleDeleteSession}
        availableWindows={availableWindows}
        connectedApps={connectedApps}
        onConnect={handleConnect}
        onDisconnect={handleDisconnect}
        isDragging={isDragging}
        onDragStart={handleDragStart}
      />
      
      {/* Main Content: Canvas + Input */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Canvas Area */}
        <div className="flex-1 relative min-h-0">
          {/* Bubble Canvas - 只Display已Connect的应用 */}
          <BubbleCanvas
            availableWindows={[]} // notDisplaycanConnectApply，alreadymovetoSidebar
            connectedApps={connectedApps}
            onConnect={handleConnect}
            onDisconnect={handleDisconnect}
            onOpenLiveArea={handleOpenLiveArea}
            aiState={aiState}
            activeAppHwnd={activeAppHwnd}
            // 2026 toplevel: OutputType semanticize
            outputType={outputType}
            targetHwnd={targetHwnd}
            sourceHwnd={sourceHwnd}
            className="absolute inset-0"
          />
          
          {/* Floating Chat Panel */}
          <AnimatePresence>
            {connectedApps.length > 0 && (
              <FloatingChatPanel
                connectedApps={connectedApps}
                messages={chatMessages}
                activeAppHwnd={activeAppHwnd}
                aiState={aiState}
                isLoading={isLoading}
              />
            )}
          </AnimatePresence>
          
          
          {/* Context Insight Panel - Level 3 smart感知（支持多应用组合） */}
          <AnimatePresence>
            {insightApps.length > 0 && (
              <div className="absolute left-1/2 top-4 -translate-x-1/2 z-50">
                <ErrorBoundary fallback={<div className="p-4 bg-red-500/20 rounded-lg text-red-300 text-sm">Failed to load, please refresh</div>}>
                  <ContextInsightPanel
                    apps={insightApps}
                    onClose={() => setInsightApps([])}
                    onSuggestionClick={(suggestion: Suggestion) => {
                      console.log('[BubbleMode] Suggestion clicked:', suggestion);
                      const message = suggestion.description 
                        ? `${suggestion.label}：${suggestion.description}`
                        : suggestion.label;
                      
                      // Close panel
                      setInsightApps([]);
                      // Use unified handleSendMessage
                      handleSendMessage(message);
                    }}
                  />
                </ErrorBoundary>
              </div>
            )}
          </AnimatePresence>
        </div>
        
        {/* Bottom: Input Bar */}
        <div className="px-4 pb-4 pt-2 border-t border-white/[0.06]">
          <form onSubmit={handleSubmit} className="max-w-2xl mx-auto">
            <motion.div
              className={cn(
                "flex items-end gap-2 p-2 rounded-xl",
                "bg-white/[0.03] border transition-all duration-200",
                isFocused ? "border-white/20" : "border-white/[0.08]"
              )}
              animate={{
                boxShadow: isFocused 
                  ? '0 0 0 1px rgba(255,255,255,0.1), 0 4px 20px rgba(0,0,0,0.3)' 
                  : '0 2px 8px rgba(0,0,0,0.2)',
              }}
            >
              <textarea
                ref={textareaRef}
                value={localInput}
                onChange={(e) => setLocalInput(e.target.value)}
                onKeyDown={handleKeyDown}
                onFocus={() => setIsFocused(true)}
                onBlur={() => setIsFocused(false)}
                placeholder={connectedApps.length > 0 
                  ? `Talk to ${connectedApps.map(a => a.app_display_name).join(', ')}...`
                  : "Select an app on the left to connect..."
                }
                rows={1}
                disabled={isLoading}
                className={cn(
                  "flex-1 bg-transparent border-0 outline-none resize-none",
                  "text-sm text-white placeholder:text-white/30",
                  "py-2 px-2 max-h-[150px]"
                )}
              />

              <AnimatePresence mode="wait">
                {isLoading ? (
                  <motion.button
                    key="stop"
                    type="button"
                    onClick={stop}
                    className="w-8 h-8 rounded-lg bg-white/10 hover:bg-white/15 flex items-center justify-center"
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    exit={{ scale: 0.8, opacity: 0 }}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Square className="w-3.5 h-3.5 text-white" fill="currentColor" />
                  </motion.button>
                ) : (
                  <motion.button
                    key="send"
                    type="submit"
                    disabled={!localInput.trim() || connectedApps.length === 0}
                    className={cn(
                      "w-8 h-8 rounded-lg flex items-center justify-center transition-all",
                      localInput.trim() && connectedApps.length > 0
                        ? "bg-emerald-500 hover:bg-emerald-400 text-white" 
                        : "bg-white/5 text-white/30"
                    )}
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    exit={{ scale: 0.8, opacity: 0 }}
                    whileHover={localInput.trim() && connectedApps.length > 0 ? { scale: 1.05 } : undefined}
                    whileTap={localInput.trim() && connectedApps.length > 0 ? { scale: 0.95 } : undefined}
                  >
                    <ArrowUp className="w-4 h-4" />
                  </motion.button>
                )}
              </AnimatePresence>
            </motion.div>
          </form>
          
          {/* Status */}
          <div className="flex items-center justify-center mt-2">
            <AnimatePresence mode="wait">
              {isDragging ? (
                <motion.span
                  key="dragging"
                  className="text-[10px] flex items-center gap-1.5 text-emerald-400"
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -5 }}
                >
                  <motion.span 
                    className="w-2 h-2 rounded-full bg-emerald-400"
                    animate={{ scale: [1, 1.5, 1] }}
                    transition={{ duration: 0.6, repeat: Infinity }}
                  />
                  Release on target window to connect...
                </motion.span>
              ) : (
                <motion.span 
                  key="status"
                  className="text-[10px] flex items-center gap-1"
                  style={{ color: aiState === 'idle' ? 'rgba(16, 185, 129, 0.6)' : 'rgba(139, 92, 246, 0.8)' }}
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -5 }}
                >
                  <motion.span 
                    className="w-1.5 h-1.5 rounded-full"
                    style={{ backgroundColor: aiState === 'idle' ? '#10b981' : '#8b5cf6' }}
                    animate={{ scale: aiState !== 'idle' ? [1, 1.3, 1] : [1, 1.2, 1] }}
                    transition={{ duration: aiState !== 'idle' ? 1 : 2, repeat: Infinity }}
                  />
                  {aiState === 'idle' ? 'Ready' : aiState === 'thinking' ? 'Thinking...' : 'Working...'}
                </motion.span>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
});

export default BubbleMode;
