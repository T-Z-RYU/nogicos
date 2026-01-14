/**
 * 模式提取算法
 * 从多个 App 的 onboarding 分析数据中提取通用模式和差异化策略
 */

import type { PhaseAnalysis, ScreenData } from '@/store/analysis-store';

// 模式类型
export interface ExtractedPattern {
  id: string;
  name: string;
  pattern: string;
  description: string;
  frequency: number;
  totalApps: number;
  apps: string[];
  importance: 'must-have' | 'recommended' | 'optional';
  evidence: PatternEvidence[];
  recommendation: string;
}

export interface PatternEvidence {
  app: string;
  positions: number[];
  example: string;
}

// 差异化策略
export interface UniqueStrategy {
  app: string;
  strategyName: string;
  description: string;
  keyScreens: number[];
  borrowRecommendation: string;
}

// VitaFlow 模板页面建议
export interface TemplatePageSuggestion {
  index: number;
  phase: string;
  type: string;
  typeName: string;
  referenceApp: string;
  referenceScreen: number;
  copyDirection: string;
  psychologyTactics: string[];
  uiPatternSuggestion: string;
}

// VitaFlow 模板
export interface VitaFlowTemplate {
  totalPages: number;
  phases: TemplatePhase[];
  keyPatterns: string[];
  generatedAt: string;
}

export interface TemplatePhase {
  id: string;
  name: string;
  recommendedPages: number;
  pages: TemplatePageSuggestion[];
  tactics: string[];
}

/**
 * 从多个分析中提取通用模式
 */
export function extractCommonPatterns(analyses: PhaseAnalysis[]): ExtractedPattern[] {
  const patterns: ExtractedPattern[] = [];
  const totalApps = analyses.length;

  // 1. 权威背书位置模式
  const authorityPattern = analyzeAuthorityPlacement(analyses);
  if (authorityPattern.frequency >= totalApps * 0.6) {
    patterns.push({
      id: 'authority-early',
      name: '早期权威背书',
      pattern: 'A within first 10 screens',
      description: '在前10页内展示权威背书（医生推荐、媒体报道、用户数据）',
      frequency: authorityPattern.frequency,
      totalApps,
      apps: authorityPattern.apps,
      importance: authorityPattern.frequency >= totalApps * 0.8 ? 'must-have' : 'recommended',
      evidence: authorityPattern.evidence,
      recommendation: '在第3-5页展示权威背书，使用具体数据增强可信度'
    });
  }

  // 2. 问题-价值穿插模式
  const qvPattern = analyzeQuestionValueInterleaving(analyses);
  if (qvPattern.frequency >= totalApps * 0.6) {
    patterns.push({
      id: 'question-value-interleaving',
      name: '问题-价值穿插',
      pattern: 'Q→Q→Q→V',
      description: '每3-4个问题后穿插一个价值展示页',
      frequency: qvPattern.frequency,
      totalApps,
      apps: qvPattern.apps,
      importance: 'must-have',
      evidence: qvPattern.evidence,
      recommendation: '每3-4个问题后插入价值页，展示功能预览或用户利益'
    });
  }

  // 3. Permission Pre-priming 模式
  const permissionPattern = analyzePermissionPattern(analyses);
  if (permissionPattern.frequency >= totalApps * 0.5) {
    patterns.push({
      id: 'permission-priming',
      name: '权限预铺垫',
      pattern: 'V→X',
      description: '在系统权限请求前展示价值说明',
      frequency: permissionPattern.frequency,
      totalApps,
      apps: permissionPattern.apps,
      importance: 'recommended',
      evidence: permissionPattern.evidence,
      recommendation: '权限请求前先展示价值，如"允许通知以获取周期提醒"'
    });
  }

  // 4. Labor Illusion 模式
  const loadingPattern = analyzeLoadingPattern(analyses);
  if (loadingPattern.frequency >= totalApps * 0.5) {
    patterns.push({
      id: 'labor-illusion',
      name: '加载错觉',
      pattern: 'L→L→R',
      description: '多步加载动画创造"复杂计算"印象',
      frequency: loadingPattern.frequency,
      totalApps,
      apps: loadingPattern.apps,
      importance: 'recommended',
      evidence: loadingPattern.evidence,
      recommendation: '使用2-3步加载动画，展示"正在分析您的数据"等进度提示'
    });
  }

  // 5. 游戏化进度模式
  const gamificationPattern = analyzeGamificationPattern(analyses);
  if (gamificationPattern.frequency >= totalApps * 0.4) {
    patterns.push({
      id: 'gamification-checkpoints',
      name: '游戏化检查点',
      pattern: 'G checkpoints',
      description: '在关键节点使用游戏化元素强化成就感',
      frequency: gamificationPattern.frequency,
      totalApps,
      apps: gamificationPattern.apps,
      importance: 'optional',
      evidence: gamificationPattern.evidence,
      recommendation: '在每个阶段结束时展示"解锁"或"完成"动画'
    });
  }

  // 6. 社会认同穿插模式
  const socialProofPattern = analyzeSocialProofPattern(analyses);
  if (socialProofPattern.frequency >= totalApps * 0.6) {
    patterns.push({
      id: 'social-proof-intervals',
      name: '社会认同穿插',
      pattern: 'S every 8-15 screens',
      description: '每8-15页穿插社会认同内容',
      frequency: socialProofPattern.frequency,
      totalApps,
      apps: socialProofPattern.apps,
      importance: 'recommended',
      evidence: socialProofPattern.evidence,
      recommendation: '每8-15页展示用户证言或统计数据，正常化用户体验'
    });
  }

  return patterns.sort((a, b) => {
    const importanceOrder = { 'must-have': 0, 'recommended': 1, 'optional': 2 };
    return importanceOrder[a.importance] - importanceOrder[b.importance];
  });
}

/**
 * 提取差异化策略
 */
export function extractUniqueStrategies(analyses: PhaseAnalysis[]): UniqueStrategy[] {
  return analyses.map(analysis => {
    const insights = Object.entries(analysis.design_insights);
    const primaryInsight = insights[0] || ['unknown', ''];
    
    return {
      app: analysis.app,
      strategyName: primaryInsight[0].replace(/_/g, ' '),
      description: primaryInsight[1],
      keyScreens: getKeyScreensForStrategy(analysis),
      borrowRecommendation: generateBorrowRecommendation(analysis)
    };
  });
}

/**
 * 生成 VitaFlow 模板
 */
export function generateVitaFlowTemplate(analyses: PhaseAnalysis[]): VitaFlowTemplate {
  const patterns = extractCommonPatterns(analyses);
  const avgScreens = analyses.reduce((sum, a) => sum + a.total_screens, 0) / analyses.length;
  
  // 生成阶段结构
  const phases: TemplatePhase[] = [
    generatePhase('trust-building', '信任建立', 3, analyses, patterns),
    generatePhase('goal-setting', '目标设定', 8, analyses, patterns),
    generatePhase('data-collection', '数据收集', 20, analyses, patterns),
    generatePhase('feature-showcase', '功能展示', 10, analyses, patterns),
    generatePhase('final-setup', '最终设置', 8, analyses, patterns),
    generatePhase('conversion', '结果与转化', 12, analyses, patterns),
  ];

  return {
    totalPages: phases.reduce((sum, p) => sum + p.recommendedPages, 0),
    phases,
    keyPatterns: patterns.filter(p => p.importance === 'must-have').map(p => p.recommendation),
    generatedAt: new Date().toISOString()
  };
}

// 辅助函数
function analyzeAuthorityPlacement(analyses: PhaseAnalysis[]) {
  const result = { frequency: 0, apps: [] as string[], evidence: [] as PatternEvidence[] };
  
  analyses.forEach(analysis => {
    const authorityScreens = analysis.screens
      .filter(s => s.primary_type === 'A' && s.index <= 10)
      .map(s => s.index);
    
    if (authorityScreens.length > 0) {
      result.frequency++;
      result.apps.push(analysis.app);
      result.evidence.push({
        app: analysis.app,
        positions: authorityScreens,
        example: `页面 ${authorityScreens[0]}`
      });
    }
  });
  
  return result;
}

function analyzeQuestionValueInterleaving(analyses: PhaseAnalysis[]) {
  const result = { frequency: 0, apps: [] as string[], evidence: [] as PatternEvidence[] };
  
  analyses.forEach(analysis => {
    const valueAfterQuestions = analysis.flow_patterns?.value_after_questions;
    if (valueAfterQuestions && (Array.isArray(valueAfterQuestions) ? valueAfterQuestions.length : Object.keys(valueAfterQuestions).length) >= 3) {
      result.frequency++;
      result.apps.push(analysis.app);
      result.evidence.push({
        app: analysis.app,
        positions: Array.isArray(valueAfterQuestions) ? valueAfterQuestions : [],
        example: `${Array.isArray(valueAfterQuestions) ? valueAfterQuestions.length : 0}次穿插`
      });
    }
  });
  
  return result;
}

function analyzePermissionPattern(analyses: PhaseAnalysis[]) {
  const result = { frequency: 0, apps: [] as string[], evidence: [] as PatternEvidence[] };
  
  analyses.forEach(analysis => {
    const permissionPairs = analysis.flow_patterns?.permission_priming_pairs;
    if (permissionPairs && Array.isArray(permissionPairs) && permissionPairs.length > 0) {
      result.frequency++;
      result.apps.push(analysis.app);
      result.evidence.push({
        app: analysis.app,
        positions: permissionPairs.flat(),
        example: `${permissionPairs.length}个权限预铺垫`
      });
    }
  });
  
  return result;
}

function analyzeLoadingPattern(analyses: PhaseAnalysis[]) {
  const result = { frequency: 0, apps: [] as string[], evidence: [] as PatternEvidence[] };
  
  analyses.forEach(analysis => {
    const loadingScreens = analysis.screens.filter(s => s.primary_type === 'L');
    if (loadingScreens.length >= 2) {
      result.frequency++;
      result.apps.push(analysis.app);
      result.evidence.push({
        app: analysis.app,
        positions: loadingScreens.map(s => s.index),
        example: `${loadingScreens.length}个加载页`
      });
    }
  });
  
  return result;
}

function analyzeGamificationPattern(analyses: PhaseAnalysis[]) {
  const result = { frequency: 0, apps: [] as string[], evidence: [] as PatternEvidence[] };
  
  analyses.forEach(analysis => {
    const gamificationScreens = analysis.screens.filter(s => s.primary_type === 'G');
    if (gamificationScreens.length >= 2) {
      result.frequency++;
      result.apps.push(analysis.app);
      result.evidence.push({
        app: analysis.app,
        positions: gamificationScreens.map(s => s.index),
        example: `${gamificationScreens.length}个游戏化检查点`
      });
    }
  });
  
  return result;
}

function analyzeSocialProofPattern(analyses: PhaseAnalysis[]) {
  const result = { frequency: 0, apps: [] as string[], evidence: [] as PatternEvidence[] };
  
  analyses.forEach(analysis => {
    const socialScreens = analysis.screens.filter(s => s.primary_type === 'S');
    if (socialScreens.length >= 2) {
      result.frequency++;
      result.apps.push(analysis.app);
      result.evidence.push({
        app: analysis.app,
        positions: socialScreens.map(s => s.index),
        example: `${socialScreens.length}个社会认同页`
      });
    }
  });
  
  return result;
}

function getKeyScreensForStrategy(analysis: PhaseAnalysis): number[] {
  // 返回每个阶段的关键页面
  return analysis.phases.map(p => p.startIndex);
}

function generateBorrowRecommendation(analysis: PhaseAnalysis): string {
  const appStrategies: Record<string, string> = {
    'Flo': '医生背书和游戏化旅程地图',
    'Yazio': '卡路里计算实时反馈和进度可视化',
    'Cal AI': 'AI拍照识别的Wow Moment',
    'Noom': '心理学教育和教练支持概念'
  };
  return appStrategies[analysis.app] || '独特的差异化策略';
}

function generatePhase(
  phaseId: string, 
  phaseName: string, 
  recommendedPages: number,
  analyses: PhaseAnalysis[],
  patterns: ExtractedPattern[]
): TemplatePhase {
  // 从各个分析中找到对应阶段的最佳实践页面
  const pages: TemplatePageSuggestion[] = [];
  
  // 简化版：生成通用建议
  const phasePatterns: Record<string, string[]> = {
    'trust-building': ['Authority', 'Social Proof', 'Brand Recognition'],
    'goal-setting': ['Goal Setting', 'Commitment', 'Personalization'],
    'data-collection': ['Progressive Disclosure', 'Value Interleaving'],
    'feature-showcase': ['Interactive Demo', 'Feature Preview'],
    'final-setup': ['Permission Pre-priming', 'Value Exchange'],
    'conversion': ['Labor Illusion', 'Premium Value Chain', 'Celebration']
  };

  const tactics = phasePatterns[phaseId] || [];

  // 生成页面建议
  for (let i = 0; i < recommendedPages; i++) {
    const referenceAnalysis = analyses[i % analyses.length];
    const referencePhase = referenceAnalysis.phases.find(p => 
      p.id.includes(phaseId.split('-')[0]) || p.name.includes(phaseName.split(' ')[0])
    );
    const referenceScreen = referencePhase 
      ? referenceAnalysis.screens.find(s => s.index === referencePhase.startIndex + i)
      : referenceAnalysis.screens[i];

    pages.push({
      index: i + 1,
      phase: phaseName,
      type: referenceScreen?.primary_type || 'V',
      typeName: getTypeName(referenceScreen?.primary_type || 'V'),
      referenceApp: referenceAnalysis.app,
      referenceScreen: referenceScreen?.index || i + 1,
      copyDirection: referenceScreen?.copy.headline || '待定文案方向',
      psychologyTactics: referenceScreen?.psychology || [],
      uiPatternSuggestion: referenceScreen?.ui_pattern || '待定UI模式'
    });
  }

  return {
    id: phaseId,
    name: phaseName,
    recommendedPages,
    pages,
    tactics
  };
}

function getTypeName(type: string): string {
  const typeNames: Record<string, string> = {
    W: 'Welcome',
    Q: 'Question',
    V: 'Value',
    S: 'Social',
    A: 'Authority',
    R: 'Result',
    D: 'Demo',
    C: 'Commit',
    G: 'Gamified',
    L: 'Loading',
    X: 'Permission',
    P: 'Paywall'
  };
  return typeNames[type] || type;
}

