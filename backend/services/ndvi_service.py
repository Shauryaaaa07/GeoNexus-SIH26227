import numpy as np


def calculate_ndvi(red_band, nir_band):
    """
    NDVI calculate karta hai.

    Formula:
    NDVI = (NIR - RED) / (NIR + RED)
    """

    red = red_band.astype(np.float32)
    nir = nir_band.astype(np.float32)

    denominator = nir + red

    denominator = np.where(
        denominator == 0,
        1,
        denominator
    )

    ndvi = (
        (nir - red) /
        denominator
    )

    return ndvi


def calculate_ndvi_difference(
    before_red,
    before_nir,
    after_red,
    after_nir
):
    """
    Before aur after images ke NDVI ka difference.
    """

    before_ndvi = calculate_ndvi(
        before_red,
        before_nir
    )

    after_ndvi = calculate_ndvi(
        after_red,
        after_nir
    )

    ndvi_difference = (
        after_ndvi - before_ndvi
    )

    return {
        "before_ndvi": before_ndvi,
        "after_ndvi": after_ndvi,
        "ndvi_difference": ndvi_difference
    }


def classify_vegetation_change(ndvi_difference):
    """
    NDVI difference ke basis par
    vegetation change identify karta hai.
    """

    mean_difference = float(
        np.mean(ndvi_difference)
    )

    if mean_difference > 0.05:
        change_type = "Vegetation Increase"

    elif mean_difference < -0.05:
        change_type = "Vegetation Decrease"

    else:
        change_type = "No Significant Vegetation Change"

    return {
        "change_type": change_type,
        "mean_ndvi_difference": round(
            mean_difference,
            4
        )
    }