# Lane B — Lead Gen (Research / Lead Generation)

Whiteboard goal: 44 contacts / 100 verified emails per batch, real estate agencies first (Athens), then civil engineers.

## Pipeline (1 batch ≈ 30 min)

```
config/targets.yaml          # 1. check city + segment
        │
places_search.py             # 2. Google Places → CSV (name, address, phone, site)
        │
enrich_emails.py              # 3. scrape sites → emails (free)
        │                    #    --hunter as fallback (25/month max, use sparingly)
verify_mx.py                 # 4. filter dead domains → email_status
        │
Claude review                # 5. Claude dedupes, cleans, ranks by quality
        │                    #    (high rating/reviews = active agency = better lead)
Leon validates                # 6. Leon validates the CSV BEFORE any outreach
```

## Commands

```bash
cd lanes/B-lead-gen/scripts
python3 places_search.py --query "real estate agency" --city Athens --country GR --max 60
python3 places_search.py --query "μεσιτικό γραφείο" --city Athens --country GR --max 60
python3 enrich_emails.py ../../../outputs/leads/<file>.csv          # free scrape
python3 enrich_emails.py ../../../outputs/leads/<file>.csv --hunter # if gaps remain
python3 verify_mx.py ../../../outputs/leads/<file>_enriched.csv
```

Run both queries (EN + Greek) then ask Claude to merge/dedupe the CSVs.

## Scaling up (1000+ contacts goal)

Do NOT do this through the Claude.ai chat (burns through the Pro quota fast — ~500 companies already exhausted it once). This pipeline is free and unlimited — use `run_batch.py`, which automatically loops over every city x segment in `config/targets.yaml`:

```bash
cd lanes/B-lead-gen/scripts
python3 run_batch.py                          # everything: all cities x all segments
python3 run_batch.py --segment real-estate     # a single segment
python3 run_batch.py --city Thessaloniki       # a single city
python3 run_batch.py --max-per-query 100       # more results per query
```

To scale up volume: add cities to `config/targets.yaml` (`cities` section), rerun `run_batch.py`. Consolidated, deduplicated output (by email, or by name+address when there's no email): `outputs/leads/YYYY-MM-DD_batch-all.csv`.

## Rules

- **Nothing is sent automatically.** Output = CSV for review. Cold email is phase 2, after Leon validates the list and proper deliverability is set up.
- **Cold calling**: the CSV has phone numbers — Leon calls himself in v1. No voice AI (cost + legal risk).
- **GDPR (EU market)**: business emails only (info@agency, never personal emails outside a professional context). Any future campaign includes a clear opt-out. Legal basis: B2B legitimate interest.
- **Hunter quota**: 25 free searches/month. Site scraping usually finds 60-80% of emails — save Hunter for high-value leads with no email found.

## Costs

| Item | Cost |
|---|---|
| Google Places API | $0 (~$200/month Google Maps Platform credit) |
| Email scraping | $0 |
| Hunter.io | $0 (free tier) |
| MX verification | $0 (local dig) |

## Phase 2 (if results + budget allow)

- Real SMTP verification (ZeroBounce ~$0.008/email)
- Automated cold email (Instantly/Lemlist ~$40-90/month + dedicated domain)
- Other cities/countries, civil engineers segment
