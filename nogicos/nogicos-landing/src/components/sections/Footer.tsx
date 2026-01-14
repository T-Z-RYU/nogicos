import Link from "next/link";
import { footerContent, siteConfig } from "@/data/content";

export function Footer() {
  const { links } = footerContent;

  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-left">
          <Link href="/" className="nav-logo">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <rect
                x="3"
                y="3"
                width="18"
                height="18"
                rx="4"
                stroke="currentColor"
                strokeWidth="1.5"
              />
              <path
                d="M8 12h8M12 8v8"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
              />
            </svg>
            <span>{siteConfig.name}</span>
          </Link>
          <div className="footer-links">
            {links.social.map((link) => (
              <Link key={link.label} href={link.href} className="footer-link">
                {link.label}
              </Link>
            ))}
            {links.legal.map((link) => (
              <Link key={link.label} href={link.href} className="footer-link">
                {link.label}
              </Link>
            ))}
          </div>
        </div>
        <p className="footer-copyright">
          © {new Date().getFullYear()} {siteConfig.name}. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
