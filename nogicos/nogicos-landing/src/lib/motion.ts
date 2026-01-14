// Motion animation presets for NogicOS Landing Page
// Using spring animations via Motion MCP

export const springPresets = {
  // Hero section entrance - snappy with slight bounce
  hero: {
    type: "spring" as const,
    bounce: 0.15,
    duration: 0.8,
  },
  // Scroll reveal - smooth and subtle
  reveal: {
    type: "spring" as const,
    bounce: 0.1,
    duration: 0.5,
  },
  // Button interactions - quick and responsive
  button: {
    type: "spring" as const,
    bounce: 0.25,
    duration: 0.3,
  },
  // Card hover - gentle
  card: {
    type: "spring" as const,
    bounce: 0.1,
    duration: 0.4,
  },
};

// Stagger delays for child animations
export const staggerPresets = {
  fast: 0.05,
  normal: 0.1,
  slow: 0.15,
};

// Common animation variants
export const fadeInUp = {
  initial: { opacity: 0, y: 30 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -10 },
};

export const fadeIn = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
};

export const scaleIn = {
  initial: { opacity: 0, scale: 0.95 },
  animate: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.95 },
};

// Container variants for staggered children
export const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: staggerPresets.normal,
      delayChildren: 0.2,
    },
  },
};

export const staggerItem = {
  initial: { opacity: 0, y: 20 },
  animate: { 
    opacity: 1, 
    y: 0,
    transition: springPresets.reveal,
  },
};

// Viewport settings for scroll animations
export const viewportSettings = {
  once: true,
  margin: "-100px",
};






