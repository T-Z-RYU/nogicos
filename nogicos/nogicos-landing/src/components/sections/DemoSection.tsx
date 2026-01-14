"use client";

import { motion } from "motion/react";

export function DemoSection() {
  return (
    <section className="demo-section">
      <motion.div
        className="demo-content"
        initial={{ opacity: 0, x: -40 }}
        whileInView={{ opacity: 1, x: 0 }}
        viewport={{ once: true, amount: 0.5 }}
        transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
      >
        <h2>
          See NogicOS in action.
          <br />
          Three layers. One AI.
        </h2>
        <p style={{ 
          color: "var(--text-secondary)", 
          marginTop: 16, 
          marginBottom: 24,
          lineHeight: 1.7,
          maxWidth: 400
        }}>
          A unified interface that gives AI complete visibility into your 
          browser, files, and desktop—all working together.
        </p>
        <motion.button
          className="btn btn-filled"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => document.getElementById("waitlist")?.scrollIntoView({ behavior: "smooth" })}
        >
          Join Waitlist
        </motion.button>
      </motion.div>

      <motion.div
        className="demo-image"
        initial={{ opacity: 0, x: 40 }}
        whileInView={{ opacity: 1, x: 0 }}
        viewport={{ once: true, amount: 0.5 }}
        transition={{ duration: 0.8, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
        style={{ padding: 32 }}
      >
        {/* Horizontal Three Layer Stack */}
        <div style={{
          display: "flex",
          flexDirection: "column",
          gap: 16,
          width: "100%",
        }}>
          {/* Browser Layer */}
          <motion.div
            style={{
              background: "rgba(255,255,255,0.02)",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: 8,
              padding: 20,
            }}
            whileHover={{ backgroundColor: "rgba(255,255,255,0.04)" }}
          >
            <div style={{ 
              display: "flex",
              alignItems: "center",
              gap: 16,
            }}>
              <div style={{
                width: 40,
                height: 40,
                background: "rgba(255,255,255,0.05)",
                borderRadius: 8,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="2" y1="12" x2="22" y2="12" />
                  <path d="M12 2a15 15 0 0 1 4 10 15 15 0 0 1-4 10 15 15 0 0 1-4-10 15 15 0 0 1 4-10z" />
                </svg>
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 14, fontWeight: 500, marginBottom: 4 }}>Browser</div>
                <div style={{ fontSize: 12, color: "var(--text-muted)" }}>Web automation & interaction</div>
              </div>
              <div style={{ 
                padding: "4px 10px",
                background: "rgba(255,255,255,0.05)",
                borderRadius: 4,
                fontSize: 11,
                color: "var(--text-muted)",
              }}>
                Layer 1
              </div>
            </div>
          </motion.div>

          {/* Files Layer */}
          <motion.div
            style={{
              background: "rgba(255,255,255,0.02)",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: 8,
              padding: 20,
            }}
            whileHover={{ backgroundColor: "rgba(255,255,255,0.04)" }}
          >
            <div style={{ 
              display: "flex",
              alignItems: "center",
              gap: 16,
            }}>
              <div style={{
                width: 40,
                height: 40,
                background: "rgba(255,255,255,0.05)",
                borderRadius: 8,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
                </svg>
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 14, fontWeight: 500, marginBottom: 4 }}>Files</div>
                <div style={{ fontSize: 12, color: "var(--text-muted)" }}>Local file system access</div>
              </div>
              <div style={{ 
                padding: "4px 10px",
                background: "rgba(255,255,255,0.05)",
                borderRadius: 4,
                fontSize: 11,
                color: "var(--text-muted)",
              }}>
                Layer 2
              </div>
            </div>
          </motion.div>

          {/* Desktop Layer */}
          <motion.div
            style={{
              background: "rgba(255,255,255,0.02)",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: 8,
              padding: 20,
            }}
            whileHover={{ backgroundColor: "rgba(255,255,255,0.04)" }}
          >
            <div style={{ 
              display: "flex",
              alignItems: "center",
              gap: 16,
            }}>
              <div style={{
                width: 40,
                height: 40,
                background: "rgba(255,255,255,0.05)",
                borderRadius: 8,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <rect x="2" y="3" width="20" height="14" rx="2" ry="2" />
                  <line x1="8" y1="21" x2="16" y2="21" />
                  <line x1="12" y1="17" x2="12" y2="21" />
                </svg>
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 14, fontWeight: 500, marginBottom: 4 }}>Desktop</div>
                <div style={{ fontSize: 12, color: "var(--text-muted)" }}>Screen capture & UI control</div>
              </div>
              <div style={{ 
                padding: "4px 10px",
                background: "rgba(255,255,255,0.05)",
                borderRadius: 4,
                fontSize: 11,
                color: "var(--text-muted)",
              }}>
                Layer 3
              </div>
            </div>
          </motion.div>
        </div>
      </motion.div>
    </section>
  );
}
