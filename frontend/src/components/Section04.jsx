import Map from "../Map";
import "./Section04.css";

import urbanGrowth from "../assets/01_urban_growth.png";
import infrastructure from "../assets/02_infrastructure.png";
import vegetation from "../assets/03_vegetation.png";
import water from "../assets/04_water.png";
import landUse from "../assets/05_land_use_environment.png";
import delhiNcrMap from "../assets/06_delhi_ncr_base_map.png";

const analysisData = [
  {
    title: "URBAN GROWTH",
    description: "Built-up areas, settlements and development patterns.",
    image: urbanGrowth,
  },
  {
    title: "INFRASTRUCTURE",
    description: "Road networks, transport corridors and major structures.",
    image: infrastructure,
  },
  {
    title: "VEGETATION",
    description: "Green cover, forests, parks and environmental patterns.",
    image: vegetation,
  },
  {
    title: "WATER",
    description: "Rivers, lakes, wetlands and surface-water patterns.",
    image: water,
  },
  {
    title: "LAND USE",
    description: "Agricultural, urban, industrial and open-land patterns.",
    image: landUse,
  },
];

const observations = [
  { title: "URBAN STRUCTURE", type: "urban", position: { top: "32%", left: "29%" } },
  { title: "VEGETATION", type: "vegetation", position: { top: "63%", left: "24%" } },
  { title: "WATER BODY", type: "water", position: { top: "34%", left: "73%" } },
  { title: "INFRASTRUCTURE", type: "infrastructure", position: { top: "68%", left: "63%" } },
];

function ObservationMarker({ title, type, position }) {
  return (
    <div
      className={`section04-observation ${type}`}
      style={{ top: position.top, left: position.left }}
    >
      <span className="section04-observation-dot" />
      <span className="section04-observation-line" />
      <span className="section04-observation-label">{title}</span>
    </div>
  );
}

function AnalysisCard({ title, description, image }) {
  return (
    <article className="section04-analysis-card">
      <div className="section04-card-image">
        <img src={image} alt={title} />
        <div className="section04-card-image-shade" />
        <span className="section04-card-index">OBS / {title}</span>
      </div>

      <div className="section04-card-content">
        <div className="section04-card-heading">
          <span className="section04-card-title">{title}</span>
          <span className="section04-card-arrow">↗</span>
        </div>
        <p>{description}</p>
      </div>
    </article>
  );
}

export default function Section04() {
  return (
    <section className="section04" id="analytics">
      {/* REAL DELHI NCR IMAGE — FULL PAGE BACKGROUND */}
      <div className="section04-atmosphere" aria-hidden="true">
        <img src={delhiNcrMap} alt="" />
        <div className="section04-atmosphere-shade" />
        <div className="section04-atmosphere-vignette" />
      </div>

      <header className="section04-header">
        <div className="section04-number">
          <span />
          <strong>04</strong>
        </div>

        <div className="section04-label">WHAT CAN GEONEXUS SEE?</div>

        <div className="section04-live-status">
          <span />
          REAL SATELLITE OBSERVATION
        </div>
      </header>

      <div className="section04-intro">
        <div>
          <span className="section04-kicker">EARTH OBSERVATION</span>
          <h2>
            READING THE EARTH.
            <br />
            <em>IN LAYERS.</em>
          </h2>
        </div>

        <p>
          GeoNexus observes the patterns beneath the surface — from urban
          growth and infrastructure to vegetation, water and land use.
        </p>
      </div>

      {/* INTERACTIVE LEAFLET MAP CONTAINER */}
      <div className="section04-map-container" style={{ minHeight: "650px", position: "relative", zIndex: 10 }}>
        <Map />
      </div>

      {/* REAL IMAGE ANALYSIS CARDS */}
      <div className="section04-analysis">
        {analysisData.map((item) => (
          <AnalysisCard key={item.title} {...item} />
        ))}
      </div>

      <footer className="section04-footer">
        <div className="section04-footer-brand">
          <span>GEONEXUS</span>
          <i />
          <small>EARTH OBSERVATION / 04</small>
        </div>

        <p>Observe Earth. Understand change. Empower tomorrow.</p>

        <div className="section04-footer-flow">
          <span>OBSERVE</span>
          <i>→</i>
          <span>ANALYZE</span>
          <i>→</i>
          <strong>UNDERSTAND</strong>
        </div>
      </footer>
    </section>
  );
}
