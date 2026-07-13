"""Scrape la Meta Ad Library via Apify (actor officiel apify/facebook-ads-scraper).

Usage:
    python3 meta_ads.py --keyword "architecture" --country GR --max 20
    python3 meta_ads.py --page-url "https://www.facebook.com/SomeAgency" --max 30

Sortie: outputs/competitors/YYYY-MM-DD_ads-<slug>.md (rapport lisible, trié par
durée de diffusion décroissante — les ads qui tournent longtemps sont les rentables)
+ JSON brut à côté pour analyse ultérieure.

Coût: pay-per-event Apify, ~centimes pour 20 ads. Free tier 5$/mois = large.
"""

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "B-lead-gen" / "scripts"))
from _common import REPO_ROOT, require_key

ACTOR = "apify~facebook-ads-scraper"
OUTPUT_DIR = REPO_ROOT / "outputs" / "competitors"


def build_library_url(keyword: str, country: str) -> str:
    params = {
        "active_status": "active",
        "ad_type": "all",
        "country": country,
        "q": keyword,
        "search_type": "keyword_unordered",
        "media_type": "all",
    }
    return "https://www.facebook.com/ads/library/?" + urllib.parse.urlencode(params)


def run_actor(token: str, start_url: str, max_results: int) -> list[dict]:
    body = json.dumps({"startUrls": [{"url": start_url}], "resultsLimit": max_results}).encode()
    req = urllib.request.Request(
        f"https://api.apify.com/v2/acts/{ACTOR}/run-sync-get-dataset-items?token={token}&timeout=240",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=280) as resp:
        return json.load(resp)


def days_running(ad: dict) -> int:
    raw = ad.get("startDateFormatted", "")
    if not raw:
        return 0
    start = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    return (datetime.now(timezone.utc) - start).days


def to_report(ads: list[dict], source: str) -> str:
    ads = sorted(ads, key=days_running, reverse=True)
    lines = [
        f"# Meta Ad Library — {source}",
        f"\n{len(ads)} ads actives, triées par durée de diffusion (longue durée ≈ rentable).\n",
    ]
    for ad in ads:
        snap = ad.get("snapshot", {}) or {}
        text = ((snap.get("body") or {}).get("text") or "").strip()
        page = ad.get("pageName") or snap.get("pageName") or "?"
        days = days_running(ad)
        platforms = ", ".join(ad.get("publisherPlatform") or [])
        cta = snap.get("ctaText") or ""
        fmt = snap.get("displayFormat") or ""
        lib_link = f"https://www.facebook.com/ads/library/?id={ad.get('adArchiveID', '')}"
        lines += [
            f"## {page} — en ligne depuis {days} jours",
            f"- Format: {fmt} | Plateformes: {platforms} | CTA: {cta}",
            f"- Lien: {lib_link}",
            f"\n> {text[:400] or '(pas de texte — ad visuelle)'}\n",
        ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--keyword", help='ex: "architecture" ou nom du concurrent')
    group.add_argument("--page-url", help="URL de la page Facebook du concurrent")
    parser.add_argument("--country", default="GR")
    parser.add_argument("--max", type=int, default=20, dest="max_results")
    args = parser.parse_args()

    token = require_key("APIFY_TOKEN")
    if args.keyword:
        start_url = build_library_url(args.keyword, args.country)
        source, slug_base = f'"{args.keyword}" ({args.country})', args.keyword
    else:
        start_url, source, slug_base = args.page_url, args.page_url, args.page_url.split("/")[-1]

    print(f"Scrape en cours ({args.max_results} ads max)...")
    ads = run_actor(token, start_url, args.max_results)
    if not ads:
        sys.exit("0 ads trouvées — vérifier le mot-clé/URL ou le pays.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^\w]+", "-", slug_base.lower(), flags=re.UNICODE).strip("-") or "ads"
    base = OUTPUT_DIR / f"{date.today().isoformat()}_ads-{slug}"
    base.with_suffix(".json").write_text(json.dumps(ads, ensure_ascii=False, indent=1))
    base.with_suffix(".md").write_text(to_report(ads, source))
    print(f"{len(ads)} ads -> {base}.md (+ .json brut)")


if __name__ == "__main__":
    main()
