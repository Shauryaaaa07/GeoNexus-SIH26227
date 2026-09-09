import { useState } from "react";
import Map from "../Map";
import "./Section04.css";

import urbanGrowth from "../assets/01_urban_growth.png";
import infrastructure from "../assets/02_infrastructure.png";
import vegetation from "../assets/03_vegetation.png";
import water from "../assets/04_water.png";
import landUse from "../assets/05_land_use_environment.png";
import delhiNcrMap from "../assets/06_delhi_ncr_base_map.png";

const POPULAR_CHIPS = [
  "Dwarka Sector 10",
  "Rajouri Garden",
  "Saket",
  "Rohini Sector 7",
  "Mayur Vihar",
  "India Gate"
];

const RANDOM_DELHI_PLACES = [
  "Dwarka Sector 10",
  "Rajouri Garden",
  "Saket",
  "Rohini Sector 7",
  "Mayur Vihar",
  "India Gate",
  "Connaught Place",
  "Pitampura",
  "Vasant Kunj",
  "Lajpat Nagar",
  "Karol Bagh",
  "Hauz Khas",
  "Janakpuri",
  "Okhla",
  "Paschim Vihar",
  "Narela"
];

const YEARS_FROM = [2020, 2021, 2022, 2023, 2024, 2025];
const YEARS_TO = [2021, 2022, 2023, 2024, 2025, 2026];
const CATEGORIES = [
  "All",
  "New Buildings",
  "New Roads",
  "Vegetation Change",
  "Water Body Change",
  "Agricultural / Land-use Change"
];
const RADII = ["0.5 km", "1.0 km", "2.0 km", "5.0 km", "Entire Delhi"];

export default function Section04({ activeSearch, setActiveSearch }) {
  const [searchInput, setSearchInput] = useState(
    activeSearch?.place || "Dwarka Sector 10"
  );
  const [mapStats, setMapStats] = useState(null);

  const handleSearchSubmit = (e) => {
    if (e) e.preventDefault();
    if (!searchInput.trim()) return;

    if (setActiveSearch) {
      setActiveSearch((prev) => ({
        ...prev,
        place: searchInput.trim(),
        categoryFilter: "All"
      }));
    }
  };

  const handleRandomPlace = () => {
    const randomIndex = Math.floor(Math.random() * RANDOM_DELHI_PLACES.length);
    const place = RANDOM_DELHI_PLACES[randomIndex];
    setSearchInput(place);
    if (setActiveSearch) {
      setActiveSearch((prev) => ({
        ...prev,
        place: place,
        categoryFilter: "All"
      }));
    }
  };

  const handleChipClick = (place) => {
    setSearchInput(place);
    if (setActiveSearch) {
      setActiveSearch((prev) => ({
        ...prev,
        place: place,
        categoryFilter: "All"
      }));
    }
  };

  const handleFilterChange = (field, val) => {
    if (setActiveSearch) {
      setActiveSearch((prev) => ({
        ...prev,
        [field]: val
      }));
    }
  };

  const handleCategoryClick = (catName) => {
    if (setActiveSearch) {
      const current = activeSearch?.categoryFilter;
      const next = current === catName ? "All" : catName;
      setActiveSearch((prev) => ({
        ...prev,
        categoryFilter: next
      }));
    }
  };

  const currentCategoryFilter = activeSearch?.categoryFilter || "All";

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

      {/* TOP SEARCH BAR & FILTERS BOX */}
      <div className="section04-search-box">
        <form onSubmit={handleSearchSubmit} className="section04-search-top-row">
          <div className="section04-search-input-wrapper">
            <span className="section04-search-icon">⌕</span>
            <input
              type="text"
              className="section04-search-input"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              placeholder="Search Delhi locality or feature (e.g. Dwarka Sector 10, Rohini, Saket, Rajouri Garden)..."
            />
          </div>

          <button type="submit" className="section04-btn-analyze">
            ANALYZE →
          </button>

          <button
            type="button"
            onClick={handleRandomPlace}
            className="section04-btn-random"
          >
            🎲 RANDOM DELHI PLACE
          </button>
        </form>

        {/* QUICK PLACE CHIPS */}
        <div className="section04-chips-row">
          <span className="section04-chips-label">POPULAR PLACES:</span>
          {POPULAR_CHIPS.map((p) => (
            <button
              key={p}
              type="button"
              className={`section04-chip-btn ${
                activeSearch?.place === p ? "active" : ""
              }`}
              onClick={() => handleChipClick(p)}
            >
              {p}
            </button>
          ))}
        </div>

        {/* FILTERS ROW */}
        <div className="section04-filters-row">
          <div className="section04-filter-group">
            <label>YEAR FROM:</label>
            <select
              className="section04-filter-select"
              value={activeSearch?.yearFrom || 2020}
              onChange={(e) =>
                handleFilterChange("yearFrom", parseInt(e.target.value, 10))
              }
            >
              {YEARS_FROM.map((y) => (
                <option key={y} value={y}>
                  {y}
                </option>
              ))}
            </select>
          </div>

          <div className="section04-filter-group">
            <label>YEAR TO:</label>
            <select
              className="section04-filter-select"
              value={activeSearch?.yearTo || 2026}
              onChange={(e) =>
                handleFilterChange("yearTo", parseInt(e.target.value, 10))
              }
            >
              {YEARS_TO.map((y) => (
                <option key={y} value={y}>
                  {y}
                </option>
              ))}
            </select>
          </div>

          <div className="section04-filter-group">
            <label>CATEGORY:</label>
            <select
              className="section04-filter-select"
              value={activeSearch?.category || "All"}
              onChange={(e) => handleFilterChange("category", e.target.value)}
            >
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>

          <div className="section04-filter-group">
            <label>RADIUS / SCOPE:</label>
            <select
              className="section04-filter-select"
              value={activeSearch?.radius || "Entire Delhi"}
              onChange={(e) => handleFilterChange("radius", e.target.value)}
            >
              {RADII.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* 65% MAP & 35% ANALYSIS PANEL GRID */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "minmax(0, 65%) minmax(0, 35%)",
          gap: "20px",
          position: "relative",
          zIndex: 10,
          marginBottom: "24px"
        }}
      >
        {/* 65% MAP */}
        <div style={{ height: "560px", borderRadius: "10px", overflow: "hidden" }}>
          <Map
            activeSearch={activeSearch}
            onStatsUpdate={setMapStats}
            showControls={false}
            height="560px"
          />
        </div>

        {/* 35% ANALYSIS PANEL */}
        <div className="section04-analysis-panel">
          <div className="section04-panel-summary-header">
            <div className="section04-summary-place-title">
              <span>{mapStats?.placeInfo?.query || activeSearch?.place || "Dwarka Sector 10"}</span>
              <span className="section04-summary-badge">
                {mapStats?.placeInfo?.search_mode === "point_radius"
                  ? `Search radius: ${((mapStats?.placeInfo?.radius_m || 2000)/1000).toFixed(0)} km`
                  : (activeSearch?.radius || "Entire Delhi")}
              </span>
            </div>

            <div style={{ fontSize: "11px", color: "#94a3b8", fontFamily: "Courier New", marginBottom: "4px" }}>
              {mapStats?.placeInfo?.admin_locality && (
                <span>Admin Zone: {mapStats.placeInfo.admin_locality} &bull; </span>
              )}
              PERIOD: {activeSearch?.yearFrom || 2020} → {activeSearch?.yearTo || 2026}
            </div>

            <div className="section04-summary-stats-grid">
              <div className="section04-summary-stat-box">
                <span className="section04-summary-stat-label">TOTAL DETECTED CHANGES</span>
                <span className="section04-summary-stat-val">
                  {mapStats?.totalCount ? mapStats.totalCount.toLocaleString() : "0"}
                </span>
                <span style={{ fontSize: "9px", color: "#64748b", display: "block" }}>
                  Map displaying: {mapStats?.returnedFeatures || 0}
                </span>
              </div>

              <div className="section04-summary-stat-box">
                <span className="section04-summary-stat-label">TOTAL CHANGED AREA</span>
                <span className="section04-summary-stat-val" style={{ color: "#38bdf8" }}>
                  {mapStats?.totalAreaKm2 || "0.00"} km²
                  <small style={{ display: "block", fontSize: "10px", color: "#94a3b8" }}>
                    ({mapStats?.totalAreaHa || "0.0"} ha)
                  </small>
                </span>
              </div>
            </div>
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: "4px", alignItems: "center" }}>
            <span style={{ fontSize: "12px", fontWeight: "700", color: "#38bdf8", letterSpacing: "0.05em" }}>
              CATEGORY IMPACT BREAKDOWN
            </span>
            <span style={{ fontSize: "10px", color: "#94a3b8" }}>Click category to filter map</span>
          </div>

          <div className="section04-category-card-list">
            {mapStats?.categoryBreakdown ? (
              mapStats.categoryBreakdown.map((cat) => {
                const isActive = currentCategoryFilter === cat.name;
                const areaHa = cat.area_ha ?? (cat.areaM2 / 10000).toFixed(1);
                const areaKm2 = cat.area_km2 ?? (cat.areaM2 / 1000000).toFixed(2);
                const sharePct = cat.share ?? 0;

                return (
                  <div
                    key={cat.name}
                    className={`section04-cat-item-card ${isActive ? "active" : ""}`}
                    onClick={() => handleCategoryClick(cat.name)}
                  >
                    <div className="section04-cat-item-top">
                      <div className="section04-cat-name-pill">
                        <span
                          className="section04-cat-color-dot"
                          style={{ background: cat.color }}
                        />
                        <span>{cat.name}</span>
                      </div>
                      <span className="section04-cat-share-text">{sharePct}%</span>
                    </div>

                    <div className="section04-cat-metrics-row">
                      <span>{cat.count.toLocaleString()} polygons</span>
                      <span>
                        {areaHa} ha ({areaKm2} km²)
                      </span>
                    </div>

                    <div className="section04-cat-bar-bg">
                      <div
                        className="section04-cat-bar-fill"
                        style={{ width: `${sharePct}%`, background: cat.color }}
                      />
                    </div>
                  </div>
                );
              })
            ) : (
              <div style={{ color: "#94a3b8", fontSize: "12px", textAlign: "center", padding: "20px" }}>
                Loading category breakdown...
              </div>
            )}
          </div>
        </div>
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
