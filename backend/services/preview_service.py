import os
import glob

import numpy as np
import rasterio
from rasterio.enums import Resampling
from PIL import Image


# ==========================================
# Find Sentinel-2 Band
# ==========================================

def find_band(year, band_name, product_id=None):
    """
    Sentinel-2 10m band find karta hai.

    B02 = Blue
    B03 = Green
    B04 = Red

    Agar product_id diya gaya hai to EXACT
    same Sentinel-2 product ka band select hoga.
    """

    pattern = (
        f"data/images/bands/"
        f"**/*_{band_name}_10m.jp2"
    )

    files = glob.glob(
        pattern,
        recursive=True
    )

    # --------------------------------------
    # Exact product search
    # --------------------------------------

    if product_id:

        for file_path in files:

            if product_id in file_path:
                return file_path

    # --------------------------------------
    # Fallback: year search
    # --------------------------------------

    for file_path in files:

        if str(year) in file_path:
            return file_path

    return None


# ==========================================
# Normalize Band
# ==========================================

def normalize_band(band):

    band = band.astype(np.float32)

    low = np.percentile(
        band,
        2
    )

    high = np.percentile(
        band,
        98
    )

    if high <= low:

        return np.zeros(
            band.shape,
            dtype=np.uint8
        )

    band = np.clip(
        (band - low) /
        (high - low),
        0,
        1
    )

    return (
        band * 255
    ).astype(
        np.uint8
    )


# ==========================================
# Read Small Preview Band
# ==========================================

def read_preview_band(
    band_path,
    max_size=2000
):

    with rasterio.open(
        band_path
    ) as src:

        original_width = src.width
        original_height = src.height

        scale = min(
            max_size / original_width,
            max_size / original_height,
            1
        )

        new_width = int(
            original_width * scale
        )

        new_height = int(
            original_height * scale
        )

        band = src.read(
            1,
            out_shape=(
                1,
                new_height,
                new_width
            ),
            resampling=Resampling.bilinear
        )

    return band


# ==========================================
# Create RGB Preview
# ==========================================

def create_preview(
    red_path,
    green_path,
    blue_path,
    output_path
):

    print("Reading Red band...")

    red = read_preview_band(
        red_path
    )

    print("Reading Green band...")

    green = read_preview_band(
        green_path
    )

    print("Reading Blue band...")

    blue = read_preview_band(
        blue_path
    )

    print("Normalizing bands...")

    red = normalize_band(red)
    green = normalize_band(green)
    blue = normalize_band(blue)

    print("Creating RGB image...")

    rgb = np.dstack(
        (
            red,
            green,
            blue
        )
    )

    output_folder = os.path.dirname(
        output_path
    )

    if output_folder:

        os.makedirs(
            output_folder,
            exist_ok=True
        )

    image = Image.fromarray(
        rgb
    )

    image.save(
        output_path,
        format="JPEG",
        quality=90
    )

    print(
        "Preview created:",
        output_path
    )

    return output_path


# ==========================================
# Create Satellite Preview
# ==========================================

def create_satellite_preview(
    location,
    year,
    product_id=None
):

    print(
        f"\nCreating satellite preview "
        f"for {location} {year}..."
    )

    # --------------------------------------
    # Find RGB bands
    # --------------------------------------

    red_path = find_band(
        year,
        "B04",
        product_id
    )

    green_path = find_band(
        year,
        "B03",
        product_id
    )

    blue_path = find_band(
        year,
        "B02",
        product_id
    )

    # --------------------------------------
    # Check bands
    # --------------------------------------

    if not red_path:

        return {
            "status": "error",
            "message": f"B04 band not found for {year}"
        }

    if not green_path:

        return {
            "status": "error",
            "message": f"B03 band not found for {year}"
        }

    if not blue_path:

        return {
            "status": "error",
            "message": f"B02 band not found for {year}"
        }

    # --------------------------------------
    # Safety check
    # --------------------------------------

    if product_id:

        paths = [
            red_path,
            green_path,
            blue_path
        ]

        for path in paths:

            if product_id not in path:

                return {
                    "status": "error",
                    "message": (
                        f"RGB bands are not from the "
                        f"same Copernicus product for {year}"
                    )
                }

    print("Red:", red_path)
    print("Green:", green_path)
    print("Blue:", blue_path)

    # --------------------------------------
    # Output
    # --------------------------------------

    output_path = (
        f"data/images/"
        f"{location}_{year}_preview.jpg"
    )

    # --------------------------------------
    # Create preview
    # --------------------------------------

    try:

        create_preview(
            red_path=red_path,
            green_path=green_path,
            blue_path=blue_path,
            output_path=output_path
        )

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }

    return {
        "status": "success",
        "location": location,
        "year": year,
        "product_id": product_id,
        "image": output_path
    }