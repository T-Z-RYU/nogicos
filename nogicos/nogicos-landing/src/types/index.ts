// ================================
// Global Type Definitions
// ================================

export interface ProblemItem {
  before: string;
  pain: string;
  result: string;
}

export interface Capability {
  icon: string;
  title: string;
  description: string;
  example: string;
}

export interface Testimonial {
  quote: string;
  name: string;
  role: string;
  company: string;
}

export interface Stat {
  value: string;
  label: string;
}

export interface Link {
  label: string;
  href: string;
}

export interface Benefit {
  icon: string;
  text: string;
}

// Waitlist Form Status
export type FormStatus = "idle" | "loading" | "success" | "error";






