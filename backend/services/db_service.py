import os
import sqlite3
import json
import math
import urllib.request
import urllib.parse
from shapely.geometry import shape, Point

# Locate database relative to project root
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "database", "sih_changes.db")

# Load official Delhi NCT Polygon boundary for spatial validation
DELHI_BOUNDARY_PATH = os.path.join(BASE_DIR, "processing", "data", "boundaries", "delhi_nct.geojson")
DELHI_SHAPE = None
try:
    if os.path.exists(DELHI_BOUNDARY_PATH):
        with open(DELHI_BOUNDARY_PATH, "r") as f:
            DELHI_SHAPE = shape(json.load(f)["features"][0]["geometry"])
except Exception as err:
    print("Delhi boundary load warning:", err)

# Geocoding JSON cache
GEOCODING_CACHE_PATH = os.path.join(BASE_DIR, "backend", "data", "geocoding_cache.json")
GEOCODING_CACHE = {}

def load_geocoding_cache():
    global GEOCODING_CACHE
    if os.path.exists(GEOCODING_CACHE_PATH):
        try:
            with open(GEOCODING_CACHE_PATH, "r") as f:
                GEOCODING_CACHE = json.load(f)
        except Exception:
            GEOCODING_CACHE = {}

def save_geocoding_cache():
    try:
        os.makedirs(os.path.dirname(GEOCODING_CACHE_PATH), exist_ok=True)
        with open(GEOCODING_CACHE_PATH, "w") as f:
            json.dump(GEOCODING_CACHE, f, indent=2)
    except Exception:
        pass

load_geocoding_cache()

def is_point_inside_delhi(lat, lon):
    if DELHI_SHAPE:
        try:
            return DELHI_SHAPE.contains(Point(float(lon), float(lat)))
        except Exception:
            pass
    return (28.40 <= lat <= 28.88) and (76.84 <= lon <= 77.34)

VALID_LOCALITIES = [
    "narela", "alipur", "civil lines", "rohini", "model town",
    "chandni chowk", "karol bagh", "connaught place", "punjabi bagh",
    "paschim vihar", "janakpuri", "dwarka", "najafgarh", "saket",
    "vasant kunj", "mehrauli", "hauz khas", "defence colony",
    "kalkaji", "okhla", "sarita vihar", "mayur vihar", "shahdara",
    "yamuna vihar"
]

UNSUPPORTED_CITIES = ["mumbai", "bengaluru", "hyderabad", "chennai", "kolkata", "pune"]


def get_db_path(custom_path=None):
    """
    Resolves the SQLite database path cleanly across execution contexts.
    """
    if custom_path and os.path.exists(custom_path):
        return custom_path
    
    env_path = os.getenv("SIH_DB_PATH")
    if env_path and os.path.exists(env_path):
        return env_path
        
    if os.path.exists(DEFAULT_DB_PATH):
        return DEFAULT_DB_PATH
        
    # Fallback to local relative paths
    relative_paths = [
        "database/sih_changes.db",
        "../database/sih_changes.db"
    ]
    for p in relative_paths:
        abs_p = os.path.abspath(p)
        if os.path.exists(abs_p):
            return abs_p
            
    return DEFAULT_DB_PATH


def get_db_connection(db_path=None):
    """
    Returns an active SQLite database connection with row factory enabled.
    """
    target_path = get_db_path(db_path)
    if not os.path.exists(target_path):
        raise FileNotFoundError(f"Database file not found at: {target_path}")
        
    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    return conn


def query_change_records(city=None, year_from=None, year_to=None, db_path=None):
    """
    Queries change records from the database based on city and year interval.
    Returns a list of record dictionaries.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    query = "SELECT id, city, year_from, year_to, category, confidence, area_m2, latitude, longitude, locality, geometry FROM change_records WHERE 1=1"
    params = []

    if city:
        query += " AND LOWER(city) = LOWER(?)"
        params.append(city)
    if year_from is not None:
        query += " AND year_from >= ?"
        params.append(int(year_from))
    if year_to is not None:
        query += " AND year_to <= ?"
        params.append(int(year_to))

    query += " ORDER BY id ASC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    results = [dict(row) for row in rows]
    conn.close()
    return results


DELHI_GEOLOCATIONS = {
    "india gate": {
        "query": "India Gate",
        "display_name": "India Gate, New Delhi",
        "latitude": 28.6129,
        "longitude": 77.2295,
        "admin_locality": "Connaught Place"
    },
    "red fort": {
        "query": "Red Fort",
        "display_name": "Red Fort, Old Delhi",
        "latitude": 28.6562,
        "longitude": 77.2410,
        "admin_locality": "Chandni Chowk"
    },
    "qutub minar": {
        "query": "Qutub Minar",
        "display_name": "Qutub Minar, Mehrauli",
        "latitude": 28.5245,
        "longitude": 77.1855,
        "admin_locality": "Mehrauli"
    },
    "lotus temple": {
        "query": "Lotus Temple",
        "display_name": "Lotus Temple, Kalkaji",
        "latitude": 28.5535,
        "longitude": 77.2588,
        "admin_locality": "Kalkaji"
    },
    "rajouri garden": {
        "query": "Rajouri Garden",
        "display_name": "Rajouri Garden, West Delhi",
        "latitude": 28.6415,
        "longitude": 77.1209,
        "admin_locality": "Punjabi Bagh"
    },
    "lajpat nagar": {
        "query": "Lajpat Nagar",
        "display_name": "Lajpat Nagar, South Delhi",
        "latitude": 28.5677,
        "longitude": 77.2433,
        "admin_locality": "Defence Colony"
    },
    "nehru place": {
        "query": "Nehru Place",
        "display_name": "Nehru Place, South Delhi",
        "latitude": 28.5492,
        "longitude": 77.2517,
        "admin_locality": "Kalkaji"
    },
    "pitampura": {
        "query": "Pitampura",
        "display_name": "Pitampura, North West Delhi",
        "latitude": 28.6988,
        "longitude": 77.1384,
        "admin_locality": "Rohini"
    },
    "dwarka sector 10": {
        "query": "Dwarka Sector 10",
        "display_name": "Dwarka Sector 10, New Delhi",
        "latitude": 28.5815,
        "longitude": 77.0583,
        "admin_locality": "Dwarka"
    },
    "dwarka sector 6": {
        "query": "Dwarka Sector 6",
        "display_name": "Dwarka Sector 6, New Delhi",
        "latitude": 28.5880,
        "longitude": 77.0620,
        "admin_locality": "Dwarka"
    },
    "dwarka sector 12": {
        "query": "Dwarka Sector 12",
        "display_name": "Dwarka Sector 12, New Delhi",
        "latitude": 28.5910,
        "longitude": 77.0420,
        "admin_locality": "Dwarka"
    },
    "dwarka sector 21": {
        "query": "Dwarka Sector 21",
        "display_name": "Dwarka Sector 21, New Delhi",
        "latitude": 28.5522,
        "longitude": 77.0583,
        "admin_locality": "Dwarka"
    },
    "rohini sector 7": {
        "query": "Rohini Sector 7",
        "display_name": "Rohini Sector 7, North West Delhi",
        "latitude": 28.7118,
        "longitude": 77.1245,
        "admin_locality": "Rohini"
    },
    "rohini sector 3": {
        "query": "Rohini Sector 3",
        "display_name": "Rohini Sector 3, North West Delhi",
        "latitude": 28.7050,
        "longitude": 77.1180,
        "admin_locality": "Rohini"
    },
    "rohini sector 11": {
        "query": "Rohini Sector 11",
        "display_name": "Rohini Sector 11, North West Delhi",
        "latitude": 28.7290,
        "longitude": 77.1190,
        "admin_locality": "Rohini"
    },
    "mayur vihar phase 1": {
        "query": "Mayur Vihar Phase 1",
        "display_name": "Mayur Vihar Phase 1, East Delhi",
        "latitude": 28.6083,
        "longitude": 77.2942,
        "admin_locality": "Mayur Vihar"
    },
    "mayur vihar phase 2": {
        "query": "Mayur Vihar Phase 2",
        "display_name": "Mayur Vihar Phase 2, East Delhi",
        "latitude": 28.6150,
        "longitude": 77.3050,
        "admin_locality": "Mayur Vihar"
    },
    "janakpuri west": {
        "query": "Janakpuri West",
        "display_name": "Janakpuri West, West Delhi",
        "latitude": 28.6295,
        "longitude": 77.0782,
        "admin_locality": "Janakpuri"
    },
    "okhla phase 3": {
        "query": "Okhla Phase 3",
        "display_name": "Okhla Industrial Area Phase 3, New Delhi",
        "latitude": 28.5450,
        "longitude": 77.2720,
        "admin_locality": "Okhla"
    },
    "saket district centre": {
        "query": "Saket District Centre",
        "display_name": "Saket District Centre, South Delhi",
        "latitude": 28.5284,
        "longitude": 77.2185,
        "admin_locality": "Saket"
    }
}

ADMIN_LOCALITIES = [
    "alipur", "chandni chowk", "civil lines", "connaught place", "defence colony",
    "dwarka", "hauz khas", "janakpuri", "kalkaji", "karol bagh", "mayur vihar",
    "mehrauli", "model town", "najafgarh", "narela", "okhla", "paschim vihar",
    "punjabi bagh", "rohini", "saket", "sarita vihar", "shahdara", "vasant kunj",
    "yamuna vihar"
]

CATEGORY_COLORS = {
    "New Buildings": "#e74c3c",
    "New Roads": "#e67e22",
    "Vegetation Change": "#2ecc71",
    "Water Body Change": "#3498db",
    "Agricultural / Land-use Change": "#f1c40f",
    "Unclassified": "#95a5a6"
}

def search_change_records(place=None, year_from=None, year_to=None, category=None, radius_m=2000.0, confidence=None, limit=500, db_path=None):
    """
    Dynamic Delhi place search with strict 3-step resolution order:
    1. Exact administrative locality from dataset
    2. Local cache (DELHI_GEOLOCATIONS or GEOCODING_CACHE)
    3. Dynamic Nominatim geocoder ("query, Delhi, India") with Delhi NCT boundary validation
    """
    raw_query = (place or "Delhi").strip()
    clean_query = raw_query.lower()

    if clean_query in UNSUPPORTED_CITIES:
        return {
            "status": "data_unavailable",
            "message": "Location is outside the currently processed Delhi NCT dataset.",
            "place": {"query": raw_query, "search_mode": "unsupported", "resolution_source": "unsupported_city"},
            "summary": {"total_changes": 0, "total_area_km2": 0.0, "category_breakdown": []},
            "returned_features": 0,
            "features": []
        }

    search_mode = "entire_city"
    display_name = "Delhi NCT Boundary"
    admin_locality = "Delhi NCT"
    lat, lon = 28.6139, 77.2090
    matched_loc = None
    resolution_source = "default"
    inside_delhi = True

    if clean_query in ["delhi", "entire delhi", "delhi nct", "nct of delhi"]:
        search_mode = "entire_city"
        display_name = "Entire Delhi NCT"
        admin_locality = "Delhi NCT"
        resolution_source = "entire_city"
    else:
        # STEP 1: Exact administrative locality
        loc_match = None
        for loc in ADMIN_LOCALITIES:
            if loc == clean_query:
                loc_match = loc
                break

        if loc_match:
            search_mode = "locality"
            matched_loc = loc_match
            display_name = f"{loc_match.title()} Administrative Zone"
            admin_locality = loc_match.title()
            resolution_source = "admin_dataset"
        elif clean_query in DELHI_GEOLOCATIONS:
            # STEP 2A: Static geocoding cache
            info = DELHI_GEOLOCATIONS[clean_query]
            search_mode = "point_radius"
            display_name = info["display_name"]
            admin_locality = info["admin_locality"]
            lat, lon = info["latitude"], info["longitude"]
            resolution_source = "local_cache"
        elif clean_query in GEOCODING_CACHE:
            # STEP 2B: Persistent JSON geocoding cache
            info = GEOCODING_CACHE[clean_query]
            search_mode = "point_radius"
            display_name = info["display_name"]
            admin_locality = info["admin_locality"]
            lat, lon = info["latitude"], info["longitude"]
            inside_delhi = info.get("inside_delhi", True)
            resolution_source = "json_cache"
        else:
            # STEP 3: Dynamic geocoding fallback via OpenStreetMap Nominatim
            geocode_info = None
            try:
                # Try raw_query, India first to check for places/cities
                search_q = f"{raw_query}, India"
                url = "https://nominatim.openstreetmap.org/search?q=" + urllib.parse.quote(search_q) + "&format=json&limit=1"
                req = urllib.request.Request(url, headers={"User-Agent": "GeoNexus-SIH26227-Bot/1.0"})
                res_data = []
                with urllib.request.urlopen(req, timeout=4) as response:
                    res_data = json.loads(response.read().decode("utf-8"))

                # Check if raw_query, Delhi, India exists inside Delhi (e.g. Ashok Vihar, Delhi)
                delhi_q = f"{raw_query}, Delhi, India"
                url_delhi = "https://nominatim.openstreetmap.org/search?q=" + urllib.parse.quote(delhi_q) + "&format=json&limit=1"
                req_delhi = urllib.request.Request(url_delhi, headers={"User-Agent": "GeoNexus-SIH26227-Bot/1.0"})
                try:
                    with urllib.request.urlopen(req_delhi, timeout=4) as resp_d:
                        d_data = json.loads(resp_d.read().decode("utf-8"))
                        if d_data:
                            d_lat = float(d_data[0]["lat"])
                            d_lon = float(d_data[0]["lon"])
                            if is_point_inside_delhi(d_lat, d_lon):
                                res_data = d_data
                except Exception:
                    pass

                if res_data:
                    g_lat = float(res_data[0]["lat"])
                    g_lon = float(res_data[0]["lon"])
                    g_name = res_data[0].get("display_name", f"{raw_query.title()}, Delhi")
                    g_inside = is_point_inside_delhi(g_lat, g_lon)
                    
                    g_admin = "Delhi NCT"
                    for loc in ADMIN_LOCALITIES:
                        if loc in clean_query or loc in g_name.lower():
                            g_admin = loc.title()
                            break

                    geocode_info = {
                        "query": raw_query,
                        "display_name": g_name,
                        "latitude": g_lat,
                        "longitude": g_lon,
                        "admin_locality": g_admin,
                        "inside_delhi": g_inside
                    }
                    GEOCODING_CACHE[clean_query] = geocode_info
                    save_geocoding_cache()
            except Exception as err:
                print("Dynamic geocoding error:", err)

            if geocode_info:
                search_mode = "point_radius"
                display_name = geocode_info["display_name"]
                admin_locality = geocode_info["admin_locality"]
                lat, lon = geocode_info["latitude"], geocode_info["longitude"]
                inside_delhi = geocode_info["inside_delhi"]
                resolution_source = "nominatim_geocoder"
            else:
                # Substring locality fallback if geocoder returned no data
                sub_loc = None
                for loc in ADMIN_LOCALITIES:
                    if loc in clean_query or clean_query in loc:
                        sub_loc = loc
                        break
                if sub_loc:
                    search_mode = "locality"
                    matched_loc = sub_loc
                    display_name = f"{sub_loc.title()} Locality Area"
                    admin_locality = sub_loc.title()
                    resolution_source = "locality_substring"
                else:
                    return {
                        "status": "location_not_found",
                        "message": "Unable to resolve this place right now. You can select the location directly on the map.",
                        "place": {
                            "query": raw_query,
                            "search_mode": "not_found",
                            "resolution_source": "failed"
                        },
                        "summary": {
                            "total_changes": 0,
                            "total_area_m2": 0.0,
                            "total_area_km2": 0.0,
                            "total_area_ha": 0.0,
                            "category_breakdown": []
                        },
                        "returned_features": 0,
                        "features": []
                    }

    # Verify location lies inside Delhi NCT boundary
    if not inside_delhi:
        return {
            "status": "data_unavailable",
            "message": "Location is outside the currently processed Delhi NCT dataset.",
            "place": {
                "query": raw_query,
                "display_name": display_name,
                "latitude": lat,
                "longitude": lon,
                "search_mode": "outside_delhi",
                "inside_delhi": False,
                "resolution_source": resolution_source
            },
            "summary": {
                "total_changes": 0,
                "total_area_m2": 0.0,
                "total_area_km2": 0.0,
                "total_area_ha": 0.0,
                "category_breakdown": []
            },
            "returned_features": 0,
            "features": []
        }

    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    where_clauses = ["1=1"]
    params = []

    if search_mode == "point_radius":
        dlat = float(radius_m) / 111000.0
        dlon = float(radius_m) / 97400.0
        where_clauses.append("latitude BETWEEN ? AND ? AND longitude BETWEEN ? AND ?")
        params.extend([lat - dlat, lat + dlat, lon - dlon, lon + dlon])
        where_clauses.append("(((latitude - ?)/?)*((latitude - ?)/?) + ((longitude - ?)/?)*((longitude - ?)/?)) <= 1.0")
        params.extend([lat, dlat, lat, dlat, lon, dlon, lon, dlon])
    elif search_mode == "locality" and matched_loc:
        where_clauses.append("LOWER(locality) LIKE ?")
        params.append(f"%{matched_loc}%")

    if year_from is not None:
        where_clauses.append("year_from >= ?")
        params.append(int(year_from))
    if year_to is not None:
        where_clauses.append("year_to <= ?")
        params.append(int(year_to))
    if category and category.lower() != "all":
        where_clauses.append("LOWER(category) LIKE ?")
        params.append(f"%{category.strip().lower()}%")
    if confidence is not None:
        where_clauses.append("confidence >= ?")
        params.append(float(confidence))

    where_sql = " WHERE " + " AND ".join(where_clauses)

    # 1. Total Summary Stats over ALL matching records in SQLite DB
    summary_sql = f"SELECT COUNT(*) as total_changes, SUM(area_m2) as total_area_m2 FROM change_records{where_sql}"
    cursor.execute(summary_sql, params)
    sum_row = cursor.fetchone()
    total_changes = sum_row["total_changes"] or 0
    total_area_m2 = sum_row["total_area_m2"] or 0.0
    total_area_km2 = round(total_area_m2 / 1_000_000.0, 3)
    total_area_ha = round(total_area_m2 / 10_000.0, 1)

    # 2. Category Breakdown over ALL matching records
    cat_sql = f"SELECT category, COUNT(*) as count, SUM(area_m2) as area_m2 FROM change_records{where_sql} GROUP BY category ORDER BY area_m2 DESC"
    cursor.execute(cat_sql, params)
    cat_rows = cursor.fetchall()

    category_breakdown = []
    for r in cat_rows:
        c_name = r["category"]
        c_cnt = r["count"]
        c_area_m2 = r["area_m2"] or 0.0
        c_share = round((c_area_m2 / total_area_m2) * 100, 1) if total_area_m2 > 0 else 0
        category_breakdown.append({
            "name": c_name,
            "color": CATEGORY_COLORS.get(c_name, "#95a5a6"),
            "count": c_cnt,
            "area_m2": round(c_area_m2, 1),
            "area_ha": round(c_area_m2 / 10_000.0, 1),
            "area_km2": round(c_area_m2 / 1_000_000.0, 3),
            "share": c_share
        })

    existing_cats = {c["name"] for c in category_breakdown}
    for std_cat, color in CATEGORY_COLORS.items():
        if std_cat not in existing_cats:
            category_breakdown.append({
                "name": std_cat,
                "color": color,
                "count": 0,
                "area_m2": 0.0,
                "area_ha": 0.0,
                "area_km2": 0.0,
                "share": 0.0
            })

    # 3. Query GeoJSON features (capped by limit for rendering safety)
    features_sql = f"""
    SELECT id, city, year_from, year_to, category, confidence, area_m2, latitude, longitude, locality, geometry
    FROM change_records{where_sql}
    ORDER BY area_m2 DESC LIMIT ?
    """
    feat_params = list(params) + [int(limit)]
    cursor.execute(features_sql, feat_params)
    feat_rows = cursor.fetchall()
    conn.close()

    features = []
    for rec in feat_rows:
        try:
            geom = json.loads(rec["geometry"]) if rec["geometry"] else None
        except Exception:
            geom = None

        features.append({
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
                "locality": rec["locality"]
            },
            "geometry": geom
        })

    status = "success" if total_changes > 0 else "no_results"
    message = f"Found {total_changes} change records" if total_changes > 0 else "No matching detected changes found"

    return {
        "type": "FeatureCollection",
        "status": status,
        "message": message,
        "place": {
            "query": raw_query,
            "display_name": display_name,
            "latitude": lat,
            "longitude": lon,
            "search_mode": search_mode,
            "radius_m": float(radius_m) if search_mode == "point_radius" else None,
            "admin_locality": admin_locality
        },
        "summary": {
            "total_changes": total_changes,
            "total_area_m2": round(total_area_m2, 1),
            "total_area_km2": total_area_km2,
            "total_area_ha": total_area_ha,
            "category_breakdown": category_breakdown
        },
        "matched_locality": admin_locality,
        "count": total_changes,
        "total_area_m2": round(total_area_m2, 1),
        "total_area_km2": total_area_km2,
        "returned_features": len(features),
        "features": features
    }


def point_query_change_records(lat, lon, radius_m=1000.0, year_from=None, year_to=None, db_path=None):
    """
    Finds change polygons intersecting or near a clicked lat/lon point.
    """
    lat, lon = float(lat), float(lon)
    # Approx 1 deg lat ~ 111,000m, 1 deg lon ~ 97,000m in Delhi
    lat_delta = radius_m / 111000.0
    lon_delta = radius_m / 97000.0

    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    query = """
    SELECT id, city, year_from, year_to, category, confidence, area_m2, latitude, longitude, locality, geometry 
    FROM change_records 
    WHERE latitude BETWEEN ? AND ? AND longitude BETWEEN ? AND ?
    """
    params = [lat - lat_delta, lat + lat_delta, lon - lon_delta, lon + lon_delta]

    if year_from is not None:
        query += " AND year_from >= ?"
        params.append(int(year_from))
    if year_to is not None:
        query += " AND year_to <= ?"
        params.append(int(year_to))

    query += " ORDER BY ABS(latitude - ?) + ABS(longitude - ?) ASC LIMIT 20"
    params.extend([lat, lon])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    records = [dict(row) for row in rows]
    if not records:
        return {
            "status": "no_data",
            "message": "No detected change near this location for the selected period.",
            "count": 0,
            "features": []
        }

    features = []
    for rec in records:
        try:
            geom = json.loads(rec["geometry"]) if rec["geometry"] else None
        except Exception:
            geom = None

        features.append({
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
                "locality": rec["locality"]
            },
            "geometry": geom
        })

    return {
        "status": "success",
        "count": len(features),
        "clicked_point": {"latitude": lat, "longitude": lon},
        "nearest": features[0]["properties"],
        "features": features
    }


def bbox_query_change_records(min_lon, min_lat, max_lon, max_lat, year_from=None, year_to=None, category=None, limit=500, db_path=None):
    """
    Queries polygons intersecting map viewport bounding box.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    query = """
    SELECT id, city, year_from, year_to, category, confidence, area_m2, latitude, longitude, locality, geometry 
    FROM change_records 
    WHERE longitude BETWEEN ? AND ? AND latitude BETWEEN ? AND ?
    """
    params = [float(min_lon), float(max_lon), float(min_lat), float(max_lat)]

    if year_from is not None:
        query += " AND year_from >= ?"
        params.append(int(year_from))
    if year_to is not None:
        query += " AND year_to <= ?"
        params.append(int(year_to))
    if category:
        query += " AND LOWER(category) LIKE ?"
        params.append(f"%{category.strip().lower()}%")

    query += " ORDER BY area_m2 DESC LIMIT ?"
    params.append(int(limit))

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    records = [dict(row) for row in rows]
    features = []
    for rec in records:
        try:
            geom = json.loads(rec["geometry"]) if rec["geometry"] else None
        except Exception:
            geom = None

        features.append({
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
                "locality": rec["locality"]
            },
            "geometry": geom
        })

    return {
        "type": "FeatureCollection",
        "status": "success",
        "count": len(features),
        "bbox": [min_lon, min_lat, max_lon, max_lat],
        "features": features
    }


def paginated_change_records(page=1, limit=50, locality=None, category=None, year_from=None, year_to=None, db_path=None):
    """
    Returns paginated database records for Database Explorer table view.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    where_clause = " WHERE 1=1"
    params = []

    if locality and locality.lower() not in ["all", "delhi", "entire delhi"]:
        clean_loc = locality.strip().lower()
        matched = None
        if clean_loc in DELHI_GEOLOCATIONS:
            matched = DELHI_GEOLOCATIONS[clean_loc]["admin_locality"]
        else:
            for g_key, g_info in DELHI_GEOLOCATIONS.items():
                if g_key in clean_loc or clean_loc in g_key:
                    matched = g_info["admin_locality"]
                    break
        if not matched:
            for loc in ADMIN_LOCALITIES:
                if loc in clean_loc or clean_loc in loc:
                    matched = loc
                    break
        if not matched:
            matched = clean_loc

        where_clause += " AND LOWER(locality) LIKE ?"
        params.append(f"%{matched.lower()}%")

    if category and category.lower() != "all":
        where_clause += " AND LOWER(category) LIKE ?"
        params.append(f"%{category.strip().lower()}%")

    if year_from is not None:
        where_clause += " AND year_from >= ?"
        params.append(int(year_from))

    if year_to is not None:
        where_clause += " AND year_to <= ?"
        params.append(int(year_to))

    cursor.execute(f"SELECT COUNT(*) FROM change_records{where_clause}", params)
    total_records = cursor.fetchone()[0]

    offset = (page - 1) * limit
    total_pages = math.ceil(total_records / limit) if limit > 0 else 1

    query = f"""
    SELECT id, city, locality, category, year_from, year_to, area_m2, confidence, latitude, longitude
    FROM change_records{where_clause}
    ORDER BY id ASC LIMIT ? OFFSET ?
    """
    params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    records = [dict(row) for row in rows]
    return {
        "status": "success",
        "total_records": total_records,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "records": records
    }


def query_consecutive_range(city="Delhi", start_year=2020, end_year=2026, db_path=None):
    """
    Queries consecutive annual comparisons (e.g. 2020->2021, 2021->2022) for a given city.
    """
    consecutive_pairs = [(y, y + 1) for y in range(start_year, end_year)]
    
    all_features = []
    comparisons_meta = []

    for y_from, y_to in consecutive_pairs:
        records = query_change_records(city=city, year_from=y_from, year_to=y_to, db_path=db_path)
        
        if not records:
            comparisons_meta.append({
                "comparison": f"{y_from} -> {y_to}",
                "status": "PENDING",
                "count": 0
            })
        else:
            comparisons_meta.append({
                "comparison": f"{y_from} -> {y_to}",
                "status": "READY",
                "count": len(records)
            })
            
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
                all_features.append(feature)

    all_ready = all(c["status"] == "READY" for c in comparisons_meta)
    any_ready = any(c["status"] == "READY" for c in comparisons_meta)
    overall_status = "success" if all_ready else ("partial" if any_ready else "PENDING")

    return {
        "type": "FeatureCollection",
        "features": all_features,
        "status": overall_status,
        "count": len(all_features),
        "city": city,
        "range": f"{start_year} -> {end_year}",
        "consecutive_comparisons": comparisons_meta
    }


def get_dashboard_stats(city=None, year_from=None, year_to=None, db_path=None):
    """
    Returns dashboard statistics using real database records.
    """
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    
    where_clause = " WHERE 1=1"
    params = []
    if city and city.lower() != "all":
        where_clause += " AND LOWER(city) = LOWER(?)"
        params.append(city)
    if year_from is not None:
        where_clause += " AND year_from >= ?"
        params.append(int(year_from))
    if year_to is not None:
        where_clause += " AND year_to <= ?"
        params.append(int(year_to))
        
    cur.execute(f"SELECT COUNT(*) as total_polygons, SUM(area_m2) as total_area_m2 FROM change_records{where_clause}", params)
    row = cur.fetchone()
    total_polygons = row["total_polygons"] or 0
    total_area_m2 = row["total_area_m2"] or 0.0
    total_area_km2 = round(total_area_m2 / 1_000_000.0, 2)
    
    cur.execute(f"SELECT category, COUNT(*) as count, SUM(area_m2) as area_m2 FROM change_records{where_clause} GROUP BY category ORDER BY area_m2 DESC", params)
    categories = []
    for r in cur.fetchall():
        cnt = r["count"]
        a_m2 = r["area_m2"] or 0.0
        a_km2 = round(a_m2 / 1_000_000.0, 2)
        poly_pct = round((cnt / total_polygons) * 100, 1) if total_polygons > 0 else 0
        area_pct = round((a_m2 / total_area_m2) * 100, 1) if total_area_m2 > 0 else 0
        categories.append({
            "category": r["category"],
            "count": cnt,
            "area_m2": a_m2,
            "area_km2": a_km2,
            "polygon_percentage": poly_pct,
            "area_percentage": area_pct
        })
        
    cur.execute(f"SELECT year_from, year_to, COUNT(*) as count, SUM(area_m2) as area_m2 FROM change_records{where_clause} GROUP BY year_from, year_to ORDER BY year_from ASC", params)
    intervals = []
    for r in cur.fetchall():
        intervals.append({
            "year_from": r["year_from"],
            "year_to": r["year_to"],
            "interval": f"{r['year_from']} -> {r['year_to']}",
            "count": r["count"],
            "area_m2": r["area_m2"] or 0.0,
            "area_km2": round((r["area_m2"] or 0.0) / 1_000_000.0, 2)
        })

    cur.execute(f"SELECT confidence, COUNT(*) as count FROM change_records{where_clause} GROUP BY confidence ORDER BY count DESC", params)
    confidence = []
    for r in cur.fetchall():
        cnt = r["count"]
        pct = round((cnt / total_polygons) * 100, 1) if total_polygons > 0 else 0
        confidence.append({
            "confidence": r["confidence"],
            "count": cnt,
            "percentage": pct
        })

    cur.execute(f"SELECT locality, COUNT(*) as count, SUM(area_m2) as area_m2 FROM change_records{where_clause} GROUP BY locality ORDER BY count DESC LIMIT 10", params)
    top_localities = [
        {
            "locality": r["locality"],
            "count": r["count"],
            "area_km2": round((r["area_m2"] or 0.0) / 1_000_000.0, 2)
        }
        for r in cur.fetchall()
    ]

    cur.execute(f"SELECT id, city, locality, category, year_from, year_to, confidence, area_m2, latitude, longitude FROM change_records{where_clause} ORDER BY area_m2 DESC LIMIT 10", params)
    largest_polygons = [dict(r) for r in cur.fetchall()]
    
    conn.close()
    
    return {
        "metric_label": "Sum of Detected Change Areas",
        "total_polygons": total_polygons,
        "total_area_m2": total_area_m2,
        "total_area_km2": total_area_km2,
        "categories": categories,
        "intervals": intervals,
        "confidence": confidence,
        "top_localities": top_localities,
        "largest_polygons": largest_polygons
    }
