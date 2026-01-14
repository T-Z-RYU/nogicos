import { ctaContent } from "@/data/content";
import { FadeIn } from "@/components/motion";
import { WaitlistForm } from "@/components/ui/WaitlistForm";

export function FinalCTA() {
  const { eyebrow, title, description, benefits, waitlistCount } = ctaContent;

  return (
    <section id="waitlist" className="final-cta-section">
      <FadeIn className="cta-content" amount={0.5} duration={0.8}>
        {/* 稀缺性 */}
        <div className="cta-scarcity">
          <span className="scarcity-dot" />
          <span>
            Only <strong>{waitlistCount.count} spots</strong> {waitlistCount.suffix}
          </span>
        </div>

        <h2>
          {title.split(" ").slice(0, 2).join(" ")}
          <br />
          {title.split(" ").slice(2).join(" ")}
        </h2>
        <p className="cta-description">{description}</p>

        {/* Table单 */}
        <WaitlistForm />

        {/* 权益 */}
        <div className="cta-benefits">
          {benefits.map((benefit, i) => (
            <div key={i} className="benefit">
              <span>{benefit.icon}</span>
              <span>{benefit.text}</span>
            </div>
          ))}
        </div>
      </FadeIn>
    </section>
  );
}
