import os
import rasterio
from rasterio.features import shapes, geometry_mask
import geopandas as gpd
from shapely.geometry import shape
import numpy as np

CITY_METADATA = {
    "delhi": {"name": "Delhi", "center": [28.6139, 77.2090], "zoom": 11, "utm_epsg": 32643, "bbox": [77.15, 28.58, 77.27, 28.68]},
    "mumbai": {"name": "Mumbai", "center": [19.0760, 72.8777], "zoom": 11, "utm_epsg": 32643, "bbox": [72.70, 18.85, 73.10, 19.30]},
    "bengaluru": {"name": "Bengaluru", "center": [12.9716, 77.5946], "zoom": 11, "utm_epsg": 32643, "bbox": [77.35, 12.80, 77.80, 13.15]},
    "hyderabad": {"name": "Hyderabad", "center": [17.3850, 78.4867], "zoom": 11, "utm_epsg": 32644, "bbox": [78.25, 17.20, 78.70, 17.60]},
    "chennai": {"name": "Chennai", "center": [13.0827, 80.2707], "zoom": 11, "utm_epsg": 32644, "bbox": [80.05, 12.90, 80.40, 13.25]}
}


def compute_index(num, denom):
    with np.errstate(divide='ignore', invalid='ignore'):
        idx = np.where(denom == 0, 0.0, num / denom)
        idx = np.nan_to_num(idx, nan=0.0, posinf=0.0, neginf=0.0)
    return idx.astype(np.float32)


def classify_polygon(d_ndvi, d_ndwi, d_ndbi):
    abs_ndvi = abs(d_ndvi)
    abs_ndwi = abs(d_ndwi)
    abs_ndbi = abs(d_ndbi)

    # New Buildings & New Roads
    if d_ndbi > 0.10 and abs_ndbi >= abs_ndwi:
        if d_ndvi < 0:
            confidence = "High" if (d_ndbi > 0.15 and d_ndvi < -0.05) else "Medium"
            return "New Buildings", confidence
        else:
            confidence = "Medium" if d_ndbi > 0.12 else "Low"
            return "New Roads", confidence

    max_idx = max(abs_ndvi, abs_ndwi, abs_ndbi)

    # Water Body Change
    if abs_ndwi > 0.12 and abs_ndwi == max_idx and (abs_ndwi - abs_ndvi) > 0.02:
        confidence = "High" if abs_ndwi > 0.18 else "Medium"
        return "Water Body Change", confidence

    # Vegetation Change
    if abs_ndvi > 0.12 and abs_ndvi == max_idx and (abs_ndvi - abs_ndwi) > 0.02:
        confidence = "High" if abs_ndvi > 0.20 else "Medium"
        return "Vegetation Change", confidence

    # Agricultural / Land-use Change
    if max_idx > 0.06:
        return "Agricultural / Land-use Change", "Low"

    return "Unclassified", "Low"


def run_gis_analysis(city, year_from, year_to):
    """
    Runs multi-spectral change detection analysis for a given city and year pair.
    Returns GeoDataFrame or None if input satellite rasters are missing.
    """
    city_key = city.lower()
    if city_key not in CITY_METADATA:
        return None

    possible_from_paths = [
        f"data/{city_key}/{year_from}/{city_key}_{year_from}_multispectral.tif",
        f"data/{city_key}/{year_from}/{city_key}_{year_from}_multispectral.tif"
    ]
    possible_to_paths = [
        f"data/{city_key}/{year_to}/{city_key}_{year_to}_multispectral.tif",
        f"data/{city_key}/{year_to}/{city_key}_{year_to}_multispectral.tif"
    ]

    ms_from_path = next((p for p in possible_from_paths if os.path.exists(p)), None)
    ms_to_path = next((p for p in possible_to_paths if os.path.exists(p)), None)

    if not ms_from_path or not ms_to_path:
        return None

    with rasterio.open(ms_from_path) as src_from, rasterio.open(ms_to_path) as src_to:
        b03_from = src_from.read(2).astype(np.float32)
        b04_from = src_from.read(3).astype(np.float32)
        b08_from = src_from.read(4).astype(np.float32)
        b11_from = src_from.read(5).astype(np.float32)

        b03_to = src_to.read(2).astype(np.float32)
        b04_to = src_to.read(3).astype(np.float32)
        b08_to = src_to.read(4).astype(np.float32)
        b11_to = src_to.read(5).astype(np.float32)

        crs = src_from.crs
        transform = src_from.transform

    ndvi_from = compute_index(b08_from - b04_from, b08_from + b04_from)
    ndvi_to = compute_index(b08_to - b04_to, b08_to + b04_to)

    ndwi_from = compute_index(b03_from - b08_from, b03_from + b08_from)
    ndwi_to = compute_index(b03_to - b08_to, b03_to + b08_to)

    ndbi_from = compute_index(b11_from - b08_from, b11_from + b08_from)
    ndbi_to = compute_index(b11_to - b08_to, b11_to + b08_to)

    d_ndvi = ndvi_to - ndvi_from
    d_ndwi = ndwi_to - ndwi_from
    d_ndbi = ndbi_to - ndbi_from

    change_score = np.abs(d_ndvi) + np.abs(d_ndwi) + np.abs(d_ndbi)
    mask = (change_score > 0.25).astype(np.uint8)

    results = shapes(mask, mask=mask == 1, transform=transform)
    polygons = [shape(geom) for geom, val in results if val == 1]

    if not polygons:
        return None

    gdf = gpd.GeoDataFrame({"geometry": polygons}, crs=crs)

    utm_epsg = CITY_METADATA[city_key]["utm_epsg"]
    gdf_utm = gdf.to_crs(epsg=utm_epsg)
    gdf["area_m2"] = gdf_utm.geometry.area

    # MMU filtering (>= 2000 m2)
    gdf = gdf[gdf["area_m2"] >= 2000].copy()
    if gdf.empty:
        return None

    gdf["latitude"] = gdf.geometry.centroid.y
    gdf["longitude"] = gdf.geometry.centroid.x

    categories, confidences = [], []
    for idx, row in gdf.iterrows():
        try:
            poly_mask = geometry_mask([row.geometry], transform=transform, invert=True, out_shape=d_ndvi.shape)
            valid_ndvi = d_ndvi[poly_mask]
            valid_ndwi = d_ndwi[poly_mask]
            valid_ndbi = d_ndbi[poly_mask]

            m_d_ndvi = float(np.mean(valid_ndvi[np.isfinite(valid_ndvi)])) if len(valid_ndvi) > 0 else 0.0
            m_d_ndwi = float(np.mean(valid_ndwi[np.isfinite(valid_ndwi)])) if len(valid_ndwi) > 0 else 0.0
            m_d_ndbi = float(np.mean(valid_ndbi[np.isfinite(valid_ndbi)])) if len(valid_ndbi) > 0 else 0.0
        except Exception:
            m_d_ndvi, m_d_ndwi, m_d_ndbi = 0.0, 0.0, 0.0

        cat, conf = classify_polygon(m_d_ndvi, m_d_ndwi, m_d_ndbi)
        categories.append(cat)
        confidences.append(conf)

    gdf["city"] = city.title()
    gdf["year_from"] = int(year_from)
    gdf["year_to"] = int(year_to)
    gdf["category"] = categories
    gdf["confidence"] = confidences

    return gdf
