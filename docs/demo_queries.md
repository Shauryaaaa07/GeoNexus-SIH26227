# SIH26227 GEONEXUS — DEMO QUERY VERIFICATION RESULTS

This document records the exact, empirical query results directly from the production SQLite database (`database/sih_changes.db`) containing **25,819** Sentinel-2 satellite change polygons for Delhi NCT across the 2020–2026 observation period.

---

## 1. QUERY 1: Show changes in Dwarka from 2021 to 2025

* **Request API:** `GET /api/changes/search?place=Dwarka&year_from=2021&year_to=2025`
* **Filter Criteria:** `locality = 'Dwarka'`, `2021 ≤ year_from`, `year_to ≤ 2025`
* **Matching Polygons:** `681`
* **Sum of Detected Change Areas:** `23,770,100.0 m²` (**23.77 km²**)
* **Intervals Present:** `2021->2022`, `2022->2023`, `2023->2024`, `2024->2025`
* **Primary Change Categories:**
  * `New Buildings`: 403 polygons (15.82 km²)
  * `Water Body Change`: 189 polygons (5.14 km²)
  * `New Roads`: 47 polygons (1.61 km²)
  * `Vegetation Change`: 28 polygons (0.85 km²)
  * `Agricultural / Land-use Change`: 14 polygons (0.35 km²)

---

## 2. QUERY 2: Show new buildings in Rohini from 2024 to 2026

* **Request API:** `GET /api/changes/search?place=Rohini&year_from=2024&year_to=2026&category=New%20Buildings`
* **Filter Criteria:** `locality = 'Rohini'`, `category = 'New Buildings'`, `2024 ≤ year_from`, `year_to ≤ 2026`
* **Matching Polygons:** `194`
* **Sum of Detected Change Areas:** `1,675,800.0 m²` (**1.68 km²**)
* **Intervals Present:** `2024->2025`, `2025->2026`
* **Average Confidence:** `0.885`

---

## 3. QUERY 3: Show vegetation changes in Delhi from 2023 to 2025

* **Request API:** `GET /api/changes/search?place=Delhi&year_from=2023&year_to=2025&category=Vegetation%20Change`
* **Filter Criteria:** `city = 'Delhi'`, `category = 'Vegetation Change'`, `2023 ≤ year_from`, `year_to ≤ 2025`
* **Matching Polygons:** `417`
* **Sum of Detected Change Areas:** `9,185,050.0 m²` (**9.19 km²**)
* **Intervals Present:** `2023->2024`, `2024->2025`
* **Top Localities Affected:** Alipur, Najafgarh, Narela, Rohini, Civil Lines

---

## 4. QUERY 4: Show water body changes in Delhi from 2023 to 2024

* **Request API:** `GET /api/changes/search?place=Delhi&year_from=2023&year_to=2024&category=Water%20Body%20Change`
* **Filter Criteria:** `city = 'Delhi'`, `category = 'Water Body Change'`, `year_from = 2023`, `year_to = 2024`
* **Matching Polygons:** `875`
* **Sum of Detected Change Areas:** `29,461,200.0 m²` (**29.46 km²**)
* **Key Observations:** Covers Yamuna river channel shifts and seasonal retention basins across Delhi NCT.
