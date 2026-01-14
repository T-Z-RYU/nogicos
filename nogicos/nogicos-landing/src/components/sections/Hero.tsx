"use client";

import { motion, AnimatePresence } from "motion/react";
import { useState, useEffect, useRef } from "react";

// User's daily pain points - more emotional
const painPoints = [
  "copy-pasting context to ChatGPT",
  "uploading files one by one",
  "describing what's on your screen",
  "being AI's human clipboard",
  "explaining the same thing twice",
];

export function Hero() {
  const [currentPain, setCurrentPain] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!isPaused) {
      intervalRef.current = setInterval(() => {
        setCurrentPain((prev) => (prev + 1) % painPoints.length);
      }, 5000); // 5SecondSwitch
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [isPaused]);

  return (
    <section className="hero">
      <motion.div
        className="hero-content"
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
      >
        {/* 痛点驱动的title */}
        <p className="hero-eyebrow">For knowledge workers tired of</p>
        
        <h1 
          className="hero-title"
          onMouseEnter={() => setIsPaused(true)}
          onMouseLeave={() => setIsPaused(false)}
        >
          <AnimatePresence mode="wait">
            <motion.span
              key={currentPain}
              className="pain-text"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
            >
              {painPoints[currentPain]}
            </motion.span>
          </AnimatePresence>
        </h1>

        <p className="hero-subtitle">
          NogicOS is an AI that actually sees your screen, reads your files, 
          and works in your browser. <strong>No more copying. No more explaining.</strong>
        </p>

        {/* Number证明 - 更具体 */}
        <div className="hero-stats">
          <div className="stat">
            <span className="stat-number">30s</span>
            <span className="stat-label">First task</span>
          </div>
          <div className="stat-arrow">→</div>
          <div className="stat">
            <span className="stat-number">&lt;1s</span>
            <span className="stat-label">Same task later</span>
          </div>
        </div>

        {/* CTA 区域 - 加紧迫感 */}
        <div className="hero-cta">
          <motion.button
            className="btn btn-primary"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => document.getElementById("waitlist")?.scrollIntoView({ behavior: "smooth" })}
          >
            Request Early Access
          </motion.button>
          <p className="hero-cta-note">
            <span className="pulse-dot" /> 
            <strong>Only 50 spots left</strong> in private beta
          </p>
        </div>

        {/* 信任徽章 */}
        <div className="hero-trust">
          <span>Trusted by teams at</span>
          <div className="trust-logos">
            <span>YC Founders</span>
            <span>•</span>
            <span>Stanford</span>
            <span>•</span>
            <span>Remote Teams</span>
          </div>
        </div>
      </motion.div>

      {/* Demo 预览 - 更True实 */}
      <motion.div
        className="hero-demo"
        initial={{ opacity: 0, y: 60 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
      >
        <div className="demo-window">
          <div className="demo-chrome">
            <div className="demo-dots">
              <span /><span /><span />
            </div>
            <div className="demo-url">
              <span className="demo-url-icon">◎</span>
              <span>nogicos://workspace</span>
            </div>
          </div>
          <div className="demo-content">
            {/* 模拟对话 - 更True实的场景 */}
            <div className="demo-message user">
              <p>"Find all competitor pricing pages and summarize them in a doc"</p>
            </div>
            <div className="demo-message ai">
              <div className="demo-thinking">
                <span className="thinking-dot" />
                <span>Working on it...</span>
              </div>
              <div className="demo-actions">
                <div className="action done">
                  <span className="action-check">✓</span>
                  <span>Found 8 competitor sites</span>
                </div>
                <div className="action done">
                  <span className="action-check">✓</span>
                  <span>Extracted pricing data</span>
                </div>
                <div className="action done">
                  <span className="action-check">✓</span>
                  <span>Created comparison.md</span>
                </div>
              </div>
              <p className="demo-complete">Done in 23 seconds</p>
            </div>
          </div>
        </div>
        <p className="demo-caption">Real workflow. No copy-paste. No uploads.</p>
      </motion.div>
    </section>
  );
}
