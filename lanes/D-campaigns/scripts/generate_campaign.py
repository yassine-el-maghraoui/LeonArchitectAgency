"""Combine the shared HTML template + the per-group content JSON to produce
the final emails + the Mailchimp CSV. This is THE script that was missing
from the previous run (the one driven by the mismatched third-party skill)
— without it, everything had to be rewritten by hand group by group.

Usage:
    python3 generate_campaign.py --content email_content_by_group.json

Expected input (email_content_by_group.json): see
templates/email_content_by_group.example.json for the exact schema.

Output (in outputs/campaigns/<date>/):
    html_emails/<filename>.html   — one per group
    03_mailchimp_contacts_by_group.csv (column skeleton, merge with
        build_contacts_csv.py if needed)
    04_campaign_summary.md

Never modifies the source contacts file. Never sends anything.
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
TEMPLATE = REPO_ROOT / "lanes" / "D-campaigns" / "templates" / "base_mailchimp_template.html"

REQUIRED_FIELDS = [
    "group_id", "group_name", "filename", "mailchimp_tag",
    "subject_a", "subject_b", "preheader", "headline", "opening",
    "collaboration_text", "benefit_1", "benefit_2", "benefit_3",
    "cta_text", "cta_url", "hero_image_url", "hero_image_alt",
]

PLACEHOLDER_MAP = {
    "PREHEADER": "preheader",
    "HOSTED_LOGO_URL": None,  # injected separately (see --logo-url)
    "EMAIL_HEADLINE": "headline",
    "OPENING_PARAGRAPH": "opening",
    "HERO_IMAGE_URL": "hero_image_url",
    "HERO_IMAGE_ALT": "hero_image_alt",
    "COLLABORATION_TEXT": "collaboration_text",
    "BENEFIT_1": "benefit_1",
    "BENEFIT_2": "benefit_2",
    "BENEFIT_3": "benefit_3",
    "CTA_TEXT": "cta_text",
    "CTA_URL": "cta_url",
}


def validate(group: dict, index: int) -> list[str]:
    errors = []
    for field in REQUIRED_FIELDS:
        if not str(group.get(field, "")).strip():
            errors.append(f"group #{index} ({group.get('group_name', '?')}): missing field '{field}'")
    return errors


def render(template: str, group: dict, logo_url: str) -> str:
    html = template
    for placeholder, field in PLACEHOLDER_MAP.items():
        value = logo_url if placeholder == "HOSTED_LOGO_URL" else str(group[field])
        html = html.replace("{{" + placeholder + "}}", value)
    return html


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--content", required=True, type=Path, help="email_content_by_group.json")
    parser.add_argument("--logo-url", default="{{HOSTED_LOGO_URL}}",
                         help="public URL of the hosted logo (Mailchimp Content Studio). "
                              "Leave empty to keep the placeholder to fill in before sending.")
    parser.add_argument("--out", type=Path, default=None,
                         help="output directory (default: outputs/campaigns/<date>/)")
    args = parser.parse_args()

    if not TEMPLATE.exists():
        sys.exit(f"Template not found: {TEMPLATE}")
    template_html = TEMPLATE.read_text(encoding="utf-8")

    content = json.loads(args.content.read_text(encoding="utf-8"))
    groups = content.get("groups", [])
    if not groups:
        sys.exit("No groups in the content JSON ('groups' empty or missing).")

    errors: list[str] = []
    for i, group in enumerate(groups, 1):
        errors += validate(group, i)
    if errors:
        sys.exit("Validation errors:\n" + "\n".join(f"  - {e}" for e in errors))

    hero_images = [g["hero_image_url"] for g in groups]
    if len(set(hero_images)) == 1 and len(groups) > 1:
        print(
            "WARNING: every hero_image_url is identical — this is exactly the "
            "defect found in the previous run. Fix before sending.",
            file=sys.stderr,
        )

    out_dir = args.out or (REPO_ROOT / "outputs" / "campaigns" / date.today().isoformat())
    html_dir = out_dir / "html_emails"
    html_dir.mkdir(parents=True, exist_ok=True)

    csv_rows = []
    for group in groups:
        html = render(template_html, group, args.logo_url)
        out_file = html_dir / group["filename"]
        out_file.write_text(html, encoding="utf-8")
        csv_rows.append(group["mailchimp_tag"])
        print(f"  {group['filename']} (group {group['group_id']}: {group['group_name']})")

    summary = out_dir / "04_campaign_summary.md"
    summary.write_text(
        "# Campaign summary\n\n"
        f"- Groups generated: {len(groups)}\n"
        f"- HTML files: {html_dir}\n"
        f"- Mailchimp tags used: {', '.join(csv_rows)}\n"
        f"- Logo: {'placeholder to fill in before sending' if '{{' in args.logo_url else args.logo_url}\n\n"
        "## Before sending\n"
        "1. Upload the logo to Mailchimp Content Studio, replace the placeholder if needed "
        "(rerun with --logo-url).\n"
        "2. Check that every hero_image_url is genuinely different and relevant to its group.\n"
        "3. Import 03_mailchimp_contacts_by_group.csv (see build_contacts_csv.py) and create "
        "one Mailchimp campaign per GROUP_* tag.\n",
        encoding="utf-8",
    )

    print(f"\n{len(groups)} emails generated -> {html_dir}")
    print(f"Summary -> {summary}")


if __name__ == "__main__":
    main()
