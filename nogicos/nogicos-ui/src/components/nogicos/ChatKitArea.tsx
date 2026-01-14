/**
 * ChatKitArea - OpenAI ChatKit IntegrationComponent
 * 
 * Usage OpenAI 官方 ChatKit Framework，提供 ChatGPT 级别的聊Day体验
 * 支持流式Response、ClientTool、Theme定制等High级功能
 */

import { ChatKit, useChatKit } from '@openai/chatkit-react';

interface ChatKitAreaProps {
  /** TriggerDisplay可视化面板 */
  onShowVisualization?: () => void;
  /** TriggerHigh亮Animation */
  onHighlight?: (params: { x: number; y: number; width: number; height: number; label?: string }) => void;
  /** Trigger光标Move */
  onCursorMove?: (params: { x: number; y: number }) => void;
  /** API 基础 URL */
  apiUrl?: string;
  /** 自定义Class名 */
  className?: string;
}

export function ChatKitArea({ 
  onShowVisualization, 
  onHighlight,
  onCursorMove,
  apiUrl = 'http://localhost:8080/chatkit',
  className = '',
}: ChatKitAreaProps) {
  const { control } = useChatKit({
    api: {
      url: apiUrl,
      domainKey: 'nogicos',
    },
    
    // ========================================
    // extreme theme config - match NogicOS dark color style
    // ========================================
    theme: {
      colorScheme: 'dark',
      density: 'normal',
      radius: 'round',
      color: {
        grayscale: { hue: 220, tint: 6, shade: -1 },
        accent: { primary: '#8B5CF6', level: 2 },  // purple accent color，consistent with NogicOS
      },
    },
    
    // ========================================
    // HeadpartConfig
    // ========================================
    header: {
      enabled: false,  // Usage NogicOS self's  TitleBar
    },
    
    // ========================================
    // Smart Start Screen
    // ========================================
    startScreen: {
      greeting: 'Welcome to NogicOS',
      prompts: [
        { 
          label: 'Web Search', 
          prompt: 'Search for iPhone 16 on Google', 
          icon: 'globe',
        },
        { 
          label: 'Organize Files', 
          prompt: 'Help me organize desktop files by type', 
          icon: 'lightbulb',
        },
        { 
          label: 'AI News', 
          prompt: 'Search for latest AI news and summarize', 
          icon: 'search',
        },
        { 
          label: 'System Info', 
          prompt: 'Show my system information', 
          icon: 'lifesaver',
        },
      ],
    },
    
    // ========================================
    // Composer Config
    // ========================================
    composer: {
      placeholder: 'Tell me what you want to do...',
      // Attachments disabled for now
      // attachments: { enabled: true, maxCount: 5 },
    },
    
    // ========================================
    // Message Actions
    // ========================================
    threadItemActions: {
      feedback: true,   // 👍👎 Feedback button
      retry: true,      // Retry button
    },
    
    // ========================================
    // History
    // ========================================
    history: {
      enabled: true,
      showDelete: true,
      showRename: true,
    },
    
    // ========================================
    // ClientTool - AI CanTriggerBeforeendaction
    // ========================================
    onClientTool: async (invocation) => {
      // DisplaycanvisualizationPanel
      if (invocation.name === 'show_visualization') {
        onShowVisualization?.();
        return { success: true };
      }
      
      // HighbrightElements
      if (invocation.name === 'highlight_element') {
        const params = invocation.params as { 
          x: number; 
          y: number; 
          width: number; 
          height: number; 
          label?: string;
        };
        onHighlight?.(params);
        return { success: true };
      }
      
      // Movecursor
      if (invocation.name === 'move_cursor') {
        const params = invocation.params as { x: number; y: number };
        onCursorMove?.(params);
        return { success: true };
      }
      
      // playTipaudio
      if (invocation.name === 'play_sound') {
        const soundType = (invocation.params as { type?: string })?.type || 'complete';
        try {
          // Usage Web Audio API playsimpleTipaudio
          const audioContext = new (window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)();
          const oscillator = audioContext.createOscillator();
          const gainNode = audioContext.createGain();
          
          oscillator.connect(gainNode);
          gainNode.connect(audioContext.destination);
          
          oscillator.frequency.value = soundType === 'error' ? 200 : 800;
          oscillator.type = 'sine';
          gainNode.gain.value = 0.1;
          
          oscillator.start();
          oscillator.stop(audioContext.currentTime + 0.1);
          
          return { success: true };
        } catch {
          return { success: false };
        }
      }
      
      // UnknownTool
      return { success: false };
    },
    
    // ========================================
    // ErrorHandle
    // ========================================
    onError: ({ error }) => {
      console.error('[ChatKit] Error:', error);
    },
  });

  return (
    <ChatKit 
      control={control} 
      className={`flex-1 h-full ${className}`}
    />
  );
}

export default ChatKitArea;

