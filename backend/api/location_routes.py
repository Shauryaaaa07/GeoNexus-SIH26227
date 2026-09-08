from fastapi import APIRouter
from data.locations import LOCATIONS

router = APIRouter(
    prefix="/api",
    tags=["Locations"]
)

CITIES = [
    {"id": "delhi", "name": "Delhi", "center": [28.6139, 77.2090], "zoom": 11, "bbox": [77.15, 28.58, 77.27, 28.68]},
    {"id": "mumbai", "name": "Mumbai", "center": [19.0760, 72.8777], "zoom": 11, "bbox": [72.70, 18.85, 73.10, 19.30]},
    {"id": "bengaluru", "name": "Bengaluru", "center": [12.9716, 77.5946], "zoom": 11, "bbox": [77.35, 12.80, 77.80, 13.15]},
    {"id": "hyderabad", "name": "Hyderabad", "center": [17.3850, 78.4867], "zoom": 11, "bbox": [78.25, 17.20, 78.70, 17.60]},
    {"id": "chennai", "name": "Chennai", "center": [13.0827, 80.2707], "zoom": 11, "bbox": [80.05, 12.90, 80.40, 13.25]}
]

COMPARISONS = [
    "2020 → 2021",
    "2021 → 2022",
    "2022 → 2023",
    "2023 → 2024",
    "2024 → 2025",
    "2025 → 2026"
]


@router.get("/locations")
def get_locations():
    locations_list = []
    for key, data in LOCATIONS.items():
        locations_list.append({
            "id": key,
            "name": data["name"],
            "center": data["center"],
            "zoom": data["zoom"],
            "bbox": data.get("bbox")
        })
    return {"locations": locations_list}


@router.get("/cities")
def get_cities():
    return CITIES


@router.get("/comparisons")
def get_comparisons():
    return COMPARISONS