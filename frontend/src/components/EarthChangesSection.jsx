import "./EarthChangesSection.css";

import Delhi2021Satellite from "../assets/Delhi2021Satellite.png";
import Delhi2023Satellite from "../assets/Delhi2023Satellite.png";
import Delhi2026Satellite from "../assets/Delhi2026Satellite.png";


const comparisons = [
  {
    id: "delhi-2021-2023",

    name: "DELHI",

    coords: "28.5838° N, 77.2528° E",

    theme: "SHORT-TERM TRANSFORMATION",

    beforeYear: "2021",
    afterYear: "2023",

    beforeImage: Delhi2021Satellite,
    afterImage: Delhi2023Satellite,

    period: "2021 → 2023",

    metrics: [
      {
        icon: "▥",
        value: "—",
        label: "Built-up Area",
        type: "positive",
      },
      {
        icon: "▰",
        value: "—",
        label: "Infrastructure",
        type: "positive",
      },
      {
        icon: "◒",
        value: "—",
        label: "Vegetation Cover",
        type: "neutral",
      },
      {
        icon: "⌁",
        value: "—",
        label: "Road Network",
        type: "positive",
      },
      {
        icon: "◇",
        value: "—",
        label: "New Structures",
        type: "positive",
      },
    ],
  },

  {
    id: "delhi-2021-2026",

    name: "DELHI",

    coords: "28.5838° N, 77.2528° E",

    theme: "LONG-TERM TRANSFORMATION",

    beforeYear: "2021",
    afterYear: "2026",

    beforeImage: Delhi2021Satellite,
    afterImage: Delhi2026Satellite,

    period: "2021 → 2026",

    metrics: [
      {
        icon: "▥",
        value: "—",
        label: "Built-up Area",
        type: "positive",
      },
      {
        icon: "▰",
        value: "—",
        label: "Infrastructure",
        type: "positive",
      },
      {
        icon: "◒",
        value: "—",
        label: "Vegetation Cover",
        type: "neutral",
      },
      {
        icon: "⌁",
        value: "—",
        label: "Road Network",
        type: "positive",
      },
      {
        icon: "◇",
        value: "—",
        label: "New Structures",
        type: "positive",
      },
    ],
  },
];


function SatelliteImage({
  year,
  image,
}) {
  return (
    <div className="ecs-image">

      <img
        src={image}
        alt={`Delhi satellite imagery from ${year}`}
      />

      <div className="ecs-image-overlay" />

      <span className="ecs-image-source">
        SENTINEL-2 / COPERNICUS
      </span>

      <span className="ecs-image-status">
        SATELLITE FEED
      </span>

      <span className="ecs-year">
        {year}
      </span>

    </div>
  );
}


function ComparisonCard({
  comparison,
}) {
  return (
    <article className="ecs-card">

      {/* CARD HEADER */}

      <div className="ecs-card-header">

        <div className="ecs-location">

          <div className="ecs-location-title">

            <span className="ecs-live-dot" />

            <h3>
              {comparison.name}
            </h3>

          </div>

          <span className="ecs-coordinates">
            {comparison.coords}
          </span>

        </div>

        <div className="ecs-theme">

          <span>
            TEMPORAL ANALYSIS
          </span>

          <strong>
            {comparison.theme}
          </strong>

        </div>

      </div>


      {/* COMPARISON AREA */}

      <div className="ecs-comparison">

        <SatelliteImage
          year={comparison.beforeYear}
          image={comparison.beforeImage}
        />


        <div className="ecs-divider">

          <span>
            CHANGE
          </span>

        </div>


        <SatelliteImage
          year={comparison.afterYear}
          image={comparison.afterImage}
        />


        {/* METRICS */}

        <div className="ecs-metrics">

          <div className="ecs-metrics-header">

            <span>
              DETECTED SIGNALS
            </span>

            <b>
              {comparison.period}
            </b>

          </div>


          {comparison.metrics.map(
            (metric) => (
              <div
                className="ecs-metric"
                key={metric.label}
              >

                <span className="ecs-icon">
                  {metric.icon}
                </span>

                <div className="ecs-metric-info">

                  <b
                    className={
                      metric.type === "negative"
                        ? "negative"
                        : metric.type === "neutral"
                          ? "neutral"
                          : ""
                    }
                  >
                    {metric.value}
                  </b>

                  <small>
                    {metric.label}
                  </small>

                </div>

              </div>
            )
          )}

        </div>

      </div>

    </article>
  );
}


export default function EarthChangesSection() {

  const handlePointerMove = (event) => {

    const section =
      event.currentTarget;

    const rect =
      section.getBoundingClientRect();

    const x =
      ((event.clientX - rect.left) /
        rect.width) *
      100;

    const y =
      ((event.clientY - rect.top) /
        rect.height) *
      100;

    section.style.setProperty(
      "--mouse-x",
      `${x}%`
    );

    section.style.setProperty(
      "--mouse-y",
      `${y}%`
    );
  };


  const resetPointer = (event) => {

    const section =
      event.currentTarget;

    section.style.setProperty(
      "--mouse-x",
      "78%"
    );

    section.style.setProperty(
      "--mouse-y",
      "50%"
    );
  };


  return (
    <section
      className="earth-changes-section"

      onPointerMove={
        handlePointerMove
      }

      onPointerLeave={
        resetPointer
      }
    >

      {/* ATMOSPHERIC CONTOURS */}

      <div
        className="ecs-contours"
        aria-hidden="true"
      >

        <span />
        <span />
        <span />
        <span />
        <span />
        <span />
        <span />

      </div>


      {/* SOFT DATA GLOW */}

      <div
        className="ecs-data-glow"
        aria-hidden="true"
      />


      {/* MAIN CONTENT */}

      <div className="ecs-content">


        {/* =================================================
            LEFT — SATELLITE COMPARISONS
        ================================================= */}

        <div className="ecs-left">

          <div className="ecs-section-label">

            <span>
              02
            </span>

            <div>
              EARTH OBSERVATION
              <small>
                MULTI-TEMPORAL CHANGE ANALYSIS
              </small>
            </div>

          </div>


          {comparisons.map(
            (comparison) => (
              <ComparisonCard
                key={comparison.id}
                comparison={comparison}
              />
            )
          )}


          {/* ANALYSIS DETAIL */}

          <div className="ecs-analysis-panel">

            <div className="ecs-analysis-mark">
              ∿
            </div>

            <div className="ecs-analysis-content">

              <span>
                GEO NEXUS / TEMPORAL ENGINE
              </span>

              <h4>
                FROM IMAGERY TO EVIDENCE.
              </h4>

              <p>
                Comparing the same geographic
                region across different acquisition
                dates allows GeoNexus to identify
                meaningful changes in land use,
                infrastructure, vegetation and
                built-up patterns.
              </p>

            </div>


            <div className="ecs-analysis-period">

              <small>
                COMPARISONS
              </small>

              <strong>
                02
              </strong>

              <span>
                TIME SERIES
              </span>

            </div>

          </div>

        </div>


        {/* =================================================
            RIGHT — SECTION MESSAGE
        ================================================= */}

        <div className="ecs-right">

          <div className="ecs-right-content">

            <span className="ecs-kicker">
              REAL IMAGE, REAL IMPACT.
            </span>


            <h2>

              THE EARTH

              <br />

              IS ALWAYS

              <br />

              <em>
                CHANGING.
              </em>

            </h2>


            <div className="ecs-line" />


            <p className="ecs-lead">

              Satellite imagery turns
              change into something
              we can see, compare
              and understand.

            </p>


            <p className="ecs-text">

              Earth is constantly evolving.
              By comparing observations of
              the same place across time,
              GeoNexus helps reveal where
              transformation occurs and
              what those changes mean.

            </p>


            {/* DETAIL INFORMATION */}

            <div className="ecs-detail-grid">

              <div className="ecs-detail-item">

                <span>
                  01
                </span>

                <div>
                  <strong>
                    OBSERVE
                  </strong>

                  <small>
                    Access real satellite
                    observations.
                  </small>
                </div>

              </div>


              <div className="ecs-detail-item">

                <span>
                  02
                </span>

                <div>
                  <strong>
                    COMPARE
                  </strong>

                  <small>
                    Examine the same
                    location over time.
                  </small>
                </div>

              </div>


              <div className="ecs-detail-item">

                <span>
                  03
                </span>

                <div>
                  <strong>
                    DETECT
                  </strong>

                  <small>
                    Identify meaningful
                    spatial changes.
                  </small>
                </div>

              </div>


              <div className="ecs-detail-item">

                <span>
                  04
                </span>

                <div>
                  <strong>
                    UNDERSTAND
                  </strong>

                  <small>
                    Turn observations
                    into intelligence.
                  </small>
                </div>

              </div>

            </div>

          </div>


          {/* RIGHT HUD */}

          <div className="ecs-hud">

            <span>
              OBSERVE
            </span>

            <span>
              COMPARE
            </span>

            <span>
              DETECT
            </span>

            <span>
              UNDERSTAND
            </span>

          </div>

        </div>

      </div>

    </section>
  );
}