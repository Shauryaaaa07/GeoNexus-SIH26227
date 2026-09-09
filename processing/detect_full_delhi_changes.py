import os
import json
import numpy as np
from pathlib import Path
import rasterio
import geopandas as gpd
from shapely.geometry import Polygon, Point, mapping
import cv2

BASE_DIR = Path(r"C:\Users\shaur\OneDrive\Desktop\GeoNexus-SIH26227")
PROCESSED_DIR = BASE_DIR / "processing" / "data" / "processed" / "delhi"
BOUND_FILE = BASE_DIR / "processing" / "data" / "boundaries" / "delhi_nct.geojson"
LOCALITY_FILE = BASE_DIR / "processing" / "data" / "boundaries" / "delhi_localities.geojson"
OUT_JSON = BASE_DIR / "processing" / "data" / "delhi_change_polygons.json"

# Load Delhi locality boundaries for spatial join
gdf_localities = gpd.read_file(LOCALITY_FILE).to_crs(epsg=4326)

INTERVALS = [
    (2020, 2021),
    (2021, 2022),
    (2022, 2023),
    (2023, 2024),
    (2024, 2025),
    (2025, 2026)
]

all_polygons = []
poly_id_counter = 1
kernel_3x3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

for y_from, y_to in INTERVALS:
    dir_from = PROCESSED_DIR / str(y_from)
    dir_to = PROCESSED_DIR / str(y_to)
    
    if not (dir_from / "NDVI.tif").exists() or not (dir_to / "NDVI.tif").exists():
        print(f"Skipping interval {y_from}->{y_to}: Processed rasters missing.", flush=True)
        continue
        
    print(f"Detecting changes for interval {y_from} -> {y_to}...", flush=True)
    
    with rasterio.open(dir_from / "NDVI.tif") as ds_f, rasterio.open(dir_to / "NDVI.tif") as ds_t:
        ndvi_from = ds_f.read(1)
        ndvi_to = ds_t.read(1)
        transform = ds_f.transform
        crs = ds_f.crs

    with rasterio.open(dir_from / "NDWI.tif") as ds_f, rasterio.open(dir_to / "NDWI.tif") as ds_t:
        ndwi_from = ds_f.read(1)
        ndwi_to = ds_t.read(1)

    with rasterio.open(dir_from / "NDBI.tif") as ds_f, rasterio.open(dir_to / "NDBI.tif") as ds_t:
        ndbi_from = ds_f.read(1)
        ndbi_to = ds_t.read(1)

    valid_mask = (ndvi_from > -9000) & (ndvi_to > -9000)
    
    # Calculate scene-relative deltas (median centered to remove seasonal baseline offset)
    raw_d_ndvi = np.where(valid_mask, ndvi_to - ndvi_from, 0.0)
    raw_d_ndwi = np.where(valid_mask, ndwi_to - ndwi_from, 0.0)
    raw_d_ndbi = np.where(valid_mask, ndbi_to - ndbi_from, 0.0)

    med_ndvi = float(np.median(raw_d_ndvi[valid_mask]))
    med_ndwi = float(np.median(raw_d_ndwi[valid_mask]))
    med_ndbi = float(np.median(raw_d_ndbi[valid_mask]))

    d_ndvi = np.where(valid_mask, raw_d_ndvi - med_ndvi, 0.0)
    d_ndwi = np.where(valid_mask, raw_d_ndwi - med_ndwi, 0.0)
    d_ndbi = np.where(valid_mask, raw_d_ndbi - med_ndbi, 0.0)
    
    # Robust Category Masks
    m_buildings = (d_ndbi >= 0.15) & (d_ndvi <= -0.10)
    m_roads = (d_ndbi >= 0.10) & (d_ndbi < 0.16) & (d_ndvi <= -0.08)
    m_veg = np.abs(d_ndvi) >= 0.22
    m_water = np.abs(d_ndwi) >= 0.22
    m_agri = (d_ndvi <= -0.15) & (d_ndbi < 0.10)
    
    change_raster = np.zeros(d_ndvi.shape, dtype=np.uint8)
    change_raster[m_veg] = 3
    change_raster[m_water] = 4
    change_raster[m_agri] = 5
    change_raster[m_roads] = 2
    change_raster[m_buildings] = 1
    
    # 3x3 Morphological Opening
    change_raster = cv2.morphologyEx(change_raster, cv2.MORPH_OPEN, kernel_3x3)

    # OpenCV Contour Vectorization
    raw_geoms = []
    raw_vals = []
    
    binary_mask = (change_raster > 0).astype(np.uint8)
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    a, b, c = transform.a, transform.b, transform.c
    d, e, f = transform.d, transform.e, transform.f

    for cnt in contours:
        if len(cnt) < 3:
            continue
        # Noise filter threshold >= 25 pixels (2,500 m2)
        if cv2.contourArea(cnt) < 25.0:
            continue
            
        pts_px = cnt.reshape(-1, 2) + 0.5
        xs = c + pts_px[:, 0] * a + pts_px[:, 1] * b
        ys = f + pts_px[:, 0] * d + pts_px[:, 1] * e
        pts_utm = np.column_stack([xs, ys])
        
        poly_g = Polygon(pts_utm)
        area_m2 = poly_g.area

        # Filter giant scene artifacts (> 5.0 km2 = 5,000,000 m2)
        if area_m2 > 5_000_000.0:
            continue
        
        rx, ry, rw, rh = cv2.boundingRect(cnt)
        cy, cx = min(change_raster.shape[0]-1, ry + rh//2), min(change_raster.shape[1]-1, rx + rw//2)
        val = change_raster[cy, cx]
        if val == 0:
            val = 3
        raw_geoms.append(poly_g)
        raw_vals.append(int(val))

    if not raw_geoms:
        print(f"  No change polygons >= 2500m2 for {y_from}->{y_to}.", flush=True)
        continue

    # Batch GeoPandas spatial join
    gdf_interval = gpd.GeoDataFrame({"val": raw_vals, "geometry": raw_geoms}, crs=crs)
    gdf_wgs84 = gdf_interval.to_crs(epsg=4326)
    
    gdf_joined = gpd.sjoin(gdf_wgs84, gdf_localities[["locality", "geometry"]], how="left", predicate="intersects")
    gdf_joined = gdf_joined.loc[~gdf_joined.index.duplicated(keep="first")]

    area_m2_arr = gdf_interval.area.values
    perimeter_arr = gdf_interval.length.values
    compactness_arr = (4 * np.pi * area_m2_arr) / (perimeter_arr ** 2 + 1e-6)
    centroids_wgs = gdf_wgs84.centroid.values
    
    mean_ndbi_b = float(np.mean(d_ndbi[m_buildings])) if np.any(m_buildings) else 0.15
    mean_ndbi_r = float(np.mean(d_ndbi[m_roads])) if np.any(m_roads) else 0.12
    mean_ndvi_v = float(np.mean(np.abs(d_ndvi[m_veg]))) if np.any(m_veg) else 0.25
    mean_ndwi_w = float(np.mean(np.abs(d_ndwi[m_water]))) if np.any(m_water) else 0.25
    mean_ndvi_a = float(np.mean(np.abs(d_ndvi[m_agri]))) if np.any(m_agri) else 0.18

    interval_polys = 0
    for idx, (original_idx, row) in enumerate(gdf_joined.iterrows()):
        poly_geom_wgs = row.geometry
        val = int(row["val"])
        area_m2 = float(area_m2_arr[original_idx])
        compactness = float(compactness_arr[original_idx])
        
        centroid = centroids_wgs[original_idx]
        lat, lon = float(centroid.y), float(centroid.x)
        loc_name = str(row["locality"]) if not (isinstance(row["locality"], float) and np.isnan(row["locality"])) else "Unassigned"
        
        if val == 1:
            category = "New Buildings" if compactness >= 0.15 else "New Roads"
            conf = min(0.98, max(0.65, mean_ndbi_b * 2.5 + 0.50))
        elif val == 2:
            category = "New Roads"
            conf = min(0.95, max(0.60, mean_ndbi_r * 2.5 + 0.50))
        elif val == 3:
            category = "Vegetation Change"
            conf = min(0.98, max(0.65, mean_ndvi_v * 2.0 + 0.40))
        elif val == 4:
            category = "Water Body Change"
            conf = min(0.98, max(0.65, mean_ndwi_w * 2.0 + 0.40))
        elif val == 5:
            category = "Agricultural / Land-use Change"
            conf = min(0.92, max(0.55, mean_ndvi_a * 1.8 + 0.45))
        else:
            category = "Unclassified"
            conf = 0.50
            
        record = {
            "id": poly_id_counter,
            "city": "Delhi",
            "year_from": y_from,
            "year_to": y_to,
            "category": category,
            "confidence": round(conf, 3),
            "area_m2": round(area_m2, 1),
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "locality": loc_name,
            "geometry": mapping(poly_geom_wgs)
        }
        all_polygons.append(record)
        poly_id_counter += 1
        interval_polys += 1

    print(f"  Generated {interval_polys} change polygons for {y_from}->{y_to}.", flush=True)

OUT_JSON.write_text(json.dumps({"polygons": all_polygons}, indent=2), encoding="utf-8")
print(f"\n====================================", flush=True)
print(f"TOTAL STABILIZED CHANGE POLYGONS GENERATED: {len(all_polygons)}", flush=True)
print(f"Saved to {OUT_JSON}", flush=True)
