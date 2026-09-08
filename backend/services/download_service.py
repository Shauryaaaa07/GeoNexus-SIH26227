import os
import requests
import zipfile

from services.copernicus_auth import get_access_token


DOWNLOAD_URL = (
    "https://download.dataspace.copernicus.eu"
    "/odata/v1/Products"
)

CATALOGUE_URL = (
    "https://catalogue.dataspace.copernicus.eu"
    "/odata/v1/Products"
)


# ==========================================
# Get Product UUID
# ==========================================

def get_product_uuid(product_name: str):

    token = get_access_token()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    if not product_name.endswith(".SAFE"):
        product_name = product_name + ".SAFE"

    params = {
        "$filter": f"Name eq '{product_name}'"
    }

    try:

        response = requests.get(
            CATALOGUE_URL,
            params=params,
            headers=headers,
            timeout=60
        )

        response.raise_for_status()

        data = response.json()

    except requests.RequestException as e:

        print(
            "Copernicus catalogue error:",
            e
        )

        return None

    products = data.get(
        "value",
        []
    )

    if not products:

        print(
            "Product not found:",
            product_name
        )

        return None

    product = products[0]

    return {
        "id": product.get("Id"),
        "name": product.get("Name"),
        "size": product.get("ContentLength"),
        "online": product.get("Online"),
        "s3_path": product.get("S3Path")
    }


# ==========================================
# Resumable Product Download
# ==========================================

def download_product(
    product_id: str,
    output_path: str
):
    """
    Copernicus product ko resumable download karta hai.

    Agar connection break ho jaye to existing
    partial file se download continue karega.
    """

    token = get_access_token()

    url = (
        f"{DOWNLOAD_URL}"
        f"({product_id})/$value"
    )

    folder = os.path.dirname(
        output_path
    )

    if folder:

        os.makedirs(
            folder,
            exist_ok=True
        )

    # --------------------------------------
    # Existing partial file check
    # --------------------------------------

    existing_size = 0

    if os.path.exists(output_path):

        existing_size = os.path.getsize(
            output_path
        )

    print(
        f"Existing downloaded size: "
        f"{existing_size / (1024 * 1024):.2f} MB"
    )

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Resume request
    if existing_size > 0:

        headers["Range"] = (
            f"bytes={existing_size}-"
        )

        print(
            "Resuming download..."
        )

    else:

        print(
            "Starting new download..."
        )

    try:

        response = requests.get(
            url,
            headers=headers,
            stream=True,
            timeout=(30, 300)
        )

        print(
            "Status:",
            response.status_code
        )

        # ----------------------------------
        # Server should return 206
        # when resuming
        # ----------------------------------

        if existing_size > 0:

            if response.status_code == 206:

                print(
                    "Resume supported."
                )

            elif response.status_code == 200:

                print(
                    "Server ignored Range request."
                )

                print(
                    "Restarting download..."
                )

                existing_size = 0

                response.close()

                headers.pop(
                    "Range",
                    None
                )

                response = requests.get(
                    url,
                    headers=headers,
                    stream=True,
                    timeout=(30, 300)
                )

                print(
                    "Restart status:",
                    response.status_code
                )

        response.raise_for_status()

        # ----------------------------------
        # Write mode
        # ----------------------------------

        if existing_size > 0:

            file_mode = "ab"

        else:

            file_mode = "wb"

        downloaded = existing_size

        # ----------------------------------
        # Total size
        # ----------------------------------

        content_length = response.headers.get(
            "Content-Length"
        )

        if content_length:

            total_size = (
                downloaded +
                int(content_length)
            )

        else:

            total_size = None

        # ----------------------------------
        # Download chunks
        # ----------------------------------

        with open(
            output_path,
            file_mode
        ) as file:

            for chunk in response.iter_content(
                chunk_size=1024 * 1024
            ):

                if not chunk:
                    continue

                file.write(chunk)

                downloaded += len(chunk)

                if total_size:

                    percent = (
                        downloaded /
                        total_size
                    ) * 100

                    print(
                        f"Downloaded: "
                        f"{downloaded / (1024 * 1024):.2f} MB "
                        f"/ "
                        f"{total_size / (1024 * 1024):.2f} MB "
                        f"({percent:.1f}%)",
                        end="\r"
                    )

                else:

                    print(
                        f"Downloaded: "
                        f"{downloaded / (1024 * 1024):.2f} MB",
                        end="\r"
                    )

        print(
            "\nDownload completed."
        )

        return output_path

    except requests.RequestException as e:

        print(
            "\nDownload failed:",
            e
        )

        # IMPORTANT:
        # Partial file ko delete nahi karna.
        # Next attempt isi file se resume karega.

        print(
            "Partial download preserved."
        )

        return None

    except Exception as e:

        print(
            "\nUnexpected download error:",
            e
        )

        print(
            "Partial download preserved."
        )

        return None


# ==========================================
# Extract Required RGB Bands
# ==========================================

def extract_required_bands(
    zip_path: str,
    extract_dir: str
):
    """
    Copernicus ZIP se required RGB bands extract karta hai.

    B02 = Blue
    B03 = Green
    B04 = Red
    """

    if not os.path.exists(zip_path):

        print(
            "ZIP file not found:",
            zip_path
        )

        return False

    os.makedirs(
        extract_dir,
        exist_ok=True
    )

    required_bands = (
        "_B02_10m.jp2",
        "_B03_10m.jp2",
        "_B04_10m.jp2"
    )

    extracted = []

    try:

        with zipfile.ZipFile(
            zip_path,
            "r"
        ) as archive:

            for file_name in archive.namelist():

                if file_name.endswith(
                    required_bands
                ):

                    archive.extract(
                        file_name,
                        extract_dir
                    )

                    extracted.append(
                        file_name
                    )

        print(
            "\nExtracted RGB bands:"
        )

        for file_name in extracted:

            print(
                file_name
            )

        if len(extracted) < 3:

            print(
                "Required RGB bands are incomplete."
            )

            return False

        print(
            "RGB bands extracted successfully."
        )

        return True

    except zipfile.BadZipFile:

        print(
            "Invalid ZIP file:",
            zip_path
        )

        return False

    except Exception as e:

        print(
            "Band extraction failed:",
            e
        )

        return False