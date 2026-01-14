"use client";

import { motion } from "motion/react";
import { type ReactNode, Children } from "react";

interface StaggerListProps {
  children: ReactNode;
  staggerDelay?: number;
  initialDelay?: number;
  duration?: number;
  className?: string;
  itemClassName?: string;
  once?: boolean;
  amount?: number;
}

export function StaggerList({
  children,
  staggerDelay = 0.1,
  initialDelay = 0,
  duration = 0.5,
  className,
  itemClassName,
  once = true,
  amount = 0.3,
}: StaggerListProps) {
  const childArray = Children.toArray(children);

  return (
    <div className={className}>
      {childArray.map((child, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once, amount }}
          transition={{
            delay: initialDelay + i * staggerDelay,
            duration,
            ease: [0.16, 1, 0.3, 1],
          }}
          className={itemClassName}
        >
          {child}
        </motion.div>
      ))}
    </div>
  );
}






