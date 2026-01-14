import requests
import json
import os


def get_shopping_admin_auth_token():
    ENDPOINT = os.getenv("WA_SHOPPING_API")
    response = requests.post(
        url=f"{ENDPOINT}/rest/default/V1/integration/admin/token",
        headers={"content-type": "application/json"},
        data=json.dumps({"username": "admin", "password": "admin1234"}),
    )
    return response.json()


def get_shopping_admin_admin_auth_token():
    # NOTE(Michael): SHOPPING_ADMIN uses the same environment variable as SHOPPING. This is how the APIs for Beyond Browsing are set up. This is OK because they are never hosted at the same time.
    ENDPOINT = os.getenv("WA_SHOPPING_API")
    response = requests.post(
        url=f"{ENDPOINT}/rest/default/V1/integration/admin/token",
        headers={"content-type": "application/json"},
        data=json.dumps({"username": "admin", "password": "admin1234"}),
    )
    return response.json()
