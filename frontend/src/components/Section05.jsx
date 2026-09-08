import { useState } from "react";
import "./Section05.css";
import section05Image from "../assets/geonexus-section05.png";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "https://geonexus-backend1.onrender.com";

const DEFAULT_RESULTS = [
  {
    title: "URBAN EXPANSION",
    match: "96.4%",
    period: "2021 → 2026",
    type: "urban",
    category: "New Buildings",
    confidence: "High",
    area: "+2.4 km²",
    location: "Delhi",
  },
  {
    title: "ROAD NETWORK CHANGE",
    match: "92.8%",
    period: "2021 → 2026",
    type: "roads",
    category: "New Roads",
    confidence: "High",
    area: "+12.6 km",
    location: "Delhi",
  },
  {
    title: "VEGETATION CHANGE",
    match: "89.6%",
    period: "2021 → 2026",
    type: "vegetation",
    category: "Vegetation Change",
    confidence: "Medium",
    area: "-3.1 km²",
    location: "Delhi",
  },
];

const analysisSteps = [
  {
    number: "01",
    title: "Query understood",
    description: "Analyzing your request...",
  },
  {
    number: "02",
    title: "Searching satellite data",
    description: "Scanning multi-temporal imagery...",
  },
  {
    number: "03",
    title: "Finding relevant results",
    description: "Filtering and ranking matches...",
  },
  {
    number: "04",
    title: "Results ready",
    description: "Showing the best matches.",
  },
];

function SearchResult({
  title,
  match,
  period,
  type,
  onClick,
  selected,
}) {
  return (
    <article
      className={`section05-result-card ${type} ${
        selected ? "selected" : ""
      }`}
      onClick={onClick}
    >
      <div className="section05-result-image">
        <span></span>
      </div>

      <div className="section05-result-info">
        <strong>{title}</strong>

        <span className="section05-match">
          {match} match
        </span>

        <small>{period}</small>
      </div>

      <button
        className="section05-result-arrow"
        aria-label={`Open ${title}`}
        onClick={(event) => {
          event.stopPropagation();
          onClick();
        }}
      >
        →
      </button>
    </article>
  );
}

function QueryAnalysis() {
  return (
    <aside className="section05-query-panel">
      <div className="section05-query-header">
        <span>INTELLIGENT SEARCH</span>
        <i></i>
      </div>

      <div className="section05-query-title">
        QUERY ANALYSIS
      </div>

      <div className="section05-analysis-list">
        {analysisSteps.map((step, index) => (
          <div
            className={`section05-analysis-step ${
              index === analysisSteps.length - 1
                ? "complete"
                : ""
            }`}
            key={step.number}
          >
            <div className="section05-step-icon">
              {index === analysisSteps.length - 1
                ? "✓"
                : step.number}
            </div>

            <div className="section05-step-line"></div>

            <div className="section05-step-content">
              <strong>{step.title}</strong>
              <span>{step.description}</span>
            </div>
          </div>
        ))}
      </div>
    </aside>
  );
}

function ResultIntelligence({ result }) {
  if (!result) return null;

  return (
    <div className="section05-intelligence">
      <div className="section05-intelligence-header">
        <div>
          <span>RESULT INTELLIGENCE</span>
          <h3>{result.title}</h3>
        </div>

        <div className="section05-result-score">
          <small>RELEVANCE</small>
          <strong>{result.match}</strong>
        </div>
      </div>

      <div className="section05-intelligence-content">
        <div className="section05-detail-image">
          <div className="section05-detail-image-overlay">
            <span>DETECTED AREA</span>
            <strong>{result.area}</strong>
          </div>

          <div className="section05-detail-grid"></div>
        </div>

        <div className="section05-detail-info">
          <div className="section05-detail-row">
            <span>CATEGORY</span>
            <strong>{result.category}</strong>
          </div>

          <div className="section05-detail-row">
            <span>CONFIDENCE</span>
            <strong className="confidence">
              {result.confidence}
            </strong>
          </div>

          <div className="section05-detail-row">
            <span>AREA / CHANGE</span>
            <strong>{result.area}</strong>
          </div>

          <div className="section05-detail-row">
            <span>PERIOD</span>
            <strong>{result.period}</strong>
          </div>

          <div className="section05-detail-row">
            <span>LOCATION</span>
            <strong>{result.location}</strong>
          </div>
        </div>
      </div>

      <div className="section05-detail-timeline">
        <span>2021</span>

        <div>
          <i></i>
          <b></b>
        </div>

        <span>2026</span>
      </div>
    </div>
  );
}

export default function Section05() {
  const [query, setQuery] = useState(
    "Show urban expansion in Delhi between 2021 and 2026"
  );

  const [resultsList, setResultsList] =
    useState(DEFAULT_RESULTS);

  const [loading, setLoading] = useState(false);

  const [showAll, setShowAll] = useState(false);

  const [selectedResult, setSelectedResult] =
    useState(DEFAULT_RESULTS[0]);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);

    try {
      const apiUrl =
        `${API_BASE_URL}/api/search/semantic?query=${encodeURIComponent(
          query
        )}`;

      const res = await fetch(apiUrl);

      if (!res.ok) {
        throw new Error(
          `Semantic API returned ${res.status}`
        );
      }

      const data = await res.json();

      if (
        data.status === "success" &&
        data.results &&
        data.results.length > 0
      ) {
        const mapped = data.results.map(
          (item, idx) => {
            const similarity =
              typeof item.similarity_score === "number"
                ? item.similarity_score
                : 0;

            return {
              title: item.description
                ? item.description.toUpperCase()
                : `SATELLITE IMAGE ${item.year || ""}`,

              match:
                similarity > 0
                  ? `${(similarity * 100).toFixed(1)}%`
                  : "N/A",

              period: item.year
                ? `${item.year}`
                : "2021 → 2026",

              type:
                idx % 3 === 0
                  ? "urban"
                  : idx % 3 === 1
                  ? "roads"
                  : "vegetation",

              category:
                item.description ||
                "Satellite Image",

              confidence:
                similarity >= 0.7
                  ? "High"
                  : similarity >= 0.4
                  ? "Medium"
                  : "Low",

              area:
                item.location || "Delhi",

              location:
                item.location || "Delhi",
            };
          }
        );

        setResultsList(mapped);
        setSelectedResult(mapped[0]);
        setShowAll(true);
      } else {
        console.warn(
          "No semantic results received",
          data
        );
      }
    } catch (error) {
      console.warn(
        "Semantic search fetch failed:",
        error
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="section05">
      {/* BACKGROUND */}

      <div
        className="section05-background"
        style={{
          backgroundImage: `url(${section05Image})`,
        }}
      ></div>

      <div className="section05-overlay"></div>

      {/* HEADER */}

      <header className="section05-header">
        <div className="section05-section-label">
          <span>05</span>
          <i></i>
          <strong>SEMANTIC RETRIEVAL</strong>
        </div>

        <div className="section05-powered">
          POWERED BY AI
          <i></i>
        </div>
      </header>

      {/* MAIN CONTENT */}

      <div className="section05-content">
        <div className="section05-left">
          {/* INTRO */}

          <div className="section05-intro">
            <h2>
              SEARCH EARTH.
              <br />
              <span>FIND MEANING.</span>
            </h2>

            <p>
              Describe what you're looking for.
              GeoNexus finds the right satellite
              imagery, understands the context and
              shows you the most relevant results.
            </p>
          </div>

          {/* SEARCH */}

          <div className="section05-search">
            <div className="section05-search-icon">
              ⌕
            </div>

            <input
              type="text"
              value={query}
              onChange={(e) =>
                setQuery(e.target.value)
              }
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  handleSearch();
                }
              }}
              placeholder="Describe your search query..."
              aria-label="Semantic satellite search"
            />

            <button
              aria-label="Search"
              onClick={handleSearch}
              disabled={loading}
            >
              {loading ? "..." : "→"}
            </button>
          </div>

          {/* FILTERS */}

          <div className="section05-filters">
            {/* LOCATION */}

            <label className="section05-filter">
              <select defaultValue="Delhi">
                <option value="Delhi">
                  Delhi
                </option>
              </select>
            </label>

            {/* TIME */}

            <label className="section05-filter">
              <select defaultValue="2021-2026">
                <option value="2020-2021">
                  2020 – 2021
                </option>

                <option value="2021-2022">
                  2021 – 2022
                </option>

                <option value="2022-2023">
                  2022 – 2023
                </option>

                <option value="2023-2024">
                  2023 – 2024
                </option>

                <option value="2024-2025">
                  2024 – 2025
                </option>

                <option value="2025-2026">
                  2025 – 2026
                </option>

                <option value="2021-2026">
                  2021 – 2026
                </option>
              </select>
            </label>

            {/* FEATURE */}

            <label className="section05-filter">
              <select defaultValue="Urban Growth">
                <option value="Urban Growth">
                  Urban Growth
                </option>

                <option value="Road Network">
                  Road Network
                </option>

                <option value="Vegetation">
                  Vegetation
                </option>

                <option value="Water Body">
                  Water Body
                </option>

                <option value="Agricultural / Land Use">
                  Agricultural / Land Use
                </option>
              </select>
            </label>

            {/* CHANGE TYPE */}

            <label className="section05-filter">
              <select defaultValue="Change Detection">
                <option value="Change Detection">
                  Change Detection
                </option>

                <option value="New Buildings">
                  New Buildings
                </option>

                <option value="New Roads">
                  New Roads
                </option>

                <option value="Vegetation Change">
                  Vegetation Change
                </option>

                <option value="Water Body Change">
                  Water Body Change
                </option>

                <option value="Land-Use Change">
                  Land-Use Change
                </option>
              </select>
            </label>
          </div>

          {/* METRICS */}

          <div className="section05-metrics">
            <div>
              <strong>96.4%</strong>
              <span>ACCURACY</span>
            </div>

            <div>
              <strong>3M+</strong>
              <span>SATELLITE IMAGES</span>
            </div>

            <div>
              <strong>AI</strong>
              <span>POWERED SEARCH</span>
            </div>

            <div>
              <strong>DELHI</strong>
              <span>FOCUS AREA</span>
            </div>
          </div>

          {/* TOP MATCHES */}

          <div className="section05-results-header">
            <h3>Top Matches</h3>

            <button
              onClick={() =>
                setShowAll(!showAll)
              }
            >
              {showAll
                ? "HIDE DETAILS"
                : "VIEW ALL"}
              <span>→</span>
            </button>
          </div>

          <div className="section05-results">
            {resultsList.map(
              (result, index) => (
                <SearchResult
                  key={`${result.title}-${index}`}
                  {...result}
                  selected={
                    selectedResult &&
                    selectedResult.title ===
                      result.title
                  }
                  onClick={() => {
                    setSelectedResult(result);
                    setShowAll(true);
                  }}
                />
              )
            )}
          </div>

          {/* RESULT INTELLIGENCE */}

          {showAll && selectedResult && (
            <ResultIntelligence
              result={selectedResult}
            />
          )}
        </div>

        {/* RIGHT PANEL */}

        <QueryAnalysis />
      </div>

      {/* FOOTER */}

      <footer className="section05-footer">
        <strong>GEONEXUS</strong>

        <div></div>

        <span>
          FROM DATA TO A CLEARER TOMORROW.
        </span>
      </footer>
    </section>
  );
}