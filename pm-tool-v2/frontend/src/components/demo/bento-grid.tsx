'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { StaggerChildren, StaggerItem } from '@/components/motion'
import { motion } from 'framer-motion'
import { Layers, Palette, Sparkles, Zap, Box, MousePointer } from 'lucide-react'

const features = [
  {
    icon: Layers,
    title: 'Bento Grid',
    description: 'Modular card layouts with visual hierarchy',
    className: 'md:col-span-2',
    gradient: 'from-blue-500/10 to-cyan-500/10',
  },
  {
    icon: Palette,
    title: 'Design Tokens',
    description: 'Consistent colors, spacing, and typography',
    className: 'md:col-span-1',
    gradient: 'from-purple-500/10 to-pink-500/10',
  },
  {
    icon: Sparkles,
    title: 'Glassmorphism',
    description: 'Modern frosted glass effects',
    className: 'md:col-span-1',
    gradient: 'from-orange-500/10 to-yellow-500/10',
  },
  {
    icon: Zap,
    title: 'Framer Motion',
    description: 'Smooth animations and transitions',
    className: 'md:col-span-1',
    gradient: 'from-green-500/10 to-emerald-500/10',
  },
  {
    icon: Box,
    title: 'shadcn/ui',
    description: 'Beautiful, accessible components',
    className: 'md:col-span-1',
    gradient: 'from-red-500/10 to-rose-500/10',
  },
  {
    icon: MousePointer,
    title: 'Micro-interactions',
    description: 'Delightful hover and click effects',
    className: 'md:col-span-2',
    gradient: 'from-indigo-500/10 to-violet-500/10',
  },
]

export function BentoGrid() {
  return (
    <section className="px-4 py-24">
      <div className="mx-auto max-w-6xl">
        <StaggerChildren className="grid grid-cols-1 gap-4 md:grid-cols-4" delayChildren={0.2}>
          {features.map((feature) => (
            <StaggerItem key={feature.title} className={feature.className}>
              <motion.div
                whileHover={{ scale: 1.02, y: -4 }}
                transition={{ type: 'spring', stiffness: 300, damping: 20 }}
              >
                <Card className="group relative h-full overflow-hidden border-border/50 bg-card/50 backdrop-blur-sm transition-colors hover:border-border">
                  {/* Gradient Background */}
                  <div
                    className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-0 transition-opacity group-hover:opacity-100`}
                  />

                  <CardHeader className="relative">
                    <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                      <feature.icon className="h-5 w-5 text-primary" />
                    </div>
                    <CardTitle className="text-lg">{feature.title}</CardTitle>
                    <CardDescription>{feature.description}</CardDescription>
                  </CardHeader>

                  <CardContent className="relative">
                    {/* Placeholder content area */}
                    <div className="h-16 rounded-lg bg-muted/50" />
                  </CardContent>
                </Card>
              </motion.div>
            </StaggerItem>
          ))}
        </StaggerChildren>
      </div>
    </section>
  )
}
