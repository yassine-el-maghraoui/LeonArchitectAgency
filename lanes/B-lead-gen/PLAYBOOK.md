# Lane B — Lead Gen (Research / Lead Generation)

Objectif whiteboard: 44 contacts / 100 emails vérifiés par batch, agences immobilières d'abord (Athènes), puis ingénieurs civils.

## Pipeline (1 batch ≈ 30 min)

```
config/targets.yaml          # 1. vérifier ville + segment
        │
places_search.py             # 2. Google Places → CSV (nom, adresse, tel, site)
        │
enrich_emails.py             # 3. scrape sites → emails (gratuit)
        │                    #    --hunter en fallback (25/mois max, économiser)
verify_mx.py                 # 4. filtre domaines morts → email_status
        │
Revue Claude                 # 5. Claude dédupe, nettoie, classe par qualité
        │                    #    (rating/reviews élevés = agence active = meilleur lead)
Validation Leon              # 6. Leon valide le CSV AVANT tout envoi
```

## Commandes

```bash
cd lanes/B-lead-gen/scripts
python3 places_search.py --query "real estate agency" --city Athens --country GR --max 60
python3 places_search.py --query "μεσιτικό γραφείο" --city Athens --country GR --max 60
python3 enrich_emails.py ../../../outputs/leads/<fichier>.csv          # scrape gratuit
python3 enrich_emails.py ../../../outputs/leads/<fichier>.csv --hunter # si trous
python3 verify_mx.py ../../../outputs/leads/<fichier>_enriched.csv
```

Lancer les deux requêtes (EN + grec) puis demander à Claude de fusionner/déduper les CSVs.

## Règles

- **Rien n'est envoyé automatiquement.** Sortie = CSV pour revue. Cold email = phase 2, après validation de la liste par Leon et setup deliverability propre.
- **Cold call**: le CSV contient les téléphones — Leon appelle lui-même en v1. Pas d'IA vocale (coût + légal).
- **RGPD (marché EU)**: emails business uniquement (info@agence, pas d'emails perso hors contexte pro). Toute future campagne inclut un opt-out clair. Base légale: intérêt légitime B2B.
- **Quota Hunter**: 25 recherches/mois en gratuit. Le scrape de site trouve généralement 60-80% des emails — Hunter seulement pour les leads à forte valeur sans email.

## Coûts

| Poste | Coût |
|---|---|
| Google Places API | 0€ (crédit mensuel ~200$ Google Maps Platform) |
| Scrape emails | 0€ |
| Hunter.io | 0€ (free tier) |
| Vérification MX | 0€ (dig local) |

## Phase 2 (si résultats + budget)

- Vérification SMTP réelle (ZeroBounce ~0.008$/email)
- Cold email automatisé (Instantly/Lemlist ~40-90$/mois + domaine dédié)
- Autres villes/pays, segment ingénieurs civils
