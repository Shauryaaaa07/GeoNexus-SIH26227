import "./GeoNexusIntelligenceSection.css";

const processSteps = [
  {
    number: "01",
    title: "RAW IMAGERY",
    subtitle: "SATELLITE DATA",
    description:
      "High-resolution satellite imagery captures the Earth's surface.",
    type: "image",
  },
  {
    number: "02",
    title: "ANALYZE",
    subtitle: "AI ANALYSIS",
    description:
      "AI extracts meaningful layers such as buildings, roads, vegetation and water.",
    type: "layers",
  },
  {
    number: "03",
    title: "COMPARE",
    subtitle: "MULTI-TEMPORAL",
    description:
      "Images from different points in time are aligned and compared.",
    type: "compare",
  },
  {
    number: "04",
    title: "DETECT CHANGE",
    subtitle: "CHANGE DETECTION",
    description:
      "Significant changes are identified and measured automatically.",
    type: "change",
  },
  {
    number: "05",
    title: "INTELLIGENCE",
    subtitle: "REAL IMPACT",
    description:
      "Complex satellite observations become clear, measurable insights.",
    type: "intelligence",
  },
];

function ProcessVisual({ type }) {
  if (type === "image") {
    return (
      <div className="process-visual raw-visual">
        <div className="satellite-land">
          <span />
          <span />
          <span />
          <span />
        </div>

        <div className="visual-scan-line" />

        <div className="visual-corner top-left" />
        <div className="visual-corner top-right" />
        <div className="visual-corner bottom-left" />
        <div className="visual-corner bottom-right" />

        <div className="visual-label">RAW DATA</div>
      </div>
    );
  }

  if (type === "layers") {
    return (
      <div className="process-visual layers-visual">
        <div className="layer layer-buildings" />
        <div className="layer layer-roads" />
        <div className="layer layer-vegetation" />
        <div className="layer layer-water" />

        <div className="layer-labels">
          <span>BUILDINGS</span>
          <span>ROADS</span>
          <span>VEGETATION</span>
          <span>WATER</span>
        </div>
      </div>
    );
  }

  if (type === "compare") {
    return (
      <div className="process-visual compare-visual">
        <div className="compare-image compare-before">
          <span>2023</span>
        </div>

        <div className="compare-divider">
          <i />
        </div>

        <div className="compare-image compare-after">
          <span>2026</span>
        </div>

        <div className="compare-center">
          <span>↔</span>
        </div>
      </div>
    );
  }

  if (type === "change") {
    return (
      <div className="process-visual change-visual">
        <div className="change-map">
          <span className="change-point point-one" />
          <span className="change-point point-two" />
          <span className="change-point point-three" />
          <span className="change-point point-four" />
        </div>

        <div className="change-reading">
          <strong>+38%</strong>
          <small>CHANGE DETECTED</small>
        </div>
      </div>
    );
  }

  return (
    <div className="process-visual intelligence-visual">
      <div className="intelligence-chart">
        <span />
        <span />
        <span />
        <span />
        <span />
      </div>

      <div className="intelligence-data">
        <div>
          <small>BUILT-UP</small>
          <strong>+38%</strong>
        </div>

        <div>
          <small>VEGETATION</small>
          <strong>-16%</strong>
        </div>
      </div>
    </div>
  );
}

function ProcessCard({ step, index }) {
  return (
    <div className={`process-card-wrapper card-position-${index + 1}`}>
      <article className="process-card">

        <div className="card-depth" />

        <div className="process-card-top">
          <span className="process-number">
            {step.number}
          </span>

          <span className="process-status">
            ANALYSIS NODE
          </span>
        </div>

        <ProcessVisual type={step.type} />

        <div className="process-card-content">

          <h3>{step.title}</h3>

          <div className="process-card-subtitle">
            {step.subtitle}
          </div>

          <p>
            {step.description}
          </p>

        </div>

        <div className="process-card-bottom">

          <span className="bottom-indicator" />

          <span>
            GEONEXUS / {step.number}
          </span>

        </div>

      </article>
    </div>
  );
}

export default function Process() {
  return (
    <section className="intelligence-process-section">

      {/* =========================
          BACKGROUND
      ========================= */}

      <div
        className="process-background"
        aria-hidden="true"
      >
        <div className="process-grid" />

        <div className="process-wave wave-one" />
        <div className="process-wave wave-two" />
        <div className="process-wave wave-three" />
        <div className="process-wave wave-four" />

        <div className="process-glow glow-one" />
        <div className="process-glow glow-two" />

        <div className="process-particles">
          <span />
          <span />
          <span />
          <span />
          <span />
          <span />
          <span />
          <span />
        </div>
      </div>


      {/* =========================
          MAIN CONTENT
      ========================= */}

      <div className="process-container">

        {/* HEADER */}

        <header className="process-header">

          <div className="process-heading">

            <span className="process-kicker">
              THE GEONEXUS METHOD
            </span>

            <h2>
              FROM RAW IMAGERY
              <br />
              <em>TO INTELLIGENCE.</em>
            </h2>

          </div>


          <div className="process-intro">

            <span className="process-line" />

            <p>
              One image can contain thousands of signals.
              GeoNexus transforms satellite observations
              into meaningful intelligence through a
              structured process of analysis, comparison
              and change detection.
            </p>

          </div>

        </header>


        {/* PROCESS CARDS */}

        <div className="process-flow">

          {processSteps.map((step, index) => (

            <div
              className="process-flow-item"
              key={step.number}
            >

              <ProcessCard
                step={step}
                index={index}
              />

              {index < processSteps.length - 1 && (

                <div
                  className="process-connector"
                  aria-hidden="true"
                >
                  <span />
                  <i>→</i>
                </div>

              )}

            </div>

          ))}

        </div>


        {/* FOOTER */}

        <footer className="process-footer">

          <div className="process-footer-title">

            <span>OUTPUT / 05</span>

            <h3>
              A CLEARER <em>TOMORROW.</em>
            </h3>

          </div>


          <p>
            Better observation leads to better understanding —
            helping us monitor our planet, measure change and
            make more informed decisions.
          </p>


          <div className="process-footer-stats">

            <div>
              <strong>01</strong>
              <span>OBSERVE</span>
            </div>

            <div>
              <strong>02</strong>
              <span>COMPARE</span>
            </div>

            <div>
              <strong>03</strong>
              <span>DETECT</span>
            </div>

            <div>
              <strong>04</strong>
              <span>UNDERSTAND</span>
            </div>

          </div>

        </footer>

      </div>

    </section>
  );
}