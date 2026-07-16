# Lane D — Campaign Builder (cold email per professional group)

## Why this lane exists

Run of 2026-07-16: Leon used a third-party Claude skill found on TikTok (`cold-email-builder`, by @sully.fazie) to generate the cold email campaign. That skill is built to score/rebuild ONE email at a time in interactive chat (with a "brain" memory system, profiling forms) — not a bulk campaign across 15 segments from an Excel file. Result: mismatch, missing intermediate deliverables, the same hero image reused across all 15 groups.

**Rule:** never install a third-party skill found online for this project. This lane provides all the tooling needed, versioned and tested.

## What's in this lane

```
config/professional_groups.json       # the 15 canonical groups (source: Leon's TASK.md)
templates/base_mailchimp_template.html # validated HTML template (real colors/fonts from the site)
templates/email_content_by_group.example.json  # expected content JSON schema
scripts/build_contacts_csv.py         # classifies contacts into groups (1st auto pass + REVIEW)
scripts/generate_campaign.py          # generates the 15 HTML files + summary from the content JSON
```

## Full pipeline

```
Leon's Excel contacts
    │ export to UTF-8 CSV (no Excel library install needed)
    ▼
build_contacts_csv.py          # classifies by group via keywords, flags everything REVIEW
    │
Human/Claude review            # confirms/corrects the groups flagged REVIEW
    │
Analysis of Leon's real site   # Claude reads leonarchitectgroup.com, writes the content
    │                          # (headline, opening, benefits, CTA) per group
    ▼
email_content_by_group.json    # follow the example.json schema EXACTLY
    │
generate_campaign.py           # generates the 15 HTML files from the shared template
    │
outputs/campaigns/<date>/
    ├── html_emails/*.html
    └── 04_campaign_summary.md
    │
Leon validates                 # BEFORE any Mailchimp import
```

## Commands

```bash
cd lanes/D-campaigns/scripts

# 1. Classify the contacts (from a CSV exported from Leon's Excel)
python3 build_contacts_csv.py --input /path/to/contacts.csv --out ../../../outputs/campaigns/03_mailchimp_contacts_by_group.csv

# 2. After writing email_content_by_group.json (done by Claude in a session,
#    by reading the real site — not scriptable, it's judgment work)
python3 generate_campaign.py --content email_content_by_group.json
```

## Rules inherited from TASK.md (don't break these)

- **One email per group, never one email per contact.** 12-15 groups max.
- **Every group must have a different `hero_image_url`** (or at least per broad category: real estate/legal/health/hospitality). `generate_campaign.py` warns if every image is identical — don't ignore that warning.
- **Logo**: use Leon's official local file (not the favicon, not a third-party logo). The final HTML keeps `{{HOSTED_LOGO_URL}}` as a placeholder until the logo is uploaded to Mailchimp Content Studio (Mailchimp can't read a local path).
- **No invented email, no unverified claim.** Any ambiguous row stays `REVIEW_STATUS=REVIEW`.
- **Nothing is sent automatically.** CSV import + campaign creation = manual in Mailchimp, after Leon validates.
- **Only the text + JSON content change per group** — the HTML design is single and shared (`base_mailchimp_template.html`), never rewritten by hand per group.

## What's been tested (self-test with synthetic data, not Leon's real data)

- `generate_campaign.py` — tested with `email_content_by_group.example.json`, every placeholder resolved except the logo (expected), duplicate-image warning works.
- `build_contacts_csv.py` — tested with synthetic Greek contacts, email dedup works, matching is robust to accents (tonos) after fixing a Unicode normalization bug.

**Not tested with Leon's real data** (Excel + site + logo) — that's for him/you to run with the real files.
