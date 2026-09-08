import { useState } from "react";
import "./Section06.css";
import section06Image from "../assets/geonexus-section06.png";

const features = [
  {
    icon: "◈",
    title: "SATELLITE",
    subtitle: "INTELLIGENCE",
  },
  {
    icon: "⌕",
    title: "SEMANTIC",
    subtitle: "SEARCH",
  },
  {
    icon: "▥",
    title: "CHANGE",
    subtitle: "DETECTION",
  },
  {
    icon: "◷",
    title: "MULTI-TEMPORAL",
    subtitle: "ANALYSIS",
  },
];

const information = {
  ABOUT: {
    title: "WHAT IS GEONEXUS?",
    text:
      "GeoNexus is a satellite intelligence platform designed to turn Earth observation data into meaningful and actionable insights.",
    points: [
      "Understand changes happening across the Earth.",
      "Search satellite imagery using natural language.",
      "Compare locations across different points in time.",
      "Transform visual changes into measurable intelligence.",
    ],
  },

  TECHNOLOGY: {
    title: "THE GEONEXUS TECHNOLOGY",
    text:
      "GeoNexus combines semantic retrieval and multi-temporal satellite analysis to discover, compare and understand changes across locations.",
    points: [
      "Semantic Retrieval",
      "Satellite Imagery Analysis",
      "Multi-Temporal Comparison",
      "Change Detection",
      "Geospatial Intelligence",
    ],
  },

  IMPACT: {
    title: "INTELLIGENCE THAT MATTERS.",
    text:
      "GeoNexus aims to make satellite intelligence easier to understand and useful for people, places and a more sustainable planet.",
    points: [
      "Urban growth monitoring",
      "Infrastructure change detection",
      "Vegetation and environmental observation",
      "Water and land-use change analysis",
      "Better understanding of long-term Earth changes",
    ],
  },

  CONTACT: {
    title: "TEAM GEONEXUS",
    text:
      "GeoNexus is a six-member student project developed at Invertis University.",
    points: [
      "Shauray",
      "Prakhar",
      "Vaishnavi",
      "Anchal",
      "Saumay",
      "Vivek",
    ],
    contact: true,
  },
};

function FeatureItem({ icon, title, subtitle }) {
  return (
    <div className="section06-feature">
      <div className="section06-feature-icon">
        {icon}
      </div>

      <div className="section06-feature-text">
        <span>{title}</span>
        <span>{subtitle}</span>
      </div>
    </div>
  );
}

function InformationPanel({ type, onClose }) {
  const content = information[type];

  return (
    <div
      className="section06-info-overlay"
      onClick={onClose}
    >
      <div
        className="section06-info-panel"
        onClick={(event) => event.stopPropagation()}
      >
        <button
          className="section06-info-close"
          onClick={onClose}
        >
          ×
        </button>

        <div className="section06-info-label">
          GEONEXUS / {type}
        </div>

        <div className="section06-info-line" />

        <h2>{content.title}</h2>

        <p className="section06-info-description">
          {content.text}
        </p>

        <div className="section06-info-heading">
          {type === "CONTACT" ? "TEAM MEMBERS" : "KEY INFORMATION"}
        </div>

        <div className="section06-info-points">
          {content.points.map((point, index) => (
            <div
              className="section06-info-point"
              key={point}
            >
              <span>
                {String(index + 1).padStart(2, "0")}
              </span>

              <p>{point}</p>
            </div>
          ))}
        </div>

        {content.contact && (
          <div className="section06-contact-details">

            <div>
              <span>UNIVERSITY</span>
              <strong>INVERTIS UNIVERSITY</strong>
            </div>

            <div>
              <span>EMAIL</span>
              <strong>anchalgpt@gmail.com</strong>
            </div>

            <div>
              <span>CONTACT</span>
              <strong>9997610348</strong>
              <strong>93350 33477</strong>
            </div>

          </div>
        )}

        <div className="section06-info-footer">
          <span>TEAM GEONEXUS</span>
          <span>SAME PLANET. BRIGHTER TOMORROWS.</span>
        </div>
      </div>
    </div>
  );
}

export default function Section06() {
  const [activeInfo, setActiveInfo] = useState(null);

  return (
    <section
      className="section06"
      style={{
        "--section06-bg": `url(${section06Image})`,
      }}
    >
      {/* Background */}
      <div className="section06-background" />
      <div className="section06-overlay" />
      <div className="section06-grid" />

      {/* =========================
          TOP HEADER
      ========================== */}
      <header className="section06-header">
        <div className="section06-brand">

          <div className="section06-logo">
            GEO<span>NEXUS</span>
          </div>

          <div className="section06-brand-divider" />

          <div className="section06-tagline">
            TURNING EARTH'S CHANGES
            <br />
            INTO INTELLIGENCE.
          </div>

        </div>

        <nav className="section06-nav">
          <span>FOR PEOPLE</span>
          <i>|</i>
          <span>FOR PLACES</span>
          <i>|</i>
          <span>FOR A BETTER PLANET</span>
        </nav>
      </header>

      {/* =========================
          MAIN CONTENT
      ========================== */}
      <div className="section06-content">

        <div className="section06-section-label">
          <span>06</span>
          <div />
          <strong>A CLEARER TOMORROW</strong>
        </div>

        <div className="section06-main">

          {/* LEFT CONTENT */}
          <div className="section06-copy">

            <h1>
              A BRIGHTER
              <br />
              TOMORROW
              <br />
              IS <em>A MORE INFORMED</em>
              <br />
              <em>TODAY.</em>
            </h1>

            <p className="section06-description">
              GeoNexus turns satellite observations into meaningful
              insights for people, places and a more sustainable planet.
            </p>

            <p className="section06-thanks">
              Thank you for being part of this journey.
            </p>

            <div className="section06-statement">
              <span />
              <strong>
                SAME PLANET. BRIGHTER TOMORROWS.
              </strong>
            </div>

          </div>

          {/* RIGHT HUD */}
          <div className="section06-hud">

            <div className="section06-hud-line" />

            <span>OBSERVE</span>
            <span>ANALYZE</span>
            <span>UNDERSTAND</span>
            <span>FOR A BETTER</span>
            <span>TOMORROW</span>

          </div>

        </div>

        {/* =========================
            FEATURE STRIP
        ========================== */}
        <div className="section06-features">

          {features.map((feature) => (
            <FeatureItem
              key={feature.title}
              icon={feature.icon}
              title={feature.title}
              subtitle={feature.subtitle}
            />
          ))}

        </div>

      </div>

      {/* =========================
          FOOTER
      ========================== */}
      <footer className="section06-footer">

        <div className="section06-footer-left">

          <div className="section06-footer-logo">
            GEO<span>NEXUS</span>
          </div>

          <span className="section06-copyright">
            © 2026 GeoNexus. All rights reserved.
          </span>

        </div>

        {/* CLICKABLE INFORMATION */}
        <div className="section06-footer-links">

          <span
            className="section06-footer-link"
            onClick={() => setActiveInfo("ABOUT")}
          >
            ABOUT
          </span>

          <i>|</i>

          <span
            className="section06-footer-link"
            onClick={() => setActiveInfo("TECHNOLOGY")}
          >
            TECHNOLOGY
          </span>

          <i>|</i>

          <span
            className="section06-footer-link"
            onClick={() => setActiveInfo("IMPACT")}
          >
            IMPACT
          </span>

          <i>|</i>

          <span
            className="section06-footer-link"
            onClick={() => setActiveInfo("CONTACT")}
          >
            CONTACT
          </span>

        </div>

        <div className="section06-footer-divider" />

        <div className="section06-footer-message">
          FOR A
          <br />
          BETTER
          <br />
          PLANET.
        </div>

      </footer>

      {/* =========================
          INFORMATION PANEL
      ========================== */}
      {activeInfo && (
        <InformationPanel
          type={activeInfo}
          onClose={() => setActiveInfo(null)}
        />
      )}

    </section>
  );
}