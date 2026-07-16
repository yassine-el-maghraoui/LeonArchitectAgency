# Lane A — Competitors & Ads (Advert Digital Agency)

Whiteboard goal: find competitors (architecture agencies in Athens/EU), understand how they acquire clients, analyze all their ads, isolate the best ones, produce 5-20 copy variants to test.

## Pipeline (Claude Code session, ~$0)

1. **Find competitors** — Claude web search: architecture agencies in Athens + EU agencies with an online presence. Criteria: active site, social presence, running ads. Output: `outputs/competitors/YYYY-MM-DD_competitors.md` (table: name, site, positioning, channels).
2. **Analyze their client acquisition** — for each competitor: local SEO (Google Maps ranking), organic content, portfolios, reviews. What makes them findable?
3. **Scrape their ads** — via Apify (direct access to the Meta Ad Library is blocked by anti-bot protection):
   ```bash
   cd lanes/A-ads-research/scripts
   python3 meta_ads.py --keyword "ανακαίνιση" --country GR --max 20   # by keyword
   python3 meta_ads.py --page-url "https://www.facebook.com/<page>"   # by competitor
   ```
   Output: Markdown report sorted by run length (longer run ≈ profitable ad = the whiteboard's "best perf ads") + raw JSON. Cost: ~cents/run, Apify's $5/month free tier is enough.
   Google Ads Transparency Center (https://adstransparency.google.com): manual lookup.
4. **Best ads report** — winning patterns: which angles, offers, and visuals keep recurring. Output: `outputs/competitors/YYYY-MM-DD_best-ads.md`
5. **Copywriting** — Claude generates 5-20 ad variants for Leon's agency (different angles: price, turnaround, style, portfolio, before/after). Leon picks, tests with a small Meta budget.

## Rules

- Public data only (ad libraries are public by EU/DSA legal obligation).
- The report names its sources (ad links) so Leon can verify.
- Copy variants are drafts. Leon approves before anything goes live.

## Costs

Everything free. Only future cost: Leon's Meta/Google media budget to test the variants (outside the tooling's scope).
