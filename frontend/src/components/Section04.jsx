import "./Section04.css";
import backgroundImage from "../assets/geonexus-background.png";

const analysisData = [
  {
    title: "URBAN GROWTH",
    value: "+32%",
    description: "Increase in built-up area",
    type: "urban",
  },
  {
    title: "INFRASTRUCTURE",
    value: "+18%",
    description: "Expansion in road network",
    type: "infrastructure",
  },
  {
    title: "VEGETATION",
    value: "-14%",
    description: "Decrease in vegetation cover",
    type: "vegetation",
  },
  {
    title: "WATER",
    value: "+06%",
    description: "Change in water exposure",
    type: "water",
  },
  {
    title: "ENVIRONMENT",
    value: "DETECTED",
    description: "Flooding, coastline & land-cover changes",
    type: "environment",
  },
];

const detections = [
  {
    title: "BUILDING DETECTED",
    value: "+2.4 km²",
    type: "building",
  },
  {
    title: "ROAD EXPANSION",
    value: "+12.6 km",
    type: "road",
  },
  {
    title: "VEGETATION CHANGE",
    value: "-3.1 km²",
    type: "vegetation",
  },
  {
    title: "WATER LEVEL VARIATION",
    value: "+1.8 km²",
    type: "water",
  },
];

function DetectionMarker({ title, value, type }) {
  return (
    <div className={`section04-detection ${type}`}>
      <span className="section04-detection-dot"></span>

      <div className="section04-detection-line"></div>

      <div className="section04-detection-box">
        <strong>{title}</strong>
        <span>{value}</span>
      </div>
    </div>
  );
}

function AnalysisCard({ title, value, description, type }) {
  return (
    <article className={`section04-analysis-card ${type}`}>
      <div className="section04-card-image"></div>

      <div className="section04-card-content">
        <span className="section04-card-title">{title}</span>

        <strong className="section04-card-value">
          {value}
        </strong>

        <p>{description}</p>
      </div>

      <button className="section04-card-arrow" aria-label={`Explore ${title}`}>
        →
      </button>

      <div className="section04-card-graph">
        <span></span>
        <span></span>
        <span></span>
        <span></span>
        <span></span>
        <span></span>
      </div>
    </article>
  );
}

export default function Section04() {
  return (
    <section className="section04">

      {/* HEADER */}
      <div className="section04-header">

        <div className="section04-number">
          <span></span>
          04
        </div>

        <p className="section04-label">
          WHAT CAN GEONEXUS SEE?
        </p>

        <div className="section04-live-status">
          <span></span>
          LIVE SATELLITE VIEW
        </div>

      </div>


      {/* INTRODUCTION */}
      <div className="section04-intro">

        <h2>
          REAL CHANGES.
          <br />
          <span>REAL INTELLIGENCE.</span>
        </h2>

        <p>
          From urban growth to environmental shifts — GeoNexus
          detects, measures and visualizes the changes that matter.
        </p>

      </div>


      {/* MAIN SATELLITE ANALYSIS AREA */}
      <div className="section04-map-container">

        <div className="section04-map">

          {/* Satellite image placeholder */}
     <div
  className="section04-satellite-image"
  style={{ backgroundImage: `url(${backgroundImage})` }}
>
            <div className="section04-map-grid"></div>

            <div className="section04-map-scan"></div>

            <span className="section04-map-label">
              MULTI-TEMPORAL SATELLITE DATA
            </span>

            <span className="section04-map-coordinates">
              28.6139° N &nbsp; 77.2090° E
            </span>

            {/* Detection markers */}
            {detections.map((detection) => (
              <DetectionMarker
                key={detection.title}
                {...detection}
              />
            ))}

          </div>


          {/* MAP INFORMATION */}
          <div className="section04-map-info">

            <div>
              <span>SATELLITE INTELLIGENCE</span>
              <small>A CLEARER TOMORROW</small>
            </div>

            <div className="section04-compass">
              N
            </div>

          </div>


          {/* TIMELINE */}
          <div className="section04-timeline">

            <span>2021</span>

            <div className="section04-timeline-track">
              <span className="section04-timeline-progress"></span>
              <span className="section04-timeline-dot"></span>
            </div>

            <span>2026</span>

          </div>

        </div>

      </div>


      {/* ANALYSIS CARDS */}
      <div className="section04-analysis">

        {analysisData.map((item) => (
          <AnalysisCard
            key={item.title}
            {...item}
          />
        ))}

      </div>


      {/* FOOTER LINE */}
      <div className="section04-footer">

        <span>GEONEXUS</span>

        <div></div>

        <small>
          OBSERVE EARTH. EMPOWER TOMORROW.
        </small>

        <small>
          REAL DATA. REAL IMPACT.
        </small>

      </div>

    </section>
  );
}