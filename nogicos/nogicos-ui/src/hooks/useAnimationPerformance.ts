/**
 * useAnimationPerformance - 2026 顶级PerformanceMonitor Hook
 * 
 * 功能：
 * 1. 实时 FPS Monitor
 * 2. Low端设备AutoDowngrade
 * 3. Animation复杂度自适应
 * 4. PerformanceAlert
 */

import { useState, useEffect, useRef, useCallback } from 'react';

// ============================================================================
// Types
// ============================================================================

interface PerformanceMetrics {
  fps: number;
  avgFps: number;
  frameTime: number;  // ms
  isLowPerformance: boolean;
}

interface AnimationConfig {
  enableComplexAnimations: boolean;
  enableParticles: boolean;
  enableBlur: boolean;
  enableShadows: boolean;
  particleCount: number;  // particle count limit
  animationDuration: number;  // animation duration multiplier (1 = normal, 2 = moreFast)
}

interface UseAnimationPerformanceOptions {
  /** FPS Threshold：Low于此值TriggerDowngrade (Default 30) */
  fpsThreshold?: number;
  /** 采样WindowSize (Default 60 帧) */
  sampleSize?: number;
  /** YesNoEnableAutoDowngrade (Default true) */
  autoDegrade?: boolean;
  /** YesNo在On发模式Display FPS (Default true) */
  showDebugFps?: boolean;
}

interface UseAnimationPerformanceReturn {
  metrics: PerformanceMetrics;
  config: AnimationConfig;
  /** ManualSetDowngrade级别 (0 = 全特效, 1 = 轻度Downgrade, 2 = Medium度Downgrade, 3 = 最LowConfig) */
  setDegradeLevel: (level: 0 | 1 | 2 | 3) => void;
  /** 强制Reset为最HighConfig */
  resetToHighest: () => void;
}

// ============================================================================
// Constants
// ============================================================================

const DEFAULT_CONFIG: AnimationConfig = {
  enableComplexAnimations: true,
  enableParticles: true,
  enableBlur: true,
  enableShadows: true,
  particleCount: 5,
  animationDuration: 1,
};

const DEGRADE_CONFIGS: Record<0 | 1 | 2 | 3, AnimationConfig> = {
  0: { // mostHighConfig
    enableComplexAnimations: true,
    enableParticles: true,
    enableBlur: true,
    enableShadows: true,
    particleCount: 5,
    animationDuration: 1,
  },
  1: { // light downgrade
    enableComplexAnimations: true,
    enableParticles: true,
    enableBlur: true,
    enableShadows: false,
    particleCount: 3,
    animationDuration: 1,
  },
  2: { // MediumdegreeDowngrade
    enableComplexAnimations: true,
    enableParticles: false,
    enableBlur: false,
    enableShadows: false,
    particleCount: 2,
    animationDuration: 1.5,
  },
  3: { // mostLowConfig
    enableComplexAnimations: false,
    enableParticles: false,
    enableBlur: false,
    enableShadows: false,
    particleCount: 0,
    animationDuration: 2,
  },
};

// ============================================================================
// Hook
// ============================================================================

export function useAnimationPerformance(
  options: UseAnimationPerformanceOptions = {}
): UseAnimationPerformanceReturn {
  const {
    fpsThreshold = 30,
    sampleSize = 60,
    autoDegrade = true,
  } = options;

  // State
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    fps: 60,
    avgFps: 60,
    frameTime: 16.67,
    isLowPerformance: false,
  });
  
  const [degradeLevel, setDegradeLevel] = useState<0 | 1 | 2 | 3>(0);
  const [config, setConfig] = useState<AnimationConfig>(DEFAULT_CONFIG);
  
  // Refs
  const frameTimesRef = useRef<number[]>([]);
  const lastTimeRef = useRef<number>(performance.now());
  const rafRef = useRef<number>(0);
  const consecutiveLowFramesRef = useRef<number>(0);
  
  // FPS MonitorLoop
  useEffect(() => {
    let isActive = true;
    
    const measureFrame = () => {
      if (!isActive) return;
      
      const now = performance.now();
      const delta = now - lastTimeRef.current;
      lastTimeRef.current = now;
      
      // RecordframeTime
      frameTimesRef.current.push(delta);
      if (frameTimesRef.current.length > sampleSize) {
        frameTimesRef.current.shift();
      }
      
      // calculate FPS
      const currentFps = delta > 0 ? Math.round(1000 / delta) : 60;
      const avgDelta = frameTimesRef.current.reduce((a, b) => a + b, 0) / frameTimesRef.current.length;
      const avgFps = avgDelta > 0 ? Math.round(1000 / avgDelta) : 60;
      
      // DetectionLowPerformance
      const isLow = avgFps < fpsThreshold;
      
      if (isLow) {
        consecutiveLowFramesRef.current++;
      } else {
        consecutiveLowFramesRef.current = 0;
      }
      
      // update state (throttle：each 10 frameUpdateonce）
      if (frameTimesRef.current.length % 10 === 0) {
        setMetrics({
          fps: currentFps,
          avgFps,
          frameTime: avgDelta,
          isLowPerformance: isLow,
        });
        
        // AutoDowngradelogic
        if (autoDegrade && consecutiveLowFramesRef.current > 30) {
          // continuous 30 frameLowatThreshold，UpgradeoneaDowngradelevelother
          setDegradeLevel(prev => Math.min(prev + 1, 3) as 0 | 1 | 2 | 3);
          consecutiveLowFramesRef.current = 0;
        }
      }
      
      rafRef.current = requestAnimationFrame(measureFrame);
    };
    
    rafRef.current = requestAnimationFrame(measureFrame);
    
    return () => {
      isActive = false;
      cancelAnimationFrame(rafRef.current);
    };
  }, [fpsThreshold, sampleSize, autoDegrade]);
  
  // RootdataDowngradelevelotherUpdateConfig
  useEffect(() => {
    setConfig(DEGRADE_CONFIGS[degradeLevel]);
  }, [degradeLevel]);
  
  // ManualSetDowngradelevelother
  const handleSetDegradeLevel = useCallback((level: 0 | 1 | 2 | 3) => {
    setDegradeLevel(level);
    consecutiveLowFramesRef.current = 0;
  }, []);
  
  // ResettomostHighConfig
  const resetToHighest = useCallback(() => {
    setDegradeLevel(0);
    consecutiveLowFramesRef.current = 0;
    frameTimesRef.current = [];
  }, []);
  
  return {
    metrics,
    config,
    setDegradeLevel: handleSetDegradeLevel,
    resetToHighest,
  };
}

// ============================================================================
// Context (Optional：for global sharedPerformanceConfig)
// ============================================================================

import { createContext, useContext } from 'react';

interface AnimationPerformanceContextValue {
  config: AnimationConfig;
  metrics: PerformanceMetrics;
}

export const AnimationPerformanceContext = createContext<AnimationPerformanceContextValue>({
  config: DEFAULT_CONFIG,
  metrics: {
    fps: 60,
    avgFps: 60,
    frameTime: 16.67,
    isLowPerformance: false,
  },
});

export const useAnimationConfig = () => {
  const { config } = useContext(AnimationPerformanceContext);
  return config;
};

export const useAnimationMetrics = () => {
  const { metrics } = useContext(AnimationPerformanceContext);
  return metrics;
};
