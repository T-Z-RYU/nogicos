import type { Metadata } from "next";
import { Urbanist, JetBrains_Mono, Outfit } from "next/font/google";
import "./globals.css";

// 复刻老版字体: Urbanist
const urbanist = Urbanist({
  variable: "--font-urbanist",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  display: "swap",
});

// VitaFlow 字体: Outfit
const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  display: "swap",
});

// 等宽字体: JetBrains Mono (更现代的替代 SF Mono)
const jetbrainsMono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
  weight: ["400", "500"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "PM Tool v2 - 竞品截图分析",
  description: "产品经理竞品截图分析工具 - 现代化重构版",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN" className="dark">
      <body
        className={`${urbanist.variable} ${jetbrainsMono.variable} ${outfit.variable} antialiased`}
        style={{ fontFamily: "var(--font-urbanist)" }}
      >
        {children}
      </body>
    </html>
  );
}
