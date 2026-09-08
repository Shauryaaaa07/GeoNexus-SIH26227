import cv2


def mask_to_geojson(
    change_mask,
    bbox,
    min_area=100,
    max_features=100
):
    """
    Change mask ko geographic GeoJSON polygons mein convert karta hai.

    bbox format:
    [min_lon, min_lat, max_lon, max_lat]

    max_features:
    Maximum change polygons jo GeoJSON mein return honge.
    """

    min_lon, min_lat, max_lon, max_lat = bbox

    height, width = change_mask.shape

    contours, _ = cv2.findContours(
        change_mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    # Bade change areas ko pehle rakho
    contours = sorted(
        contours,
        key=cv2.contourArea,
        reverse=True
    )

    features = []

    for contour in contours:

        # Maximum polygons limit
        if len(features) >= max_features:
            break

        area = cv2.contourArea(contour)

        if area < min_area:
            continue

        # Polygon ko simplify karo
        perimeter = cv2.arcLength(
            contour,
            True
        )

        epsilon = 0.01 * perimeter

        simplified_contour = cv2.approxPolyDP(
            contour,
            epsilon,
            True
        )

        polygon = []

        for point in simplified_contour:

            x, y = point[0]

            lon = min_lon + (
                x / width
            ) * (max_lon - min_lon)

            lat = max_lat - (
                y / height
            ) * (max_lat - min_lat)

            polygon.append([
                float(lon),
                float(lat)
            ])

        if len(polygon) < 3:
            continue

        if polygon[0] != polygon[-1]:
            polygon.append(polygon[0])

        features.append({
            "type": "Feature",

            "properties": {
                "change": "Detected Change",
                "pixel_area": round(
                    float(area),
                    2
                )
            },

            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    polygon
                ]
            }
        })

    return {
        "type": "FeatureCollection",
        "features": features
    }