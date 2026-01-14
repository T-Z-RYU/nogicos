"use client";

import { AnimatePresence, motion, useInView } from "motion/react";
import { useRef, useState } from "react";

export function Waitlist() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !email.includes("@")) {
      setStatus("error");
      return;
    }
    setStatus("loading");
    try {
      const res = await fetch("/api/waitlist", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      if (res.ok) {
        setStatus("success");
        setEmail("");
      } else {
        setStatus("error");
      }
    } catch {
      setStatus("error");
    }
  };

  return (
    <section id="waitlist" className="section" ref={ref} style={{ position: "relative", overflow: "hidden" }}>
      {/* Background glow */}
      <div style={{
        position: "absolute",
        bottom: "-50%",
        left: "50%",
        transform: "translateX(-50%)",
        width: "150%",
        height: "100%",
        background: "radial-gradient(ellipse 50% 50% at 50% 100%, var(--blue-glow), transparent 60%)",
        opacity: 0.4,
        pointerEvents: "none",
      }} />

      <div className="container" style={{ position: "relative", zIndex: 10 }}>
        <motion.div
          className="text-center max-w-2xl mx-auto"
          initial={{ opacity: 0, y: 40 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        >
          <h2 className="section-title mb-6">
            Be the first to try{" "}
            <span className="text-gradient">NogicOS</span>
          </h2>
          <p className="section-desc mb-12">
            Join the waitlist for early access. We're onboarding users in waves.
          </p>

          <AnimatePresence mode="wait">
            {status === "success" ? (
              <motion.div
                key="success"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }}
                className="glass-card max-w-md mx-auto text-center py-12"
              >
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
                  style={{
                    width: 72,
                    height: 72,
                    borderRadius: "50%",
                    background: "rgba(34, 197, 94, 0.15)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    margin: "0 auto 20px",
                    fontSize: "2rem",
                    color: "#22c55e",
                  }}
                >
                  ✓
                </motion.div>
                <h3 style={{ fontSize: "1.5rem", fontWeight: 600, marginBottom: 8 }}>You're on the list!</h3>
                <p style={{ color: "var(--gray-300)" }}>We'll notify you when NogicOS is ready.</p>
              </motion.div>
            ) : (
              <motion.form
                key="form"
                onSubmit={handleSubmit}
                className="flex flex-col sm:flex-row gap-4 max-w-lg mx-auto"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <input
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => { setEmail(e.target.value); if (status === "error") setStatus("idle"); }}
                  className="input flex-1"
                  style={{
                    borderColor: status === "error" ? "#ef4444" : undefined,
                  }}
                  disabled={status === "loading"}
                />
                <motion.button
                  type="submit"
                  className="btn-primary"
                  style={{ padding: "18px 32px", whiteSpace: "nowrap" }}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  disabled={status === "loading"}
                >
                  {status === "loading" ? (
                    <motion.span
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      style={{
                        display: "block",
                        width: 20,
                        height: 20,
                        border: "2px solid rgba(0,0,0,0.2)",
                        borderTopColor: "var(--void)",
                        borderRadius: "50%",
                      }}
                    />
                  ) : (
                    "Join Waitlist"
                  )}
                </motion.button>
              </motion.form>
            )}
          </AnimatePresence>

          <motion.p
            style={{ color: "var(--gray-500)", fontSize: "0.875rem", marginTop: 20 }}
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            transition={{ delay: 0.4 }}
          >
            No spam. Unsubscribe anytime.
          </motion.p>
        </motion.div>
      </div>
    </section>
  );
}
