import { Component, type ReactNode } from 'react';
import { motion } from 'motion/react';
import { AlertTriangle, RefreshCw, Home, Bug } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

/**
 * ErrorBoundary - Catch React errors and display friendly UI
 * 
 * Features:
 * - Catches rendering errors in child components
 * - Shows glassmorphism error card
 * - Provides retry and home buttons
 * - Shows error details in dev mode
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    this.setState({ errorInfo });
    
    // Log error for debugging
    console.error('[ErrorBoundary] Caught error:', error);
    console.error('[ErrorBoundary] Component stack:', errorInfo.componentStack);
    
      }

  handleRetry = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    // Clear state and reload
    sessionStorage.clear();
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen w-full flex items-center justify-center bg-background p-6">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
            className="max-w-lg w-full"
          >
            {/* Error Card */}
            <div className="glass-panel rounded-2xl p-8 text-center">
              {/* Icon */}
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.1, type: 'spring', bounce: 0.5 }}
                className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-red-500/20 flex items-center justify-center"
              >
                <AlertTriangle className="w-8 h-8 text-red-400" />
              </motion.div>

              {/* Title */}
              <h1 className="text-xl font-semibold text-foreground mb-2">
                Something went wrong
              </h1>
              
              {/* Description */}
              <p className="text-muted-foreground text-sm mb-6">
                An unexpected error occurred. You can try reloading or go back to start fresh.
              </p>

              {/* Error Details (Dev Mode) */}
              {import.meta.env.DEV && this.state.error && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="mb-6 text-left"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <Bug className="w-4 h-4 text-amber-400" />
                    <span className="text-xs font-medium text-amber-400 uppercase tracking-wider">
                      Error Details
                    </span>
                  </div>
                  <div className="bg-black/40 rounded-lg p-3 border border-white/5 overflow-auto max-h-40">
                    <pre className="text-xs text-red-300 font-mono whitespace-pre-wrap break-all">
                      {this.state.error.message}
                    </pre>
                    {this.state.errorInfo && (
                      <pre className="text-xs text-muted-foreground font-mono mt-2 whitespace-pre-wrap break-all">
                        {this.state.errorInfo.componentStack?.slice(0, 500)}
                      </pre>
                    )}
                  </div>
                </motion.div>
              )}

              {/* Actions */}
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <Button
                  onClick={this.handleRetry}
                  variant="outline"
                  className="gap-2"
                >
                  <RefreshCw className="w-4 h-4" />
                  Try Again
                </Button>
                <Button
                  onClick={this.handleReload}
                  variant="outline"
                  className="gap-2"
                >
                  <RefreshCw className="w-4 h-4" />
                  Reload Page
                </Button>
                <Button
                  onClick={this.handleGoHome}
                  variant="default"
                  className="gap-2"
                >
                  <Home className="w-4 h-4" />
                  Start Fresh
                </Button>
              </div>
            </div>

            {/* Footer */}
            <p className="text-center text-xs text-muted-foreground/60 mt-4">
              If this keeps happening, please contact support.
            </p>
          </motion.div>
        </div>
      );
    }

    return this.props.children;
  }
}

/**
 * Smaller inline error for non-critical components
 */
export function InlineError({ 
  message = 'Failed to load',
  onRetry,
}: { 
  message?: string;
  onRetry?: () => void;
}) {
  return (
    <div className="flex items-center gap-3 p-4 rounded-xl bg-red-500/10 border border-red-500/20">
      <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0" />
      <span className="text-sm text-red-300">{message}</span>
      {onRetry && (
        <button
          onClick={onRetry}
          className="ml-auto px-3 py-1 text-xs bg-red-500/20 hover:bg-red-500/30 rounded-lg text-red-300 transition-colors"
        >
          Retry
        </button>
      )}
    </div>
  );
}

