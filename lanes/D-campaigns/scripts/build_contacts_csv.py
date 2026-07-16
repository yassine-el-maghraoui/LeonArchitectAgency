"""Classify a contact list into the 15 canonical professional groups
(config/professional_groups.json) by keyword matching on profession/
category, then produce the Mailchimp CSV expected by the campaign.

This is a first automatic pass, not a final judgment call: any row
without a clear match is flagged REVIEW_STATUS=REVIEW for a human check
(Leon or Claude), per TASK.md.

Usage:
    python3 build_contacts_csv.py --input contacts.csv --out 03_mailchimp_contacts_by_group.csv

The input CSV must be a plain CSV export (not .xlsx — export the Excel
sheet to UTF-8 CSV first, no extra Python dependency required).
Expected columns (case-insensitive, variants tolerated):
    EMAIL, COMPANY (or NAME), PROFESSION (or CATEGORY), FNAME, LNAME,
    MASTER_ID (or any identifier), PRIORITY

Never modifies the source file.
"""

import argparse
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
GROUPS_FILE = REPO_ROOT / "lanes" / "D-campaigns" / "config" / "professional_groups.json"

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

OUT_FIELDS = [
    "EMAIL", "COMPANY", "FNAME", "LNAME", "CATEGORY", "PROFESSION",
    "CAMPAIGN_GROUP", "MAILCHIMP_TAG", "PRIORITY", "SOURCE_MASTER_ID",
    "REVIEW_STATUS", "REVIEW_NOTES",
]


def col(row: dict, *names: str) -> str:
    lower = {k.lower(): v for k, v in row.items()}
    for name in names:
        if name.lower() in lower and lower[name.lower()]:
            return str(lower[name.lower()]).strip()
    return ""


def strip_accents(text: str) -> str:
    # normalize Greek tonos marks (and Latin accents) for robust matching:
    # "δικηγόρ" must match "δικηγορικό" despite the different declension/accent.
    decomposed = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn")


def match_group(text: str, groups: list[dict]) -> dict | None:
    text_norm = strip_accents(text)
    for group in groups:
        for kw in group["keywords_match"]:
            if strip_accents(kw) in text_norm:
                return group
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    groups = json.loads(GROUPS_FILE.read_text(encoding="utf-8"))["groups"]

    with args.input.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        sys.exit("Input CSV is empty.")

    out_rows = []
    seen_emails: set[str] = set()
    stats = {"matched": 0, "review": 0, "no_email": 0, "duplicate": 0}

    for row in rows:
        email = col(row, "email").lower()
        if not email or not EMAIL_RE.match(email):
            stats["no_email"] += 1
            continue
        if email in seen_emails:
            stats["duplicate"] += 1
            continue
        seen_emails.add(email)

        profession = col(row, "profession", "category", "services", "notes")
        group = match_group(profession, groups)

        if group:
            stats["matched"] += 1
            review_status, review_notes = "REVIEW", "auto-matched, needs confirmation"
        else:
            stats["review"] += 1
            review_status, review_notes = "REVIEW", "no group found automatically"

        out_rows.append({
            "EMAIL": email,
            "COMPANY": col(row, "company", "name"),
            "FNAME": col(row, "fname", "first_name"),
            "LNAME": col(row, "lname", "last_name"),
            "CATEGORY": col(row, "category"),
            "PROFESSION": profession,
            "CAMPAIGN_GROUP": group["label_el"] if group else "",
            "MAILCHIMP_TAG": group["mailchimp_tag"] if group else "",
            "PRIORITY": col(row, "priority"),
            "SOURCE_MASTER_ID": col(row, "master_id", "master id", "id"),
            "REVIEW_STATUS": review_status,
            "REVIEW_NOTES": review_notes,
        })

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUT_FIELDS)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"{len(out_rows)} contacts written -> {args.out}")
    print(
        f"  matched (needs confirmation): {stats['matched']} | "
        f"no group (REVIEW): {stats['review']} | "
        f"no valid email (skipped): {stats['no_email']} | "
        f"duplicates (skipped): {stats['duplicate']}"
    )
    print("Every row is flagged REVIEW by default — human confirmation required before sending (TASK.md rule).")


if __name__ == "__main__":
    main()
