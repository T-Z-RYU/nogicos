import { problemContent } from "@/data/content";
import { FadeIn, StaggerList } from "@/components/motion";

export function Problem() {
  const { eyebrow, title, titleHighlight, titleSuffix, description, problems, quote } =
    problemContent;

  return (
    <section id="problem" className="problem-section">
      <FadeIn className="section-header" amount={0.5}>
        <p className="section-eyebrow">{eyebrow}</p>
        <h2>
          {title} <span className="highlight">{titleHighlight}</span>
          <br />
          {titleSuffix}
        </h2>
        <p className="section-description">{description}</p>
      </FadeIn>

      <StaggerList className="problem-flow" staggerDelay={0.1}>
        {problems.map((problem, i) => (
          <div key={i} className="problem-item">
            <div className="problem-step">
              <span className="step-number">{i + 1}</span>
              <p className="step-before">{problem.before}</p>
            </div>
            <div className="problem-pain">
              <p>{problem.pain}</p>
            </div>
            <div className="problem-result">
              <p>{problem.result}</p>
            </div>
          </div>
        ))}
      </StaggerList>

      <FadeIn delay={0.3} duration={0.6} amount={0.5} className="problem-quote">
        <blockquote>{quote.text}</blockquote>
        <cite>{quote.cite}</cite>
      </FadeIn>
    </section>
  );
}
