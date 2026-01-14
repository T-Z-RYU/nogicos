'use client'

import { Button } from '@/components/ui/button'
import { FadeIn } from '@/components/motion'
import { ArrowRight, Sparkles } from 'lucide-react'

export function HeroSection() {
  return (
    <section className="relative flex min-h-[80vh] flex-col items-center justify-center overflow-hidden px-4 py-24">
      {/* Aurora Background */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -left-1/4 -top-1/4 h-[600px] w-[600px] rounded-full bg-gradient-to-br from-purple-500/20 via-blue-500/20 to-cyan-500/20 blur-3xl" />
        <div className="absolute -bottom-1/4 -right-1/4 h-[600px] w-[600px] rounded-full bg-gradient-to-tl from-pink-500/20 via-orange-500/20 to-yellow-500/20 blur-3xl" />
      </div>

      <div className="relative z-10 flex max-w-4xl flex-col items-center text-center">
        <FadeIn delay={0}>
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-border/50 bg-background/50 px-4 py-2 text-sm backdrop-blur-sm">
            <Sparkles className="h-4 w-4 text-primary" />
            <span className="text-muted-foreground">Zino Design System</span>
          </div>
        </FadeIn>

        <FadeIn delay={0.1}>
          <h1 className="mb-6 text-5xl font-bold tracking-tight sm:text-6xl md:text-7xl">
            <span className="bg-gradient-to-r from-foreground via-foreground/80 to-foreground bg-clip-text">
              Build Beautiful
            </span>
            <br />
            <span className="bg-gradient-to-r from-primary via-purple-500 to-pink-500 bg-clip-text text-transparent">
              Interfaces
            </span>
          </h1>
        </FadeIn>

        <FadeIn delay={0.2}>
          <p className="mb-8 max-w-2xl text-lg text-muted-foreground sm:text-xl">
            A modern Next.js template with shadcn/ui, Framer Motion, and design tokens. 
            Ready for building stunning applications.
          </p>
        </FadeIn>

        <FadeIn delay={0.3}>
          <div className="flex flex-col gap-4 sm:flex-row">
            <Button size="lg" className="gap-2">
              Get Started
              <ArrowRight className="h-4 w-4" />
            </Button>
            <Button size="lg" variant="outline">
              View Components
            </Button>
          </div>
        </FadeIn>
      </div>
    </section>
  )
}
