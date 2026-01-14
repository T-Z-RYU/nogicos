"use client";

import { motion, useInView } from "motion/react";
import { useRef } from "react";

const features = [
  {
    icon: "👁️",
    title: "Complete Context",
    subtitle: "AI that sees your whole workspace",
    description: "Browser tabs, local files, desktop state. NogicOS sees everything you're working with—no copy-paste needed.",
    color: "#f59e0b",
  },
  {
    icon: "🎯",
    title: "Direct Action",
    subtitle: "Not just chat, actual execution",
    description: "Click buttons, fill forms, create files. NogicOS doesn't just suggest—it does the work in your environment.",
    color: "#3b82f6",
  },
  {
    icon: "🔒",
    title: "Local-First",
    subtitle: "Your data never leaves",
    description: "Everything runs on your machine. No cloud uploads, no data mining. Complete privacy by design.",
    color: "#22c55e",
  },
];

export function Features() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section id="features" className="section" ref={ref}>
      <div className="container">
        {/* Section Header */}
        <motion.div
          className="section-header"
          initial={{ opacity: 0, y: 40 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        >
          <h2 className="section-title">
            Built different.{" "}
            <span className="text-gradient">Works better.</span>
          </h2>
          <p className="section-desc">
            Three principles that make NogicOS uniquely powerful.
          </p>
        </motion.div>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-3 gap-6">
          {features.map((feature, i) => (
            <motion.div
              key={feature.title}
              className="glass-card"
              style={{ display: "flex", flexDirection: "column" }}
              initial={{ opacity: 0, y: 40 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.1 + i * 0.15, duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
              whileHover={{ y: -8 }}
            >
              {/* Icon */}
              <div
                className="feature-icon"
                style={{
                  background: `linear-gradient(135deg, ${feature.color}20, ${feature.color}08)`,
                  border: `1px solid ${feature.color}30`,
                  boxShadow: `0 8px 32px ${feature.color}20`,
                }}
              >
                {feature.icon}
              </div>

              {/* Title */}
              <h3 style={{
                fontSize: "2rem",
                fontWeight: 700,
                color: feature.color,
                marginBottom: 4,
                letterSpacing: "-0.02em",
              }}>
                {feature.title}
              </h3>

              {/* Subtitle */}
              <p style={{
                fontSize: "1rem",
                fontWeight: 500,
                color: "var(--white)",
                marginBottom: 12,
              }}>
                {feature.subtitle}
              </p>

              {/* Description */}
              <p style={{
                fontSize: "0.9375rem",
                color: "var(--gray-300)",
                lineHeight: 1.7,
                flex: 1,
              }}>
                {feature.description}
              </p>

              {/* Progress bar */}
              <div style={{ marginTop: 24, paddingTop: 20, borderTop: "1px solid var(--glass-border)" }}>
                <motion.div
                  style={{
                    height: 4,
                    borderRadius: 2,
                    background: `linear-gradient(90deg, ${feature.color}, ${feature.color}80)`,
                  }}
                  initial={{ width: 0 }}
                  animate={inView ? { width: `${30 + i * 25}%` } : {}}
                  transition={{ delay: 0.6 + i * 0.1, duration: 1, ease: [0.16, 1, 0.3, 1] }}
                />
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
