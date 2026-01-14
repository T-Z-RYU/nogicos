'use client'

import { motion, type HTMLMotionProps } from 'framer-motion'
import { forwardRef } from 'react'

interface StaggerChildrenProps extends HTMLMotionProps<'div'> {
  staggerDelay?: number
  delayChildren?: number
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: (custom: { staggerDelay: number; delayChildren: number }) => ({
    opacity: 1,
    transition: {
      staggerChildren: custom.staggerDelay,
      delayChildren: custom.delayChildren,
    },
  }),
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
      ease: [0.25, 0.4, 0.25, 1] as const,
    },
  },
}

export const StaggerChildren = forwardRef<HTMLDivElement, StaggerChildrenProps>(
  ({ children, staggerDelay = 0.1, delayChildren = 0, ...props }, ref) => {
    return (
      <motion.div
        ref={ref}
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        custom={{ staggerDelay, delayChildren }}
        {...props}
      >
        {children}
      </motion.div>
    )
  }
)

StaggerChildren.displayName = 'StaggerChildren'

export const StaggerItem = forwardRef<HTMLDivElement, HTMLMotionProps<'div'>>(
  ({ children, ...props }, ref) => {
    return (
      <motion.div ref={ref} variants={itemVariants} {...props}>
        {children}
      </motion.div>
    )
  }
)

StaggerItem.displayName = 'StaggerItem'
