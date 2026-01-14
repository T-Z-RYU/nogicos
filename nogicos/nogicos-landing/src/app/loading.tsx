// Streaming Loading Skeleton
// inpageInnercontentLoadtimeDisplay，mentionupgradeperceptionPerformance

export default function Loading() {
  return (
    <div className="loading-skeleton">
      {/* Navigation skeleton */}
      <nav className="skeleton-nav">
        <div className="skeleton-logo" />
        <div className="skeleton-links">
          <div className="skeleton-link" />
          <div className="skeleton-link" />
          <div className="skeleton-link" />
        </div>
        <div className="skeleton-button" />
      </nav>

      {/* Hero skeleton */}
      <section className="skeleton-hero">
        <div className="skeleton-content">
          <div className="skeleton-eyebrow" />
          <div className="skeleton-title" />
          <div className="skeleton-subtitle" />
          <div className="skeleton-cta" />
        </div>
        <div className="skeleton-demo" />
      </section>

      <style>{`
        .loading-skeleton {
          min-height: 100vh;
          background: var(--bg-primary, #0a0a0a);
          padding: 0 48px;
        }
        
        .skeleton-nav {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 24px 0;
          max-width: 1400px;
          margin: 0 auto;
        }
        
        .skeleton-logo {
          width: 120px;
          height: 24px;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 4px;
          animation: pulse 1.5s ease-in-out infinite;
        }
        
        .skeleton-links {
          display: flex;
          gap: 32px;
        }
        
        .skeleton-link {
          width: 60px;
          height: 16px;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 4px;
          animation: pulse 1.5s ease-in-out infinite;
        }
        
        .skeleton-button {
          width: 140px;
          height: 40px;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 8px;
          animation: pulse 1.5s ease-in-out infinite;
        }
        
        .skeleton-hero {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 80px;
          align-items: center;
          min-height: calc(100vh - 100px);
          max-width: 1600px;
          margin: 0 auto;
        }
        
        .skeleton-content {
          display: flex;
          flex-direction: column;
          gap: 24px;
        }
        
        .skeleton-eyebrow {
          width: 200px;
          height: 16px;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 4px;
          animation: pulse 1.5s ease-in-out infinite;
        }
        
        .skeleton-title {
          width: 100%;
          height: 80px;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 8px;
          animation: pulse 1.5s ease-in-out infinite;
        }
        
        .skeleton-subtitle {
          width: 80%;
          height: 48px;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 4px;
          animation: pulse 1.5s ease-in-out infinite;
        }
        
        .skeleton-cta {
          width: 200px;
          height: 48px;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 8px;
          animation: pulse 1.5s ease-in-out infinite;
        }
        
        .skeleton-demo {
          width: 100%;
          height: 400px;
          background: rgba(255, 255, 255, 0.03);
          border-radius: 16px;
          border: 1px solid rgba(255, 255, 255, 0.06);
          animation: pulse 1.5s ease-in-out infinite;
        }
        
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
        
        @media (max-width: 768px) {
          .loading-skeleton {
            padding: 0 24px;
          }
          .skeleton-hero {
            grid-template-columns: 1fr;
            gap: 48px;
          }
          .skeleton-links {
            display: none;
          }
        }
      `}</style>
    </div>
  );
}






