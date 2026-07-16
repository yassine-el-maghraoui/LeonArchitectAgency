# Tutorial — Running Leon Architect Group's Marketing Toolkit

This repo automates three things for the agency: finding leads (real estate agencies, engineers, etc.), researching competitors and their ads, and building content/email campaigns. This doc walks through everything step by step — no prior experience with this specific repo needed. Read `CLAUDE.md` first for the big-picture layout; this doc is the hands-on "how do I actually run this" guide.

Ask Yassine (WhatsApp) if anything below doesn't work as described.

## 1. What you need before starting

- **This repo**, cloned locally (ask Yassine for the GitHub link if you don't have it, or it's already on Leon's machine at `Leon_Arch_Claude_Github`).
- **Python 3** installed (check with `python3 --version` in a terminal — 3.10+ is fine). Everything here uses Python's standard library only, nothing to `pip install`.
- **Claude Code** (or another Claude/Codex CLI/chat access) — some steps in this toolkit are judgment work (reading a website, writing email copy) that only Claude can do; the scripts handle the mechanical, repeatable parts.
- **A `.env` file** at the repo root with API keys (see step 2).

You do **not** need to install any third-party "skill", plugin, or tool you find online (TikTok, YouTube, marketplaces) to use this repo. Everything needed is already here. Installing an unrelated skill caused a broken campaign once already — don't repeat that.

## 2. First-time setup

```bash
cd path/to/leon_architect
cp .env.example .env
```

Open `.env` and fill in three keys:

| Key | Where to get it | Free tier |
|---|---|---|
| `GOOGLE_PLACES_API_KEY` | console.cloud.google.com → enable "Places API (New)" → Credentials → Create API key | ~$200/month free credit |
| `HUNTER_API_KEY` | hunter.io/api_keys (sign up free) | 25 searches/month |
| `APIFY_TOKEN` | apify.com → Settings → API & Integrations → Personal API token | $5/month free credit |

Never commit `.env` or share it outside the team — it's already gitignored.

Sanity check everything is wired correctly:
```bash
cd lanes/B-lead-gen/scripts
python3 _targets.py
```
This should print the cities/segments from `config/targets.yaml` as JSON. If it errors, the repo isn't set up right — check you're in the right folder.

## 3. Lane B — Finding leads (real estate agencies, engineers, etc.)

**What it does:** searches Google Places for a business type in a city, scrapes their websites for a contact email, checks the email's domain is real, and writes a CSV.

**Single run** (one city, one search term):
```bash
cd lanes/B-lead-gen/scripts
python3 places_search.py --query "real estate agency" --city Athens --country GR --max 60
python3 enrich_emails.py ../../../outputs/leads/<the file it just created>.csv
python3 verify_mx.py ../../../outputs/leads/<file>_enriched.csv
```
The final file (`..._verified.csv`) has a `email_status` column — only rows marked `valid_mx` have a confirmed-real email.

**Bulk run** (every city x segment defined in `config/targets.yaml`, for reaching large volumes like 1000+ contacts):
```bash
python3 run_batch.py
```
This can take a while (it's making real API calls per query). It writes one consolidated, deduplicated file: `outputs/leads/YYYY-MM-DD_batch-all.csv`.

To change which cities/business types get searched, edit `config/targets.yaml` — never hardcode a city into the scripts.

**Before you do anything with the results:** these are leads, not a validated list. Leon (or whoever owns outreach) should skim the CSV before calling/emailing anyone.

## 4. Lane A — Competitor & ad research

**What it does:** finds competitor agencies and analyzes their running ads (the Meta Ad Library blocks direct scraping, so this goes through Apify).

Two parts:

**a) Finding competitors and their acquisition patterns** — this is judgment work, done by asking Claude directly (in a Claude Code session in this repo, or in the Claude.ai project):
> "Find the main architecture agencies in Athens and how they attract clients — SEO, social, portfolio, reviews."

**b) Scraping their ads** (scriptable, deterministic):
```bash
cd lanes/A-ads-research/scripts
python3 meta_ads.py --keyword "ανακαίνιση" --country GR --max 20
# or, for one specific competitor:
python3 meta_ads.py --page-url "https://www.facebook.com/<their page>"
```
Output: a Markdown report in `outputs/competitors/`, sorted by how long each ad has been running — a long-running ad is usually a profitable one. That's your signal for "what messaging works."

Full details: `lanes/A-ads-research/PLAYBOOK.md`.

## 5. Lane C — Social media content

No scripts — this is pure Claude judgment work. Ask directly:
> "Make this month's content calendar: 15 ideas using these projects: [describe 2-3 recent projects]."

Full details: `lanes/C-social/PLAYBOOK.md`.

## 6. Lane D — Cold email campaign builder

This is the most involved lane — it has both a scripted part and a judgment part. Follow this order:

**Step 1 — Classify contacts into professional groups** (scriptable):
```bash
cd lanes/D-campaigns/scripts
python3 build_contacts_csv.py --input /path/to/contacts.csv --out ../../../outputs/campaigns/03_mailchimp_contacts_by_group.csv
```
- Input must be a **CSV**, not `.xlsx` — if you're starting from an Excel file, open it and "Save As → CSV UTF-8" first.
- The 15 groups it classifies into are defined in `config/professional_groups.json` — don't invent new ones without a real reason (TASK.md caps it at ~12-15 groups on purpose).
- Every row comes out marked `REVIEW` — that's intentional. A human (or Claude) needs to eyeball the ambiguous ones before moving on.

**Step 2 — Write the email content per group** (judgment work, done by Claude):
Ask Claude, in a session with access to this repo:
> "Read https://leonarchitectgroup.com/ and write email_content_by_group.json for the cold email campaign, following the schema in lanes/D-campaigns/templates/email_content_by_group.example.json. One entry per professional group. Give every group a *different* hero_image_url relevant to that group — never reuse the same image across groups."

That last instruction matters: a past run reused one generic image on all 15 emails, which is exactly the mistake to avoid. Real, distinct images per group (or at minimum per broad category — real estate / legal / health / hospitality) make a real difference.

**Step 3 — Generate the final HTML emails** (scriptable):
```bash
python3 generate_campaign.py --content email_content_by_group.json
```
Output goes to `outputs/campaigns/<today's date>/`:
- `html_emails/*.html` — one file per group, ready to paste into Mailchimp
- `04_campaign_summary.md` — what was generated, what to check before sending

If the script warns that all hero images are identical, stop and fix step 2 before continuing.

**Step 4 — Logo:** the HTML keeps `{{HOSTED_LOGO_URL}}` as a placeholder. Upload the real logo (`leon_architect_group_logo.jpg` or whatever the current official file is) to Mailchimp's Content Studio first, then rerun step 3 with `--logo-url "<the uploaded URL>"`.

**Step 5 — Human review, always.** Before importing anything into Mailchimp:
- Open a few of the generated HTML files in a browser, check they look right.
- Check `03_mailchimp_contacts_by_group.csv` — resolve every row still marked `REVIEW`.
- Get Leon's sign-off on the email text.

Full details, including why this lane exists at all: `lanes/D-campaigns/PLAYBOOK.md`.

## 7. Rules that apply everywhere in this repo

- **Nothing gets sent automatically.** No script here sends an email, makes a call, or posts to social media. Every output is a draft/CSV for a human to act on.
- **GDPR / EU market:** collect business contact info only (agency emails, not personal ones out of context). Any real campaign needs a clear unsubscribe/opt-out.
- **Don't hardcode cities, segments, or groups into scripts.** Edit `config/targets.yaml` (lane B) or `lanes/D-campaigns/config/professional_groups.json` (lane D) instead.
- **Don't install external skills/plugins for this project.** If a tutorial online tells you to add some tool to make this easier, don't — ask Yassine first.
- **All generated files go to `outputs/`** (`leads/`, `competitors/`, `content/`, `campaigns/`), prefixed with the date. This folder is gitignored — it's working output, not something to commit.

## 8. If something breaks

- **`Error: <KEY> missing`** — your `.env` isn't filled in, or you're running the script from the wrong folder (it looks for `.env` at the repo root).
- **A script produces 0 results** — check the API key is valid and has quota left (Google Cloud Console / Hunter dashboard / Apify Console all show usage).
- **Not sure which command to run** — check the relevant lane's `PLAYBOOK.md` first, it has copy-pasteable commands for the common cases.
- **Still stuck** — message Yassine.
