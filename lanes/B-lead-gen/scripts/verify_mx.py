"""Vérification email gratuite: syntaxe + enregistrement MX du domaine.

Pas une vérification SMTP complète (ça, c'est ZeroBounce/NeverBounce, payant),
mais élimine domaines morts et typos — suffisant pour une v1.

Usage:
    python3 verify_mx.py outputs/leads/2026-07-10_..._enriched.csv

Sortie: même fichier avec suffixe _verified.csv, colonne + email_status
(valid_mx | no_mx | bad_syntax | empty)
"""

import argparse
import csv
import re
import subprocess
import sys
from pathlib import Path

from _common import write_csv

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def has_mx(domain: str, cache: dict) -> bool:
    if domain in cache:
        return cache[domain]
    result = subprocess.run(
        ["dig", "+short", "MX", domain],
        capture_output=True, text=True, timeout=10,
    )
    ok = bool(result.stdout.strip())
    cache[domain] = ok
    return ok


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", type=Path)
    args = parser.parse_args()

    with args.csv_file.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        sys.exit("CSV vide.")

    cache: dict = {}
    for row in rows:
        email = row.get("email", "").strip()
        if not email:
            row["email_status"] = "empty"
        elif not EMAIL_RE.match(email):
            row["email_status"] = "bad_syntax"
        elif has_mx(email.split("@")[1], cache):
            row["email_status"] = "valid_mx"
        else:
            row["email_status"] = "no_mx"

    valid = sum(1 for r in rows if r["email_status"] == "valid_mx")
    print(f"{valid}/{len(rows)} emails avec MX valide")

    out = args.csv_file.with_name(args.csv_file.stem.replace("_enriched", "") + "_verified.csv")
    write_csv(out, rows, list(rows[0].keys()))


if __name__ == "__main__":
    main()
