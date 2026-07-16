"""Run the full pipeline (places_search -> enrich_emails -> verify_mx)
for EVERY city x segment combination defined in config/targets.yaml,
then consolidate everything into a single CSV.

Don't edit this script to add a city/segment: edit config/targets.yaml
instead (see CLAUDE.md).

Usage:
    python3 run_batch.py                       # every city x every segment
    python3 run_batch.py --segment real-estate # a single segment
    python3 run_batch.py --max-per-query 60 --hunter

Output: one run per city x segment x query_term (same as a manual
places_search.py run), plus a consolidated + deduplicated CSV:
    outputs/leads/YYYY-MM-DD_batch-all.csv
"""

import argparse
import csv
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

from _common import OUTPUT_DIR
from _targets import load_targets

SCRIPTS_DIR = Path(__file__).resolve().parent


def run(cmd: list[str]) -> None:
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=SCRIPTS_DIR)
    if result.returncode != 0:
        print(f"  -> failed (code {result.returncode}), continuing with the rest of the batch", file=sys.stderr)


def latest_csv(slug_fragment: str) -> Path | None:
    today = date.today().isoformat()
    candidates = sorted(OUTPUT_DIR.glob(f"{today}_*{slug_fragment}*_verified.csv"))
    return candidates[-1] if candidates else None


def consolidate(files: list[Path]) -> Path:
    seen_emails: set[str] = set()
    seen_names_no_email: set[tuple] = set()
    rows: list[dict] = []
    fieldnames: list[str] = []

    for f in files:
        with f.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            if not fieldnames:
                fieldnames = reader.fieldnames or []
            for row in reader:
                email = (row.get("email") or "").strip().lower()
                if email:
                    if email in seen_emails:
                        continue
                    seen_emails.add(email)
                else:
                    key = (row.get("name", "").strip().lower(), row.get("address", "").strip().lower())
                    if key in seen_names_no_email:
                        continue
                    seen_names_no_email.add(key)
                rows.append(row)

    out = OUTPUT_DIR / f"{date.today().isoformat()}_batch-all.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n{len(rows)} consolidated (deduplicated) rows -> {out}")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--segment", help="segment id (e.g. real-estate) — otherwise all")
    parser.add_argument("--city", help="city name — otherwise all cities in targets.yaml")
    parser.add_argument("--max-per-query", type=int, default=60)
    parser.add_argument("--hunter", action="store_true", help="enable the Hunter.io fallback (limited quota)")
    args = parser.parse_args()

    targets = load_targets()
    segments = [s for s in targets["segments"] if not args.segment or s["id"] == args.segment]
    cities = [c for c in targets["cities"] if not args.city or c["name"] == args.city]
    if not segments:
        sys.exit(f"Segment '{args.segment}' not found in config/targets.yaml")
    if not cities:
        sys.exit(f"City '{args.city}' not found in config/targets.yaml")

    produced: list[Path] = []
    for city in cities:
        for segment in segments:
            for term in segment["query_terms"]:
                run([
                    "python3", "places_search.py",
                    "--query", term,
                    "--city", city["name"],
                    "--country", city.get("country", "GR"),
                    "--max", str(args.max_per_query),
                ])
                slug = re.sub(r"[^a-z0-9]+", "-", f"{term}-{city['name']}".lower()).strip("-")
                raw = OUTPUT_DIR / f"{date.today().isoformat()}_{slug}.csv"
                if not raw.exists():
                    continue
                enrich_cmd = ["python3", "enrich_emails.py", str(raw)]
                if args.hunter:
                    enrich_cmd.append("--hunter")
                run(enrich_cmd)
                enriched = raw.with_name(raw.stem + "_enriched.csv")
                if not enriched.exists():
                    continue
                run(["python3", "verify_mx.py", str(enriched)])
                verified = raw.with_name(raw.stem + "_verified.csv")
                if verified.exists():
                    produced.append(verified)

    if not produced:
        sys.exit("No results produced — check the API keys in .env")
    consolidate(produced)


if __name__ == "__main__":
    main()
