import os
import argparse
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pipeline import process_change_analysis
from database import save_geojson_to_db, sync_geojson_to_public


def run_master_pipeline(city="delhi", start=2021, end=2022):
    city_key = city.lower()
    print(f"Running pipeline for {city.title()} ({start} -> {end})")

    results_summary = {}

    for y_from in range(start, end):
        y_to = y_from + 1
        comp_label = f"{y_from} -> {y_to}"

        gdf = process_change_analysis(city=city_key, year_from=y_from, year_to=y_to)

        if gdf is not None and len(gdf) > 0:
            count = len(gdf)
            base_out = "output"
            geojson_path = f"{base_out}/{city_key}/{y_from}_{y_to}.geojson"

            save_geojson_to_db(geojson_path, city=city_key.title(), year_from=y_from, year_to=y_to)
            sync_geojson_to_public(geojson_path, city=city_key, year_from=y_from, year_to=y_to)
            results_summary[comp_label] = f"{count} polygons"
        else:
            results_summary[comp_label] = "PENDING"

    print("Pipeline finished.")
    return results_summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Master Satellite Pipeline")
    parser.add_argument("--city", type=str, default="delhi", help="City name")
    parser.add_argument("--start", type=int, default=2021, help="Start year")
    parser.add_argument("--end", type=int, default=2022, help="End year")

    args = parser.parse_args()
    run_master_pipeline(city=args.city, start=args.start, end=args.end)
