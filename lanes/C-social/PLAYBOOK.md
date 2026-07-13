# Lane C — Social Media (S.M.)

Objectif whiteboard: pipeline contenu multi-plateforme (TikTok, Pinterest, YouTube, …) — batch de ~15 contenus → post → analyse → replan.

## Pipeline (mensuel)

1. **Calendrier** — Claude génère calendrier 15 contenus/mois à partir de:
   - projets récents de Leon (photos chantier, rendus, avant/après)
   - patterns gagnants de lane A (ce qui marche chez les concurrents)
   - Sortie: `outputs/content/YYYY-MM_calendar.md`
2. **Production textes** — pour chaque contenu: hook, script (si vidéo), caption par plateforme, hashtags. TikTok ≠ Pinterest ≠ YouTube: Claude adapte format/ton par plateforme.
   - Sortie: `outputs/content/YYYY-MM-DD_<slug>.md`
3. **Post** — v1 manuel par Leon, ou Buffer free tier (3 comptes, 10 posts programmés/compte).
4. **Replan** — fin de mois: Leon note ce qui a marché (vues/saves), Claude ajuste le calendrier suivant.

## Ce que Claude ne fait PAS en v1

- Pas de génération vidéo/image (les visuels = photos/rendus de Leon, c'est son atout crédibilité).
- Pas de posting auto via API TikTok/YouTube (accès API restrictif, pas rentable à cette échelle).

## Coûts

| Poste | Coût |
|---|---|
| Textes/calendrier | 0€ (sessions Claude) |
| Buffer free tier | 0€ (3 comptes max — choisir les 3 plateformes prioritaires) |
