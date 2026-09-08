
import rasterio
import rasterio.mask
import geopandas as gpd
import numpy as np


def get_mean(raster, geometry):

    data, _ = rasterio.mask.mask(
        raster,
        [geometry],
        crop=True,
        nodata=np.nan
    )

    data = data[0]
    data = data[np.isfinite(data)]

    if len(data) == 0:
        return 0.0

    return float(np.mean(data))


def classify(ndvi_change, ndwi_change, ndbi_change):

    # vegetation decrease + built-up increase
    if ndvi_change < -0.08 and ndbi_change > 0.08:
        return "New Buildings", "High"

    # strong built-up increase with little vegetation signal
    if ndbi_change > 0.12 and ndvi_change < 0.02:
        return "New Roads", "Medium"

    # vegetation change
    if abs(ndvi_change) > 0.10 and abs(ndvi_change) > abs(ndwi_change):
        return "Vegetation Change", "Medium"

    # water related change
    if abs(ndwi_change) > 0.10 and abs(ndwi_change) > abs(ndvi_change):
        return "Water Body Change", "Medium"

    # remaining land-use changes
    if abs(ndvi_change) > 0.05 or abs(ndwi_change) > 0.05:
        return "Agricultural / Land-use Change", "Low"

    return "Unclassified", "Low"


def main():

    geojson_file = "output/change_polygons_2021_2022.geojson"

    ndvi_2021 = "output/delhi_2021_ndvi.tif"
    ndwi_2021 = "output/delhi_2021_ndwi.tif"
    ndbi_2021 = "output/delhi_2021_ndbi.tif"

    ndvi_2022 = "output/delhi_2022_ndvi.tif"
    ndwi_2022 = "output/delhi_2022_ndwi.tif"
    ndbi_2022 = "output/delhi_2022_ndbi.tif"

    gdf = gpd.read_file(geojson_file)

    print("Polygons found:", len(gdf))
    print()

    src_ndvi21 = rasterio.open(ndvi_2021)
    src_ndwi21 = rasterio.open(ndwi_2021)
    src_ndbi21 = rasterio.open(ndbi_2021)

    src_ndvi22 = rasterio.open(ndvi_2022)
    src_ndwi22 = rasterio.open(ndwi_2022)
    src_ndbi22 = rasterio.open(ndbi_2022)

    categories = []
    confidences = []
    ndvi_changes = []
    ndwi_changes = []
    ndbi_changes = []

    print("Classification results")
    print("-" * 80)

    for i, row in gdf.iterrows():

        geom = row.geometry

        ndvi21 = get_mean(src_ndvi21, geom)
        ndvi22 = get_mean(src_ndvi22, geom)

        ndwi21 = get_mean(src_ndwi21, geom)
        ndwi22 = get_mean(src_ndwi22, geom)

        ndbi21 = get_mean(src_ndbi21, geom)
        ndbi22 = get_mean(src_ndbi22, geom)

        d_ndvi = ndvi22 - ndvi21
        d_ndwi = ndwi22 - ndwi21
        d_ndbi = ndbi22 - ndbi21

        category, confidence = classify(
            d_ndvi,
            d_ndwi,
            d_ndbi
        )

        categories.append(category)
        confidences.append(confidence)

        ndvi_changes.append(d_ndvi)
        ndwi_changes.append(d_ndwi)
        ndbi_changes.append(d_ndbi)

        print(
            "Polygon", i,
            "| Category:", category,
            "| Confidence:", confidence
        )

    src_ndvi21.close()
    src_ndwi21.close()
    src_ndbi21.close()

    src_ndvi22.close()
    src_ndwi22.close()
    src_ndbi22.close()

    gdf["category"] = categories
    gdf["confidence"] = confidences

    gdf["d_ndvi"] = ndvi_changes
    gdf["d_ndwi"] = ndwi_changes
    gdf["d_ndbi"] = ndbi_changes

    output_file = "output/change_polygons_classified.geojson"

    gdf.to_file(
        output_file,
        driver="GeoJSON"
    )

    print()
    print("Classification complete!")
    print("Saved:", output_file)


if __name__ == "__main__":
    main()

