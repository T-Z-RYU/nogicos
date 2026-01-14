# NogicOS Landing Page

The AI that works where you work - Browser. Files. Desktop. Complete context.

## Tech Stack

- **Framework**: Next.js 16 (App Router)
- **Styling**: Tailwind CSS v4
- **Animation**: Motion
- **TypeScript**: Strict mode
- **Deployment**: Vercel

## Design System

Inherits from NogicOS Vision Pro Design System:

- **Background**: `#101012` (Deep Space Black)
- **Primary**: `#4D9FFF` (Vision Pro Blue)
- **Font**: Urbanist
- **Effects**: Glassmorphism + Blur

### Layer Colors
- Browser: `#4ecdc4` (Teal)
- Files: `#a78bfa` (Violet)
- Desktop: `#f472b6` (Pink)

## Getting Started

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## Project Structure

```
src/
├── app/
│   ├── layout.tsx      # Root layout with Urbanist font
│   ├── page.tsx        # Main landing page
│   └── api/waitlist/   # Waitlist API endpoint
├── components/
│   ├── sections/       # Page sections (Hero, Problem, etc.)
│   ├── ui/             # Reusable UI components
│   └── visuals/        # Visual/animation components
└── lib/
    ├── cn.ts           # Classname utility
    └── motion.ts       # Animation presets
```

## Deployment

Deploy to Vercel:

```bash
npx vercel
```

Or connect your GitHub repository to Vercel for automatic deployments.

## License

Private - NogicOS Team
