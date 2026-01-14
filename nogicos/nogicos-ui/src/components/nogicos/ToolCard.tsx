import { useState } from 'react';
import { 
  ChevronDown, 
  ChevronUp, 
  Check, 
  X, 
  Loader2,
  Terminal,
  Globe,
  FolderOpen,
  FileText,
  Move,
  Trash2,
  Copy,
  Search
} from 'lucide-react';
import { cn } from '@/lib/utils';

export type ToolStatus = 'pending' | 'executing' | 'success' | 'error';

export interface ToolExecution {
  id: string;
  messageId: string;
  name: string;
  args: Record<string, unknown>;
  status: ToolStatus;
  output?: string;
  error?: string;
  startTime: Date;
  endTime?: Date;
}

interface ToolCardProps {
  tool: ToolExecution;
}

const TOOL_ICONS: Record<string, typeof Terminal> = {
  shell_execute: Terminal,
  browser_navigate: Globe,
  browser_click: Globe,
  browser_type: Globe,
  list_directory: FolderOpen,
  read_file: FileText,
  write_file: FileText,
  move_file: Move,
  delete_file: Trash2,
  copy_file: Copy,
  glob_search: Search,
  grep_search: Search,
};

const TOOL_LABELS: Record<string, string> = {
  shell_execute: 'Shell',
  browser_navigate: 'Navigate',
  browser_click: 'Click',
  browser_type: 'Type',
  list_directory: 'List Dir',
  read_file: 'Read File',
  write_file: 'Write File',
  move_file: 'Move',
  delete_file: 'Delete',
  copy_file: 'Copy',
  glob_search: 'Glob',
  grep_search: 'Grep',
};

export function ToolCard({ tool }: ToolCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  
  const Icon = TOOL_ICONS[tool.name] || Terminal;
  const label = TOOL_LABELS[tool.name] || tool.name;
  
  const StatusIcon = {
    pending: () => <div className="w-3 h-3 rounded-full bg-muted-foreground/30" />,
    executing: () => <Loader2 className="w-3.5 h-3.5 text-primary animate-spin" />,
    success: () => <Check className="w-3.5 h-3.5 text-green-500" />,
    error: () => <X className="w-3.5 h-3.5 text-destructive" />,
  }[tool.status];

  const duration = tool.endTime 
    ? `${((tool.endTime.getTime() - tool.startTime.getTime()) / 1000).toFixed(1)}s`
    : null;

  return (
    <div
      className={cn(
        'tool-card transition-all',
        tool.status === 'executing' && 'executing',
        tool.status === 'success' && 'success',
        tool.status === 'error' && 'error'
      )}
    >
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between gap-2"
      >
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-secondary/80 flex items-center justify-center">
            <Icon className="w-3.5 h-3.5 text-muted-foreground" />
          </div>
          <div className="text-left">
            <div className="text-sm font-medium text-foreground">{label}</div>
            <div className="text-[10px] text-muted-foreground font-mono truncate max-w-[200px]">
              {formatArgs(tool.args)}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {duration && (
            <span className="text-[10px] text-muted-foreground">{duration}</span>
          )}
          <StatusIcon />
          {isExpanded ? (
            <ChevronUp className="w-4 h-4 text-muted-foreground" />
          ) : (
            <ChevronDown className="w-4 h-4 text-muted-foreground" />
          )}
        </div>
      </button>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="mt-3 pt-3 border-t border-border/30 animate-fade-in">
          {/* Arguments */}
          <div className="mb-3">
            <div className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1.5">
              Arguments
            </div>
            <pre className="text-xs font-mono bg-black/20 rounded-lg p-2.5 overflow-x-auto">
              {JSON.stringify(tool.args, null, 2)}
            </pre>
          </div>

          {/* Output or Error */}
          {(tool.output || tool.error) && (
            <div>
              <div className={cn(
                'text-[10px] uppercase tracking-wider mb-1.5',
                tool.error ? 'text-destructive' : 'text-muted-foreground'
              )}>
                {tool.error ? 'Error' : 'Output'}
              </div>
              <pre className={cn(
                'text-xs font-mono rounded-lg p-2.5 overflow-x-auto max-h-[200px]',
                tool.error ? 'bg-destructive/10 text-destructive' : 'bg-black/20'
              )}>
                {tool.error || tool.output}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function formatArgs(args: Record<string, unknown>): string {
  const entries = Object.entries(args);
  if (entries.length === 0) return '(no args)';
  
  const [firstKey, firstValue] = entries[0];
  const valueStr = typeof firstValue === 'string' 
    ? firstValue 
    : JSON.stringify(firstValue);
  
  const truncated = valueStr.length > 40 
    ? valueStr.slice(0, 40) + '...' 
    : valueStr;
  
  return `${firstKey}: ${truncated}`;
}

