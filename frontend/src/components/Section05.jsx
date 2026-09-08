import { API_BASE_URL } from "../config";
import { useMemo, useState, useEffect } from "react";
import "./Section05.css";

import section05Image from "../assets/geonexus-section05.png";

import urbanImage from "../assets/01_urban_growth.png";
import infrastructureImage from "../assets/02_infrastructure.png";
import vegetationImage from "../assets/03_vegetation.png";
import waterImage from "../assets/04_water.png";
import landUseImage from "../assets/05_land_use_environment.png";

/*
  Automatically reads images from src/assets.
  This avoids Vite crashing if the yearly image filename
  is slightly different.
*/
const assetFiles = import.meta.glob(
  "../assets/*",
  {
    eager: true,
    query: "?url",
    import: "default",
  }
);

function findYearImage(year) {
  const entries = Object.entries(assetFiles);

  const match = entries.find(([path]) => {
    const filename = path.split("/").pop().toLowerCase();

    return (
      filename.includes(String(year)) &&
      (
        filename.includes("delhi") ||
        filename.includes("satellite") ||
        filename.includes("202")
      )
    );
  });

  return match ? match[1] : null;
}

const YEAR_IMAGES = {
  2020: findYearImage(2020),
  2021: findYearImage(2021),
  2022: findYearImage(2022),
  2023: findYearImage(2023),
  2024: findYearImage(2024),
  2025: findYearImage(2025),
  2026: findYearImage(2026),
};

const YEARS = [2020, 2021, 2022, 2023, 2024, 2025, 2026];

const categories = [
  {
    title: "URBAN GROWTH",
    image: urbanImage,
    description: "Built-up areas and settlement expansion.",
  },
  {
    title: "INFRASTRUCTURE",
    image: infrastructureImage,
    description: "Roads, corridors and development patterns.",
  },
  {
    title: "VEGETATION",
    image: vegetationImage,
    description: "Green cover and environmental patterns.",
  },
  {
    title: "WATER",
    image: waterImage,
    description: "Rivers, lakes and surface-water patterns.",
  },
  {
    title: "LAND USE",
    image: landUseImage,
    description: "Agricultural, urban and open-land patterns.",
  },
];

function getYears(text) {
  const years = [
    ...new Set(
      (text.match(/20(?:20|21|22|23|24|25|26)/g) || []).map(Number)
    ),
  ];

  if (years.length >= 2) {
    return {
      start: Math.min(years[0], years[1]),
      end: Math.max(years[0], years[1]),
    };
  }

  return {
    start: 2020,
    end: 2023,
  };
}

function CategoryCard({ item, active, onClick }) {
  return (
    <button
      className={`section05-category ${active ? "active" : ""}`}
      onClick={onClick}
      type="button"
    >
      <img src={item.image} alt={item.title} />

      <span className="section05-category-shade" />

      <span className="section05-category-number">
        {item.title.slice(0, 2)}
      </span>

      <span className="section05-category-text">
        <strong>{item.title}</strong>
        <small>{item.description}</small>
      </span>

      <span className="section05-category-arrow">
        →
      </span>
    </button>
  );
}

function QueryPanel({ start, end }) {
  return (
    <aside className="section05-query-panel">
      <div className="section05-query-top">
        <span>INTELLIGENT SEARCH</span>
        <i />
      </div>

      <small className="section05-query-label">
        QUERY ANALYSIS
      </small>

      <div className="section05-query-period">
        <span>SELECTED PERIOD</span>

        <strong>
          {start} → {end}
        </strong>
      </div>

      {[
        [
          "01",
          "Query understood",
          "Location and requested years detected.",
        ],
        [
          "02",
          "Satellite data found",
          `Delhi ${start} and ${end} imagery selected.`,
        ],
        [
          "03",
          "Temporal comparison",
          "Before / after observations prepared.",
        ],
        [
          "✓",
          "Results ready",
          "Change categories are available below.",
        ],
      ].map(([number, title, text], index) => (
        <div
          className="section05-query-step"
          key={number}
        >
          <div
            className={`section05-step-circle ${
              index === 3 ? "done" : ""
            }`}
          >
            {number}
          </div>

          {index < 3 && (
            <div className="section05-step-connector" />
          )}

          <div>
            <strong>{title}</strong>
            <span>{text}</span>
          </div>
        </div>
      ))}
    </aside>
  );
}

export default function Section05() {
  const [dashboardStats, setDashboardStats] = useState(null);
  const [searchResults, setSearchResults] = useState(null);
  const [isSearching, setIsSearching] = useState(false);

  // backend se stats le rahe hain
  useEffect(() => {
    fetch(`${API_BASE_URL}/api/dashboard/stats`)
      .then((res) => res.json())
      .then((data) => setDashboardStats(data))
      .catch((err) => console.log("Dashboard stats error:", err));
  }, []);
  const [query, setQuery] = useState(
    "Show the difference between Delhi 2020 and 2023"
  );

  const [start, setStart] = useState(2020);
  const [end, setEnd] = useState(2023);

  const [activeCategory, setActiveCategory] =
    useState("URBAN GROWTH");

  const [uploadedImage, setUploadedImage] =
    useState(null);

  const selectedCategory = useMemo(
    () =>
      categories.find(
        (item) => item.title === activeCategory
      ) || categories[0],
    [activeCategory]
  );

  function runSearch(value = query) {
    const years = getYears(value);

    setStart(years.start);
    setEnd(years.end);

    setIsSearching(true);
    // backend se semantic search result le rahe hain
    fetch(`${API_BASE_URL}/api/search/semantic?query=${encodeURIComponent(value)}`)
      .then((res) => res.json())
      .then((data) => {
        setSearchResults(data);
        setIsSearching(false);
      })
      .catch((err) => {
        console.log("Semantic search error:", err);
        setIsSearching(false);
      });
  }

  function updatePeriod(newStart, newEnd) {
    let safeStart = newStart;
    let safeEnd = newEnd;

    if (safeStart >= safeEnd) {
      if (newStart < 2026) {
        safeEnd = newStart + 1;
      } else {
        safeStart = newEnd - 1;
      }
    }

    safeStart = Math.max(2020, safeStart);
    safeEnd = Math.min(2026, safeEnd);

    setStart(safeStart);
    setEnd(safeEnd);

    setQuery(
      `Show the difference between Delhi ${safeStart} and ${safeEnd}`
    );
  }

  function handleUpload(event) {
    const file = event.target.files?.[0];

    if (!file) return;

    const preview = URL.createObjectURL(file);

    setUploadedImage({
      name: file.name,
      preview,
    });
  }

  const beforeImage = YEAR_IMAGES[start];
  const afterImage = YEAR_IMAGES[end];

  return (
    <section
      className="section05"
      id="search"
      style={{
        "--section05-bg": `url(${section05Image})`,
      }}
    >
      <div className="section05-background" />

      <div className="section05-overlay" />

      {/* HEADER */}

      <header className="section05-header">
        <div className="section05-label">
          <span>05</span>

          <i />

          <strong>
            SEMANTIC RETRIEVAL
          </strong>
        </div>

        <div className="section05-status">
          <span />
          MULTI-TEMPORAL SEARCH
        </div>
      </header>

      {/* MAIN */}

      <div className="section05-layout">

        <main className="section05-main">

          {/* HEADING */}

          <div className="section05-heading">
            <h1>
              SEARCH EARTH.
              <br />
              <em>FIND MEANING.</em>
            </h1>

            <p>
              Describe the change you want to explore.
              GeoNexus finds the matching satellite
              observations and compares the requested
              time period.
            </p>
          </div>

          {/* SEARCH */}

          <div className="section05-search-row">

            <div className="section05-search-icon">
              ⌕
            </div>

            <input
              type="text"
              value={query}
              onChange={(event) =>
                setQuery(event.target.value)
              }
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  runSearch();
                }
              }}
              placeholder="Example: Show the difference between Delhi 2020 and 2023"
            />

            <button
              type="button"
              onClick={() => runSearch()}
            >
              →
            </button>

          </div>

          {/* NATURAL LANGUAGE GUIDE */}

          <div className="section05-natural-language">
            <span className="section05-natural-label">
              NATURAL LANGUAGE
            </span>

            <span className="section05-natural-text">
              Describe what you want in your own words:
            </span>

            <button
              type="button"
              onClick={() => {
                const text =
                  "Show urban growth in Delhi between 2020 and 2023";
                setQuery(text);
                runSearch(text);
              }}
            >
              “Show urban growth in Delhi between 2020 and 2023”
            </button>

            <button
              type="button"
              onClick={() => {
                const text =
                  "Compare vegetation change from 2021 to 2026";
                setQuery(text);
                runSearch(text);
              }}
            >
              “Compare vegetation change from 2021 to 2026”
            </button>
          </div>

          {/* CONTROLS */}

          <div className="section05-controls">

            <select
              value={start}
              onChange={(event) =>
                updatePeriod(
                  Number(event.target.value),
                  end
                )
              }
            >
              {YEARS.slice(0, -1).map((year) => (
                <option
                  key={year}
                  value={year}
                >
                  BEFORE: {year}
                </option>
              ))}
            </select>

            <select
              value={end}
              onChange={(event) =>
                updatePeriod(
                  start,
                  Number(event.target.value)
                )
              }
            >
              {YEARS.slice(1).map((year) => (
                <option
                  key={year}
                  value={year}
                >
                  AFTER: {year}
                </option>
              ))}
            </select>

            <label className="section05-upload">

              <input
                type="file"
                accept="image/*"
                onChange={handleUpload}
              />

              <span>＋</span>

              UPLOAD IMAGE

            </label>

            {uploadedImage && (
              <button
                type="button"
                className="section05-upload-name"
                onClick={() =>
                  setUploadedImage(null)
                }
              >
                {uploadedImage.name.slice(0, 18)} ×
              </button>
            )}

          </div>

          {/* REAL DATABASE STATS */}

          <div className="section05-stats">

            <div>
              <strong>{dashboardStats ? dashboardStats.total_polygons.toLocaleString() : "9,411"}</strong>
              <span>TOTAL POLYGONS</span>
            </div>

            <div>
              <strong>{dashboardStats ? `${dashboardStats.total_area_km2} km²` : "392.31 km²"}</strong>
              <span>TOTAL CHANGED AREA</span>
            </div>

            <div>
              <strong>{end - start}</strong>
              <span>YEARS DIFFERENCE</span>
            </div>

            <div>
              <strong>{dashboardStats ? dashboardStats.categories.length : "6"}</strong>
              <span>ACTIVE CATEGORIES</span>
            </div>

          </div>

          {/* RESULTS */}

          <div className="section05-results-title">

            <h2>
              CHANGE CATEGORIES
            </h2>

            <span>
              DELHI / {start} → {end}
            </span>

          </div>

          {/* CATEGORY IMAGES */}

          <div className="section05-categories">

            {categories.map((item) => (
              <CategoryCard
                key={item.title}
                item={item}
                active={
                  activeCategory === item.title
                }
                onClick={() =>
                  setActiveCategory(item.title)
                }
              />
            ))}

          </div>

          {/* BEFORE / AFTER RESULT */}

          <div className="section05-result">

            <div className="section05-result-head">

              <div>
                <small>
                  RESULT INTELLIGENCE
                </small>

                <h3>
                  {selectedCategory.title}
                </h3>
              </div>

              <strong>
                {start} → {end}
              </strong>

            </div>

            <div className="section05-images">

              <div>
                <span>
                  BEFORE / {start}
                </span>

                {beforeImage ? (
                  <img
                    src={beforeImage}
                    alt={`Delhi satellite imagery ${start}`}
                  />
                ) : (
                  <div className="section05-image-missing">
                    IMAGE NOT FOUND
                    <small>
                      Add the {start} Delhi image
                      to src/assets
                    </small>
                  </div>
                )}
              </div>

              <b>→</b>

              <div>
                <span>
                  AFTER / {end}
                </span>

                {afterImage ? (
                  <img
                    src={afterImage}
                    alt={`Delhi satellite imagery ${end}`}
                  />
                ) : (
                  <div className="section05-image-missing">
                    IMAGE NOT FOUND
                    <small>
                      Add the {end} Delhi image
                      to src/assets
                    </small>
                  </div>
                )}
              </div>

            </div>

            <p>
              {selectedCategory.description}
              {" "}
              Compare the visible satellite
              observations between {start} and {end}.
            </p>

          </div>

          {/* UPLOADED IMAGE */}

          {uploadedImage && (
            <div className="section05-upload-result">

              <span>
                UPLOADED IMAGE
              </span>

              <img
                src={uploadedImage.preview}
                alt="Uploaded analysis"
              />

            </div>
          )}

        </main>

        {/* QUERY PANEL */}

        <QueryPanel
          start={start}
          end={end}
        />

      </div>

      {/* FOOTER */}

      <footer className="section05-footer">

        <strong>
          GEONEXUS
        </strong>

        <i />

        <span>
          FROM DATA TO A CLEARER TOMORROW.
        </span>

      </footer>

    </section>
  );
}