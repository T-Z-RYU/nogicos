import { motion } from 'motion/react';
import ReactMarkdown from 'react-markdown';
import { memo } from 'react';
import remarkGfm from 'remark-gfm';

interface StreamingTextProps {
  content: string;
  isStreaming?: boolean;
  speed?: number; // ms per character (unused now, kept for API compatibility)
  className?: string;
}

/**
 * StreamingText - Real-time streaming text with Markdown rendering
 * 
 * Uses react-markdown with remark-gfm for proper Markdown support:
 * - Tables (GFM)
 * - Code blocks with syntax highlighting
 * - Inline code, bold, italic
 * - Lists, blockquotes
 * - Emojis and Unicode
 */
export const StreamingText = memo(function StreamingText({ 
  content, 
  isStreaming = false,
  className = ''
}: StreamingTextProps) {
  return (
    <div className={className}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Code blocks - no animation to prevent flicker during streaming
          pre: ({ children }) => (
            <pre className="my-3 p-4 rounded-xl bg-black/40 border border-white/5 overflow-x-auto">
              {children}
            </pre>
          ),
          code: ({ className, children, ...props }) => {
            const isInline = !className;
            if (isInline) {
              return (
                <code className="px-1.5 py-0.5 mx-0.5 rounded-md bg-white/10 text-[13px] font-mono text-amber-300/90" {...props}>
                  {children}
                </code>
              );
            }
            // Code block
            const language = className?.replace('language-', '') || '';
            return (
              <>
                {language && (
                  <div className="text-[10px] text-white/40 uppercase tracking-wider mb-2 font-medium">
                    {language}
                  </div>
                )}
                <code className="text-[13px] font-mono text-emerald-300/90 leading-relaxed block" {...props}>
                  {children}
                </code>
              </>
            );
          },
          // Tables - no animation to prevent flicker during streaming
          table: ({ children }) => (
            <div className="my-3 rounded-xl overflow-hidden border border-white/10">
              <table className="w-full text-[13px]">
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => (
            <thead className="bg-white/5">{children}</thead>
          ),
          th: ({ children }) => (
            <th className="px-3 py-2 text-left font-medium text-white/70 border-b border-white/5">
              {children}
            </th>
          ),
          tbody: ({ children }) => <tbody>{children}</tbody>,
          tr: ({ children }) => (
            <tr className="border-b border-white/5 last:border-0 hover:bg-white/[0.02]">
              {children}
            </tr>
          ),
          td: ({ children }) => (
            <td className="px-3 py-2 text-white/80">{children}</td>
          ),
          // Lists
          ul: ({ children }) => (
            <ul className="my-2 space-y-1">{children}</ul>
          ),
          ol: ({ children }) => (
            <ol className="my-2 space-y-1 list-decimal list-inside">{children}</ol>
          ),
          li: ({ children }) => (
            <li className="flex items-start gap-2">
              <span className="text-primary/80 text-xs mt-1.5">●</span>
              <span className="flex-1">{children}</span>
            </li>
          ),
          // Text formatting
          strong: ({ children }) => (
            <strong className="font-semibold text-white">{children}</strong>
          ),
          em: ({ children }) => (
            <em className="italic text-white/80">{children}</em>
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
          // Blockquote
          blockquote: ({ children }) => (
            <blockquote className="border-l-2 border-primary/50 pl-3 my-2 text-white/70 italic">
              {children}
            </blockquote>
          ),
          // Links
          a: ({ href, children }) => (
            <a href={href} className="text-primary hover:underline" target="_blank" rel="noopener noreferrer">
              {children}
            </a>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
      {isStreaming && (
        <motion.span
          className="inline-block w-0.5 h-4 bg-primary ml-0.5 align-middle"
          animate={{ opacity: [1, 0] }}
          transition={{ duration: 0.5, repeat: Infinity, repeatType: 'reverse' }}
        />
      )}
    </div>
  );
});

