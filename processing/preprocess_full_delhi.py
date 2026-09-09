import os
import json
import numpy as np
from pathlib import Path
import rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
from rasterio.features import geometry_mask
import geopandas as gpd
from PIL import Image

BASE_DIR = Path(r"C:\Users\shaur\OneDrive\Desktop\GeoNexus-SIH26227")
RAW_DIR = BASE_DIR / "processing" / "data" / "raw" / "delhi"
PROCESSED_DIR = BASE_DIR / "processing" / "data" / "processed" / "delhi"
BOUND_FILE = BASE_DIR / "processing" / "data" / "boundaries" / "delhi_nct.geojson"

YEARS = [2020, 2021, 2022, 2023, 2024, 2025, 2026]

# 1. Load Delhi NCT boundary in UTM 43N (EPSG:32643)
gdf_delhi = gpd.read_file(BOUND_FILE).to_crs(epsg=32643)
delhi_shape = [gdf_delhi.geometry.iloc[0]]
minx, miny, maxx, maxy = gdf_delhi.total_bounds

# Add 500m padding to master grid bounding box
grid_minx = np.floor((minx - 500) / 10.0) * 10.0
grid_maxy = np.ceil((maxy + 500) / 10.0) * 10.0
grid_maxx = np.ceil((maxx + 500) / 10.0) * 10.0
grid_miny = np.floor((miny - 500) / 10.0) * 10.0

width = int((grid_maxx - grid_minx) / 10.0)
height = int((grid_maxy - grid_miny) / 10.0)
master_transform = from_origin(grid_minx, grid_maxy, 10.0, 10.0)
master_crs = "EPSG:32643"

print(f"Master Delhi NCT Grid defined:")
print(f"  CRS: {master_crs} | Res: 10.0m x 10.0m")
print(f"  Dimensions: {height} rows x {width} cols ({height * width / 1e6:.2f} Mpix)")
print(f"  Bounds: ({grid_minx}, {grid_miny}, {grid_maxx}, {grid_maxy})\n")

# Create polygon mask (False inside Delhi, True outside)
delhi_mask = geometry_mask(delhi_shape, out_shape=(height, width), transform=master_transform, invert=False)

def reproject_band(src_ds, resampling_alg):
    dst_array = np.zeros((height, width), dtype=np.float32 if resampling_alg == Resampling.bilinear else np.uint8)
    reproject(
        source=rasterio.band(src_ds, 1),
        destination=dst_array,
        src_transform=src_ds.transform,
        src_crs=src_ds.crs,
        dst_transform=master_transform,
        dst_crs=master_crs,
        resampling=resampling_alg
    )
    return dst_array

def save_geotiff(output_path, array, dtype, nodata=None):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(
        output_path,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=1,
        dtype=dtype,
        crs=master_crs,
        transform=master_transform,
        nodata=nodata,
        compress="lzw"
    ) as dst:
        dst.write(array.astype(dtype), 1)

def save_rgb_preview(output_path, b04, b03, b02, mask):
    def norm(band):
        valid = band[~mask & (band > 0)]
        if len(valid) == 0:
            return np.zeros_like(band, dtype=np.uint8)
        p2, p98 = np.percentile(valid, (2, 98))
        clipped = np.clip((band - p2) / (p98 - p2 + 1e-6) * 255.0, 0, 255)
        clipped[mask] = 0
        return clipped.astype(np.uint8)

    r = norm(b04)
    g = norm(b03)
    b = norm(b02)
    rgb = np.dstack([r, g, b])
    img = Image.fromarray(rgb)
    img.save(output_path, quality=90)

for y in YEARS:
    print(f"====================================")
    print(f"PROCESSING YEAR {y}")
    print(f"====================================")
    y_raw_dir = RAW_DIR / str(y)
    y_out_dir = PROCESSED_DIR / str(y)
    y_out_dir.mkdir(parents=True, exist_ok=True)
    
    scene_dirs = [d for d in y_raw_dir.iterdir() if d.is_dir() and (d / "metadata.json").exists()]
    print(f"Found {len(scene_dirs)} scene directories for Year {y}.")
    
    bands_grid = {
        "B02": np.zeros((height, width), dtype=np.float32),
        "B03": np.zeros((height, width), dtype=np.float32),
        "B04": np.zeros((height, width), dtype=np.float32),
        "B08": np.zeros((height, width), dtype=np.float32),
        "B11": np.zeros((height, width), dtype=np.float32),
        "SCL": np.zeros((height, width), dtype=np.uint8),
    }
    
    for sc in scene_dirs:
        print(f"  Mosaicing scene {sc.name}...")
        for b_name in ["B02", "B03", "B04", "B08", "B11"]:
            tif_p = sc / f"{b_name}.tif"
            if tif_p.exists():
                with rasterio.open(tif_p) as ds:
                    arr = reproject_band(ds, Resampling.bilinear)
                    bands_grid[b_name] = np.maximum(bands_grid[b_name], arr)
                    
        scl_p = sc / "SCL.tif"
        if scl_p.exists():
            with rasterio.open(scl_p) as ds_scl:
                scl_arr = reproject_band(ds_scl, Resampling.nearest)
                bands_grid["SCL"] = np.where(bands_grid["SCL"] == 0, scl_arr, bands_grid["SCL"])
                
    # Create Cloud/Shadow Mask from SCL
    # SCL Classes: 3 (Shadow), 8 (Cloud Medium), 9 (Cloud High), 10 (Cirrus), 11 (Snow)
    scl = bands_grid["SCL"]
    cloud_mask = np.isin(scl, [3, 8, 9, 10, 11]) | delhi_mask
    
    # Save optical bands clipped to Delhi NCT
    for b_name in ["B02", "B03", "B04", "B08", "B11"]:
        b_data = bands_grid[b_name]
        b_data[delhi_mask] = 0.0
        save_geotiff(y_out_dir / f"{b_name}.tif", b_data, dtype=np.uint16, nodata=0)
        
    save_geotiff(y_out_dir / "SCL.tif", scl, dtype=np.uint8, nodata=0)
    
    # Compute Spectral Indices
    b02 = bands_grid["B02"].astype(np.float32)
    b03 = bands_grid["B03"].astype(np.float32)
    b04 = bands_grid["B04"].astype(np.float32)
    b08 = bands_grid["B08"].astype(np.float32)
    b11 = bands_grid["B11"].astype(np.float32)
    
    ndvi = (b08 - b04) / (b08 + b04 + 1e-6)
    ndwi = (b03 - b08) / (b03 + b08 + 1e-6)
    ndbi = (b11 - b08) / (b11 + b08 + 1e-6)
    
    # Apply Delhi mask & Cloud mask to index rasters
    index_mask = delhi_mask | cloud_mask | (b08 == 0)
    ndvi[index_mask] = -9999.0
    ndwi[index_mask] = -9999.0
    ndbi[index_mask] = -9999.0
    
    save_geotiff(y_out_dir / "NDVI.tif", ndvi, dtype=np.float32, nodata=-9999.0)
    save_geotiff(y_out_dir / "NDWI.tif", ndwi, dtype=np.float32, nodata=-9999.0)
    save_geotiff(y_out_dir / "NDBI.tif", ndbi, dtype=np.float32, nodata=-9999.0)
    
    # Generate True-Color RGB Preview Image
    save_rgb_preview(y_out_dir / "rgb_preview.jpg", b04, b03, b02, delhi_mask)
    
    valid_ndvi = ndvi[~index_mask]
    print(f"==> Year {y} Preprocessing Complete:")
    print(f"    NDVI Valid Pixels: {len(valid_ndvi)} | Min: {valid_ndvi.min():.4f}, Max: {valid_ndvi.max():.4f}, Mean: {valid_ndvi.mean():.4f}")
    print(f"    Outputs saved in {y_out_dir}\n")

print("ALL YEARS FULL DELHI PREPROCESSING COMPLETE!")
