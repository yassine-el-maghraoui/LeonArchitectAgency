"""Enrich a places_search.py CSV with emails.

Two sources, in order:
1. Light scrape of the agency's website (free, unlimited): /, /contact, etc.
2. Hunter.io domain-search if HUNTER_API_KEY is set (free tier: 25 searches/month)
   — only used for domains where the scrape found nothing, pass --hunter to enable.

Usage:
    python3 enrich_emails.py outputs/leads/2026-07-10_real-estate-agency-athens.csv
    python3 enrich_emails.py <file.csv> --hunter

Output: same file with an _enriched.csv suffix, columns + email, email_source
"""

import argparse
import csv
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from _common import load_env, write_csv
import os

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
CONTACT_PATHS = ["", "/contact", "/contact-us", "/epikoinonia", "/επικοινωνία"]
SKIP_DOMAINS = {"facebook.com", "instagram.com", "linkedin.com", "google.com"}
UA = "Mozilla/5.0 (compatible; lead-research; +mailto:contact@example.com)"


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read(500_000).decode("utf-8", errors="ignore")
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        return ""


def scrape_site(website: str) -> str:
    base = website.rstrip("/")
    for path in CONTACT_PATHS:
        html = fetch(base + path)
        emails = [
            e for e in EMAIL_RE.findall(html)
            if not e.lower().endswith((".png", ".jpg", ".svg", ".webp", ".gif"))
        ]
        if emails:
            # prefer info@/contact@ if present, otherwise the first one found
            for e in emails:
                if e.lower().startswith(("info@", "contact@", "sales@")):
                    return e
            return emails[0]
    return ""


def hunter_lookup(domain: str, api_key: str) -> str:
    url = (
        "https://api.hunter.io/v2/domain-search?"
        + urllib.parse.urlencode({"domain": domain, "api_key": api_key, "limit": 1})
    )
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.load(resp)
    except (urllib.error.URLError, TimeoutError, OSError):
        return ""
    emails = data.get("data", {}).get("emails", [])
    return emails[0]["value"] if emails else ""


def domain_of(website: str) -> str:
    netloc = urllib.parse.urlparse(website).netloc.lower().removeprefix("www.")
    return "" if any(s in netloc for s in SKIP_DOMAINS) else netloc


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", type=Path)
    parser.add_argument("--hunter", action="store_true", help="Hunter.io fallback (25/month quota)")
    args = parser.parse_args()

    load_env()
    hunter_key = os.environ.get("HUNTER_API_KEY", "") if args.hunter else ""
    if args.hunter and not hunter_key:
        sys.exit("--hunter requested but HUNTER_API_KEY missing from .env")

    with args.csv_file.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        sys.exit("Empty CSV.")

    hunter_used = 0
    for i, row in enumerate(rows, 1):
        website = row.get("website", "")
        row["email"], row["email_source"] = "", ""
        if not website:
            continue
        email = scrape_site(website)
        if email:
            row["email"], row["email_source"] = email, "site"
        elif hunter_key:
            domain = domain_of(website)
            if domain:
                email = hunter_lookup(domain, hunter_key)
                hunter_used += 1
                if email:
                    row["email"], row["email_source"] = email, "hunter"
        print(f"[{i}/{len(rows)}] {row.get('name', '?')}: {row['email'] or '—'}")

    found = sum(1 for r in rows if r["email"])
    print(f"\n{found}/{len(rows)} emails found (Hunter called {hunter_used}x)")

    out = args.csv_file.with_name(args.csv_file.stem + "_enriched.csv")
    fieldnames = list(rows[0].keys())
    write_csv(out, rows, fieldnames)


if __name__ == "__main__":
    main()
