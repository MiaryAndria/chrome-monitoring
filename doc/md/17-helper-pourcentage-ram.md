# 17 — Centralisation du pourcentage RAM (un seul helper)

## Objectif
Supprimer les calculs de pourcentage dupliqués et n'avoir **qu'une seule source** pour
le % RAM, pour que l'affichage, la comparaison et le futur moteur de seuil donnent
exactement le même chiffre.

## Problème initial : 3 calculs différents
| Où | Fichier | Formule |
|---|---|---|
| Frontend (RAM, stockage) | `frontend/src/fonction/utils/util.js:72` `usagePercent` | `Math.round((total-libre)/total*100)` |
| Backend comparaison | `backend/utils/comparaison_stats.py:8` `normaliser_ram_pct` | `round(clamp(utiliser/total*100),1)` |
| Backend (dormant) | `backend/utils/format_valeur.py:38` `usage_percent` | `round(used/total*100,1)` |

Contrainte : le front (JS) et le back (Python) ne peuvent pas partager une fonction.
Décision retenue (**Option A**) : **le backend calcule, le front consomme**.

## Ce qui a changé

### Backend — un seul helper : `usage_percent`
- `backend/utils/format_valeur.py` → **helper unique** `usage_percent(used, total, decimals=1)`
  (borné à `[0, 100]`, retourne `None` si total <= 0). C'est désormais la seule
  implémentation côté backend (utilisée par la RAM, la comparaison et le futur seuil).
- `backend/utils/comparaison_stats.py` → **suppression** de `normaliser_ram_pct`.
- `backend/fonction/metier/service/comparaison_service.py` → import de
  `usage_percent` (au lieu de `normaliser_ram_pct`) pour `moyenne_pct`.
- `backend/fonction/metier/service/ram_service.py` → `get_latest_ram` renvoie un champ
  **`utilisation_pct`** calculé via le helper (dérive `ram_utiliser` si absent).

### Frontend — consommation de la valeur backend
- `frontend/src/page/device/detail/ram_tab.jsx` → `pct = latest.utilisation_pct`
  (le calcul local ne reste qu'en repli si aucun relevé RAM n'existe).
- `usagePercent` (util.js) reste le helper unique **front**, toujours utilisé pour le
  **stockage** (`storage_tab.jsx`, `general_tab.jsx`) et le repli RAM.

## Contrat API
`GET /ram/{device_id}/latest` renvoie désormais :
```json
{
  "id": 64773, "id_device": 1,
  "ram_total": 8589934592, "ram_utiliser": 6986981376, "ram_libre": 1602953216,
  "utilisation_pct": 81.3,
  "date": "2026-10-23 13:03:06.022000+03:00"
}
```

## Validations
- `compileall` des modules modifiés : OK.
- Import `comparaison_service` + `backend.main` (venv) : OK.
- `get_latest_ram(1)` → `utilisation_pct = 81.3` (6.99 Go / 8.59 Go) : conforme.
- `npm run build` : OK.
- Plus aucune référence à `normaliser_ram_pct` (grep repo) : OK.

## À faire (manuel)
1. Redémarrer le backend uvicorn (nouveau champ + imports modifiés).
2. Redémarrer / rebuild le frontend (`npm run dev` ou servir `dist/`).
3. Optionnel : supprimer le repli front de `ram_tab.jsx` si tu veux que la RAM dépende
   strictement du backend.
