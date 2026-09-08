import os
import sqlite3
import json

# Locate database relative to project root
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
# database ka path yaha se mil jayega
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "database", "sih_changes.db")


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

    query = "SELECT id, city, year_from, year_to, category, confidence, area_m2, latitude, longitude, geometry FROM change_records WHERE 1=1"
    params = []

    if city:
        query += " AND LOWER(city) = LOWER(?)"
        params.append(city)
    if year_from is not None:
        query += " AND year_from = ?"
        params.append(int(year_from))
    if year_to is not None:
        query += " AND year_to = ?"
        params.append(int(year_to))

    query += " ORDER BY id ASC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    results = [dict(row) for row in rows]
    conn.close()
    return results


def query_consecutive_range(city="Delhi", start_year=2020, end_year=2026, db_path=None):
    """
    Queries consecutive annual comparisons (e.g. 2020->2021, 2021->2022) for a given city.
    Returns a structured dictionary with features and consecutive interval statuses.
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
                        "longitude": rec["longitude"]
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


def get_db_stats(db_path=None):
    """
    Returns database summary statistics: total record count and interval breakdowns.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM change_records")
    total_count = cursor.fetchone()[0]

    cursor.execute("SELECT city, year_from, year_to, COUNT(*) FROM change_records GROUP BY city, year_from, year_to ORDER BY city, year_from")
    intervals = cursor.fetchall()
    
    interval_stats = [
        {
            "city": row[0],
            "year_from": row[1],
            "year_to": row[2],
            "count": row[3]
        }
        for row in intervals
    ]

    conn.close()
    return {
        "total_records": total_count,
        "interval_breakdown": interval_stats
    }


def get_dashboard_stats(city=None, year_from=None, year_to=None, db_path=None):
    # backend se stats le rahe hain
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    
    where_clause = " WHERE 1=1"
    params = []
    if city:
        where_clause += " AND LOWER(city) = LOWER(?)"
        params.append(city)
    if year_from is not None:
        where_clause += " AND year_from = ?"
        params.append(int(year_from))
    if year_to is not None:
        where_clause += " AND year_to = ?"
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
        
    cur.execute(f"SELECT id, city, category, year_from, year_to, confidence, area_m2, latitude, longitude FROM change_records{where_clause} ORDER BY area_m2 DESC LIMIT 10", params)
    largest_polygons = [dict(r) for r in cur.fetchall()]
    
    conn.close()
    
    return {
        "total_polygons": total_polygons,
        "total_area_m2": total_area_m2,
        "total_area_km2": total_area_km2,
        "categories": categories,
        "intervals": intervals,
        "confidence": confidence,
        "largest_polygons": largest_polygons
    }
