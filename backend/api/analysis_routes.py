from fastapi import APIRouter, HTTPException, Query
import cv2
import os
import numpy as np
import re
import glob
import rasterio

from data.locations import LOCATIONS

from services.change_detection_service import (
    detect_changes,
    classify_change
)

from services.geojson_service import (
    mask_to_geojson
)

from services.ndvi_service import (
    calculate_ndvi_difference,
    classify_vegetation_change
)


router = APIRouter(
    prefix="/api",
    tags=["Analysis"]
)


# ==========================================
# Temporary Analysis Storage
# ==========================================

analysis_results = {}

analysis_counter = 1


# ==========================================
# Find NDVI Bands
# ==========================================

def find_band(location_key, year, band_name):

    pattern = (
        f"data/images/bands/"
        f"**/*B{band_name}_10m.jp2"
    )

    files = glob.glob(
        pattern,
        recursive=True
    )

    for file in files:

        filename = os.path.basename(file)

        if (
            str(year) in filename
            and f"B{band_name}_10m" in filename
        ):
            return file

    return None


# ==========================================
# Calculate NDVI Difference
# ==========================================

def calculate_real_ndvi(
    location_key,
    before_year,
    after_year
):

    before_red_file = find_band(
        location_key,
        before_year,
        "04"
    )

    before_nir_file = find_band(
        location_key,
        before_year,
        "08"
    )

    after_red_file = find_band(
        location_key,
        after_year,
        "04"
    )

    after_nir_file = find_band(
        location_key,
        after_year,
        "08"
    )

    # Both years ke bands available nahi hain
    if not all([
        before_red_file,
        before_nir_file,
        after_red_file,
        after_nir_file
    ]):

        return {
            "status": "not_available",
            "message": (
                "NDVI requires B04 and B08 bands "
                "for both before and after years."
            )
        }

    # Same small crop process karenge
    window = rasterio.windows.Window(
        col_off=4000,
        row_off=4000,
        width=2000,
        height=2000
    )

    with rasterio.open(before_red_file) as src:
        before_red = src.read(
            1,
            window=window
        )

    with rasterio.open(before_nir_file) as src:
        before_nir = src.read(
            1,
            window=window
        )

    with rasterio.open(after_red_file) as src:
        after_red = src.read(
            1,
            window=window
        )

    with rasterio.open(after_nir_file) as src:
        after_nir = src.read(
            1,
            window=window
        )

    ndvi_result = calculate_ndvi_difference(
        before_red=before_red,
        before_nir=before_nir,
        after_red=after_red,
        after_nir=after_nir
    )

    vegetation_result = classify_vegetation_change(
        ndvi_result["ndvi_difference"]
    )

    return {
        "status": "success",

        "before_mean": round(
            float(
                np.mean(
                    ndvi_result["before_ndvi"]
                )
            ),
            4
        ),

        "after_mean": round(
            float(
                np.mean(
                    ndvi_result["after_ndvi"]
                )
            ),
            4
        ),

        "difference_mean": (
            vegetation_result[
                "mean_ndvi_difference"
            ]
        ),

        "change_type": (
            vegetation_result[
                "change_type"
            ]
        )
    }


# ==========================================
# Existing Analysis API
# ==========================================

@router.post("/analysis")
def run_analysis(
    location: str = Query("delhi"),
    before_year: int = Query(2024),
    after_year: int = Query(2025)
):

    global analysis_counter

    location_key = location.strip().lower()

    # ==========================================
    # Location Check
    # ==========================================

    if location_key not in LOCATIONS:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Location '{location}' "
                "is not supported"
            )
        )

    location_data = LOCATIONS[location_key]

    # ==========================================
    # Image Paths
    # ==========================================

    before_path = (
        f"data/images/"
        f"{location_key}_{before_year}.jpg"
    )

    after_path = (
        f"data/images/"
        f"{location_key}_{after_year}.jpg"
    )

    # ==========================================
    # Check Before Image
    # ==========================================

    if not os.path.exists(before_path):

        raise HTTPException(
            status_code=404,
            detail=(
                f"Before image not found: "
                f"{before_path}"
            )
        )

    # ==========================================
    # Check After Image
    # ==========================================

    if not os.path.exists(after_path):

        raise HTTPException(
            status_code=404,
            detail=(
                f"After image not found: "
                f"{after_path}"
            )
        )

    # ==========================================
    # Read Images
    # ==========================================

    before = cv2.imread(
        before_path
    )

    after = cv2.imread(
        after_path
    )

    if before is None or after is None:

        raise HTTPException(
            status_code=400,
            detail=(
                "Could not read satellite images"
            )
        )

    # ==========================================
    # Change Detection
    # ==========================================

    result = detect_changes(
        before,
        after
    )

    # ==========================================
    # Change Classification
    # ==========================================

    change_type = classify_change(
        result["change_percentage"]
    )

    # ==========================================
    # Get Change Mask
    # ==========================================

    change_mask = result["change_mask"]

    # ==========================================
    # Save Change Mask
    # ==========================================

    os.makedirs(
        "data/images",
        exist_ok=True
    )

    mask_path = (
        "data/images/change_mask.png"
    )

    cv2.imwrite(
        mask_path,
        change_mask
    )

    # ==========================================
    # Convert Change Mask to GeoJSON
    # ==========================================

    geojson = mask_to_geojson(
        change_mask=change_mask,
        bbox=location_data["bbox"]
    )

    # ==========================================
    # Remove Image Data from JSON
    # ==========================================

    result.pop(
        "change_mask"
    )

    # ==========================================
    # Calculate Area
    # ==========================================

    bbox = location_data["bbox"]

    min_lon, min_lat, max_lon, max_lat = bbox

    center_latitude = (
        location_data["center"][0]
    )

    latitude_km = (
        max_lat - min_lat
    ) * 111

    longitude_km = (
        max_lon - min_lon
    ) * 111 * np.cos(
        np.radians(center_latitude)
    )

    total_area_km2 = (
        latitude_km *
        longitude_km
    )

    changed_area_km2 = (
        total_area_km2
        * result["change_percentage"]
        / 100
    )

    # ==========================================
    # Real NDVI Analysis
    # ==========================================

    ndvi_result = calculate_real_ndvi(
        location_key=location_key,
        before_year=before_year,
        after_year=after_year
    )

    # ==========================================
    # Generate Analysis ID
    # ==========================================

    analysis_id = str(
        analysis_counter
    )

    analysis_counter += 1

    # ==========================================
    # Final Response
    # ==========================================

    response = {

        "status": "success",

        "analysis_id": analysis_id,

        "analysis": {

            "location": (
                location_data["name"]
            ),

            "before": before_year,

            "after": after_year,

            "change_type": change_type,

            "change_percentage": (
                result[
                    "change_percentage"
                ]
            ),

            "changed_pixels": (
                result[
                    "changed_pixels"
                ]
            ),

            "total_pixels": (
                result[
                    "total_pixels"
                ]
            ),

            "total_area_km2": round(
                total_area_km2,
                2
            ),

            "changed_area_km2": round(
                changed_area_km2,
                2
            ),

            "ndvi": ndvi_result
        },

        # ==========================================
        # Images
        # ==========================================

        "images": {

            "before": (
                f"/images/"
                f"{location_key}_{before_year}.jpg"
            ),

            "after": (
                f"/images/"
                f"{location_key}_{after_year}.jpg"
            ),

            "change_mask": (
                "/images/change_mask.png"
            )
        },

        # ==========================================
        # GeoJSON
        # ==========================================

        "geojson": geojson
    }

    # ==========================================
    # Save Analysis Result
    # ==========================================

    analysis_results[
        analysis_id
    ] = response

    return response


# ==========================================
# Get Analysis by ID
# ==========================================

@router.get("/analysis/{analysis_id}")
def get_analysis(
    analysis_id: str
):

    result = analysis_results.get(
        analysis_id
    )

    if result is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Analysis '{analysis_id}' "
                "not found"
            )
        )

    return result


# ==========================================
# Natural Language Analysis API
# ==========================================

@router.post("/analyze-query")
def analyze_query(
    query: str = Query(
        ...,
        description=(
            "Example: Delhi satellite changes "
            "from 2024 to 2025"
        )
    )
):

    # ==========================================
    # Detect Location
    # ==========================================

    query_lower = query.lower()

    detected_location = None

    for location in LOCATIONS:

        if location.lower() in query_lower:

            detected_location = location

            break

    if not detected_location:

        raise HTTPException(
            status_code=400,
            detail=(
                "Location not found. "
                "Try Delhi, Mumbai, Bengaluru, "
                "Hyderabad or Chennai."
            )
        )

    # ==========================================
    # Detect Years
    # ==========================================

    years = re.findall(
        r"\b(2020|2021|2022|2023|2024|2025|2026)\b",
        query
    )

    if len(years) < 2:

        raise HTTPException(
            status_code=400,
            detail=(
                "Please provide two years. "
                "Example: Delhi changes from "
                "2024 to 2025."
            )
        )

    before_year = int(
        years[0]
    )

    after_year = int(
        years[1]
    )

    # ==========================================
    # Validate Year Order
    # ==========================================

    if before_year >= after_year:

        raise HTTPException(
            status_code=400,
            detail=(
                "First year must be earlier "
                "than the second year."
            )
        )

    # ==========================================
    # Run Existing Analysis
    # ==========================================

    result = run_analysis(
        location=detected_location,
        before_year=before_year,
        after_year=after_year
    )

    # ==========================================
    # Add Query Information
    # ==========================================

    result["query"] = query

    result["query_parameters"] = {

        "location": (
            detected_location
        ),

        "before_year": (
            before_year
        ),

        "after_year": (
            after_year
        )
    }

    # ==========================================
    # Update Stored Result
    # ==========================================

    analysis_id = (
        result["analysis_id"]
    )

    analysis_results[
        analysis_id
    ] = result

    return result