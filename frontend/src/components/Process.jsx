import "./GeoNexusIntelligenceSection.css";

import rawImagery from "../assets/01_raw_imagery.png";
import analyzeNdvi from "../assets/02_analyze_ndvi.png";
import compare2023_2026 from "../assets/03_compare_2023_2026.png";
import detectChange from "../assets/04_detect_change.png";
import intelligence from "../assets/05_intelligence.png";

const processSteps = [
  { number: "01", title: "RAW IMAGERY", subtitle: "SATELLITE DATA", description: "Real satellite imagery provides the starting observation.", image: rawImagery },
  { number: "02", title: "ANALYZE", subtitle: "AI ANALYSIS", description: "Spectral and spatial signals are transformed into meaningful information.", image: analyzeNdvi },
  { number: "03", title: "COMPARE", subtitle: "MULTI-TEMPORAL", description: "Observations from different dates are aligned to reveal temporal differences.", image: compare2023_2026 },
  { number: "04", title: "DETECT CHANGE", subtitle: "CHANGE DETECTION", description: "Potential changes are isolated and organized by observable category.", image: detectChange },
  { number: "05", title: "INTELLIGENCE", subtitle: "ACTIONABLE INSIGHT", description: "Complex observations become clear information for better decisions.", image: intelligence },
];

function ProcessCard({ step, index }) {
  const move = (e) => {
    const card = e.currentTarget;
    const r = card.getBoundingClientRect();
    const x = e.clientX - r.left;
    const y = e.clientY - r.top;
    card.style.setProperty("--rx", `${((y / r.height) - 0.5) * -7}deg`);
    card.style.setProperty("--ry", `${((x / r.width) - 0.5) * 7}deg`);
    card.style.setProperty("--lift", "-7px");
  };

  const reset = (e) => {
    e.currentTarget.style.setProperty("--rx", "0deg");
    e.currentTarget.style.setProperty("--ry", "0deg");
    e.currentTarget.style.setProperty("--lift", "0px");
  };

  return (
    <div className={`process-card-wrapper card-position-${index + 1}`}>
      <article className="process-card" onPointerMove={move} onPointerLeave={reset}>
        <div className="card-depth card-depth-back" />
        <div className="card-depth card-depth-bottom" />
        <div className="card-depth card-depth-right" />

        <div className="process-card-surface">
          <div className="process-card-top">
            <span className="process-number">{step.number}</span>
            <span className="process-status">ANALYSIS NODE</span>
          </div>

          <div className="process-visual">
            <img src={step.image} alt={`${step.title} satellite analysis`} />
            <div className="process-visual-overlay" />
            <div className="process-visual-scan" />
            <span className="process-visual-label">{step.subtitle}</span>
            <span className="process-visual-corner top-left" />
            <span className="process-visual-corner top-right" />
            <span className="process-visual-corner bottom-left" />
            <span className="process-visual-corner bottom-right" />
          </div>

          <div className="process-card-content">
            <h3>{step.title}</h3>
            <div className="process-card-subtitle">{step.subtitle}</div>
            <p>{step.description}</p>
          </div>

          <div className="process-card-bottom">
            <span className="bottom-indicator" />
            <span>GEONEXUS / {step.number}</span>
          </div>
        </div>
      </article>
    </div>
  );
}

export default function Process() {
  return (
    <section className="intelligence-process-section">
      <div className="process-background" aria-hidden="true">
        <div className="process-grid" />
        <div className="process-wave wave-one" />
        <div className="process-wave wave-two" />
        <div className="process-wave wave-three" />
        <div className="process-wave wave-four" />
        <div className="process-glow glow-one" />
        <div className="process-glow glow-two" />
        <div className="process-particles">
          <span /><span /><span /><span /><span /><span /><span /><span />
        </div>
      </div>

      <div className="process-container">
        <header className="process-header">
          <div className="process-heading">
            <span className="process-kicker">THE GEONEXUS METHOD</span>
            <h2>FROM RAW IMAGERY<br /><em>TO INTELLIGENCE.</em></h2>
          </div>

          <div className="process-intro">
            <span className="process-line" />
            <p>
              One image can contain thousands of signals. GeoNexus transforms
              satellite observations into meaningful intelligence through
              analysis, comparison and change detection.
            </p>
          </div>
        </header>

        <div className="process-flow">
          {processSteps.map((step, index) => (
            <div className="process-flow-item" key={step.number}>
              <ProcessCard step={step} index={index} />
              {index < processSteps.length - 1 && (
                <div className="process-connector" aria-hidden="true">
                  <span /><i>→</i>
                </div>
              )}
            </div>
          ))}
        </div>

        <footer className="process-footer">
          <div className="process-footer-title">
            <span>OUTPUT / 05</span>
            <h3>A CLEARER <em>TOMORROW.</em></h3>
          </div>
          <p>
            Better observation leads to better understanding — helping us
            monitor our planet, measure change and make more informed decisions.
          </p>
          <div className="process-footer-stats">
            <div><strong>01</strong><span>OBSERVE</span></div>
            <div><strong>02</strong><span>COMPARE</span></div>
            <div><strong>03</strong><span>DETECT</span></div>
            <div><strong>04</strong><span>UNDERSTAND</span></div>
          </div>
        </footer>
      </div>
    </section>
  );
}
