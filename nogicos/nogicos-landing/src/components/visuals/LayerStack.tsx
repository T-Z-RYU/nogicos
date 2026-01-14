"use client";

import { cn } from "@/lib/cn";
import { motion, useMotionValue, useSpring, useTransform } from "motion/react";
import { useRef } from "react";

const layers = [
  {
    id: "desktop",
    label: "Desktop",
    color: "var(--layer-desktop)",
    glowVar: "--layer-desktop-glow",
    description: "See your screen",
    zOffset: 0,
    position: { x: 60, y: 80 },
  },
  {
    id: "files",
    label: "Files",
    color: "var(--layer-files)",
    glowVar: "--layer-files-glow",
    description: "Access your documents",
    zOffset: 40,
    position: { x: 0, y: 0 },
  },
  {
    id: "browser",
    label: "Browser",
    color: "var(--layer-browser)",
    glowVar: "--layer-browser-glow",
    description: "Navigate the web",
    zOffset: 80,
    position: { x: -60, y: -80 },
  },
];

export function LayerStack() {
  const containerRef = useRef<HTMLDivElement>(null);
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  const springConfig = { stiffness: 100, damping: 20, mass: 0.5 };
  const rotateX = useSpring(useTransform(mouseY, [-0.5, 0.5], [12, -12]), springConfig);
  const rotateY = useSpring(useTransform(mouseX, [-0.5, 0.5], [-12, 12]), springConfig);

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top) / rect.height - 0.5;
    mouseX.set(x);
    mouseY.set(y);
  };

  const handleMouseLeave = () => {
    mouseX.set(0);
    mouseY.set(0);
  };

  return (
    <div
      ref={containerRef}
      className="relative w-full max-w-[500px] aspect-square mx-auto"
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{ perspective: "1200px" }}
    >
      {/* Ambient glow behind layers */}
      <div 
        className="absolute inset-0 rounded-full blur-[100px] opacity-40"
        style={{
          background: `radial-gradient(circle, var(--primary-glow) 0%, transparent 70%)`
        }}
      />

      <motion.div
        className="relative w-full h-full"
        style={{
          rotateX,
          rotateY,
          transformStyle: "preserve-3d",
        }}
      >
        {layers.map((layer, index) => (
          <motion.div
            key={layer.id}
            className={cn(
              "absolute w-56 h-36 rounded-[var(--radius-xl)]",
              "flex flex-col justify-between p-5"
            )}
            style={{
              background: `linear-gradient(135deg, ${layer.color}18, ${layer.color}08)`,
              backdropFilter: "blur(var(--glass-blur))",
              WebkitBackdropFilter: "blur(var(--glass-blur))",
              border: `1px solid ${layer.color}50`,
              boxShadow: `
                0 8px 32px rgba(0,0,0,0.4),
                0 0 60px var(${layer.glowVar}),
                inset 0 1px 0 ${layer.color}25
              `,
              left: `calc(50% - 112px + ${layer.position.x}px)`,
              top: `calc(50% - 72px + ${layer.position.y}px)`,
              zIndex: index + 1,
              transform: `translateZ(${layer.zOffset}px)`,
              transformStyle: "preserve-3d",
              willChange: "transform",
            }}
            initial={{ opacity: 0, scale: 0.7, y: 60 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{
              delay: 0.3 + index * 0.15,
              duration: 0.8,
              ease: [0.22, 1, 0.36, 1],
            }}
            whileHover={{
              scale: 1.08,
              transition: { type: "spring", bounce: 0.3, duration: 0.4 },
            }}
          >
            {/* Layer icon & label */}
            <div className="flex items-center gap-2.5">
              <div
                className="w-8 h-8 rounded-[var(--radius-sm)] flex items-center justify-center text-lg"
                style={{
                  background: `${layer.color}20`,
                  border: `1px solid ${layer.color}40`,
                }}
              >
                {layer.id === "browser" ? "🌐" : layer.id === "files" ? "📁" : "🖥️"}
              </div>
              <span
                className="font-semibold text-sm tracking-wide"
                style={{ color: layer.color }}
              >
                {layer.label}
              </span>
            </div>

            {/* Description */}
            <p className="text-xs text-[var(--muted-foreground)] leading-relaxed">
              {layer.description}
            </p>

            {/* Decorative grid */}
            <div 
              className="absolute inset-0 rounded-[var(--radius-xl)] overflow-hidden opacity-10 pointer-events-none"
              style={{
                backgroundImage: `
                  linear-gradient(${layer.color}30 1px, transparent 1px),
                  linear-gradient(90deg, ${layer.color}30 1px, transparent 1px)
                `,
                backgroundSize: "24px 24px",
              }}
            />
          </motion.div>
        ))}

        {/* Central pulse point */}
        <motion.div
          className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-4 h-4 rounded-full"
          style={{
            background: "var(--primary)",
            boxShadow: "0 0 30px var(--primary-glow-strong)",
            zIndex: 10,
          }}
          animate={{
            scale: [1, 1.3, 1],
            boxShadow: [
              "0 0 30px var(--primary-glow)",
              "0 0 50px var(--primary-glow-strong)",
              "0 0 30px var(--primary-glow)",
            ],
          }}
          transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
        />

        {/* Connection lines */}
        <svg
          className="absolute inset-0 w-full h-full pointer-events-none"
          style={{ zIndex: 5 }}
        >
          <defs>
            <linearGradient id="lineGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="var(--layer-desktop)" stopOpacity="0.6" />
              <stop offset="50%" stopColor="var(--layer-files)" stopOpacity="0.6" />
              <stop offset="100%" stopColor="var(--layer-browser)" stopOpacity="0.6" />
            </linearGradient>
          </defs>
          <motion.path
            d="M 38% 68% Q 50% 50% 62% 32%"
            stroke="url(#lineGrad)"
            strokeWidth="2"
            fill="none"
            strokeLinecap="round"
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 1 }}
            transition={{ delay: 1, duration: 1.2, ease: "easeOut" }}
          />
        </svg>
      </motion.div>
    </div>
  );
}
