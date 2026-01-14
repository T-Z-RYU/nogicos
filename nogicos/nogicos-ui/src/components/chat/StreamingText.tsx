import { motion } from 'motion/react';
import ReactMarkdown from 'react-markdown';
import { memo } from 'react';
import remarkGfm from 'remark-gfm';
import { cn } from '@/lib/utils';
import './styles/cursor-theme.css';

interface StreamingTextProps {
  content: string;
  isStreaming?: boolean;
  className?: string;
}

/**
 * StreamingText - Cursor-style streaming text with Markdown
 * 
 * Features:
 * - Real-time streaming display
 * - Blinking cursor animation
 * - Full Markdown support (GFM)
 * - VS Code-style syntax highlighting colors
 */
export const StreamingText = memo(function StreamingText({ 
  content, 
  isStreaming = false,
  className = ''
}: StreamingTextProps) {
  return (
    <div className={cn('text-[var(--chat-text-primary)]', className)}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Code blocks
          pre: ({ children }) => (
            <pre className="chat-code-block my-3 overflow-x-auto">
              {children}
            </pre>
          ),
          code: ({ className, children, ...props }) => {
            const isInline = !className;
            if (isInline) {
              return (
                <code className="chat-code-inline" {...props}>
                  {children}
                </code>
              );
            }
            const language = className?.replace('language-', '') || '';
            return (
              <>
                {language && (
                  <div className="text-[10px] text-[var(--chat-text-secondary)] uppercase tracking-wider mb-2 font-medium">
                    {language}
                  </div>
                )}
                <code 
                  className="text-[13px] font-mono text-[var(--syntax-function)] leading-relaxed block" 
                  {...props}
                >
                  {children}
                </code>
              </>
            );
          },
          // Tables - Fixed column width for proper alignment
          table: ({ children }) => (
            <div className="my-3 rounded-md overflow-hidden border border-[var(--chat-border)] overflow-x-auto">
              <table className="w-full text-[13px] table-fixed border-collapse">
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => (
            <thead className="bg-[var(--chat-bg-tertiary)]">{children}</thead>
          ),
          th: ({ children }) => (
            <th className="px-4 py-2.5 text-left font-semibold text-[var(--chat-text-secondary)] border-b border-[var(--chat-border)] whitespace-nowrap">
              {children}
            </th>
          ),
          tbody: ({ children }) => <tbody>{children}</tbody>,
          tr: ({ children }) => (
            <tr className="border-b border-[var(--chat-border-light)] last:border-0 hover:bg-[var(--chat-bg-secondary)]">
              {children}
            </tr>
          ),
          td: ({ children }) => (
            <td className="px-4 py-2.5 text-[var(--chat-text-primary)] align-top">
              {children}
            </td>
          ),
          // Lists
          ul: ({ children }) => (
            <ul className="my-2 space-y-1 ml-4">{children}</ul>
          ),
          ol: ({ children }) => (
            <ol className="my-2 space-y-1 list-decimal ml-6">{children}</ol>
          ),
          li: ({ children }) => (
            <li className="flex items-start gap-2">
              <span className="text-[var(--chat-accent-green)] text-xs mt-1.5">●</span>
              <span className="flex-1">{children}</span>
            </li>
          ),
          // Text formatting
          strong: ({ children }) => (
            <strong className="font-semibold text-white">{children}</strong>
          ),
          em: ({ children }) => (
            <em className="italic text-[var(--chat-text-primary)]">{children}</em>
          ),
          // Paragraphs
          p: ({ children }) => (
            <p className="my-1.5 leading-relaxed">{children}</p>
          ),
          // Headings
          h1: ({ children }) => (
            <h1 className="text-xl font-bold text-white mt-4 mb-2">{children}</h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-lg font-bold text-white mt-3 mb-2">{children}</h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-base font-semibold text-white mt-2 mb-1">{children}</h3>
          ),
          h4: ({ children }) => (
            <h4 className="text-sm font-semibold text-white mt-2 mb-1">{children}</h4>
          ),
          // Blockquote
          blockquote: ({ children }) => (
            <blockquote className="border-l-2 border-[var(--chat-accent-blue)] pl-3 my-2 text-[var(--chat-text-secondary)] italic">
              {children}
            </blockquote>
          ),
          // Links
          a: ({ href, children }) => (
            <a 
              href={href} 
              className="chat-link" 
              target="_blank" 
              rel="noopener noreferrer"
            >
              {children}
            </a>
          ),
          // Horizontal rule
          hr: () => (
            <hr className="my-4 border-[var(--chat-border)]" />
          ),
        }}
      >
        {content}
      </ReactMarkdown>
      {isStreaming && (
        <motion.span
          className="chat-cursor"
          style={{ willChange: 'opacity' }}
          animate={{ opacity: [1, 0] }}
          transition={{ duration: 0.5, repeat: Infinity, repeatType: 'reverse' }}
        />
      )}
    </div>
  );
});

