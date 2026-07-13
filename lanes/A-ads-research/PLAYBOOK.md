# Lane A — Concurrents & Ads (Advert Digital Agency)

Objectif whiteboard: trouver les concurrents (agences archi Athènes/EU), comprendre comment ils captent des clients, analyser toutes leurs pubs, isoler les meilleures, produire 5-20 variantes de copy à tester.

## Pipeline (session Claude Code, ~0€)

1. **Trouver concurrents** — Claude web search: agences architecture Athènes + agences EU visibles en ligne. Critères: site actif, présence social, pubs en cours. Sortie: `outputs/competitors/YYYY-MM-DD_competitors.md` (tableau: nom, site, positionnement, canaux).
2. **Analyser leurs acquisitions** — pour chaque concurrent: SEO local (Google Maps ranking), contenu organique, portfolios, avis clients. Qu'est-ce qui les fait trouver?
3. **Scraper leurs pubs** — via Apify (l'accès direct à la Meta Ad Library est bloqué anti-bot):
   ```bash
   cd lanes/A-ads-research/scripts
   python3 meta_ads.py --keyword "ανακαίνιση" --country GR --max 20   # par mot-clé
   python3 meta_ads.py --page-url "https://www.facebook.com/<page>"   # par concurrent
   ```
   Sortie: rapport Markdown trié par durée de diffusion (longue diffusion ≈ pub rentable = "best perf ads" du whiteboard) + JSON brut. Coût: ~centimes/run, free tier Apify 5$/mois suffit.
   Google Ads Transparency Center (https://adstransparency.google.com): consultation manuelle.
4. **Rapport best ads** — patterns gagnants: quels angles reviennent, quelles offres, quels visuels. Sortie: `outputs/competitors/YYYY-MM-DD_best-ads.md`
5. **Copywriting** — Claude génère 5-20 variantes d'ads pour l'agence de Leon (angles différents: prix, délai, style, portfolio, avant/après). Leon choisit, teste avec petit budget Meta.

## Règles

- Données publiques uniquement (ad libraries = publiques par obligation légale EU/DSA).
- Le rapport nomme les sources (liens ads) pour que Leon vérifie.
- Les variantes de copy = brouillons. Leon valide avant toute mise en ligne.

## Coûts

Tout gratuit. Seul coût futur: budget média Meta/Google de Leon pour tester les variantes (hors scope outils).
