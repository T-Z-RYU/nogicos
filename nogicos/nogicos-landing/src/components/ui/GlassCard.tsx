"use client";

import { cn } from "@/lib/cn";
import { motion } from "motion/react";
import { ReactNode } from "react";

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  elevated?: boolean;
  hover?: boolean;
  glow?: "primary" | "browser" | "files" | "desktop" | false;
}

export function GlassCard({
  children,
  className,
  elevated = false,
  hover = true,
  glow = false,
}: GlassCardProps) {
  const glowClasses = {
    primary: "glow-primary",
    browser: "glow-browser",
    files: "glow-files",
    desktop: "glow-desktop",
  };

  return (
    <motion.div
      className={cn(
        elevated ? "glass-panel-elevated" : "glass-panel",
        glow && glowClasses[glow],
        "p-6",
        className
      )}
      whileHover={
        hover
          ? {
              borderColor: "rgba(255, 255, 255, 0.15)",
              y: -4,
            }
          : undefined
      }
      transition={{ type: "spring", bounce: 0.1, duration: 0.4 }}
      style={{ willChange: "transform" }}
    >
      {children}
    </motion.div>
  );
}
