from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse
import os

from data.locations import LOCATIONS

from services.satellite_service import (
    get_before_after_images,
    search_best_image_for_year
)

from services.download_service import (
    get_product_uuid,
    download_product,
    extract_required_bands
)

from services.preview_service import (
    find_band,
    create_preview,
    create_satellite_preview
)


router = APIRouter(
    prefix="/api/satellite",
    tags=["Satellite Data"]
)


# ============================================================
# GET SATELLITE IMAGES BETWEEN TWO DATES
# ============================================================

@router.get("/images")
def get_satellite_images(
    location: str = Query(...),
    start_date: str = Query(...),
    end_date: str = Query(...),
    max_cloud_cover: float = Query(30)
):

    location_key = location.strip().lower()

    if location_key not in LOCATIONS:

        raise HTTPException(
            status_code=404,
            detail=f"Location '{location}' not supported"
        )

    location_data = LOCATIONS[location_key]

    result = get_before_after_images(
        bbox=location_data["bbox"],
        start_date=start_date,
        end_date=end_date,
        max_cloud_cover=max_cloud_cover
    )

    return {

        "satellite": "Sentinel-2",

        "location": {
            "id": location_key,
            "name": location_data["name"],
            "center": location_data["center"],
            "bbox": location_data["bbox"]
        },

        "date_range": {
            "start": start_date,
            "end": end_date
        },

        "max_cloud_cover": max_cloud_cover,

        "before": result["before"],

        "after": result["after"],

        "count": result["count"]
    }


# ============================================================
# GET BEST SATELLITE IMAGE FOR A YEAR
# ============================================================

@router.get("/year")
def get_satellite_image_for_year(
    location: str = Query(...),
    year: int = Query(...),
    max_cloud_cover: float = Query(30)
):

    location_key = location.strip().lower()

    if location_key not in LOCATIONS:

        raise HTTPException(
            status_code=404,
            detail=f"Location '{location}' not supported"
        )

    if year < 2020 or year > 2026:

        raise HTTPException(
            status_code=400,
            detail="Supported years are 2020 to 2026"
        )

    location_data = LOCATIONS[location_key]

    image = search_best_image_for_year(
        bbox=location_data["bbox"],
        year=year,
        max_cloud_cover=max_cloud_cover
    )

    if image is None:

        return {

            "status": "not_found",

            "location": {
                "id": location_key,
                "name": location_data["name"]
            },

            "year": year,

            "image": None
        }

    return {

        "status": "success",

        "satellite": "Sentinel-2",

        "location": {
            "id": location_key,
            "name": location_data["name"],
            "center": location_data["center"],
            "bbox": location_data["bbox"]
        },

        "year": year,

        "image": image
    }


# ============================================================
# SATELLITE RGB PREVIEW
# ============================================================

@router.get("/preview")
def satellite_image_preview(
    location: str = Query(...),
    year: int = Query(...)
):

    location_key = location.strip().lower()

    # --------------------------------------------------------
    # Validate location
    # --------------------------------------------------------

    if location_key not in LOCATIONS:

        raise HTTPException(
            status_code=404,
            detail=f"Location '{location}' not supported"
        )

    # --------------------------------------------------------
    # Validate year
    # --------------------------------------------------------

    if year < 2020 or year > 2026:

        raise HTTPException(
            status_code=400,
            detail="Supported years are 2020 to 2026"
        )

    # --------------------------------------------------------
    # Output preview path
    # --------------------------------------------------------

    output_path = (
        f"data/images/"
        f"{location_key}_{year}_preview.jpg"
    )

    # --------------------------------------------------------
    # If preview already exists
    # --------------------------------------------------------

    if os.path.exists(output_path):

        print(
            f"Preview already exists: "
            f"{output_path}"
        )

        return FileResponse(
            path=output_path,
            media_type="image/jpeg",
            filename=(
                f"{location_key}_"
                f"{year}_satellite_preview.jpg"
            )
        )

    # --------------------------------------------------------
    # Search Copernicus
    # --------------------------------------------------------

    print(
        f"\nSearching Copernicus for "
        f"{location_key} {year}..."
    )

    location_data = LOCATIONS[location_key]

    image = search_best_image_for_year(
        bbox=location_data["bbox"],
        year=year,
        max_cloud_cover=30
    )

    if image is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"No Sentinel-2 image found "
                f"for {location_key} in {year}"
            )
        )

    print(
        "Best image found:",
        image["id"]
    )

    # --------------------------------------------------------
    # Get Copernicus product
    # --------------------------------------------------------

    product = get_product_uuid(
        image["id"]
    )

    if product is None:

        raise HTTPException(
            status_code=404,
            detail="Copernicus product not found"
        )

    print(
        "Product found:",
        product["name"]
    )

    product_id = product["id"]

    # --------------------------------------------------------
    # Download product
    # --------------------------------------------------------

    zip_path = (
        f"data/images/"
        f"{location_key}_"
        f"{year}_product.zip"
    )

    print(
        "Downloading satellite product..."
    )

    downloaded_file = download_product(
        product_id=product_id,
        output_path=zip_path
    )

    if downloaded_file is None:

        raise HTTPException(
            status_code=500,
            detail="Satellite product download failed"
        )

    # --------------------------------------------------------
    # Extract RGB bands
    # --------------------------------------------------------

    print(
        "Extracting B02, B03 and B04..."
    )

    extracted = extract_required_bands(
        zip_path=zip_path,
        extract_dir="data/images/bands"
    )

    # --------------------------------------------------------
    # Delete ZIP after extraction
    # --------------------------------------------------------

    if os.path.exists(zip_path):

        print(
            "Deleting downloaded ZIP..."
        )

        os.remove(zip_path)

    if not extracted:

        raise HTTPException(
            status_code=500,
            detail=(
                "Required RGB bands "
                "could not be extracted"
            )
        )

    # --------------------------------------------------------
    # Create preview from SAME product
    # --------------------------------------------------------

    print(
        "Creating RGB preview from "
        "selected Copernicus product..."
    )

    result = create_satellite_preview(
        location=location_key,
        year=year,
        product_id=product_id
    )

    if result["status"] != "success":

        raise HTTPException(
            status_code=500,
            detail=result["message"]
        )

    # --------------------------------------------------------
    # Final check
    # --------------------------------------------------------

    if not os.path.exists(output_path):

        raise HTTPException(
            status_code=500,
            detail="Preview image was not created"
        )

    print(
        "Preview ready:",
        output_path
    )

    return FileResponse(
        path=output_path,
        media_type="image/jpeg",
        filename=(
            f"{location_key}_"
            f"{year}_satellite_preview.jpg"
        )
    )


# ============================================================
# DOWNLOAD COMPLETE SATELLITE PRODUCT
# ============================================================

@router.post("/download")
def download_satellite_product(
    location: str = Query(...),
    year: int = Query(...)
):

    location_key = location.strip().lower()

    if location_key not in LOCATIONS:

        raise HTTPException(
            status_code=404,
            detail=f"Location '{location}' not supported"
        )

    if year < 2020 or year > 2026:

        raise HTTPException(
            status_code=400,
            detail="Supported years are 2020 to 2026"
        )

    location_data = LOCATIONS[location_key]

    # --------------------------------------------------------
    # Search best image
    # --------------------------------------------------------

    image = search_best_image_for_year(
        bbox=location_data["bbox"],
        year=year,
        max_cloud_cover=30
    )

    if image is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"No satellite image found "
                f"for {location} in {year}"
            )
        )

    print(
        "Best image:",
        image["id"]
    )

    # --------------------------------------------------------
    # Product
    # --------------------------------------------------------

    product = get_product_uuid(
        image["id"]
    )

    if product is None:

        raise HTTPException(
            status_code=404,
            detail="Copernicus product not found"
        )

    # --------------------------------------------------------
    # Download
    # --------------------------------------------------------

    output_path = (
        f"data/images/"
        f"{location_key}_"
        f"{year}_product.zip"
    )

    downloaded_file = download_product(
        product_id=product["id"],
        output_path=output_path
    )

    if downloaded_file is None:

        raise HTTPException(
            status_code=500,
            detail="Satellite product download failed"
        )

    return {

        "status": "success",

        "location": location_data["name"],

        "year": year,

        "satellite": "Sentinel-2",

        "product": {
            "id": product["id"],
            "name": product["name"],
            "size": product["size"]
        },

        "file": downloaded_file
    }


# ============================================================
# DOWNLOAD FILE TO USER
# ============================================================

@router.get("/download-file")
def download_file(
    location: str = Query(...),
    year: int = Query(...)
):

    location_key = location.strip().lower()

    if location_key not in LOCATIONS:

        raise HTTPException(
            status_code=404,
            detail=f"Location '{location}' not supported"
        )

    if year < 2020 or year > 2026:

        raise HTTPException(
            status_code=400,
            detail="Supported years are 2020 to 2026"
        )

    file_path = (
        f"data/images/"
        f"{location_key}_"
        f"{year}_product.zip"
    )

    if not os.path.exists(file_path):

        raise HTTPException(
            status_code=404,
            detail=(
                "Downloaded satellite file "
                "not found"
            )
        )

    return FileResponse(

        path=file_path,

        media_type="application/zip",

        filename=(
            f"{location_key}_"
            f"{year}_satellite_data.zip"
        )
    )


# ============================================================
# GET SATELLITE RASTER OVERLAY PNG
# ============================================================

@router.get("/rasters/{city}/{year}")
def get_satellite_raster(city: str, year: int):
    city_key = city.strip().lower()
    
    # Locate project root relative to this file
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    
    possible_paths = [
        os.path.join(base_dir, "frontend", "dist", "data", city_key, "rasters", f"{city_key}_{year}.png"),
        os.path.join(base_dir, "frontend", "public", "data", city_key, "rasters", f"{city_key}_{year}.png"),
        os.path.join(base_dir, "output", f"{city_key}_{year}.png"),
        os.path.join(base_dir, "backend", "data", "images", f"{city_key}_{year}_preview.jpg")
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            media_type = "image/png" if path.endswith(".png") else "image/jpeg"
            return FileResponse(path=path, media_type=media_type, filename=os.path.basename(path))
            
    raise HTTPException(
        status_code=404,
        detail=f"Satellite raster overlay for {city.title()} ({year}) is PENDING."
    )
