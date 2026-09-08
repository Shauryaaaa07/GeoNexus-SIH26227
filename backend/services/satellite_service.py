try:
    from pystac_client import Client
    from pystac_client.exceptions import APIError
    STAC_URL = "https://stac.dataspace.copernicus.eu/v1/"
    try:
        catalog = Client.open(STAC_URL)
    except Exception:
        catalog = None
except ImportError:
    Client = None
    APIError = Exception
    catalog = None



# ==========================================
# Search Sentinel-2 Images
# ==========================================

def search_sentinel_images(
    bbox: list,
    start_date: str,
    end_date: str,
    max_cloud_cover: float = 30
):
    """
    Search Sentinel-2 L2A images from
    Copernicus STAC.
    """

    try:

        search = catalog.search(
            collections=["sentinel-2-l2a"],
            bbox=bbox,
            datetime=f"{start_date}/{end_date}",
            query={
                "eo:cloud_cover": {
                    "lt": max_cloud_cover
                }
            }
        )

        items = search.item_collection()

    except APIError as e:

        print("Copernicus STAC API error:", e)

        return []

    except Exception as e:

        print("Satellite search error:", e)

        return []


    results = []

    for item in items:

        # ------------------------------------------
        # Get B04 and B08 assets
        # ------------------------------------------

        red_asset = item.assets.get("B04_10m")
        nir_asset = item.assets.get("B08_10m")


        results.append({

            # --------------------------------------
            # Basic information
            # --------------------------------------

            "id": item.id,

            "date": (
                item.datetime.isoformat()
                if item.datetime
                else None
            ),

            "cloud_cover": item.properties.get(
                "eo:cloud_cover"
            ),

            "collection": item.collection_id,


            # --------------------------------------
            # Satellite
            # --------------------------------------

            "satellite": "Sentinel-2",


            # --------------------------------------
            # Bands
            # --------------------------------------

            "bands": {

                "red": (
                    red_asset.href
                    if red_asset
                    else None
                ),

                "nir": (
                    nir_asset.href
                    if nir_asset
                    else None
                )
            }

        })


    return results


# ==========================================
# Select Best Image
# ==========================================

def select_best_image(images: list):
    """
    Select image having the lowest cloud cover.
    """

    if not images:
        return None


    valid_images = [
        image
        for image in images
        if image.get("cloud_cover") is not None
    ]


    if not valid_images:
        return images[0]


    return min(
        valid_images,
        key=lambda image: image["cloud_cover"]
    )


# ==========================================
# Search Best Image For A Year
# ==========================================

def search_best_image_for_year(
    bbox: list,
    year: int,
    max_cloud_cover: float = 30
):
    """
    Automatically search the best Sentinel-2
    image for a complete year.
    """

    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"


    images = search_sentinel_images(
        bbox=bbox,
        start_date=start_date,
        end_date=end_date,
        max_cloud_cover=max_cloud_cover
    )


    if not images:
        return None


    return select_best_image(images)


# ==========================================
# Get Best Product For A Specific Year
# ==========================================

def get_best_product_for_year(
    bbox: list,
    year: int,
    max_cloud_cover: float = 30
):
    """
    Find the best Sentinel-2 image for a year
    and get its Copernicus OData product details.
    """

    from services.download_service import get_product_uuid


    # ------------------------------------------
    # Find best STAC image
    # ------------------------------------------

    image = search_best_image_for_year(
        bbox=bbox,
        year=year,
        max_cloud_cover=max_cloud_cover
    )


    if image is None:
        return None


    # ------------------------------------------
    # Product name
    # ------------------------------------------

    product_name = image["id"]


    # ------------------------------------------
    # Get OData product information
    # ------------------------------------------

    product = get_product_uuid(
        product_name
    )


    if product is None:
        return None


    # ------------------------------------------
    # Combine STAC + OData
    # ------------------------------------------

    return {

        "year": year,

        "image": image,

        "product": product

    }


# ==========================================
# Search Multiple Years
# ==========================================

def search_images_for_years(
    bbox: list,
    start_year: int,
    end_year: int,
    max_cloud_cover: float = 30
):
    """
    Automatically search best image for
    every year in a given range.
    """

    results = []


    for year in range(
        start_year,
        end_year + 1
    ):

        print(
            f"Searching Sentinel-2 image for {year}..."
        )


        best_image = search_best_image_for_year(
            bbox=bbox,
            year=year,
            max_cloud_cover=max_cloud_cover
        )


        results.append({

            "year": year,

            "image": best_image

        })


    return results


# ==========================================
# Search Multiple Cities + Multiple Years
# ==========================================

def search_all_city_year_images(
    locations: dict,
    start_year: int = 2020,
    end_year: int = 2026,
    max_cloud_cover: float = 30
):
    """
    Automatically search satellite images
    for all cities and all years.
    """

    all_results = {}


    for city_id, city_data in locations.items():

        print(
            f"\nSearching images for "
            f"{city_data['name']}..."
        )


        city_results = search_images_for_years(

            bbox=city_data["bbox"],

            start_year=start_year,

            end_year=end_year,

            max_cloud_cover=max_cloud_cover

        )


        all_results[city_id] = {

            "name": city_data["name"],

            "center": city_data["center"],

            "bbox": city_data["bbox"],

            "years": city_results

        }


    return all_results


# ==========================================
# Get Before And After Images
# ==========================================

def get_before_after_images(
    bbox: list,
    start_date: str,
    end_date: str,
    max_cloud_cover: float = 30
):
    """
    Search satellite images between two dates
    and select best before and after images.
    """

    images = search_sentinel_images(

        bbox=bbox,

        start_date=start_date,

        end_date=end_date,

        max_cloud_cover=max_cloud_cover

    )


    if not images:

        return {

            "before": None,

            "after": None,

            "count": 0

        }


    # ==========================================
    # Sort Images By Date
    # ==========================================

    images = sorted(

        images,

        key=lambda image: image["date"]

    )


    # ==========================================
    # Divide Images
    # ==========================================

    middle = len(images) // 2


    before_images = images[:middle]

    after_images = images[middle:]


    # ==========================================
    # Select Best Images
    # ==========================================

    before_image = select_best_image(
        before_images
    )


    after_image = select_best_image(
        after_images
    )


    # ==========================================
    # Return
    # ==========================================

    return {

        "before": before_image,

        "after": after_image,

        "count": len(images)

    }