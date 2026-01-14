"use client";

import { motion } from "motion/react";

const traditionalSteps = [
  "Open ChatGPT/Claude",
  "Copy text from browser",
  "Paste and explain context",
  "Get response",
  "Manually execute actions",
  "Repeat for each task",
];

const nogicosSteps = [
  "Tell NogicOS what you need",
  "AI sees your full context",
  "AI takes action directly",
  "Done.",
];

export function Method() {
  return (
    <section id="method" className="method-section">
      <motion.div
        className="method-header"
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.5 }}
        transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
      >
        <div>
          <div className="section-label">
            <div className="section-number">3</div>
            <span className="section-name">The Method</span>
          </div>
          <h2>
            Learn how it all
            <br />
            comes together
          </h2>
        </div>
        <p>
          NogicOS creates a seamless workflow where AI has complete context and can take action. 
          No more context switching. No more manual execution. Just tell the AI what you need 
          and watch it work across your browser, files, and desktop.
        </p>
      </motion.div>

      <div className="method-compare">
        <motion.div
          className="method-card"
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="method-card-label">Traditional Workflow</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {traditionalSteps.map((step, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 16 }}>
                <div style={{
                  width: 24,
                  height: 24,
                  borderRadius: "50%",
                  border: "1px solid #e5e5e5",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 12,
                  fontWeight: 500,
                  color: "#999",
                  flexShrink: 0,
                }}>
                  {i + 1}
                </div>
                <span style={{
                  fontSize: 14,
                  color: "#666",
                }}>
                  {step}
                </span>
              </div>
            ))}
          </div>
        </motion.div>

        <motion.div
          className="method-card highlight"
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.6, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="method-card-label">NogicOS Workflow</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {nogicosSteps.map((step, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 16 }}>
                <div style={{
                  width: 24,
                  height: 24,
                  borderRadius: "50%",
                  background: i === nogicosSteps.length - 1 ? "white" : "transparent",
                  border: "1px solid white",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 12,
                  fontWeight: 500,
                  color: i === nogicosSteps.length - 1 ? "#0a0a0a" : "white",
                  flexShrink: 0,
                }}>
                  {i === nogicosSteps.length - 1 ? "✓" : i + 1}
                </div>
                <span style={{
                  fontSize: 14,
                  color: i === nogicosSteps.length - 1 ? "white" : "#a3a3a3",
                  fontWeight: i === nogicosSteps.length - 1 ? 600 : 400,
                }}>
                  {step}
                </span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}

