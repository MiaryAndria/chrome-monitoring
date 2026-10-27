# AJUSTEMENT 9 — Format date/heure `t_evenements`

## 1. Contexte

Guide agent, §3 AJUSTEMENT 9. Objectif : stocker les dates
d'événements en `TIMESTAMPTZ` UTC et fournir un affichage formaté
`dd/MM/yyyy HH:mm:ss` dans le fuseau de l'administrateur.

> La table réelle est `t_evenement_device` (colonne `date_evenement`),
> et non `t_evenements`.

## 2. Fichiers existants vérifiés

- [x] `code/bdd/create/versionFinal.sql` — `t_evenement_device`
      (`date_evenement TIMESTAMPTZ NOT NULL`)
- [x] `service/import_service.py` — `insert_event` passait la date
      Google brute (`crash["time"]`) à `create_evenement_device`
- [x] `repository/evenement/evenement_device.py` — `create_evenement_device`
      (SQL uniquement, inchangé)
- [x] `service/event_service.py` — `_serialize_evenement_row` renvoyait
      `str(datetime)` sans normalisation UTC
- [x] `utils/format_date.py` — `parse_date_safe` existant (réutilisé)
- [x] `frontend/src/fonction/utils/util.js` — `formatDate`
      (sans secondes ni fuseau admin)
- [x] `component_event.jsx`, `page/event/liste.jsx` — affichage des dates

## 3. Décision : fichiers/fonctions identifiés

- Parsing Google → UTC dans le **service** de synchronisation
  (`_parse_google_datetime`), pas dans le repository.
- Normalisation UTC à la sérialisation (`_date_evenement_utc`).
- Helper d'affichage plat `formatDateTime` au niveau module, côté
  frontend, avec `VITE_ADMIN_TIMEZONE` (défaut
  `Indian/Antananarivo`) et secondes.

## 4. Fichiers créés / modifiés

| Fichier | Nature |
|---|---|
| `service/import_service.py` | `_parse_google_datetime` + usage dans `insert_event` |
| `service/event_service.py` | `_date_evenement_utc` + sérialisation ISO UTC |
| `frontend/src/fonction/utils/util.js` | ajout `formatDateTime` |
| `frontend/src/page/component/component_event.jsx` | utilise `formatDateTime` |
| `frontend/src/page/event/liste.jsx` | colonne Date formatée (l'ancien `accessor: "date"` ne correspondait à aucune colonne) |

## 5. ⚠️ Views à créer — À exécuter manuellement par l'utilisateur

**Aucune nouvelle VIEW.** Rappel : les VIEWS des AJUSTEMENTS 3 et 8
restent à créer.

## 6. Spécifications

- Insertion : `_parse_google_datetime(value)` accepte RFC3339 (`Z`,
  offset), datetime naïve (considérée UTC) et datetime aware ;
  retourne un `datetime` UTC ou `None`.
- Si la date est absente/invalide, l'événement est ignoré (`continue`)
  car `date_evenement` est `NOT NULL`.
- Sérialisation API : `datetime` normalisé en ISO 8601 UTC
  (`2026-10-19T10:56:16+00:00`).
- Affichage : `formatDateTime(dateStr)` →
  `Intl.DateTimeFormat('fr-FR', { ..., hour12:false, timeZone })`,
  format `dd/MM/yyyy HH:mm:ss`.
- Fuseau : `VITE_ADMIN_TIMEZONE` si défini, sinon
  `Indian/Antananarivo` (le projet utilise UTC+3).

## 7. Critères d'acceptation

- [x] Dates Google parsées et stockées en UTC (service)
- [x] API renvoie un ISO UTC explicite
- [x] Helper `formatDateTime` plat au niveau module
- [x] Affichage avec secondes et fuseau admin
- [x] Aucun SQL ajouté hors repository
- [x] Build frontend OK

## 8. Tests réalisés (vérifications BDD §2.7, lecture seule)

| Test | Résultat |
|---|---|
| `2026-10-19T07:56:16.152Z` | `2026-10-19 07:56:16.152000+00:00` |
| `2026-10-19T10:56:16+03:00` | `2026-10-19 07:56:16+00:00` |
| `2026-10-19T07:56:16` (naïf) | interprété UTC |
| `"pas une date"` / `None` | `None` |
| Sérialisation aware +03 | `2026-10-19T10:56:16+00:00` |
| Dates réelles en base | `TIMESTAMPTZ` (ex. 2026-10-19 14:10:08+03) |
| Build frontend | OK |

`py_compile` OK sur les 2 fichiers backend modifiés.

## 9. Risques / régressions

- Les événements dont la date Google est absente/invalide sont
  désormais ignorés au lieu d'être insérés avec une valeur invalide.
- Le format d'affichage passe de `jj/mm/aaaa hh:mm` à
  `jj/mm/aaaa hh:mm:ss` : plus précis, aucune rupture fonctionnelle.
- `VITE_ADMIN_TIMEZONE` n'est lu que si Vite est configuré avec ce
  fichier d'environnement ; le défaut reste correct.

## 10. Respect §2.4

`_parse_google_datetime`, `_date_evenement_utc` et `formatDateTime`
sont des fonctions plates au niveau module ; aucune fonction
imbriquée.
