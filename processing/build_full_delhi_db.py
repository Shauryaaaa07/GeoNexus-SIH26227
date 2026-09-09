import os
import json
import sqlite3
import shutil
from pathlib import Path

BASE_DIR = Path(r"C:\Users\shaur\OneDrive\Desktop\GeoNexus-SIH26227")
DB_DIR = BASE_DIR / "database"
ORIGINAL_DB = DB_DIR / "sih_changes.db"
BACKUP_DB = DB_DIR / "sih_changes_prototype_backup.db"
FULL_DB = DB_DIR / "sih_changes_full_delhi.db"
INPUT_JSON = BASE_DIR / "processing" / "data" / "delhi_change_polygons.json"

# 1. Backup old database if present
if ORIGINAL_DB.exists() and not BACKUP_DB.exists():
    shutil.copy2(ORIGINAL_DB, BACKUP_DB)
    print(f"Backed up prototype database to {BACKUP_DB}")

# 2. Load generated change polygons
if not INPUT_JSON.exists():
    raise FileNotFoundError(f"Input JSON missing: {INPUT_JSON}")

data = json.loads(INPUT_JSON.read_text(encoding="utf-8"))
polygons = data.get("polygons", [])

print(f"Loaded {len(polygons)} change polygons for database insertion.")

# 3. Create new database
if FULL_DB.exists():
    FULL_DB.unlink()

conn = sqlite3.connect(FULL_DB)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    year_from INTEGER NOT NULL,
    year_to INTEGER NOT NULL,
    category TEXT NOT NULL,
    confidence REAL NOT NULL,
    area_m2 REAL NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    locality TEXT NOT NULL,
    geometry TEXT NOT NULL
);
""")

# Create Indexes
cursor.execute("CREATE INDEX IF NOT EXISTS idx_changes_city ON changes(city);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_changes_years ON changes(year_from, year_to);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_changes_category ON changes(category);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_changes_locality ON changes(locality);")

cursor.execute("DROP VIEW IF EXISTS change_records;")
cursor.execute("CREATE VIEW change_records AS SELECT * FROM changes;")

# Insert Records
insert_query = """
INSERT INTO changes (id, city, year_from, year_to, category, confidence, area_m2, latitude, longitude, locality, geometry)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

records = []
for p in polygons:
    records.append((
        p.get("id"),
        p.get("city", "Delhi"),
        p.get("year_from"),
        p.get("year_to"),
        p.get("category"),
        p.get("confidence"),
        p.get("area_m2"),
        p.get("latitude"),
        p.get("longitude"),
        p.get("locality", "Delhi NCT"),
        json.dumps(p.get("geometry"))
    ))

cursor.executemany(insert_query, records)
conn.commit()

# Verify Row Count & Locality Distribution
cursor.execute("SELECT COUNT(*) FROM changes;")
total_count = cursor.fetchone()[0]

cursor.execute("SELECT locality, COUNT(*) FROM changes GROUP BY locality ORDER BY COUNT(*) DESC LIMIT 10;")
top_localities = cursor.fetchall()

cursor.execute("SELECT category, COUNT(*) FROM changes GROUP BY category ORDER BY COUNT(*) DESC;")
categories = cursor.fetchall()

conn.close()

# Activate new database as primary sih_changes.db
shutil.copy2(FULL_DB, ORIGINAL_DB)

print(f"\n====================================")
print(f"FULL DELHI DATABASE CREATION COMPLETE:")
print(f"  Primary DB: {ORIGINAL_DB}")
print(f"  Full DB: {FULL_DB}")
print(f"  Total Inserted Records: {total_count}")
print(f"  Categories Breakdown: {categories}")
print(f"  Top Localities: {top_localities}")
