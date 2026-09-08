import os
import rasterio
import numpy as np

def compute_index(num, denom):
    """
    Computes a spectral index safely handling division by zero and invalid floats.
    """
    with np.errstate(divide='ignore', invalid='ignore'):
        index = np.where(denom == 0, 0.0, num / denom)
        index = np.nan_to_num(index, nan=0.0, posinf=0.0, neginf=0.0)
    return index.astype(np.float32)


def process_year(year, multispectral_path):
    print(f"\n==========================================")
    print(f"  Processing {year} Spectral Indices")
    print(f"==========================================")
    
    if not os.path.exists(multispectral_path):
        print(f"Error: Multispectral file not found at {multispectral_path}")
        return

    with rasterio.open(multispectral_path) as src:
        b02 = src.read(1).astype(np.float32)  # Blue
        b03 = src.read(2).astype(np.float32)  # Green
        b04 = src.read(3).astype(np.float32)  # Red
        b08 = src.read(4).astype(np.float32)  # NIR
        b11 = src.read(5).astype(np.float32)  # SWIR

        profile = src.profile.copy()
        profile.update(
            dtype=rasterio.float32,
            count=1,
            driver='GTiff'
        )

    # 1. NDVI = (NIR - Red) / (NIR + Red)
    ndvi = compute_index(b08 - b04, b08 + b04)

    # 2. NDWI = (Green - NIR) / (Green + NIR)
    ndwi = compute_index(b03 - b08, b03 + b08)

    # 3. NDBI = (SWIR - NIR) / (SWIR + NIR)
    ndbi = compute_index(b11 - b08, b11 + b08)

    indices = {
        f"output/delhi_{year}_ndvi.tif": ("NDVI", ndvi),
        f"output/delhi_{year}_ndwi.tif": ("NDWI", ndwi),
        f"output/delhi_{year}_ndbi.tif": ("NDBI", ndbi),
    }

    os.makedirs("output", exist_ok=True)

    for out_path, (name, data) in indices.items():
        with rasterio.open(out_path, "w", **profile) as dst:
            dst.write(data, 1)

        min_val = float(np.min(data))
        max_val = float(np.max(data))
        mean_val = float(np.mean(data))

        print(f"\n--- {name} ({year}) ---")
        print(f"File Path: {out_path}")
        print(f"Min Value:  {min_val:.4f}")
        print(f"Max Value:  {max_val:.4f}")
        print(f"Mean Value: {mean_val:.4f}")


def main():
    files = {
        "2021": "data/delhi/2021/delhi_2021_multispectral.tif",
        "2022": "data/delhi/2022/delhi_2022_multispectral.tif"
    }

    for year, path in files.items():
        process_year(year, path)

if __name__ == "__main__":
    main()
