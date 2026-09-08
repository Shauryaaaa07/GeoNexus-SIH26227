import os
import requests
from dotenv import load_dotenv


# ==========================================
# Load Environment Variables
# ==========================================

load_dotenv()


# ==========================================
# Copernicus Authentication URL
# ==========================================

TOKEN_URL = (
    "https://identity.dataspace.copernicus.eu/"
    "auth/realms/CDSE/protocol/openid-connect/token"
)


# ==========================================
# Get Access Token
# ==========================================

def get_access_token():

    username = os.getenv(
        "COPERNICUS_USERNAME"
    )

    password = os.getenv(
        "COPERNICUS_PASSWORD"
    )


    # ==========================================
    # Check Credentials
    # ==========================================

    if not username:
        raise ValueError(
            "COPERNICUS_USERNAME is not configured"
        )

    if not password:
        raise ValueError(
            "COPERNICUS_PASSWORD is not configured"
        )


    # ==========================================
    # Authentication Data
    # ==========================================

    data = {

        "client_id": "cdse-public",

        "grant_type": "password",

        "username": username,

        "password": password
    }


    # ==========================================
    # Request Token
    # ==========================================

    response = requests.post(
        TOKEN_URL,
        data=data,
        timeout=60
    )


    # ==========================================
    # Check Response
    # ==========================================

    if response.status_code != 200:

        raise Exception(
            "Copernicus authentication failed: "
            f"{response.text}"
        )


    # ==========================================
    # Extract Token
    # ==========================================

    token_data = response.json()

    access_token = token_data.get(
        "access_token"
    )


    if not access_token:

        raise Exception(
            "Access token not found in response"
        )


    return access_token