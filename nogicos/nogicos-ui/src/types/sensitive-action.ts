/**
 * 敏感操作Class型定义
 * Phase 7.4: 敏感操作Confirm（重New设计）
 */

// Risketclevel
export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

// sensitiveActionInterface
export interface SensitiveAction {
  id: string;
  taskId: string;
  toolName: string;
  description: string;
  humanReadable: string;        // human readabledescribe
  risk: RiskLevel;
  timeout: number;              // TimeoutAutoReject（Second）
  params: Record<string, unknown>;
  screenshot?: string;          // captureGraph base64
  coordinates?: { x: number; y: number };
  windowName?: string;
  impact?: string;              // ActionaffectDescription
  createdAt: number;
}

// sensitiveActionminutelevelConfig
export const SENSITIVE_TOOLS: Record<string, RiskLevel> = {
  'delete_file': 'critical',
  'execute_command': 'critical',
  'send_message': 'high',
  'window_type': 'medium',      // PasswordInputtimeDynamicUpgradefor high
  'window_click': 'low',
  'keyboard_shortcut': 'medium',
  'open_application': 'medium',
  'close_window': 'high',
};

// TimeoutConfig（Second）
export const TIMEOUT_BY_RISK: Record<RiskLevel, number> = {
  'low': 30,
  'medium': 20,
  'high': 15,
  'critical': 10,
};

// RisketclevelColor
export const RISK_COLORS: Record<RiskLevel, string> = {
  'low': '#10b981',      // green
  'medium': '#f59e0b',   // yellow
  'high': '#ef4444',     // red
  'critical': '#dc2626', // dark red
};

// RisketclevelLabel
export const RISK_LABELS: Record<RiskLevel, string> = {
  'low': 'LowRisk',
  'medium': 'MediumRisk',
  'high': 'HighRisk',
  'critical': '危险操作',
};

// ConfirmResult
export interface ConfirmationResult {
  actionId: string;
  taskId: string;
  approved: boolean;
  timestamp: number;
}
