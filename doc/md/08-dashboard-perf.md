# AJUSTEMENT 8 — Dashboard rapide

## 1. Contexte

Guide agent, §3 AJUSTEMENT 8. Objectif : charger le dashboard en **un
seul appel API**, rapide (< 500 ms avec cache), via la VIEW
`v_tableau_de_bord_resume`.

## 2. Fichiers existants vérifiés

- [x] `code/bdd/create/versionFinal.sql` — toutes les tables agrégées
- [x] `controller/dashboard_controller.py` — `GET /dashboard/stats`
- [x] `service/statistique_service.py` — comptages device/statut/type
- [x] `page/dashboard.jsx` — 3 appels séparés
      (`/dashboard/stats`, `/evenement/liste`, `/imprimante/liste`)
- [x] `components/skeletons/DashboardSkeleton.jsx` — créé en AJUSTEMENT 5
- [x] Aucun `dashboard_repository.py` ni `dashboard_service.py`

## 3. Décision : fichiers/fonctions identifiés

- Une VIEW unique `v_tableau_de_bord_resume` (une seule ligne) remplace
  tous les comptages.
- Le backend expose `GET /dashboard/summary` (équivalent réel de
  `/api/dashboard/summary`), caché côté service.
- `/dashboard/stats` est conservé pour compatibilité, mais le frontend
  ne l'appelle plus.
- Le dashboard ne fait plus qu'**un seul** appel.

## 4. Fichiers créés / modifiés

| Ordre | Fichier | Nature |
|---|---|---|
| — | `code/bdd/views.sql` | ajout de `v_tableau_de_bord_resume` |
| 1 | `repository/dashboard/dashboard.py` | créé : `get_summary(cur)` |
| 1 | `repository/dashboard/__init__.py` | créé |
| 2 | `service/dashboard_service.py` | créé : `get_summary` + cache |
| 3 | `controller/dashboard_controller.py` | ajout `GET /dashboard/summary` |
| 3 | `models/dashboard.py` | créé : `DashboardSummaryResponse` |
| 3 | `service/import_service.py` | invalidation `dashboard:` |
| 4 | `fonction/deviceFonction.js` | `getDashboardSummary` |
| 4 | `page/dashboard.jsx` | un seul appel + `DashboardSkeleton` |

## 5. ⚠️ Views à créer — À exécuter manuellement par l'utilisateur

> **À exécuter dans `code/bdd/views.sql` puis sur la base PostgreSQL.**
> Tant que cette VIEW n'existe pas, `GET /dashboard/summary` (et donc le
> dashboard) échouera.

```sql
-- ------------------------------------------------------------
-- v_tableau_de_bord_resume
-- But : indicateurs agrégés du tableau de bord en une seule ligne.
-- Colonnes : nb_total_appareils, nb_actifs, nb_indisponibles,
--            nb_anomalie, nb_reparation, nb_crashs,
--            nb_incidents, nb_imprimantes,
--            repartition_statuts, repartition_types,
--            repartition_evenements
-- Mapping métier :
--   actifs        = dernier statut ACTIVE
--   indisponibles = dernier statut DISABLED ou DEPROVISIONED
--   anomalie      = dernier statut DELINQUENT
--   reparation    = devices ayant au moins une alerte non RESOLUE
--   crashs        = nombre de lignes t_evenement_device
--   incidents     = nombre d'incident_key distincts
-- Utilisée par : AJUSTEMENT 8 (dashboard rapide)
-- À exécuter dans code/bdd/views.sql puis sur la base.
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_tableau_de_bord_resume AS
WITH derniers_statuts AS (
    SELECT DISTINCT ON (ds.id_device)
        ds.id_device,
        s.nom
    FROM t_device_statut ds
    JOIN t_statut s ON s.id = ds.id_statut
    ORDER BY ds.id_device, ds.date DESC, ds.id DESC
),
repartition_statuts AS (
    SELECT COALESCE(jsonb_object_agg(nom, nb), '{}'::jsonb) AS valeur
    FROM (
        SELECT nom, COUNT(*) AS nb
        FROM derniers_statuts
        WHERE nom IN ('ACTIVE', 'DELINQUENT', 'DISABLED', 'DEPROVISIONED')
        GROUP BY nom
    ) t
),
repartition_types AS (
    SELECT COALESCE(jsonb_object_agg(nom, nb), '{}'::jsonb) AS valeur
    FROM (
        SELECT ta.nom, COUNT(*) AS nb
        FROM t_device d
        JOIN t_type_appareil ta ON ta.id = d.id_type_appareil
        GROUP BY ta.nom
    ) t
),
repartition_evenements AS (
    SELECT COALESCE(jsonb_object_agg(type, nb), '{}'::jsonb) AS valeur
    FROM (
        SELECT te.type, COUNT(*) AS nb
        FROM t_evenement_device ed
        JOIN t_type_evenement te ON te.id = ed.id_type_evenement
        GROUP BY te.type
    ) t
)
SELECT
    (SELECT COUNT(*) FROM t_device) AS nb_total_appareils,
    (SELECT COUNT(*) FROM derniers_statuts WHERE nom = 'ACTIVE') AS nb_actifs,
    (SELECT COUNT(*) FROM derniers_statuts
      WHERE nom IN ('DISABLED', 'DEPROVISIONED')) AS nb_indisponibles,
    (SELECT COUNT(*) FROM derniers_statuts WHERE nom = 'DELINQUENT') AS nb_anomalie,
    (SELECT COUNT(DISTINCT da.id_device)
       FROM t_device_alerte da
      WHERE NOT EXISTS (
          SELECT 1
          FROM t_device_alerte_statut das
          JOIN t_statut s ON s.id = das.id_statut
          WHERE das.id_device_alerte = da.id AND s.nom = 'RESOLUE'
      )) AS nb_reparation,
    (SELECT COUNT(*) FROM t_evenement_device) AS nb_crashs,
    (SELECT COUNT(DISTINCT ed.details->>'incident_key')
       FROM t_evenement_device ed) AS nb_incidents,
    (SELECT COUNT(*) FROM t_imprimante) AS nb_imprimantes,
    (SELECT valeur FROM repartition_statuts) AS repartition_statuts,
    (SELECT valeur FROM repartition_types) AS repartition_types,
    (SELECT valeur FROM repartition_evenements) AS repartition_evenements;
```

## 6. Spécifications

- Repository : `SELECT * FROM v_tableau_de_bord_resume` (une ligne).
- Service : cache `dashboard:summary`, TTL `CACHE_TTL_SECONDS` ;
  invalidation après synchronisation (`cache_invalidate_prefix`).
- Controller : `GET /dashboard/summary` validé par
  `DashboardSummaryResponse`.
- Frontend : `getDashboardSummary()` unique, `DashboardSkeleton` au
  chargement, suppression des appels `/dashboard/stats`,
  `/evenement/liste` et `/imprimante/liste`.
- Les sous-compteurs Kernel / EC / App / Autre sont dérivés de
  `repartition_evenements` (objet JSON déjà agrégé par la VIEW).

## 7. Critères d'acceptation

- [x] SQL de `v_tableau_de_bord_resume` rédigé et livré
- [x] `dashboard_repository.get_summary`
- [x] `dashboard_service.get_summary` + cache
- [x] `GET /dashboard/summary`
- [x] Frontend à un seul appel + `DashboardSkeleton`
- [x] Aucun `CREATE VIEW` exécuté par l'agent
- [x] Build frontend OK

## 8. Tests réalisés (vérifications BDD §2.7, lecture seule)

Le corps `WITH ... SELECT` de la VIEW a été exécuté **sans CREATE VIEW** :

| Indicateur | Résultat |
|---|---|
| nb_total_appareils | 565 |
| nb_actifs (ACTIVE) | 560 |
| nb_indisponibles (DISABLED + DEPROVISIONED) | 3 |
| nb_anomalie (DELINQUENT) | 2 |
| nb_reparation (alertes non résolues) | 0 |
| nb_crashs | 5 557 |
| nb_incidents (incident_key distincts) | 5 557 |
| nb_imprimantes | 15 |
| repartition_statuts | `{ACTIVE:560, DELINQUENT:2, DISABLED:1, DEPROVISIONED:2}` |
| repartition_types | 5 modèles, Chromebox G4 = 522 |
| repartition_evenements | `{KERNEL:1133, EMBEDDED_CONTROLLER:4376, UNKNOWN:48}` |

Autres vérifications :
- route OpenAPI `/dashboard/summary` présente et typée ;
- service avec cache pré-rempli → retour immédiat sans BDD ;
- `py_compile` OK sur les 7 fichiers backend ;
- build frontend OK.

## 9. Risques / régressions

- **Bloquant tant que la VIEW n'est pas créée** : `/dashboard/summary`
  échoue (500). Le bloc SQL complet est fourni ci-dessus.
- `nb_incidents` égale `nb_crashs` aujourd'hui car chaque
  `incident_key` est unique ; la métrique reste correcte si des
  événements partagent une clé.
- `nb_reparation` vaut 0 tant qu'aucune alerte n'existe
  (`t_device_alerte` vide).
- `/dashboard/stats` reste disponible (aucune rupture d'API).

## 10. Respect §2.4

Fonctions module-level : `_fetch_summary`, `get_summary`, et
`get_summary(cur)` côté repository. Aucune fonction imbriquée, aucune
closure.

## 11. C2 — Redirections du dashboard (POST_AJUSTEMENT)

### Cause exacte

- La carte « Imprimantes » appelait `navigate("/liste/imprimante")`.
- La route réellement déclarée dans `App.jsx` est `/imprimantes`.
- Résultat : navigation vers une route inexistante (page vide / erreur),
  alors que le lien Sidebar utilise bien `/imprimantes`.

### Corrections

- `dashboard.jsx` : `navigate("/liste/imprimante")` →
  `navigate("/imprimantes")`.
- Les 4 sous-cartes événements (Kernel / EC / App-Web / Autre) sont
  désormais cliquables : `cursor-pointer`, hover, `stopPropagation`
  pour ne pas déclencher la navigation de la carte parente.
  - Kernel → `/liste/event?type=CRASH_TYPE_KERNEL`
  - EC → `/liste/event?type=CRASH_TYPE_EMBEDDED_CONTROLLER`
  - App/Web → `/liste/event` (aucun type BROWSER/APP en base)
  - Autre → `/liste/event?type=UNKNOWN`
- `page/event/liste.jsx` lit `?type=` via `useSearchParams` et
  initialise `typeEvenement`.

### Vérifications

- `grep "liste/imprimante"` → 0 occurrence restante.
- Route `/imprimantes` déclarée dans `App.jsx` et Sidebar.
- Build frontend OK.
- Si la VIEW `v_imprimantes_filtrees` n'est pas créée, la page
  imprimantes affiche son état d'erreur (`EmptyState`) au lieu de
  planter.
