"""Cherche des entreprises via Google Places API (New) et sort un CSV.

Usage:
    python3 places_search.py --query "real estate agency" --city Athens --country GR
    python3 places_search.py --query "μεσιτικό γραφείο" --city Athens --country GR --max 60

Sortie: outputs/leads/YYYY-MM-DD_<slug>.csv
Colonnes: name, address, phone, website, google_maps_url, rating, reviews
"""

import argparse
import json
import re
import time
import urllib.request

from _common import output_path, require_key, write_csv

ENDPOINT = "https://places.googleapis.com/v1/places:searchText"
FIELD_MASK = ",".join(
    f"places.{f}"
    for f in (
        "displayName",
        "formattedAddress",
        "internationalPhoneNumber",
        "websiteUri",
        "googleMapsUri",
        "rating",
        "userRatingCount",
    )
) + ",nextPageToken"


def search(api_key: str, query: str, max_results: int) -> list[dict]:
    rows: list[dict] = []
    page_token = None
    while len(rows) < max_results:
        body: dict = {"textQuery": query, "pageSize": 20}
        if page_token:
            body["pageToken"] = page_token
        req = urllib.request.Request(
            ENDPOINT,
            data=json.dumps(body).encode(),
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": api_key,
                "X-Goog-FieldMask": FIELD_MASK,
            },
        )
        with urllib.request.urlopen(req) as resp:
            data = json.load(resp)
        for place in data.get("places", []):
            rows.append(
                {
                    "name": place.get("displayName", {}).get("text", ""),
                    "address": place.get("formattedAddress", ""),
                    "phone": place.get("internationalPhoneNumber", ""),
                    "website": place.get("websiteUri", ""),
                    "google_maps_url": place.get("googleMapsUri", ""),
                    "rating": place.get("rating", ""),
                    "reviews": place.get("userRatingCount", ""),
                }
            )
        page_token = data.get("nextPageToken")
        if not page_token:
            break
        time.sleep(1)  # le token de pagination met ~1s à devenir valide
    return rows[:max_results]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True, help='ex: "real estate agency"')
    parser.add_argument("--city", required=True, help="ex: Athens")
    parser.add_argument("--country", default="GR", help="code pays, ex: GR")
    parser.add_argument("--max", type=int, default=60, dest="max_results")
    args = parser.parse_args()

    api_key = require_key("GOOGLE_PLACES_API_KEY")
    full_query = f"{args.query} in {args.city}, {args.country}"
    rows = search(api_key, full_query, args.max_results)

    slug = re.sub(r"[^a-z0-9]+", "-", f"{args.query}-{args.city}".lower()).strip("-")
    write_csv(
        output_path(slug),
        rows,
        ["name", "address", "phone", "website", "google_maps_url", "rating", "reviews"],
    )


if __name__ == "__main__":
    main()
