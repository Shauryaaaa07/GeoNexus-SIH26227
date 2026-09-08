import rasterio
import numpy as np


# ==========================================
# Read Raster
# ==========================================

def read_raster(path):
    """
    Satellite raster image read karta hai.

    Returns:
    - data: raster pixel data
    - profile: raster metadata
    """

    with rasterio.open(path) as src:

        data = src.read()
        profile = src.profile

    return data, profile


# ==========================================
# Normalize Raster
# ==========================================

def normalize_raster(data):
    """
    Raster pixel values ko 0-1 range me normalize karta hai.
    """

    data = data.astype(np.float32)

    minimum = np.min(data)
    maximum = np.max(data)

    if maximum == minimum:
        return np.zeros_like(data)

    normalized = (
        data - minimum
    ) / (
        maximum - minimum
    )

    return normalized


# ==========================================
# Get Raster Information
# ==========================================

def get_raster_info(path):
    """
    Raster image ki basic information return karta hai.
    """

    with rasterio.open(path) as src:

        return {
            "width": src.width,
            "height": src.height,
            "bands": src.count,
            "crs": str(src.crs),
            "transform": str(src.transform),
            "dtype": str(src.dtypes[0])
        }