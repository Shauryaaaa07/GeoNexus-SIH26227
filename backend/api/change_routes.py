from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse
import os
import cv2
import json

from data.locations import LOCATIONS
from services.db_service import query_change_records, query_consecutive_range, get_dashboard_stats
from services.preview_service import create_satellite_preview
from services.change_detection_service import detect_changes, classify_change
from services.geojson_service import mask_to_geojson

router = APIRouter(
    prefix="/api",
    tags=["Change Detection"]
)


def records_to_feature_collection(records, city="Delhi", year_from=2021, year_to=2022):
    features = []
    for rec in records:
        try:
            geom = json.loads(rec["geometry"]) if rec["geometry"] else None
        except Exception:
            geom = None

        feature = {
            "type": "Feature",
            "properties": {
                "id": rec["id"],
                "city": rec["city"],
                "year_from": rec["year_from"],
                "year_to": rec["year_to"],
                "category": rec["category"],
                "confidence": rec["confidence"],
                "area_m2": rec["area_m2"],
                "latitude": rec["latitude"],
                "longitude": rec["longitude"]
            },
            "geometry": geom
        }
        features.append(feature)

    status = "success" if features else "PENDING"
    return {
        "type": "FeatureCollection",
        "status": status,
        "count": len(features),
        "city": city,
        "year_from": year_from,
        "year_to": year_to,
        "features": features
    }


@router.get("/changes")
def get_changes(
    city: str = Query(None),
    location: str = Query(None),
    year_from: int = Query(None),
    year_to: int = Query(None),
    start: int = Query(None),
    end: int = Query(None),
    before_year: int = Query(None),
    after_year: int = Query(None)
):
    target_city = city or location or "Delhi"
    y_from = year_from or start or before_year or 2021
    y_to = year_to or end or after_year or 2022

    records = query_change_records(city=target_city, year_from=y_from, year_to=y_to)
    return records_to_feature_collection(records, city=target_city, year_from=y_from, year_to=y_to)


@router.get("/changes/range")
def get_changes_range(
    city: str = Query(None),
    location: str = Query(None),
    start: int = Query(None),
    end: int = Query(None),
    year_from: int = Query(None),
    year_to: int = Query(None)
):
    target_city = city or location or "Delhi"
    start_year = start or year_from or 2020
    end_year = end or year_to or 2026

    if end_year <= start_year:
        end_year = start_year + 1

    return query_consecutive_range(city=target_city, start_year=start_year, end_year=end_year)


@router.get("/changes/geojson")
def get_change_geojson(
    city: str = Query(None),
    location: str = Query(None),
    year_from: int = Query(None),
    year_to: int = Query(None),
    before_year: int = Query(None),
    after_year: int = Query(None)
):
    target_city = city or location or "Delhi"
    y_from = year_from or before_year or 2021
    y_to = year_to or after_year or 2022

    records = query_change_records(city=target_city, year_from=y_from, year_to=y_to)
    if records:
        return records_to_feature_collection(records, city=target_city, year_from=y_from, year_to=y_to)

    # Fallback to change mask if preview mask exists
    mask_path = f"data/images/{target_city.lower()}_{y_from}_{y_to}_change_mask.png"
    if os.path.exists(mask_path):
        change_mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        if change_mask is not None:
            loc_key = target_city.lower()
            bbox = LOCATIONS.get(loc_key, {}).get("bbox", [77.15, 28.58, 77.27, 28.68])
            return mask_to_geojson(change_mask=change_mask, bbox=bbox)

    return {
        "type": "FeatureCollection",
        "status": "PENDING",
        "count": 0,
        "city": target_city,
        "year_from": y_from,
        "year_to": y_to,
        "features": []
    }


@router.get("/changes/mask")
def get_change_mask(
    location: str = Query(None),
    city: str = Query(None),
    before_year: int = Query(None),
    after_year: int = Query(None),
    year_from: int = Query(None),
    year_to: int = Query(None)
):
    location_key = (location or city or "delhi").strip().lower()
    y_from = before_year or year_from or 2021
    y_to = after_year or year_to or 2022

    mask_path = f"data/images/{location_key}_{y_from}_{y_to}_change_mask.png"
    if os.path.exists(mask_path):
        return FileResponse(
            path=mask_path,
            media_type="image/png",
            filename=f"{location_key}_{y_from}_{y_to}_change_mask.png"
        )

    raise HTTPException(
        status_code=404,
        detail=f"Change mask for {location_key} ({y_from} -> {y_to}) not found."
    )


@router.post("/changes")
def detect_satellite_changes(
    location: str = Query(...),
    before_year: int = Query(...),
    after_year: int = Query(...)
):
    location_key = location.strip().lower()
    if location_key not in LOCATIONS:
        raise HTTPException(status_code=404, detail=f"Location '{location}' not supported")

    if before_year >= after_year:
        raise HTTPException(status_code=400, detail="before_year must be smaller than after_year")

    # Query existing database first
    records = query_change_records(city=location_key, year_from=before_year, year_to=after_year)
    if records:
        return {
            "status": "success",
            "location": LOCATIONS[location_key],
            "comparison": {"before_year": before_year, "after_year": after_year},
            "change_count": len(records),
            "geojson_url": f"/api/changes/geojson?location={location_key}&before_year={before_year}&after_year={after_year}"
        }

    # Fallback to preview difference
    before_result = create_satellite_preview(location=location_key, year=before_year)
    after_result = create_satellite_preview(location=location_key, year=after_year)

    if before_result.get("status") != "success" or after_result.get("status") != "success":
        raise HTTPException(status_code=500, detail="Satellite preview images unavailable")

    before_image = cv2.imread(before_result["image"])
    after_image = cv2.imread(after_result["image"])

    result = detect_changes(before_image, after_image)
    change_type = classify_change(result["change_percentage"])

    mask_path = f"data/images/{location_key}_{before_year}_{after_year}_change_mask.png"
    os.makedirs("data/images", exist_ok=True)
    cv2.imwrite(mask_path, result["change_mask"])

    return {
        "status": "success",
        "location": LOCATIONS[location_key],
        "comparison": {"before_year": before_year, "after_year": after_year},
        "change": {
            "percentage": result["change_percentage"],
            "changed_pixels": result["changed_pixels"],
            "classification": change_type
        },
        "change_mask": f"/api/changes/mask?location={location_key}&before_year={before_year}&after_year={after_year}",
        "geojson_url": f"/api/changes/geojson?location={location_key}&before_year={before_year}&after_year={after_year}"
    }

@router.get("/dashboard/stats")
def get_dashboard_statistics(
    city: str = Query(None),
    year_from: int = Query(None),
    year_to: int = Query(None)
):
    return get_dashboard_stats(city=city, year_from=year_from, year_to=year_to)
