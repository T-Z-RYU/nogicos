import { solutionContent } from "@/data/content";
import { FadeIn, StaggerList } from "@/components/motion";

export function Solution() {
  const { eyebrow, title, titleHighlight, description, capabilities, comparison } =
    solutionContent;

  return (
    <section id="solution" className="solution-section">
      <FadeIn className="section-header" amount={0.5}>
        <p className="section-eyebrow">{eyebrow}</p>
        <h2>
          {title}
          <br />
          <span className="highlight">{titleHighlight}</span>
        </h2>
        <p className="section-description">{description}</p>
      </FadeIn>

      <StaggerList className="capabilities-grid" staggerDelay={0.1}>
        {capabilities.map((cap, i) => (
          <div key={i} className="capability-card">
            <span className="capability-icon">{cap.icon}</span>
            <h3>{cap.title}</h3>
            <p>{cap.description}</p>
            <div className="capability-example">
              <code>{cap.example}</code>
            </div>
          </div>
        ))}
      </StaggerList>

      <FadeIn delay={0.2} duration={0.6} className="comparison-table">
        <h3>{comparison.title}</h3>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                {comparison.headers.map((header, i) => (
                  <th key={i} className={i === 4 ? "highlight-col" : ""}>
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {comparison.rows.map((row, rowIndex) => (
                <tr key={rowIndex}>
                  {row.map((cell, cellIndex) => {
                    // ParseUnitgrid: "yes", "no", "partial:Text", "yes:Text"
                    const [status, label] = cell.includes(":")
                      ? cell.split(":")
                      : [cell, null];

                    const cellClass =
                      status === "yes"
                        ? "yes"
                        : status === "no"
                          ? "no"
                          : status === "partial"
                            ? "partial"
                            : "";

                    const displayText =
                      status === "yes"
                        ? label || "✓"
                        : status === "no"
                          ? label || "✕"
                          : label || cell;

                    return (
                      <td key={cellIndex} className={cellClass}>
                        {displayText}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </FadeIn>
    </section>
  );
}
