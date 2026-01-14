"use client";

import { cn } from "@/lib/cn";
import { motion, type HTMLMotionProps } from "motion/react";
import { forwardRef } from "react";

interface ButtonProps extends Omit<HTMLMotionProps<"button">, "ref"> {
  variant?: "primary" | "glass" | "ghost";
  size?: "sm" | "md" | "lg";
  children: React.ReactNode;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", children, ...props }, ref) => {
    const baseStyles =
      "relative inline-flex items-center justify-center font-semibold transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--background)] disabled:opacity-50 disabled:cursor-not-allowed";

    const variants = {
      primary: "btn-primary",
      glass: "glass-button",
      ghost: "text-[var(--muted-foreground)] hover:text-[var(--foreground)] hover:bg-white/5 rounded-[var(--radius)]",
    };

    const sizes = {
      sm: "px-4 py-2 text-sm rounded-[var(--radius)]",
      md: "px-6 py-3 text-base rounded-[var(--radius-lg)]",
      lg: "px-8 py-4 text-lg rounded-[var(--radius-xl)]",
    };

    return (
      <motion.button
        ref={ref}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        transition={{ type: "spring", bounce: 0.25, duration: 0.3 }}
        style={{ willChange: "transform" }}
        {...props}
      >
        {children}
      </motion.button>
    );
  }
);

Button.displayName = "Button";

export { Button };
