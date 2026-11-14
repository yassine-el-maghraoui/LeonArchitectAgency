# Leon Architect Agency — Marketing & Lead-Gen Toolkit

A lightweight, human-in-the-loop toolkit that automates the repetitive parts of marketing for an architecture agency in Athens, Greece: finding B2B leads, researching competitors' ads, planning social content, and building cold email campaigns.

It is **not a software product**. It is a working repository where scripted pipelines (Python 3, standard library only) and Claude-driven judgment steps produce reviewable files in `outputs/`. Nothing is ever sent or posted automatically.

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)
![Budget](https://img.shields.io/badge/budget-%3C%20%24100%2Fmonth-orange)

## Why

The agency needed a repeatable marketing engine under three constraints:

- **Tiny budget** — under $100/month for all third-party tools, so everything runs on free tiers and public data.
- **Non-technical operator** — the agency owner runs day-to-day work through a Claude.ai Project (chat only); a technical operator runs batch jobs from this repo.
- **EU compliance** — B2B contact data only, with a human validating every outbound action.

## The four lanes

| Lane | Purpose | How it runs |
|---|---|---|
| **A — Ads research** | Find competitors, scrape their Meta ads, surface long-running (likely profitable) ads, draft copy variants | `meta_ads.py` (via Apify) + Claude |
| **B — Lead generation** | Find real estate agencies / civil engineers per city, collect business emails and phones, verify domains | Python pipeline, batch-capable (1000+ leads) |
| **C — Social content** | Monthly TikTok / Pinterest / YouTube calendar, scripts, captions | Claude only (text generation) |
| **D — Campaign builder** | One cold email per professional group (15 groups), rendered from a shared HTML template | Python + Claude copywriting |

Each lane has a `PLAYBOOK.md` that is the source of truth for how to run it.

## Architecture

```
config/targets.yaml            cities × segments to target (edit here, never in scripts)
        │
lanes/
├── A-ads-research/            PLAYBOOK.md, scripts/meta_ads.py
├── B-lead-gen/                PLAYBOOK.md, scripts/{places_search,enrich_emails,verify_mx,run_batch}.py
├── C-social/                  PLAYBOOK.md
└── D-campaigns/               PLAYBOOK.md, scripts/, templates/, config/professional_groups.json
        │
outputs/                       generated CSV / Markdown / HTML (gitignored, structure kept)
kit/                           handover kit for the non-technical operator
TUTORIAL.md                    full step-by-step ops guide
```

### Lane B pipeline

```
targets.yaml → places_search.py → enrich_emails.py → verify_mx.py → human review → outreach
               (Google Places)    (scrape sites;     (DNS MX check)
                                   Hunter fallback)
```

`run_batch.py` loops over every city × segment, then writes one deduplicated file: `outputs/leads/YYYY-MM-DD_batch-all.csv`.

### Lane D pipeline

```
contacts CSV → build_contacts_csv.py → review → email_content_by_group.json → generate_campaign.py
               (keyword grouping,                (copy written by Claude        (15 HTML emails +
                ambiguous = REVIEW)               from the real website)         campaign summary)
```

## Getting started

**Requirements:** Python 3.9+ (no `pip install` needed). Optional: [Claude Code](https://claude.com/claude-code) for the judgment steps.

```bash
git clone https://github.com/yassine-el-maghraoui/LeonArchitectAgency.git
cd LeonArchitectAgency
cp .env.example .env     # then fill in your keys
python3 lanes/B-lead-gen/scripts/_targets.py   # sanity check: prints parsed targets as JSON
```

### API keys (all free tier)

| Variable | Used for | Free tier |
|---|---|---|
| `GOOGLE_PLACES_API_KEY` | Lead discovery (Places API New) | ~$200/month Google Maps credit |
| `HUNTER_API_KEY` | Email fallback for high-value leads | 25 searches/month |
| `APIFY_TOKEN` | Meta Ad Library scraping | $5/month credit |

`.env` is gitignored. Never commit it.

## Usage

```bash
# Lane B — single run
cd lanes/B-lead-gen/scripts
python3 places_search.py --query "real estate agency" --city Athens --country GR --max 60
python3 enrich_emails.py ../../../outputs/leads/<file>.csv
python3 verify_mx.py ../../../outputs/leads/<file>_enriched.csv

# Lane B — everything in targets.yaml
python3 run_batch.py [--segment real-estate] [--city Thessaloniki] [--max-per-query 100]

# Lane A — competitor ads
cd ../../A-ads-research/scripts
python3 meta_ads.py --keyword "ανακαίνιση" --country GR --max 20
python3 meta_ads.py --page-url "https://www.facebook.com/<page>"

# Lane D — campaign builder
cd ../../D-campaigns/scripts
python3 build_contacts_csv.py --input contacts.csv --out ../../../outputs/campaigns/03_mailchimp_contacts_by_group.csv
python3 generate_campaign.py --content email_content_by_group.json
```

Outputs are CSV or Markdown, prefixed `YYYY-MM-DD_`, and land in `outputs/`.

For the complete walkthrough (setup, troubleshooting, when to escalate), see [`TUTORIAL.md`](TUTORIAL.md).

## Design principles

- **Human in the loop.** Every output is a draft or a CSV for review. No auto-send, no auto-post.
- **Free tiers and public data only.** Ad libraries are public by EU DSA obligation; leads come from public business listings.
- **Zero infrastructure.** Standard-library Python, no servers, no dashboards, nothing to keep alive.
- **Config over code.** Cities, segments, and professional groups live in `config/` — scripts never hardcode them.
- **Scripts for the mechanical, Claude for the judgment.** Scraping and classification are deterministic scripts; competitor analysis, copywriting, and calendars are Claude sessions.

## Compliance (GDPR)

- Business contact data only (e.g. `info@agency`), collected from public listings.
- No personal data outside a professional context.
- Legal basis: B2B legitimate interest. Any campaign must include a clear opt-out.
- Generated data in `outputs/` is gitignored and never published.

## Handover kit

`kit/` contains the materials for a non-technical operator working only through Claude.ai:

- `claude-project-instructions.md` — system prompt to paste into a Claude Project.
- `leon-guide.md` — one-page, copy-paste prompt guide.

## Costs

| Item | Monthly cost |
|---|---|
| Google Places API | $0 (within free credit) |
| Email scraping + MX verification | $0 |
| Hunter.io | $0 (25 searches) |
| Apify | ~$0 (within $5 credit) |
| Buffer (optional scheduling) | $0 (free tier) |

Possible phase 2 upgrades: SMTP verification (~$0.008/email), automated cold email tooling ($40–90/month).

## Status

- Lanes A, B, C, D implemented and documented.
- Lane D tested with synthetic data (including Greek accent-insensitive matching); not yet validated on production contacts.

## License

No license specified. All rights reserved by the repository owner unless stated otherwise.
