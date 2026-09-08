from services.satellite_service import search_sentinel_images
from data.locations import LOCATIONS
import numpy as np
import re

_semantic_model = None
_semantic_index = None
_model_attempted = False


def ensure_semantic_model_loaded():
    global _semantic_model, _semantic_index, _model_attempted
    if _model_attempted:
        return _semantic_model, _semantic_index

    _model_attempted = True
    try:
        from sentence_transformers import SentenceTransformer
        import faiss

        model = SentenceTransformer("all-MiniLM-L6-v2")
        descriptions = [item["description"] for item in SATELLITE_DATA]
        embeddings = model.encode(descriptions, convert_to_numpy=True).astype("float32")
        faiss.normalize_L2(embeddings)
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings)

        _semantic_model = model
        _semantic_index = index
    except Exception as e:
        print(f"Lazy loading semantic model failed: {e}")
        _semantic_model = None
        _semantic_index = None

    return _semantic_model, _semantic_index


# ==========================================
# Satellite Metadata: 2020 to 2026
# ==========================================

SATELLITE_DATA = []

locations = [
    "Delhi",
    "Mumbai",
    "Bengaluru",
    "Hyderabad",
    "Chennai"
]


for location in locations:

    for year in range(2020, 2027):

        SATELLITE_DATA.append({
            "id": f"{location.lower()}_{year}",
            "location": location,
            "year": year,
            "description": f"{location} satellite image from {year}"
        })


# ==========================================
# Extract Location and Year
# ==========================================

def extract_location_and_year(query: str):

    query_lower = query.lower()

    detected_location = None
    detected_year = None


    # Detect location
    for location in locations:

        if location.lower() in query_lower:

            detected_location = location

            break


    # Detect year
    years = re.findall(
        r"\b(2020|2021|2022|2023|2024|2025|2026)\b",
        query
    )


    if years:

        detected_year = int(years[0])


    return detected_location, detected_year


# ==========================================
# Semantic Search
# ==========================================

def semantic_search(
    query: str,
    top_k: int = 5
):
    model, index = ensure_semantic_model_loaded()

    if model is None or index is None:
        results = []
        for item in SATELLITE_DATA:
            if query.lower() in item["description"].lower() or query.lower() in item["location"].lower():
                res = item.copy()
                res["similarity_score"] = 1.0
                results.append(res)
        return results[:top_k]

    try:
        import faiss

        query_embedding = model.encode([query], convert_to_numpy=True).astype("float32")
        faiss.normalize_L2(query_embedding)

        scores, indices = index.search(
            query_embedding,
            top_k
        )

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue

            item = SATELLITE_DATA[idx].copy()
            item["similarity_score"] = round(float(score), 4)
            results.append(item)

        return results
    except Exception as e:
        print(f"Error executing semantic search model: {e}")
        results = []
        for item in SATELLITE_DATA:
            if query.lower() in item["description"].lower() or query.lower() in item["location"].lower():
                res = item.copy()
                res["similarity_score"] = 1.0
                results.append(res)
        return results[:top_k]


# ==========================================
# Select Best Satellite Image
# ==========================================

def select_best_satellite_image(images):

    """
    Available satellite images me se
    lowest cloud cover wali image select karta hai.
    """

    if not images:

        return None


    # Sirf wahi images jinka cloud cover available hai
    valid_images = [
        image
        for image in images
        if image.get("cloud_cover") is not None
    ]


    # Agar kisi image ka cloud cover available nahi hai
    if not valid_images:

        return images[0]


    # Lowest cloud cover wali image
    best_image = min(
        valid_images,
        key=lambda image: image["cloud_cover"]
    )


    return best_image


# ==========================================
# Real Satellite Search using Copernicus STAC
# ==========================================

def search_real_satellite_data(query: str):

    """
    Natural language query se location aur year
    identify karke Copernicus STAC se real
    Sentinel-2 metadata search karta hai.
    """


    # ------------------------------------------
    # Extract location and year
    # ------------------------------------------

    location, year = extract_location_and_year(
        query
    )


    # ------------------------------------------
    # Location check
    # ------------------------------------------

    if not location:

        return {
            "status": "error",
            "message": (
                "Location not found. "
                "Try Delhi, Mumbai, Bengaluru, "
                "Hyderabad or Chennai."
            )
        }


    # ------------------------------------------
    # Year check
    # ------------------------------------------

    if not year:

        return {
            "status": "error",
            "message": (
                "Year not found. "
                "Supported years: 2020 to 2026."
            )
        }


    # ------------------------------------------
    # Convert location to key
    # ------------------------------------------

    location_key = location.lower()


    # ------------------------------------------
    # Get location information
    # ------------------------------------------

    location_data = LOCATIONS.get(
        location_key
    )


    if not location_data:

        return {
            "status": "error",
            "message": (
                f"Location '{location}' "
                "is not supported."
            )
        }


    # ------------------------------------------
    # Get bounding box
    # ------------------------------------------

    bbox = location_data["bbox"]


    # ------------------------------------------
    # Date range for selected year
    # ------------------------------------------

    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"


    # ------------------------------------------
    # Search Copernicus STAC
    # ------------------------------------------

    images = search_sentinel_images(
        bbox=bbox,
        start_date=start_date,
        end_date=end_date,
        max_cloud_cover=30
    )


    # ------------------------------------------
    # Select best image
    # ------------------------------------------

    best_image = select_best_satellite_image(
        images
    )


    # ------------------------------------------
    # Final response
    # ------------------------------------------

    return {
        "status": "success",

        "query": query,

        "location": {
            "id": location_key,
            "name": location_data["name"]
        },

        "year": year,

        "date_range": {
            "start": start_date,
            "end": end_date
        },

        "satellite": "Sentinel-2",

        "count": len(images),

        "best_image": best_image
    }