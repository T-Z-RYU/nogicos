import os

# needed for some of the evaluations
host = "http://" + os.environ.get("IP", "127.0.0.1")

# For parallelization, we could create batches of ports that we offset.
SHOPPING = os.getenv("SHOPPING", f"{host}:7770")
SHOPPING_ADMIN = os.getenv("SHOPPING_ADMIN", f"{host}:7780") + "/admin"
REDDIT = os.getenv("REDDIT", f"{host}:9999")
GITLAB = os.getenv("GITLAB", f"{host}:8023")
MAP = os.getenv("MAP", f"{host}:3000")
WIKIPEDIA = os.getenv(
    "WIKIPEDIA",
    f"{host}:8888/wikipedia_en_all_maxi_2022-05/A/User:The_other_Kiwix_guy/Landing",
)
HOMEPAGE = os.getenv("HOMEPAGE", f"{host}:4399")
CLASSIFIEDS = os.getenv("CLASSIFIEDS", f"{host}:9980")

SITES = {
    "SHOPPING": SHOPPING,
    "SHOPPING_ADMIN": SHOPPING_ADMIN,
    "REDDIT": REDDIT,
    "GITLAB": GITLAB,
    "MAP": MAP,
    "WIKIPEDIA": WIKIPEDIA,
    "HOMEPAGE": HOMEPAGE,
    "CLASSIFIEDS": CLASSIFIEDS,
}

# From WebArena site.
ACCOUNTS = {
    "reddit": {"username": "MarvelsGrantMan136", "password": "test1234"},
    "gitlab": {"username": "byteblaze", "password": "hello1234"},
    "shopping": {
        "username": "emma.lopez@gmail.com",
        "password": "Password.123",
    },
    "shopping_admin": {"username": "admin", "password": "admin1234"},
    "shopping_site_admin": {"username": "admin", "password": "admin1234"},
}


def _resolve_start_url(start_url: str):
    # Replaces variables like "__REDDIT__" with the actual URL.
    substitutions = {"__" + key + "__": value for key, value in SITES.items()}
    for key, value in substitutions.items():
        start_url = start_url.replace(key, value)
    return start_url
