import os
from database import save_geojson_to_db, sync_geojson_to_public

years = [
    (2020, 2021),
    (2021, 2022),
    (2022, 2023),
    (2023, 2024),
    (2024, 2025),
    (2025, 2026),
]

for y_from, y_to in years:
    geojson_path = f"output/delhi/{y_from}_{y_to}_final.geojson"
    if not os.path.exists(geojson_path):
        geojson_path = f"output/delhi/{y_from}_{y_to}_final.geojson"
    if os.path.exists(geojson_path):
        save_geojson_to_db(geojson_path, city="Delhi", year_from=y_from, year_to=y_to)
        sync_geojson_to_public(geojson_path, city="delhi", year_from=y_from, year_to=y_to)
        print(f"[OK] Synced Delhi {y_from}->{y_to} to DB and Frontend Public assets.")
    else:
        print(f"[WARNING] File not found: {geojson_path}")
