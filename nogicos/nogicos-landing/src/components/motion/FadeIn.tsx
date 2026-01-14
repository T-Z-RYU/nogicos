"use client";

import { motion, type HTMLMotionProps } from "motion/react";
import { type ReactNode } from "react";

interface FadeInProps extends Omit<HTMLMotionProps<"div">, "children"> {
  children: ReactNode;
  delay?: number;
  duration?: number;
  direction?: "up" | "down" | "left" | "right" | "none";
  distance?: number;
  once?: boolean;
  amount?: number;
  className?: string;
}

const directionMap: Record<string, { x?: number; y?: number }> = {
  up: { y: 1 },
  down: { y: -1 },
  left: { x: 1 },
  right: { x: -1 },
  none: { x: 0, y: 0 },
};

export function FadeIn({
  children,
  delay = 0,
  duration = 0.6,
  direction = "up",
  distance = 30,
  once = true,
  amount = 0.3,
  className,
  ...props
}: FadeInProps) {
  const { x = 0, y = 0 } = directionMap[direction];

  return (
    <motion.div
      initial={{ opacity: 0, x: x * distance, y: y * distance }}
      whileInView={{ opacity: 1, x: 0, y: 0 }}
      viewport={{ once, amount }}
      transition={{
        delay,
        duration,
        ease: [0.16, 1, 0.3, 1],
      }}
      className={className}
      {...props}
    >
      {children}
    </motion.div>
  );
}

