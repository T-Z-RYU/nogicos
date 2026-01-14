import { socialProofContent } from "@/data/content";
import { FadeIn, StaggerList } from "@/components/motion";

export function SocialProof() {
  const { stats, testimonials, privacy } = socialProofContent;

  return (
    <section className="social-proof-section">
      {/* Stats */}
      <StaggerList className="stats-bar" staggerDelay={0.1}>
        {stats.map((stat, i) => (
          <div key={i} className="stat-item">
            <span className="stat-value">{stat.value}</span>
            <span className="stat-label">{stat.label}</span>
          </div>
        ))}
      </StaggerList>

      {/* Testimonials */}
      <div className="testimonials-container">
        <FadeIn className="section-header" amount={0.5}>
          <p className="section-eyebrow">{testimonials.eyebrow}</p>
          <h2>{testimonials.title}</h2>
        </FadeIn>

        <StaggerList className="testimonials-grid" staggerDelay={0.1} initialDelay={0.2}>
          {testimonials.items.map((t, i) => (
            <div key={i} className="testimonial-card">
              <p className="testimonial-quote">&ldquo;{t.quote}&rdquo;</p>
              <div className="testimonial-author">
                <div className="author-info">
                  <p className="author-name">{t.name}</p>
                  <p className="author-role">
                    {t.role} · {t.company}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </StaggerList>
      </div>

      {/* Privacy */}
      <FadeIn delay={0.2} duration={0.6} amount={0.5} className="privacy-section">
        <div className="privacy-badge">
          <span className="privacy-icon">{privacy.icon}</span>
          <div>
            <p className="privacy-title">{privacy.title}</p>
            <p className="privacy-desc">{privacy.description}</p>
          </div>
        </div>
      </FadeIn>
    </section>
  );
}
