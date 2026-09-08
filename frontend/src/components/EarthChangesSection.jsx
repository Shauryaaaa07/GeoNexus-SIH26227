import { API_BASE_URL } from "../config";
import { useState, useEffect } from "react";
import "./EarthChangesSection.css";

import Delhi2021Satellite from "../assets/Delhi2021Satellite.png";
import Delhi2023Satellite from "../assets/Delhi2023Satellite.png";
import Delhi2026Satellite from "../assets/Delhi2026Satellite.png";

const comparisons = [
  {
    id: "2021-2023",
    from: "2021",
    to: "2023",
    imageFrom: Delhi2021Satellite,
    imageTo: Delhi2023Satellite,

    summary:
      "The clearest visible transition is around the eastern transport corridor, while the central urban fabric and major green spaces remain comparatively stable.",

    metrics: [
      {
        label: "Agricultural Change",
        score: "302.83 km²",
        level: "PRIMARY",
        detail: "4,746 polygons detected",
      },
      {
        label: "Vegetation Change",
        score: "61.29 km²",
        level: "SIGNIFICANT",
        detail: "2,065 polygons detected",
      },
      {
        label: "Built-up Area",
        score: "8.59 km²",
        level: "URBAN",
        detail: "885 polygons detected",
      },
      {
        label: "Water Body Change",
        score: "5.56 km²",
        level: "HYDROLOGICAL",
        detail: "410 polygons detected",
      },
      {
        label: "New Infrastructure",
        score: "1.93 km²",
        level: "CORRIDOR",
        detail: "122 polygons detected",
      },
    ],
  },

  {
    id: "2021-2026",
    from: "2021",
    to: "2026",
    imageFrom: Delhi2021Satellite,
    imageTo: Delhi2026Satellite,

    summary:
      "Across the longer interval, the central urban structure remains recognizable, while infrastructure and the eastern river corridor show the most noticeable spatial differences.",

    metrics: [
      {
        label: "Infrastructure",
        score: "4 / 5",
        level: "HIGH",
        detail: "Persistent transformation",
      },
      {
        label: "Road Pattern",
        score: "4 / 5",
        level: "HIGH",
        detail: "Corridor variation visible",
      },
      {
        label: "Built-up Area",
        score: "3 / 5",
        level: "MODERATE",
        detail: "Localized development",
      },
      {
        label: "Vegetation",
        score: "1 / 5",
        level: "LOW",
        detail: "Major green areas persist",
      },
      {
        label: "Water / Floodplain",
        score: "3 / 5",
        level: "VISIBLE",
        detail: "River-side landscape differs",
      },
    ],
  },
];

function ContourField() {
  const lines = [
    "M0 80 C100 20 180 150 300 80 S500 20 700 90",
    "M0 110 C120 50 190 180 320 105 S520 45 700 120",
    "M0 145 C100 80 210 210 350 135 S540 80 700 150",
    "M0 180 C130 115 230 240 370 165 S550 110 700 180",
    "M0 215 C110 155 240 270 390 195 S570 145 700 215",
    "M0 250 C120 190 250 300 410 225 S580 180 700 250",
    "M0 285 C130 225 270 330 420 255 S590 215 700 285",
    "M0 320 C110 260 280 360 440 290 S600 245 700 320",
  ];

  return (
    <svg
      className="ecs-contours"
      viewBox="0 0 700 360"
      preserveAspectRatio="none"
      aria-hidden="true"
    >
      {lines.map((path, index) => (
        <path
          key={index}
          d={path}
          className="ecs-contour-line"
          style={{ animationDelay: `${index * -0.8}s` }}
        />
      ))}
    </svg>
  );
}

function MetricRow({ metric }) {
  return (
    <div className="ecs-metric">
      <div className="ecs-metric-top">
        <span>{metric.label}</span>
        <strong>{metric.score}</strong>
      </div>

      <div className="ecs-metric-bar">
        <span
          style={{
            width: `${Number(metric.score.split("/")[0]) * 20}%`,
          }}
        />
      </div>

      <div className="ecs-metric-bottom">
        <span>{metric.level}</span>
        <small>{metric.detail}</small>
      </div>
    </div>
  );
}

function ComparisonCard({ comparison }) {
  return (
    <article className="ecs-comparison-card">
      <div className="ecs-card-heading">
        <div>
          <span className="ecs-location">DELHI / INDIA</span>
          <h3>
            {comparison.from}
            <span> → </span>
            {comparison.to}
          </h3>
        </div>

        <span className="ecs-derived">IMAGE-DERIVED</span>
      </div>

      <div className="ecs-image-comparison">
        <div className="ecs-image-box">
          <img
            src={comparison.imageFrom}
            alt={`Delhi satellite observation ${comparison.from}`}
          />

          <div className="ecs-image-label">
            <span>BASELINE</span>
            <strong>{comparison.from}</strong>
          </div>
        </div>

        <div className="ecs-change-divider">
          <span>CHANGE</span>
          <i />
          <b>→</b>
        </div>

        <div className="ecs-image-box">
          <img
            src={comparison.imageTo}
            alt={`Delhi satellite observation ${comparison.to}`}
          />

          <div className="ecs-image-label">
            <span>OBSERVATION</span>
            <strong>{comparison.to}</strong>
          </div>
        </div>
      </div>

      <p className="ecs-summary">{comparison.summary}</p>

      <div className="ecs-metrics">
        {comparison.metrics.map((metric) => (
          <MetricRow key={metric.label} metric={metric} />
        ))}
      </div>
    </article>
  );
}

export default function EarthChangesSection() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/dashboard/stats`)
      .then((res) => res.json())
      .then((data) => setStats(data))
      .catch((err) => console.log("Stats fetch error:", err));
  }, []);
  const [activeComparison, setActiveComparison] = useState(0);

  const handlePointerMove = (event) => {
    const rect = event.currentTarget.getBoundingClientRect();

    const x = ((event.clientX - rect.left) / rect.width) * 100;
    const y = ((event.clientY - rect.top) / rect.height) * 100;

    event.currentTarget.style.setProperty("--mouse-x", `${x}%`);
    event.currentTarget.style.setProperty("--mouse-y", `${y}%`);
  };

  const active = comparisons[activeComparison];

  return (
    <section
      className="ecs-section"
      onPointerMove={handlePointerMove}
      id="earth-changes"
    >
      <div className="ecs-atmosphere" />
      <div className="ecs-light-orb" />

      <ContourField />

      <div className="ecs-content">
        <header className="ecs-header">
          <div className="ecs-eyebrow">
            <span className="ecs-status-dot" />
            02 — EARTH OBSERVATION
          </div>

          <div className="ecs-heading-row">
            <div>
              <h2>
                THE EARTH IS
                <br />
                <span>ALWAYS CHANGING.</span>
              </h2>
            </div>

            <div className="ecs-heading-copy">
              <span>REAL IMAGE · REAL LOCATION</span>
              <p>
                See how Delhi's landscape evolves through
                multi-temporal satellite observations.
              </p>
            </div>
          </div>
        </header>

        <div className="ecs-main">
          <div className="ecs-left">
            <div className="ecs-period-switcher">
              {comparisons.map((comparison, index) => (
                <button
                  key={comparison.id}
                  className={
                    activeComparison === index ? "active" : ""
                  }
                  onClick={() => setActiveComparison(index)}
                >
                  <span>DELHI</span>
                  {comparison.from} → {comparison.to}
                </button>
              ))}
            </div>

            <ComparisonCard comparison={active} />
          </div>

          <aside className="ecs-right">
            <div className="ecs-right-label">WHAT THE IMAGES REVEAL</div>

            <div className="ecs-right-line" />

            <div className="ecs-right-number">
              <strong>5</strong>
              <span>
                visual
                <br />
                indicators
              </span>
            </div>

            <p className="ecs-right-text">
              Each comparison evaluates five visible landscape
              indicators against the same Delhi baseline.
            </p>

            <div className="ecs-analysis-list">
              <div>
                <span>01</span>
                <p>Infrastructure transformation</p>
              </div>

              <div>
                <span>02</span>
                <p>Road and transport pattern</p>
              </div>

              <div>
                <span>03</span>
                <p>Urban / built-up structure</p>
              </div>

              <div>
                <span>04</span>
                <p>Vegetation stability</p>
              </div>

              <div>
                <span>05</span>
                <p>Water & floodplain variation</p>
              </div>
            </div>

            <div className="ecs-data-note">
              <span>DATA NOTE</span>
              <p>
                Scores represent visible change intensity from the
                supplied imagery. They are not area percentages and
                will be replaced by quantitative backend detection
                when available.
              </p>
            </div>
          </aside>
        </div>

        <footer className="ecs-footer">
          <div>
            <span>OBSERVATION MODE</span>
            <strong>MULTI-TEMPORAL</strong>
          </div>

          <div>
            <span>LOCATION</span>
            <strong>DELHI, INDIA</strong>
          </div>

          <div>
            <span>BASELINE</span>
            <strong>2021</strong>
          </div>

          <div className="ecs-footer-indicator">
            <span />
            VISUAL CHANGE ASSESSMENT
          </div>
        </footer>
      </div>
    </section>
  );
}