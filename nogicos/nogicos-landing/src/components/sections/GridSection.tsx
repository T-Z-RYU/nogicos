"use client";

import { motion } from "motion/react";

export function GridSection() {
  return (
    <section className="quote-section">
      <motion.div
        className="quote-content"
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.5 }}
        transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
      >
        <div className="quote-mark">"</div>
        <h2>
          AI has been blind to your workspace.
          <br />
          <span className="highlight">NogicOS changes that.</span>
        </h2>
        <p>
          Complete visibility into your browser, files, and desktop. 
          No more copy-pasting. No more explaining what's on your screen. 
          Just natural collaboration with AI that truly sees your work.
        </p>
      </motion.div>
    </section>
  );
}
