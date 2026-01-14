import type { Metadata } from "next";
import { Urbanist } from "next/font/google";
import "./globals.css";

const urbanist = Urbanist({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-urbanist",
  weight: ["300", "400", "500", "600", "700", "800"],
});

export const metadata: Metadata = {
  title: "NogicOS - The AI that works where you work",
  description:
    "Browser. Files. Desktop. One AI, complete context. NogicOS is the first AI that works across your browser, files, and desktop as one unified workspace.",
  keywords: [
    "AI",
    "artificial intelligence",
    "browser automation",
    "desktop AI",
    "productivity",
    "knowledge workers",
    "AI assistant",
  ],
  authors: [{ name: "NogicOS Team" }],
  openGraph: {
    title: "NogicOS - The AI that works where you work",
    description:
      "Browser. Files. Desktop. One AI, complete context. The first AI that sees your complete work environment.",
    type: "website",
    locale: "en_US",
    siteName: "NogicOS",
  },
  twitter: {
    card: "summary_large_image",
    title: "NogicOS - The AI that works where you work",
    description:
      "Browser. Files. Desktop. One AI, complete context. The first AI that sees your complete work environment.",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={urbanist.variable}>
      <body className="font-sans antialiased">{children}</body>
    </html>
  );
}
