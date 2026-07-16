# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Marketing/lead-gen automation for Leon's architecture agency (Athens/Europe market).
Not a software product — a working directory where Claude Code sessions execute three recurring "lanes" and write results to `outputs/`. Budget constraint: < $100/month total for third-party tools, so everything defaults to free tiers and public data sources.

## Lanes

- `lanes/A-ads-research/` — competitor research + ad analysis + copywriting for Leon's own agency. Driven by Claude web search + public ad libraries (Meta Ad Library, Google Ads Transparency Center). No paid APIs.
- `lanes/B-lead-gen/` — find real-estate agencies (and later civil engineers) per city, collect business emails/phones, verify, produce CSVs for Leon's review. Scripts in `lanes/B-lead-gen/scripts/` (Python 3, stdlib only — no pip install needed).
- `lanes/C-social/` — social media content pipeline (TikTok/Pinterest/YouTube): calendar, scripts, captions. Text generation only; posting is manual or via Buffer free tier.
- `lanes/D-campaigns/` — cold email campaign builder (one email per professional group, not per contact — see `config/professional_groups.json` for the 15 canonical groups). Built after a mismatched third-party TikTok skill produced broken results; this lane replaces it with tested, versioned tooling. No skill should ever be loaded for this project — see `kit/leon-guide.md` rule.

Each lane has a `PLAYBOOK.md` (in English) that is the source of truth for how to run that lane. Read the relevant playbook before doing lane work.

## Commands

```bash
# Lane B scripts (Python 3 stdlib, no venv needed)
python3 lanes/B-lead-gen/scripts/places_search.py --query "real estate agency" --city "Athens" --country GR
python3 lanes/B-lead-gen/scripts/hunter_domain.py --domain example.gr
python3 lanes/B-lead-gen/scripts/verify_mx.py outputs/leads/<file>.csv

# Scale to 1000+ leads: loop over every city x segment in config/targets.yaml
python3 lanes/B-lead-gen/scripts/run_batch.py

# Lane D — campaign builder (see lanes/D-campaigns/PLAYBOOK.md)
python3 lanes/D-campaigns/scripts/build_contacts_csv.py --input contacts.csv --out outputs/campaigns/03_mailchimp_contacts_by_group.csv
python3 lanes/D-campaigns/scripts/generate_campaign.py --content email_content_by_group.json
```

API keys live in `.env` (gitignored, see `.env.example`). Scripts read keys from environment or `.env` in repo root.

## Handover kit (`kit/`)

Yassine is leaving Greece; Leon (non-technical) operates autonomously via a Claude.ai Pro Project — chat only, no scripts, no infra. `kit/claude-project-instructions.md` is the text to paste into the Claude.ai Project (fill the [BRACKETS] with agency details first); `kit/leon-guide.md` is Leon's one-page copy-paste prompt guide. The kit is in English (user preference). The lane scripts remain for Yassine's optional remote batch runs only. Decided against: n8n, dashboards, auto-send — unmaintainable without a local technical operator.

## Conventions

- All generated data goes to `outputs/` (`outputs/leads/`, `outputs/competitors/`, `outputs/content/`), CSV or Markdown, filenames prefixed `YYYY-MM-DD_`.
- `config/targets.yaml` defines cities/segments to target — read it before running lead gen, don't hardcode cities in scripts.
- Nothing gets sent (emails, posts) automatically. Every outbound action requires Leon's explicit validation of the output file first. v1 is research + drafts only.
- GDPR: target market is Greece/EU. Collect business contact data only (agency emails/phones from public listings), never personal data out of professional context. Any future email campaign must include a clear opt-out.
