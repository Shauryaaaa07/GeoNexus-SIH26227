import cv2
import numpy as np


# ==========================================
# Preprocess Image
# ==========================================

def preprocess_image(image):
    """
    Satellite image ko analysis ke liye prepare karta hai.

    Steps:
    1. Grayscale conversion
    2. Noise reduction
    3. Normalization
    """

    # Color image ko grayscale mein convert karo
    if len(image.shape) == 3:
        image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

    # Small noise remove karo
    image = cv2.GaussianBlur(
        image,
        (5, 5),
        0
    )

    # Pixel values 0-255 mein normalize karo
    image = cv2.normalize(
        image,
        None,
        0,
        255,
        cv2.NORM_MINMAX
    )

    return image


# ==========================================
# Image Alignment
# ==========================================

def align_images(before, after):
    """
    Before aur after images ko same size mein karta hai.
    """

    after = cv2.resize(
        after,
        (before.shape[1], before.shape[0]),
        interpolation=cv2.INTER_LINEAR
    )

    return before, after


# ==========================================
# Change Detection
# ==========================================

def detect_changes(
    before_image,
    after_image,
    threshold=30
):
    """
    Before aur after satellite images ka
    basic image-difference based change detection.

    Returns:
    - changed pixels
    - total pixels
    - change percentage
    - change mask
    """

    # --------------------------------------
    # Preprocessing
    # --------------------------------------

    before = preprocess_image(
        before_image
    )

    after = preprocess_image(
        after_image
    )


    # --------------------------------------
    # Image Alignment / Resize
    # --------------------------------------

    before, after = align_images(
        before,
        after
    )


    # --------------------------------------
    # Calculate Difference
    # --------------------------------------

    difference = cv2.absdiff(
        before,
        after
    )


    # --------------------------------------
    # Threshold
    # --------------------------------------

    _, change_mask = cv2.threshold(
        difference,
        threshold,
        255,
        cv2.THRESH_BINARY
    )


    # --------------------------------------
    # Remove Small Noise
    # --------------------------------------

    kernel = np.ones(
        (3, 3),
        np.uint8
    )

    change_mask = cv2.morphologyEx(
        change_mask,
        cv2.MORPH_OPEN,
        kernel
    )

    change_mask = cv2.morphologyEx(
        change_mask,
        cv2.MORPH_CLOSE,
        kernel
    )


    # --------------------------------------
    # Calculate Statistics
    # --------------------------------------

    changed_pixels = int(
        np.count_nonzero(change_mask)
    )

    total_pixels = int(
        change_mask.size
    )

    change_percentage = (
        changed_pixels /
        total_pixels
    ) * 100


    # --------------------------------------
    # Return Result
    # --------------------------------------

    return {
        "changed_pixels": changed_pixels,

        "total_pixels": total_pixels,

        "change_percentage": round(
            change_percentage,
            2
        ),

        "change_mask": change_mask
    }


# ==========================================
# Change Classification
# ==========================================

def classify_change(change_percentage):
    """
    Prototype classification.

    NOTE:
    Ye actual AI/visual classification nahi hai.
    Sirf change percentage ke basis par
    provisional category deta hai.
    """

    if change_percentage < 2:

        return "Vegetation Change"

    elif change_percentage < 5:

        return "New Roads"

    elif change_percentage < 10:

        return "New Buildings"

    elif change_percentage < 20:

        return "Water Body Change"

    else:

        return "Land-use Change"