# FRONTEND API CONTRACT

**Project:** SIH26227 — *Semantic Retrieval and Multi-Temporal Change Analysis of Satellite Imagery*  
**Base URL:** `http://localhost:8000`

---

## 1. Overview & Important Integration Guidelines

This document outlines the API contract between the FastAPI backend (`Backend/main.py`) and the React + Leaflet map interface.

### Critical Notes for Frontend Developer:
1. **Rule-Based Classification**: Current land cover classification is **RULE-BASED** using multi-spectral index deltas ($\Delta\text{NDVI}, \Delta\text{NDWI}, \Delta\text{NDBI}$), NOT trained ML models.
2. **Consecutive Year-Range Analysis**: Selecting `2020 -> 2026` does **NOT** subtract 2026 image from 2020 image directly. It queries consecutive annual comparisons (`2020->2021`, `2021->2022`, ..., `2025->2026`) and aggregates all features into a single FeatureCollection. Every polygon preserves its exact `year_from` and `year_to` properties.
3. **Data Availability (`PENDING` Status)**: Currently, **Delhi (2020–2026)** contains fully processed real Sentinel-2 change records (9,411 polygons across 6 consecutive pairs). Other cities (`Mumbai`, `Bengaluru`, `Hyderabad`, `Chennai`) return `status: "PENDING"` with zero features. **No fake or dummy data is ever generated**.

---

## 2. API Endpoints

### 1. GET `/api/locations` (or `/api/cities`)
Returns supported city metadata for map initialization.

* **Response**:
```json
[
  {
    "id": "delhi",
    "name": "Delhi",
    "center": [28.6139, 77.2090],
    "zoom": 11,
    "bbox": [77.15, 28.58, 77.27, 28.68]
  },
  {
    "id": "mumbai",
    "name": "Mumbai",
    "center": [19.0760, 72.8777],
    "zoom": 11,
    "bbox": [72.70, 18.85, 73.10, 19.30]
  }
]
```

---

### 2. GET `/api/comparisons`
Returns supported annual comparison intervals.

* **Response**:
```json
[
  "2020 → 2021",
  "2021 → 2022",
  "2022 → 2023",
  "2023 → 2024",
  "2024 → 2025",
  "2025 → 2026"
]
```

---

### 3. GET `/api/changes`
Queries change polygons for a single year pair.

* **Query Parameters**:
  * `city` (string, optional, default: `"Delhi"`)
  * `year_from` (int, optional, default: `2021`)
  * `year_to` (int, optional, default: `2022`)
* **Example Request**:
  `GET http://localhost:8000/api/changes?city=Delhi&year_from=2024&year_to=2025`

* **Response (GeoJSON FeatureCollection)**:
```json
{
  "type": "FeatureCollection",
  "status": "success",
  "count": 2132,
  "city": "Delhi",
  "year_from": 2024,
  "year_to": 2025,
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[77.185, 28.621], [77.189, 28.621], [77.189, 28.625], [77.185, 28.625], [77.185, 28.621]]]
      },
      "properties": {
        "id": 3529,
        "city": "Delhi",
        "year_from": 2024,
        "year_to": 2025,
        "category": "New Buildings",
        "confidence": "High",
        "area_m2": 3450.50,
        "latitude": 28.623,
        "longitude": 77.187
      }
    }
  ]
}
```

---

### 4. GET `/api/changes/range`
Queries consecutive multi-year range comparisons (e.g. `2020 -> 2026`).

* **Query Parameters**:
  * `city` (string, optional, default: `"Delhi"`)
  * `start` (int, optional, default: `2020`)
  * `end` (int, optional, default: `2026`)
* **Example Request**:
  `GET http://localhost:8000/api/changes/range?city=Delhi&start=2020&end=2026`

* **Response**:
```json
{
  "type": "FeatureCollection",
  "status": "success",
  "count": 9411,
  "city": "Delhi",
  "range": "2020 -> 2026",
  "consecutive_comparisons": [
    { "comparison": "2020 -> 2021", "status": "READY", "count": 1192 },
    { "comparison": "2021 -> 2022", "status": "READY", "count": 93 },
    { "comparison": "2022 -> 2023", "status": "READY", "count": 52 },
    { "comparison": "2023 -> 2024", "status": "READY", "count": 2280 },
    { "comparison": "2024 -> 2025", "status": "READY", "count": 2132 },
    { "comparison": "2025 -> 2026", "status": "READY", "count": 3662 }
  ],
  "features": [...]
}
```

---

### 5. GET `/api/rasters/{city}/{year}`
Streams PNG raster overlay images for Sentinel-2 satellite visualization on Leaflet.

* **Example Request**:
  `GET http://localhost:8000/api/rasters/delhi/2024`
* **Response**: Binary PNG stream (`image/png`).

---

## 3. Land Cover Categories & Confidence Values

### Standard Categories:
1. `New Buildings`
2. `New Roads`
3. `Vegetation Change`
4. `Water Body Change`
5. `Agricultural / Land-use Change`
6. `Unclassified`

### Confidence Levels:
* `High`
* `Medium`
* `Low`

---

## 4. Leaflet Integration Example (JavaScript)

```javascript
// Fetch range change polygons
fetch('http://localhost:8000/api/changes/range?city=Delhi&start=2020&end=2026')
  .then(res => res.json())
  .then(geojson => {
    if (geojson.status === 'PENDING') {
      alert('Data for this region is currently PENDING processing.');
      return;
    }
    L.geoJSON(geojson, {
      style: (feature) => ({
        color: getColorForCategory(feature.properties.category),
        weight: 2,
        fillOpacity: 0.5
      }),
      onEachFeature: (feature, layer) => {
        layer.bindPopup(`
          <b>Category:</b> ${feature.properties.category}<br/>
          <b>Confidence:</b> ${feature.properties.confidence}<br/>
          <b>Area:</b> ${feature.properties.area_m2.toFixed(1)} m²<br/>
          <b>Interval:</b> ${feature.properties.year_from} → ${feature.properties.year_to}
        `);
      }
    }).addTo(map);
  });
```
