from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse
import os
import cv2
import json

from data.locations import LOCATIONS
from services.db_service import (
    query_change_records,
    query_consecutive_range,
    get_dashboard_stats,
    search_change_records,
    point_query_change_records,
    bbox_query_change_records,
    paginated_change_records
)

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
                "longitude": rec["longitude"],
                "locality": rec.get("locality", "Delhi NCT")
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


@router.get("/changes/search")
def search_changes(
    place: str = Query(None),
    location: str = Query(None),
    year_from: int = Query(None),
    year_to: int = Query(None),
    before_year: int = Query(None),
    after_year: int = Query(None),
    category: str = Query(None),
    radius_m: float = Query(2000.0),
    confidence: float = Query(None),
    limit: int = Query(500)
):
    target_place = place or location or "Delhi"
    y_from = year_from or before_year
    y_to = year_to or after_year

    return search_change_records(
        place=target_place,
        year_from=y_from,
        year_to=y_to,
        category=category,
        radius_m=radius_m,
        confidence=confidence,
        limit=limit
    )


@router.get("/changes/point")
def query_point(
    lat: float = Query(...),
    lon: float = Query(...),
    radius_m: float = Query(1000.0),
    year_from: int = Query(None),
    year_to: int = Query(None)
):
    return point_query_change_records(
        lat=lat,
        lon=lon,
        radius_m=radius_m,
        year_from=year_from,
        year_to=year_to
    )


@router.get("/changes/bbox")
def query_bbox(
    min_lon: float = Query(...),
    min_lat: float = Query(...),
    max_lon: float = Query(...),
    max_lat: float = Query(...),
    year_from: int = Query(None),
    year_to: int = Query(None),
    category: str = Query(None),
    limit: int = Query(500)
):
    return bbox_query_change_records(
        min_lon=min_lon,
        min_lat=min_lat,
        max_lon=max_lon,
        max_lat=max_lat,
        year_from=year_from,
        year_to=year_to,
        category=category,
        limit=limit
    )


@router.get("/changes/records")
def get_change_records_paginated(
    page: int = Query(1),
    limit: int = Query(50),
    locality: str = Query(None),
    category: str = Query(None),
    year_from: int = Query(None),
    year_to: int = Query(None)
):
    return paginated_change_records(
        page=page,
        limit=limit,
        locality=locality,
        category=category,
        year_from=year_from,
        year_to=year_to
    )


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
    y_from = year_from or start or before_year
    y_to = year_to or end or after_year

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

    return {
        "type": "FeatureCollection",
        "status": "PENDING",
        "count": 0,
        "city": target_city,
        "year_from": y_from,
        "year_to": y_to,
        "features": []
    }


@router.get("/dashboard/stats")
def get_dashboard_statistics(
    city: str = Query(None),
    year_from: int = Query(None),
    year_to: int = Query(None)
):
    return get_dashboard_stats(city=city, year_from=year_from, year_to=year_to)
