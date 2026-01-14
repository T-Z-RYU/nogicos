"use client";

import { motion } from "motion/react";
import { useState } from "react";
import type { FormStatus } from "@/types";

interface WaitlistFormProps {
  variant?: "default" | "compact";
  placeholder?: string;
  buttonText?: string;
  onSuccess?: () => void;
}

export function WaitlistForm({
  variant = "default",
  placeholder = "your@email.com",
  buttonText = "Get Early Access",
  onSuccess,
}: WaitlistFormProps) {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<FormStatus>("idle");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

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
        onSuccess?.();
      } else {
        setStatus("error");
      }
    } catch {
      setStatus("error");
    }
  };

  if (status === "success") {
    return (
      <motion.div
        className="form-success"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
      >
        <span className="success-icon">✓</span>
        <span>You&apos;re on the list!</span>
      </motion.div>
    );
  }

  return (
    <form
      onSubmit={handleSubmit}
      className={`waitlist-form ${variant === "compact" ? "waitlist-form--compact" : ""}`}
    >
      <input
        type="email"
        placeholder={placeholder}
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        disabled={status === "loading"}
        required
        className="waitlist-input"
      />
      <motion.button
        type="submit"
        className="btn btn-primary"
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        disabled={status === "loading"}
      >
        {status === "loading" ? "Joining..." : buttonText}
      </motion.button>
      {status === "error" && (
        <p className="form-error">Something went wrong. Please try again.</p>
      )}
    </form>
  );
}






