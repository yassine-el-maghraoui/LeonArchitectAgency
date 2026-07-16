# Tutorial — Running Leon Architect Group's Marketing Toolkit

This repo automates three things for the agency: finding leads (real estate agencies, engineers, etc.), researching competitors and their ads, and building content/email campaigns. This doc walks through everything step by step — no prior experience with this specific repo needed. Read `CLAUDE.md` first for the big-picture layout; this doc is the hands-on "how do I actually run this" guide.

## 0. Read this first — what you handle alone vs. what needs Yassine

**Handle yourself, no need to ask:**
- Running any of the lane B/A/D scripts with the commands below.
- Adding a city, segment, or professional group to the config files (following the exact format already there).
- Asking Claude to do the judgment steps (competitor research, email copy, content calendars).
- Normal API errors covered in section 12 (quota, bad key, etc.).

**Stop and message Yassine before continuing:**
- Any script throws a Python error you don't understand (a stack trace, not a plain `Error: ...` message).
- You need to change a script's actual code (`.py` files), not just a config file.
- You're about to send/import anything into Mailchimp for the first time on a new list — get a second pair of eyes once.
- Claude Code won't authenticate and the fix in section 2 doesn't resolve it.
- Anything involving billing (upgrading a paid tier, adding a credit card) — confirm with Leon/Yassine first, budget is capped on purpose.

If in doubt, it's cheaper to ask than to guess. But for everything in the first list, you don't need permission — just do it.

## 1. Getting the code and staying up to date

The repo lives on GitHub. If it's already on this machine (check for a folder like `Leon_Arch_Claude_Github` or `leon_architect`), you don't need to clone it again — you just need to keep it updated.

**First time only** (if you don't have it yet):
```bash
git clone https://github.com/yassine-el-maghraoui/LeonArchitectAgency.git
cd LeonArchitectAgency
```

**Every time you sit down to work**, pull the latest version first — Yassine may have pushed fixes:
```bash
git pull origin main
```

**Never** run `git push` unless Yassine has explicitly told you to and shown you how — pushing broken changes affects the shared repo everyone (including Yassine) relies on. If you've edited a config file (like `config/targets.yaml`) and want to save that change permanently, message Yassine and he'll commit it, or he'll walk you through it once.

If `git pull` shows a conflict or complains about local changes, **stop and ask Yassine** rather than forcing anything (`git reset --hard`, `git checkout .` etc. can destroy work).

## 2. Installing Claude Code and logging in

Some steps here are judgment work (reading a website, writing email copy) that only Claude can do — the scripts handle the mechanical, repeatable parts. You need Claude Code (or equivalent Claude/Codex CLI access) installed and logged in.

1. Install: follow Anthropic's official Claude Code install instructions for your OS.
2. Check it's really installed and working:
   ```
   claude --version
   ```
3. Log in with the agency's subscription:
   ```
   claude /login
   ```

**If you get "unable to connect to API" despite having an active subscription (this happened before on Windows):**
The usual cause is a leftover `ANTHROPIC_API_KEY` environment variable overriding the subscription login. Check for it:
```powershell
[Environment]::GetEnvironmentVariable("ANTHROPIC_API_KEY", "User")
[Environment]::GetEnvironmentVariable("ANTHROPIC_API_KEY", "Machine")
```
If either prints a value, clear it:
```powershell
[Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", $null, "User")
[Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", $null, "Machine")
```
Close the terminal completely and reopen it (a value set this way won't disappear from an already-open terminal), then `claude /login` again.

If that doesn't fix it, this is a "message Yassine" situation (section 0).

## 3. First-time setup (API keys)

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

**Never commit `.env`, never send it over email/Slack/WhatsApp, never paste it into a Claude chat.** It's already gitignored so `git push` won't leak it, but treat the file itself as a password.

Sanity check everything is wired correctly:
```bash
cd lanes/B-lead-gen/scripts
python3 _targets.py
```
This should print the cities/segments from `config/targets.yaml` as JSON. If it errors, the repo isn't set up right — check you're in the right folder.

## 4. Lane B — Finding leads (real estate agencies, engineers, etc.)

**What it does:** searches Google Places for a business type in a city, scrapes their websites for a contact email, checks the email's domain is real, and writes a CSV.

**Single run** (one city, one search term):
```bash
cd lanes/B-lead-gen/scripts
python3 places_search.py --query "real estate agency" --city Athens --country GR --max 60
python3 enrich_emails.py ../../../outputs/leads/<the file it just created>.csv
python3 verify_mx.py ../../../outputs/leads/<file>_enriched.csv
```
The final file (`..._verified.csv`) has an `email_status` column — only rows marked `valid_mx` have a confirmed-real email.

**Bulk run** (every city x segment defined in `config/targets.yaml`, for reaching large volumes like 1000+ contacts):
```bash
python3 run_batch.py
```
This can take a while (it's making real API calls per query). It writes one consolidated, deduplicated file: `outputs/leads/YYYY-MM-DD_batch-all.csv`.

**To change which cities/business types get searched, edit `config/targets.yaml`** — never hardcode a city into the scripts. This file is parsed by a small custom script, not a full YAML library, so it's **strict about spacing**:
- Keep exactly the same indentation as the existing entries (2 spaces for a new city/segment `-` item, 4 spaces for its fields, 6 spaces for a `query_terms` sub-item).
- Don't use tabs.
- If you're not sure, **copy an existing block and only change the text**, don't retype the structure from scratch.
- After editing, always re-run `python3 _targets.py` (section 3) to confirm it still parses correctly — if the output looks wrong or a field is missing, you likely broke the indentation. Undo your edit and ask Yassine rather than guessing at the fix.

**Before you do anything with the results:** these are leads, not a validated list. Skim the CSV before calling/emailing anyone — see section 9 for what happens after you have the file.

## 5. Lane A — Competitor & ad research

**What it does:** finds competitor agencies and analyzes their running ads (the Meta Ad Library blocks direct scraping, so this goes through Apify).

**a) Finding competitors and their acquisition patterns** — judgment work, done by asking Claude directly (in a Claude Code session in this repo, or in the Claude.ai project):
> "Find the main architecture agencies in Athens and how they attract clients — SEO, social, portfolio, reviews."

**b) Scraping their ads** (scriptable, deterministic):
```bash
cd lanes/A-ads-research/scripts
python3 meta_ads.py --keyword "ανακαίνιση" --country GR --max 20
# or, for one specific competitor:
python3 meta_ads.py --page-url "https://www.facebook.com/<their page>"
```
Output: a Markdown report in `outputs/competitors/`, sorted by how long each ad has been running — a long-running ad is usually a profitable one. That's the signal for "what messaging works."

Full details: `lanes/A-ads-research/PLAYBOOK.md`.

## 6. Lane C — Social media content

No scripts — this is pure Claude judgment work. Ask directly:
> "Make this month's content calendar: 15 ideas using these projects: [describe 2-3 recent projects]."

Full details: `lanes/C-social/PLAYBOOK.md`.

## 7. Lane D — Cold email campaign builder

This is the most involved lane — it has both a scripted part and a judgment part. Follow this order:

**Step 1 — Classify contacts into professional groups** (scriptable):
```bash
cd lanes/D-campaigns/scripts
python3 build_contacts_csv.py --input /path/to/contacts.csv --out ../../../outputs/campaigns/03_mailchimp_contacts_by_group.csv
```
- Input must be a **CSV**, not `.xlsx` — if you're starting from an Excel file, open it and "Save As → CSV UTF-8" first.
- The 15 groups it classifies into are defined in `lanes/D-campaigns/config/professional_groups.json` — don't invent new ones without a real reason (the original task caps it at ~12-15 groups on purpose, to avoid one email per contact).
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

**If the script warns that all hero images are identical, stop and fix step 2 before continuing.** Don't proceed past this warning "to save time" — it's the exact defect that caused a redo last time.

**Step 4 — Logo:** the HTML keeps `{{HOSTED_LOGO_URL}}` as a placeholder. Upload the real logo (`leon_architect_group_logo.jpg` or whatever the current official file is) to Mailchimp's Content Studio first, then rerun step 3 with `--logo-url "<the uploaded URL>"`.

**Step 5 — Human review, always.** Before importing anything into Mailchimp:
- Open a few of the generated HTML files in a browser, check they look right.
- Check `03_mailchimp_contacts_by_group.csv` — resolve every row still marked `REVIEW`.
- Get Leon's sign-off on the email text (see section 9).

Full details, including why this lane exists at all: `lanes/D-campaigns/PLAYBOOK.md`.

## 8. Mailchimp access

Actually sending anything requires the agency's Mailchimp login — ask Leon for it, it's not stored in this repo (and never should be). Import flow once you have access: Audience → Import Contacts → upload `03_mailchimp_contacts_by_group.csv` → tag by `MAILCHIMP_TAG` column → create one campaign per tag using the matching HTML file from `html_emails/`.

**Never click "Send" without Leon's explicit go-ahead on that specific batch.** A test send to yourself first is always fine and encouraged.

## 9. Getting results to Leon for review

Nothing in this repo sends anything automatically — every lane produces a file in `outputs/` that a human needs to look at and act on. Once you have a finished CSV or report:
1. Share it with Leon the way he prefers (Google Sheet, email, WhatsApp — ask him once, then stick to it).
2. Wait for his sign-off before any outreach, campaign send, or post goes out.
3. If Leon has a shared Google Sheet for leads, that's the source of truth for outreach status (contacted / replied / etc.) — the CSV from this repo is the starting point, not the tracker itself.

## 10. Rules that apply everywhere in this repo

- **Nothing gets sent automatically.** No script here sends an email, makes a call, or posts to social media. Every output is a draft/CSV for a human to act on.
- **GDPR / EU market:** collect business contact info only (agency emails, not personal ones out of context). Any real campaign needs a clear unsubscribe/opt-out.
- **Don't hardcode cities, segments, or groups into scripts.** Edit `config/targets.yaml` (lane B) or `lanes/D-campaigns/config/professional_groups.json` (lane D) instead.
- **All generated files go to `outputs/`** (`leads/`, `competitors/`, `content/`, `campaigns/`), prefixed with the date. This folder is gitignored — it's working output, not something to commit.

## 11. What to avoid — do NOT do these

- ❌ **Don't install any third-party "skill", plugin, or tool** you find on TikTok, YouTube, or a marketplace, even if a tutorial says it'll make this easier. This already caused one broken campaign (a mismatched skill built for scoring single emails was used to try to generate a 15-segment bulk campaign). Everything you need is already in this repo.
- ❌ **Don't run big lead/company searches through Claude chat** (asking Claude.ai directly for "1000 companies"). It burns through the plan's usage limit fast and produces worse results than the scripts. Use `run_batch.py` (section 4) instead — free, no limit.
- ❌ **Don't send, post, or email anything the scripts/Claude produce without Leon's sign-off.** Everything here is a draft.
- ❌ **Don't edit the `.py` script files** to "quickly fix" something — edit config files (`.yaml`/`.json`) for data changes; anything else goes through Yassine.
- ❌ **Don't reformat `config/targets.yaml` or `professional_groups.json`** for style/prettiness — the custom parser is strict, and a "cleanup" can silently break it (see section 4).
- ❌ **Don't commit or share `.env`, API keys, or the Mailchimp password** anywhere — not in git, not in a Claude chat, not over email.
- ❌ **Don't `git push` without Yassine's go-ahead**, and never force anything (`git push --force`, `git reset --hard`) without him walking you through why.
- ❌ **Don't skip the hero-image-per-group check in lane D** (section 7) just to move faster.

## 12. When an API quota runs out

- **Google Places** (~$200/month free credit): unlikely to hit this at agency scale. If it happens, wait for the monthly reset (Google Cloud Console → Billing shows the reset date) — don't add a payment method without confirming with Leon/Yassine first.
- **Hunter.io** (25 searches/month free): resets on the 1st of the month. In the meantime, `enrich_emails.py` still works without `--hunter` — it just relies on the free website-scraping method, which finds most emails anyway (roughly 60-80% in testing).
- **Apify** ($5/month free credit): resets monthly. If exhausted mid-month, competitor ad scraping (lane A) just has to wait — nothing else depends on it.
- In all three cases: this is not an emergency, nothing breaks — just that specific feature pauses until reset. No need to page Yassine for a quota reset; only message him if you think usage is unexpectedly high (could mean a bug looping/retrying).

## 13. If something breaks

- **`Error: <KEY> missing`** — your `.env` isn't filled in, or you're running the script from the wrong folder (it looks for `.env` at the repo root).
- **A script produces 0 results** — check the API key is valid and has quota left (Google Cloud Console / Hunter dashboard / Apify Console all show usage).
- **`config/targets.yaml` changes aren't showing up / look wrong** — almost always an indentation issue, see section 4.
- **A Python stack trace (not a clean `Error: ...` line)** — this is a real bug, not a usage mistake. Message Yassine with the exact command you ran and the full error text.
- **Not sure which command to run** — check the relevant lane's `PLAYBOOK.md` first, it has copy-pasteable commands for the common cases.
- **Still stuck** — message Yassine (WhatsApp), with what you ran and what happened.
