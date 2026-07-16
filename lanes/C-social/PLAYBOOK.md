# Lane C — Social Media (S.M.)

Whiteboard goal: multi-platform content pipeline (TikTok, Pinterest, YouTube, …) — batch of ~15 pieces of content → post → analyze → replan.

## Pipeline (monthly)

1. **Calendar** — Claude generates a 15-piece monthly calendar based on:
   - Leon's recent projects (site photos, renders, before/after)
   - winning patterns from lane A (what works for competitors)
   - Output: `outputs/content/YYYY-MM_calendar.md`
2. **Copy production** — for each piece: hook, script (if video), caption per platform, hashtags. TikTok ≠ Pinterest ≠ YouTube: Claude adapts format/tone per platform.
   - Output: `outputs/content/YYYY-MM-DD_<slug>.md`
3. **Post** — v1 is manual by Leon, or Buffer free tier (3 accounts, 10 scheduled posts/account).
4. **Replan** — end of month: Leon notes what worked (views/saves), Claude adjusts next month's calendar.

## What Claude does NOT do in v1

- No video/image generation (visuals = Leon's own photos/renders, that's his credibility asset).
- No auto-posting via TikTok/YouTube API (restrictive API access, not worth it at this scale).

## Costs

| Item | Cost |
|---|---|
| Copy/calendar | $0 (Claude sessions) |
| Buffer free tier | $0 (3 accounts max — pick the 3 priority platforms) |
