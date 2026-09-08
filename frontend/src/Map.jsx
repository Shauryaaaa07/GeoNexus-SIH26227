import "leaflet/dist/leaflet.css";

import {
  MapContainer,
  TileLayer,
  GeoJSON,
  ImageOverlay,
  LayersControl,
  useMap
} from "react-leaflet";

import { useEffect, useState, useRef } from "react";

import { API_BASE_URL } from "./config";

const CITIES = {
  Delhi: { center: [28.6139, 77.2090], zoom: 11 },
  Mumbai: { center: [19.0760, 72.8777], zoom: 11 },
  Bengaluru: { center: [12.9716, 77.5946], zoom: 11 },
  Hyderabad: { center: [17.3850, 78.4867], zoom: 11 },
  Chennai: { center: [13.0827, 80.2707], zoom: 11 }
};

const YEARS = [2020, 2021, 2022, 2023, 2024, 2025, 2026];

const DELHI_BOUNDS = [
  [28.58, 77.15],
  [28.68, 77.27]
];

function MapRecenter({ center, zoom, city }) {
  const map = useMap();
  const prevCityRef = useRef(city);

  useEffect(() => {
    if (prevCityRef.current !== city) {
      map.setView(center, zoom);
      prevCityRef.current = city;
    }
  }, [city, center, zoom, map]);

  return null;
}

function formatArea(areaM2) {
  if (!areaM2 || isNaN(areaM2)) return "0 m²";

  if (areaM2 >= 1000000) {
    return `${(areaM2 / 1000000).toFixed(2)} km²`;
  }

  return `${Math.round(areaM2).toLocaleString()} m²`;
}

function Map() {
  const [city, setCity] = useState("Delhi");
  const [startYear, setStartYear] = useState(2021);
  const [endYear, setEndYear] = useState(2022);

  const [polygons, setPolygons] = useState(null);
  const [statusMessage, setStatusMessage] = useState("");
  const [isPending, setIsPending] = useState(false);
  const [loading, setLoading] = useState(false);

  const [visibleCategories, setVisibleCategories] = useState({
    "New Buildings": true,
    "New Roads": true,
    "Vegetation Change": true,
    "Water Body Change": true,
    "Agricultural / Land-use Change": true,
    "Unclassified": true
  });

  const currentCityConfig = CITIES[city] || CITIES.Delhi;

  const handleStartYearChange = (newStart) => {
    const val = parseInt(newStart, 10);

    setStartYear(val);

    if (val >= endYear) {
      setEndYear(Math.min(val + 1, 2026));
    }
  };

  const handleEndYearChange = (newEnd) => {
    const val = parseInt(newEnd, 10);

    setEndYear(val);

    if (val <= startYear) {
      setStartYear(Math.max(val - 1, 2020));
    }
  };

  const toggleCategory = (category) => {
    setVisibleCategories((prev) => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  const beforeImage =
    `${API_BASE_URL}/api/satellite/rasters/delhi/${startYear}`;

  const afterImage =
    `${API_BASE_URL}/api/satellite/rasters/delhi/${endYear}`;

  useEffect(() => {
    const cityKey = city.toLowerCase();

    setLoading(true);
    setStatusMessage("");
    setIsPending(false);

    const apiUrl =
      `${API_BASE_URL}/api/changes/range?city=${encodeURIComponent(
        city
      )}&start=${startYear}&end=${endYear}`;

    fetch(apiUrl)
      .then((res) => {
        if (!res.ok) {
          throw new Error("API error");
        }

        return res.json();
      })

      .then((data) => {
        if (
          data.status === "PENDING" ||
          !data.features ||
          data.features.length === 0
        ) {
          setPolygons(null);
          setIsPending(true);

          setStatusMessage(
            `Satellite analysis for ${city} (${startYear} → ${endYear}) is not available yet.`
          );
        } else {
          setPolygons(data);
          setIsPending(false);

          if (data.status === "partial") {
            setStatusMessage(
              `Some years in ${startYear} → ${endYear} range for ${city} are pending.`
            );
          } else {
            setStatusMessage("");
          }
        }
      })

      .catch(() => {
        const consecutivePairs = [];

        for (let y = startYear; y < endYear; y++) {
          consecutivePairs.push([y, y + 1]);
        }

        const fetchPromises = consecutivePairs.map(([yFrom, yTo]) => {
          const staticPath =
            `/data/${cityKey}/${yFrom}_${yTo}.geojson`;

          const finalPath =
            `/data/${cityKey}/${yFrom}_${yTo}_final.geojson`;

          return fetch(staticPath)
            .then((r) => {
              if (r.ok) {
                return r.json();
              }

              return fetch(finalPath).then((r2) => {
                if (r2.ok) {
                  return r2.json();
                }

                return null;
              });
            })
            .catch(() => null);
        });

        Promise.all(fetchPromises)
          .then((results) => {
            const validCollections = results.filter(
              (res) =>
                res &&
                res.features &&
                res.features.length > 0
            );

            if (validCollections.length === 0) {
              setPolygons(null);
              setIsPending(true);

              setStatusMessage(
                `Satellite analysis for ${city} (${startYear} → ${endYear}) is not available yet.`
              );
            } else {
              const combinedFeatures = [];

              validCollections.forEach((coll) => {
                combinedFeatures.push(...coll.features);
              });

              setPolygons({
                type: "FeatureCollection",
                features: combinedFeatures
              });

              setIsPending(false);
              setStatusMessage("");
            }
          })

          .catch(() => {
            setPolygons(null);
            setIsPending(true);

            setStatusMessage(
              `Satellite analysis for ${city} (${startYear} → ${endYear}) is not available yet.`
            );
          });
      })

      .finally(() => {
        setLoading(false);
      });
  }, [city, startYear, endYear]);

  function getCategoryColor(category) {
    if (category === "New Buildings") return "#e74c3c";
    if (category === "New Roads") return "#e67e22";
    if (category === "Vegetation Change") return "#2ecc71";
    if (category === "Water Body Change") return "#3498db";

    if (category === "Agricultural / Land-use Change") {
      return "#f1c40f";
    }

    return "#95a5a6";
  }

  function polygonStyle(feature) {
    const category = feature.properties
      ? feature.properties.category
      : "Unclassified";

    const color = getCategoryColor(category);

    return {
      color: color,
      weight: 1.8,
      fillColor: color,
      fillOpacity: 0.35
    };
  }

  function onEachPolygon(feature, layer) {
    const props = feature.properties || {};

    const category =
      props.category || "Unclassified";

    const confidence =
      props.confidence || "Low";

    const area =
      props.area_m2
        ? formatArea(props.area_m2)
        : "N/A";

    const lat =
      props.latitude
        ? props.latitude.toFixed(4)
        : "N/A";

    const lon =
      props.longitude
        ? props.longitude.toFixed(4)
        : "N/A";

    const yearFrom =
      props.year_from || startYear;

    const yearTo =
      props.year_to || endYear;

    layer.bindPopup(
      "<div style='font-family:sans-serif; min-width:175px; color:#0f172a;'>" +
        "<h3 style='margin:0 0 6px 0; color:#0f172a; font-size:14px; font-weight:bold; border-bottom:1px solid #cbd5e1; padding-bottom:4px;'>Change Information</h3>" +
        "<b>Category:</b> <span style='color:" +
        getCategoryColor(category) +
        "; font-weight:bold;'>" +
        category +
        "</span><br />" +
        "<b>Confidence:</b> " +
        confidence +
        "<br />" +
        "<b>Area:</b> " +
        area +
        "<br />" +
        "<b>Period:</b> " +
        yearFrom +
        " → " +
        yearTo +
        "<br />" +
        "<b>Latitude:</b> " +
        lat +
        "<br />" +
        "<b>Longitude:</b> " +
        lon +
        "</div>",
      {
        autoPan: false
      }
    );
  }

  const filteredPolygons =
    polygons && polygons.features
      ? {
          ...polygons,

          features: [...polygons.features]
            .filter((f) => {
              const cat = f.properties
                ? f.properties.category
                : "Unclassified";

              return visibleCategories[cat] !== false;
            })

            .sort(
              (a, b) =>
                (b.properties?.area_m2 || 0) -
                (a.properties?.area_m2 || 0)
            )
        }
      : null;

  const allFeatures =
    polygons && polygons.features
      ? polygons.features
      : [];

  const totalAreaM2 =
    allFeatures.reduce(
      (acc, f) =>
        acc + (f.properties?.area_m2 || 0),
      0
    );

  const totalPolygonsCount =
    allFeatures.length;

  const largestPolygonM2 =
    allFeatures.reduce(
      (max, f) =>
        Math.max(
          max,
          f.properties?.area_m2 || 0
        ),
      0
    );

  const categoryBreakdown = [
    "New Buildings",
    "New Roads",
    "Vegetation Change",
    "Water Body Change",
    "Agricultural / Land-use Change",
    "Unclassified"
  ].map((catName) => {
    const catFeatures =
      allFeatures.filter(
        (f) =>
          (f.properties?.category ||
            "Unclassified") === catName
      );

    const catAreaM2 =
      catFeatures.reduce(
        (acc, f) =>
          acc +
          (f.properties?.area_m2 || 0),
        0
      );

    const pct =
      totalAreaM2 > 0
        ? (
            (catAreaM2 / totalAreaM2) *
            100
          ).toFixed(1)
        : 0;

    return {
      name: catName,
      color: getCategoryColor(catName),
      count: catFeatures.length,
      areaM2: catAreaM2,
      share: pct
    };
  });

  const sortedCats =
    [...categoryBreakdown].sort(
      (a, b) => b.areaM2 - a.areaM2
    );

  const dominantCatObj =
    sortedCats[0];

  const dominantCategory =
    totalPolygonsCount > 0 &&
    dominantCatObj &&
    dominantCatObj.areaM2 > 0
      ? dominantCatObj.name
      : "None";

  const intervalTrendMap = {};

  allFeatures.forEach((f) => {
    const yFrom =
      f.properties?.year_from || startYear;

    const yTo =
      f.properties?.year_to || endYear;

    const label =
      `${yFrom} → ${yTo}`;

    if (!intervalTrendMap[label]) {
      intervalTrendMap[label] = {
        label,
        count: 0,
        areaM2: 0
      };
    }

    intervalTrendMap[label].count += 1;

    intervalTrendMap[label].areaM2 +=
      f.properties?.area_m2 || 0;
  });

  const intervalTrends =
    Object.values(intervalTrendMap);

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "20px",
        width: "100%",
        fontFamily: "sans-serif"
      }}
    >
      {/* TOP CONTROLS BAR */}

      <div
        style={{
          background: "rgba(15, 23, 42, 0.95)",
          padding: "16px 20px",
          borderRadius: "10px",
          border:
            "1px solid rgba(255, 255, 255, 0.12)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "14px"
        }}
      >
        <div
          style={{
            display: "flex",
            gap: "16px",
            alignItems: "center",
            flexWrap: "wrap"
          }}
        >
          <div>
            <label
              style={{
                fontSize: "11px",
                fontWeight: "bold",
                display: "block",
                marginBottom: "4px",
                color: "#94a3b8"
              }}
            >
              CITY:
            </label>

            <select
              value={city}
              onChange={(e) =>
                setCity(e.target.value)
              }
              style={{
                padding: "8px 12px",
                borderRadius: "6px",
                border: "1px solid #334155",
                fontWeight: "bold",
                background: "#1e293b",
                color: "#f8fafc",
                cursor: "pointer"
              }}
            >
              {Object.keys(CITIES).map(
                (c) => (
                  <option
                    key={c}
                    value={c}
                  >
                    {c}
                  </option>
                )
              )}
            </select>
          </div>

          <div>
            <label
              style={{
                fontSize: "11px",
                fontWeight: "bold",
                display: "block",
                marginBottom: "4px",
                color: "#94a3b8"
              }}
            >
              BEFORE YEAR:
            </label>

            <select
              value={startYear}
              onChange={(e) =>
                handleStartYearChange(
                  e.target.value
                )
              }
              style={{
                padding: "8px 12px",
                borderRadius: "6px",
                border: "1px solid #334155",
                background: "#1e293b",
                color: "#f8fafc",
                cursor: "pointer"
              }}
            >
              {YEARS.map((y) => (
                <option
                  key={y}
                  value={y}
                >
                  {y}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label
              style={{
                fontSize: "11px",
                fontWeight: "bold",
                display: "block",
                marginBottom: "4px",
                color: "#94a3b8"
              }}
            >
              AFTER YEAR:
            </label>

            <select
              value={endYear}
              onChange={(e) =>
                handleEndYearChange(
                  e.target.value
                )
              }
              style={{
                padding: "8px 12px",
                borderRadius: "6px",
                border: "1px solid #334155",
                background: "#1e293b",
                color: "#f8fafc",
                cursor: "pointer"
              }}
            >
              {YEARS.map((y) => (
                <option
                  key={y}
                  value={y}
                >
                  {y}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          {loading && (
            <span
              style={{
                fontSize: "13px",
                color: "#38bdf8",
                fontWeight: "bold"
              }}
            >
              Loading GIS Data...
            </span>
          )}

          {statusMessage && (
            <span
              style={{
                fontSize: "12px",
                fontWeight: "bold",

                color: isPending
                  ? "#fca5a5"
                  : "#fcd34d",

                background: isPending
                  ? "rgba(153, 27, 27, 0.4)"
                  : "rgba(180, 83, 9, 0.4)",

                border: isPending
                  ? "1px solid #ef4444"
                  : "1px solid #f59e0b",

                padding: "6px 12px",
                borderRadius: "6px"
              }}
            >
              {isPending && (
                <strong
                  style={{
                    marginRight: "6px"
                  }}
                >
                  [PENDING]
                </strong>
              )}

              {statusMessage}
            </span>
          )}
        </div>
      </div>

      {/* MAIN CONTENT */}

      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "minmax(0, 65%) minmax(0, 35%)",
          gap: "20px"
        }}
      >
        {/* MAP */}

        <div
          style={{
            height: "540px",
            position: "relative",
            borderRadius: "10px",
            overflow: "hidden",
            border:
              "1px solid rgba(255,255,255,0.12)"
          }}
        >
          {/* CATEGORY FILTER */}

          <div
            style={{
              position: "absolute",
              bottom: "16px",
              left: "12px",
              zIndex: 1000,

              background:
                "rgba(15, 23, 42, 0.92)",

              backdropFilter: "blur(8px)",
              padding: "10px 14px",
              borderRadius: "8px",

              border:
                "1px solid rgba(255, 255, 255, 0.15)",

              color: "#f8fafc",
              fontSize: "11px"
            }}
          >
            <b
              style={{
                display: "block",
                marginBottom: "6px",
                color: "#38bdf8"
              }}
            >
              Category Filters & Legend
            </b>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr",
                gap: "4px"
              }}
            >
              {[
                {
                  name: "New Buildings",
                  color: "#e74c3c"
                },
                {
                  name: "New Roads",
                  color: "#e67e22"
                },
                {
                  name: "Vegetation Change",
                  color: "#2ecc71"
                },
                {
                  name: "Water Body Change",
                  color: "#3498db"
                },
                {
                  name:
                    "Agricultural / Land-use Change",
                  color: "#f1c40f"
                },
                {
                  name: "Unclassified",
                  color: "#95a5a6"
                }
              ].map((cat) => (
                <label
                  key={cat.name}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "6px",
                    cursor: "pointer",
                    userSelect: "none"
                  }}
                >
                  <input
                    type="checkbox"
                    checked={
                      visibleCategories[
                        cat.name
                      ] !== false
                    }
                    onChange={() =>
                      toggleCategory(
                        cat.name
                      )
                    }
                    style={{
                      cursor: "pointer"
                    }}
                  />

                  <span
                    style={{
                      width: "10px",
                      height: "10px",
                      background:
                        cat.color,
                      borderRadius: "2px",
                      display: "inline-block"
                    }}
                  ></span>

                  <span
                    style={{
                      opacity:
                        visibleCategories[
                          cat.name
                        ] !== false
                          ? 1
                          : 0.4
                    }}
                  >
                    {cat.name}
                  </span>
                </label>
              ))}
            </div>
          </div>

          <MapContainer
            center={
              currentCityConfig.center
            }
            zoom={
              currentCityConfig.zoom
            }
            maxZoom={19}
            style={{
              height: "100%",
              width: "100%"
            }}
          >
            <MapRecenter
              center={
                currentCityConfig.center
              }
              zoom={
                currentCityConfig.zoom
              }
              city={city}
            />

            <LayersControl position="topright">
              <LayersControl.BaseLayer
                checked
                name="Satellite Base (Esri)"
              >
                <TileLayer
                  attribution="Tiles &copy; Esri"
                  url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                  maxZoom={19}
                />
              </LayersControl.BaseLayer>

              <LayersControl.BaseLayer
                name="Street Map (OSM)"
              >
                <TileLayer
                  attribution="&copy; OpenStreetMap contributors"
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  maxZoom={19}
                />
              </LayersControl.BaseLayer>

              {filteredPolygons &&
                filteredPolygons.features &&
                !isPending && (
                  <LayersControl.Overlay
                    checked
                    name="Detected Change Polygons"
                  >
                    <GeoJSON
                      key={`${city}-${startYear}-${endYear}-${filteredPolygons.features.length}-${JSON.stringify(
                        visibleCategories
                      )}`}
                      data={
                        filteredPolygons
                      }
                      style={
                        polygonStyle
                      }
                      onEachFeature={
                        onEachPolygon
                      }
                    />
                  </LayersControl.Overlay>
                )}

              {city === "Delhi" && (
                <>
                  <LayersControl.Overlay
                    name={`Before Image (${startYear} Sentinel-2)`}
                  >
                    <ImageOverlay
                      url={
                        beforeImage
                      }
                      bounds={
                        DELHI_BOUNDS
                      }
                      opacity={0.7}
                    />
                  </LayersControl.Overlay>

                  <LayersControl.Overlay
                    name={`After Image (${endYear} Sentinel-2)`}
                  >
                    <ImageOverlay
                      url={
                        afterImage
                      }
                      bounds={
                        DELHI_BOUNDS
                      }
                      opacity={0.7}
                    />
                  </LayersControl.Overlay>
                </>
              )}
            </LayersControl>
          </MapContainer>
        </div>

        {/* ANALYTICS */}

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "12px",
            height: "540px",
            justifyContent:
              "space-between"
          }}
        >
          <div
            style={{
              background: "#0b1329",
              padding: "18px",
              borderRadius: "10px",
              border:
                "1px solid rgba(255,255,255,0.1)",
              flex: 1,
              display: "flex",
              flexDirection: "column",
              justifyContent: "center"
            }}
          >
            <span
              style={{
                fontSize: "0.75rem",
                color: "#94a3b8",
                fontWeight: "bold",
                letterSpacing:
                  "0.05em"
              }}
            >
              TOTAL CHANGED AREA
            </span>

            <div
              style={{
                fontSize: "1.6rem",
                fontWeight: "bold",
                color: "#38bdf8",
                marginTop: "4px"
              }}
            >
              {isPending
                ? "N/A"
                : formatArea(
                    totalAreaM2
                  )}
            </div>

            <span
              style={{
                fontSize: "0.75rem",
                color: "#64748b",
                marginTop: "4px"
              }}
            >
              Sum of `area_m2` for{" "}
              {city}
            </span>
          </div>

          <div
            style={{
              background: "#0b1329",
              padding: "18px",
              borderRadius: "10px",
              border:
                "1px solid rgba(255,255,255,0.1)",
              flex: 1,
              display: "flex",
              flexDirection: "column",
              justifyContent: "center"
            }}
          >
            <span
              style={{
                fontSize: "0.75rem",
                color: "#94a3b8",
                fontWeight: "bold",
                letterSpacing:
                  "0.05em"
              }}
            >
              TOTAL DETECTED POLYGONS
            </span>

            <div
              style={{
                fontSize: "1.6rem",
                fontWeight: "bold",
                color: "#4ade80",
                marginTop: "4px"
              }}
            >
              {isPending
                ? "0"
                : totalPolygonsCount.toLocaleString()}
            </div>

            <span
              style={{
                fontSize: "0.75rem",
                color: "#64748b",
                marginTop: "4px"
              }}
            >
              Detected vector shapes
            </span>
          </div>

          <div
            style={{
              background: "#0b1329",
              padding: "18px",
              borderRadius: "10px",
              border:
                "1px solid rgba(255,255,255,0.1)",
              flex: 1,
              display: "flex",
              flexDirection: "column",
              justifyContent: "center"
            }}
          >
            <span
              style={{
                fontSize: "0.75rem",
                color: "#94a3b8",
                fontWeight: "bold",
                letterSpacing:
                  "0.05em"
              }}
            >
              LARGEST POLYGON AREA
            </span>

            <div
              style={{
                fontSize: "1.6rem",
                fontWeight: "bold",
                color: "#facc15",
                marginTop: "4px"
              }}
            >
              {isPending
                ? "N/A"
                : formatArea(
                    largestPolygonM2
                  )}
            </div>

            <span
              style={{
                fontSize: "0.75rem",
                color: "#64748b",
                marginTop: "4px"
              }}
            >
              Maximum single change
              feature
            </span>
          </div>

          <div
            style={{
              background: "#0b1329",
              padding: "18px",
              borderRadius: "10px",
              border:
                "1px solid rgba(255,255,255,0.1)",
              flex: 1,
              display: "flex",
              flexDirection: "column",
              justifyContent: "center"
            }}
          >
            <span
              style={{
                fontSize: "0.75rem",
                color: "#94a3b8",
                fontWeight: "bold",
                letterSpacing:
                  "0.05em"
              }}
            >
              DOMINANT CHANGE CATEGORY
            </span>

            <div
              style={{
                fontSize: "1.25rem",
                fontWeight: "bold",
                color: "#f43f5e",
                marginTop: "4px",
                whiteSpace: "nowrap",
                overflow: "hidden",
                textOverflow:
                  "ellipsis"
              }}
            >
              {isPending
                ? "None"
                : dominantCategory}
            </div>

            <span
              style={{
                fontSize: "0.75rem",
                color: "#64748b",
                marginTop: "4px"
              }}
            >
              Highest cumulative area
              category
            </span>
          </div>
        </div>
      </div>

      {/* TABLES */}

      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "16px"
        }}
      >
        <div
          style={{
            background: "#0b1329",
            borderRadius: "10px",
            padding: "20px",
            border:
              "1px solid rgba(255,255,255,0.1)",
            color: "#f8fafc"
          }}
        >
          <h4
            style={{
              margin: "0 0 14px 0",
              fontSize: "1rem",
              color: "#38bdf8",
              fontWeight: "700"
            }}
          >
            Category-Wise Change
            Distribution — {city} (
            {startYear} → {endYear})
          </h4>

          {isPending ? (
            <div
              style={{
                color: "#f87171",
                fontSize: "0.9rem",
                padding: "10px 0"
              }}
            >
              Satellite analysis for{" "}
              {city} ({startYear} →{" "}
              {endYear}) is not
              available yet.
            </div>
          ) : (
            <div
              style={{
                overflowX: "auto"
              }}
            >
              <table
                style={{
                  width: "100%",
                  borderCollapse:
                    "collapse",
                  fontSize: "0.88rem",
                  textAlign: "left"
                }}
              >
                <thead>
                  <tr
                    style={{
                      borderBottom:
                        "1px solid #334155",
                      color: "#94a3b8",
                      fontSize:
                        "0.78rem"
                    }}
                  >
                    <th
                      style={{
                        padding:
                          "8px 12px"
                      }}
                    >
                      CATEGORY
                    </th>

                    <th
                      style={{
                        padding:
                          "8px 12px"
                      }}
                    >
                      POLYGONS
                    </th>

                    <th
                      style={{
                        padding:
                          "8px 12px"
                      }}
                    >
                      TOTAL AREA
                    </th>

                    <th
                      style={{
                        padding:
                          "8px 12px"
                      }}
                    >
                      AREA SHARE
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {categoryBreakdown.map(
                    (cat) => (
                      <tr
                        key={
                          cat.name
                        }
                        style={{
                          borderBottom:
                            "1px solid rgba(255,255,255,0.05)"
                        }}
                      >
                        <td
                          style={{
                            padding:
                              "10px 12px",
                            display:
                              "flex",
                            alignItems:
                              "center",
                            gap: "8px"
                          }}
                        >
                          <span
                            style={{
                              width:
                                "10px",
                              height:
                                "10px",
                              background:
                                cat.color,
                              borderRadius:
                                "2px",
                              display:
                                "inline-block"
                            }}
                          ></span>

                          <span
                            style={{
                              fontWeight:
                                "500"
                            }}
                          >
                            {
                              cat.name
                            }
                          </span>
                        </td>

                        <td
                          style={{
                            padding:
                              "10px 12px",
                            color:
                              "#cbd5e1"
                          }}
                        >
                          {
                            cat.count
                          }
                        </td>

                        <td
                          style={{
                            padding:
                              "10px 12px",
                            fontWeight:
                              "bold",
                            color:
                              "#f8fafc"
                          }}
                        >
                          {formatArea(
                            cat.areaM2
                          )}
                        </td>

                        <td
                          style={{
                            padding:
                              "10px 12px",
                            width: "35%"
                          }}
                        >
                          <div
                            style={{
                              display:
                                "flex",
                              alignItems:
                                "center",
                              gap: "10px"
                            }}
                          >
                            <div
                              style={{
                                flex: 1,
                                height:
                                  "8px",
                                background:
                                  "#0f172a",
                                borderRadius:
                                  "4px",
                                overflow:
                                  "hidden"
                              }}
                            >
                              <div
                                style={{
                                  width: `${cat.share}%`,
                                  height:
                                    "100%",
                                  background:
                                    cat.color,
                                  borderRadius:
                                    "4px"
                                }}
                              ></div>
                            </div>

                            <span
                              style={{
                                fontSize:
                                  "0.8rem",
                                color:
                                  "#94a3b8",
                                minWidth:
                                  "42px"
                              }}
                            >
                              {
                                cat.share
                              }
                              %
                            </span>
                          </div>
                        </td>
                      </tr>
                    )
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* MULTI YEAR TREND */}

        {intervalTrends.length >
          1 &&
          !isPending && (
            <div
              style={{
                background:
                  "#0b1329",
                borderRadius: "10px",
                padding: "20px",
                border:
                  "1px solid rgba(255,255,255,0.1)",
                color: "#f8fafc"
              }}
            >
              <h4
                style={{
                  margin:
                    "0 0 14px 0",
                  fontSize: "1rem",
                  color: "#38bdf8",
                  fontWeight: "700"
                }}
              >
                Multi-Year Interval
                Change Trend (
                {startYear} →{" "}
                {endYear})
              </h4>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns:
                    "repeat(auto-fit, minmax(150px, 1fr))",
                  gap: "12px"
                }}
              >
                {intervalTrends.map(
                  (item) => (
                    <div
                      key={
                        item.label
                      }
                      style={{
                        background:
                          "#1e293b",
                        padding:
                          "14px",
                        borderRadius:
                          "8px",
                        border:
                          "1px solid #334155"
                      }}
                    >
                      <span
                        style={{
                          fontSize:
                            "0.78rem",
                          color:
                            "#38bdf8",
                          fontWeight:
                            "bold"
                        }}
                      >
                        {
                          item.label
                        }
                      </span>

                      <div
                        style={{
                          fontSize:
                            "1.1rem",
                          fontWeight:
                            "bold",
                          marginTop:
                            "4px",
                          color:
                            "#f8fafc"
                        }}
                      >
                        {formatArea(
                          item.areaM2
                        )}
                      </div>

                      <span
                        style={{
                          fontSize:
                            "0.75rem",
                          color:
                            "#94a3b8"
                        }}
                      >
                        {
                          item.count
                        }{" "}
                        polygons
                      </span>
                    </div>
                  )
                )}
              </div>
            </div>
          )}
      </div>
    </div>
  );
}

export default Map;