# AJUSTEMENT 3 — Filtres backend + pagination 5/10

## 1. Contexte

Guide agent, §3 AJUSTEMENT 3. Objectif : traiter **tous les filtres
côté backend** et fournir une **pagination configurable (5 ou 10)** sur
les endpoints de liste, avec l'enveloppe
`{ items, total, page, page_size, total_pages }`.

## 2. Fichiers existants vérifiés

- [x] `code/bdd/create/versionFinal.sql` — tables des listes
      (`t_device`, `t_type_appareil`, `t_device_statut`, `t_statut`,
      `t_utilisateur`, `t_device_utilisateur`,
      `t_device_utilisateur_recent`, `t_device_filiale`, `t_filiale`,
      `t_cpu`, `t_device_cpu`, `t_disk`, `t_disk_device`,
      `t_evenement_device`, `t_type_evenement`, `t_imprimante`)
- [x] `controller/device_controller.py` — `GET /device/liste`,
      `GET /device/search`
- [x] `controller/evenement_controller.py` — `GET /evenement/liste`
- [x] `controller/imprimante_controller.py` — `GET /imprimante/liste`
- [x] `controller/filiale_controller.py` — `GET /filiale/{id}/devices`
- [x] `service/device_service.py`, `event_service.py`,
      `imprimante_service.py`, `filiale_service.py`
- [x] `utils/builder.py` — `_build_device_response` (N+1 : statut,
      utilisateurs, filiale, type, CPU, disque par device)
- [x] Pages React : `device/liste.jsx`, `event/liste.jsx`,
      `imprimante/liste.jsx`, `filiale/liste_device.jsx`
- [x] `dashboard.jsx` consomme `getListeEvenement` / `getListeImprimante`

Endpoints de liste identifiés :
`/device/liste`, `/device/search`, `/evenement/liste`,
`/evenement/liste/type`, `/imprimante/liste`, `/filiale/liste`,
`/filiale/{id}/devices`, `/statut/liste`, `/configuration/liste`,
`/rapport/liste`.

## 3. Décision : fichiers/fonctions identifiés

- Les listes **métier** paginées : devices, événements, imprimantes,
  devices d'une filiale.
- Les **listes de référentiel** (`/statut/liste`, `/filiale/liste`,
  `/evenement/liste/type`, `/configuration/liste`) restent complètes :
  elles alimentent les dropdowns et ne doivent pas être tronquées.
- Deux requêtes sont complexes (jointures + filtres multiples) → deux
  VIEWS rédigées (§2.5) :
  `v_appareils_filtres` et `v_evenements_avec_appareil`.
- La liste des imprimantes reste une requête simple sur `t_imprimante`.

## 4. Fichiers créés / modifiés

| Ordre | Fichier | Nature |
|---|---|---|
| — | `code/bdd/views.sql` | créé (2 VIEWS, exécution manuelle) |
| 1 | `backend/utils/pagination.py` | créé : `build_page` |
| 1 | `repository/devices/devices.py` | modifié : `find_devices_paginated` |
| 1 | `repository/evenement/evenement_device.py` | modifié : `find_evenements_paginated` |
| 1 | `repository/imprimante/imprimante.py` | modifié : `find_imprimantes_paginated` |
| 1 | `repository/*/__init__.py` | exports |
| 2 | `service/device_service.py` | `getDevicesPage` + `_serialize_device_row` |
| 2 | `service/event_service.py` | `get_events_page` + `_serialize_evenement_row` |
| 2 | `service/imprimante_service.py` | `get_imprimantes_page` |
| 2 | `service/filiale_service.py` | `get_devices_by_filiale` paginé (délégation) |
| 3 | `controller/device_controller.py` | `?page=&page_size=&filtres` |
| 3 | `controller/evenement_controller.py` | idem + `datetime_from/to` |
| 3 | `controller/imprimante_controller.py` | idem |
| 3 | `controller/filiale_controller.py` | idem |
| 3 | `models/{device,evenement,imprimante}.py` | schémas `*PageResponse` |
| 4 | `components/Pagination.jsx` | créé (5/10, total, page) |
| 4 | `fonction/{device,event,imprimante,filiale}Fonction.js` | enveloppe + paramètres |
| 4 | `page/device/liste.jsx` | filtres 100 % backend |
| 4 | `page/event/liste.jsx` | filtres 100 % backend |
| 4 | `page/imprimante/liste.jsx` | recherche backend |
| 4 | `page/filiale/liste_device.jsx` | statut + pagination backend |

Paramètres exposés :
- `GET /device/liste?page=&page_size=&id_filiale=&filiale=&statut=&type_appareil=&recherche=`
- `GET /evenement/liste?page=&page_size=&type_evenement=&id_filiale=&filiale=&recherche=&datetime_from=&datetime_to=`
- `GET /imprimante/liste?page=&page_size=&recherche=`
- `GET /filiale/{id}/devices?page=&page_size=&statut=`

## 5. ⚠️ Views à créer — À exécuter manuellement par l'utilisateur

> **À exécuter dans `code/bdd/views.sql` puis sur la base PostgreSQL.**
> Tant que ces VIEWS n'existent pas, `/device/liste`,
> `/evenement/liste` et `/filiale/{id}/devices` renverront une erreur 500.
> `/imprimante/liste` fonctionne sans VIEW.

```sql
-- ------------------------------------------------------------
-- v_appareils_filtres
-- But : appareils avec statut, filiale, utilisateur, CPU et disque
--       résolus, pour des filtres et une pagination backend.
-- Colonnes : id, device_id, serial_number, modele,
--            id_type_appareil, type_appareil, chromeos_version,
--            chrome_version, mac_adress, ip_adress, date,
--            ram_total, id_utilisateur, utilisateur_email,
--            status, id_filiale, filiale, utilisateurs_recents,
--            cpu_model, cpu_freq_max, cpu_architecture,
--            disk_total, disk_free, disk_used, disk_model,
--            disk_type
-- Utilisée par : AJUSTEMENT 3, AJUSTEMENT 12
-- À exécuter manuellement dans code/bdd/views.sql puis sur la base.
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_appareils_filtres AS
WITH dernier_statut AS (
    SELECT DISTINCT ON (ds.id_device) ds.id_device, s.nom
    FROM t_device_statut ds
    JOIN t_statut s ON s.id = ds.id_statut
    ORDER BY ds.id_device, ds.date DESC, ds.id DESC
),
dernier_utilisateur AS (
    SELECT DISTINCT ON (du.id_device) du.id_device,
           du.id_utilisateur, u.email
    FROM t_device_utilisateur du
    JOIN t_utilisateur u ON u.id = du.id_utilisateur
    ORDER BY du.id_device, du.id ASC
),
utilisateurs_recents AS (
    SELECT dur.id_device,
           array_agg(u.email ORDER BY dur.date_observation DESC) AS emails
    FROM t_device_utilisateur_recent dur
    JOIN t_utilisateur u ON u.id = dur.id_utilisateur
    GROUP BY dur.id_device
),
derniere_filiale AS (
    SELECT DISTINCT ON (df.id_device) df.id_device,
           f.id AS id_filiale, f.org_unit_path
    FROM t_device_filiale df
    JOIN t_filiale f ON f.id = df.id_filiale
    ORDER BY df.id_device, df.id ASC
),
dernier_cpu AS (
    SELECT DISTINCT ON (dc.id_device) dc.id_device,
           c.cpu_model, c.freq_max_proc, c.cpu_architecture
    FROM t_device_cpu dc
    JOIN t_cpu c ON c.id = dc.id_cpu
    ORDER BY dc.id_device, dc.date DESC, dc.id DESC
),
dernier_disk AS (
    SELECT DISTINCT ON (dd.id_device) dd.id_device,
           dd.total_reel, dd.disponible, dd.total_utiliser, dk.model, dk.type
    FROM t_disk_device dd
    JOIN t_disk dk ON dk.id = dd.id_disk
    ORDER BY dd.id_device, dd.date DESC, dd.id DESC
)
SELECT
    d.id, d.device_id, d.serial_number, d.modele, d.id_type_appareil,
    ta.nom AS type_appareil, d.chromeos_version, d.chrome_version,
    d.mac_adress, d.ip_adress, d.date_creation AS date, d.ram_total,
    du.id_utilisateur, du.email AS utilisateur_email, st.nom AS status,
    fi.id_filiale, fi.org_unit_path AS filiale, ru.emails AS utilisateurs_recents,
    cp.cpu_model, cp.freq_max_proc AS cpu_freq_max, cp.cpu_architecture,
    di.total_reel AS disk_total, di.disponible AS disk_free,
    di.total_utiliser AS disk_used, di.model AS disk_model, di.type AS disk_type
FROM t_device d
LEFT JOIN t_type_appareil ta ON ta.id = d.id_type_appareil
LEFT JOIN dernier_utilisateur du ON du.id_device = d.id
LEFT JOIN dernier_statut st ON st.id_device = d.id
LEFT JOIN derniere_filiale fi ON fi.id_device = d.id
LEFT JOIN utilisateurs_recents ru ON ru.id_device = d.id
LEFT JOIN dernier_cpu cp ON cp.id_device = d.id
LEFT JOIN dernier_disk di ON di.id_device = d.id;

-- ------------------------------------------------------------
-- v_evenements_avec_appareil
-- But : événements avec type, appareil et filiale associés,
--       pour les filtres backend et la pagination.
-- Colonnes : id, date_evenement, details, type_evenement,
--            id_device, device_id, serial_number, modele,
--            id_filiale, filiale
-- Utilisée par : AJUSTEMENT 3, AJUSTEMENT 12
-- À exécuter manuellement dans code/bdd/views.sql puis sur la base.
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_evenements_avec_appareil AS
WITH derniere_filiale AS (
    SELECT DISTINCT ON (df.id_device) df.id_device,
           f.id AS id_filiale, f.org_unit_path
    FROM t_device_filiale df
    JOIN t_filiale f ON f.id = df.id_filiale
    ORDER BY df.id_device, df.id ASC
)
SELECT
    ed.id, ed.date_evenement, ed.details, te.type AS type_evenement,
    d.id AS id_device, d.device_id, d.serial_number, d.modele,
    fi.id_filiale, fi.org_unit_path AS filiale
FROM t_evenement_device ed
LEFT JOIN t_type_evenement te ON te.id = ed.id_type_evenement
LEFT JOIN t_device d ON d.id = ed.id_device
LEFT JOIN derniere_filiale fi ON fi.id_device = d.id;
```

## 5.bis C1 — Performance pagination (POST_AJUSTEMENT)

### Diagnostic (lecture seule)

| Mesure | Avant |
|---|---|
| Pagination devices page 1 | **15 875 ms** |
| Pagination devices page 50 | **17 385 ms** |
| Pagination événements page 1 | 69 ms |
| Index existants sur `t_device_statut` | PK `id` uniquement |
| Index existants sur `t_device_utilisateur_recent` | PK `id` uniquement |

Cause : les `LATERAL` de la VIEW exécutaient un `Seq Scan` de
`t_device_statut` (87 k lignes) et `t_device_utilisateur_recent`
(154 k lignes) **pour chacun des 565 devices**. Les VIEWS ont été
réécrites avec des `DISTINCT ON` / `GROUP BY` globaux (un seul passage
par table).

### Résultats après réécriture (sans index)

| Mesure | Après |
|---|---|
| Devices page 1 | ~326 ms |
| Devices page 50 | ~459 ms |
| Événements page 1 | ~6 ms (29 ms avec `COUNT(*) OVER()`) |

### Index à exécuter manuellement (C1)

> **À exécuter par l'utilisateur.** L'agent ne crée pas les index.
> Bloc également disponible dans `code/bdd/indexes.sql`.

```sql
-- C1 — pagination liste_device
CREATE INDEX IF NOT EXISTS idx_t_device_statut_device_date
    ON t_device_statut (id_device, date DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_t_device_utilisateur_recent_device_date
    ON t_device_utilisateur_recent (id_device, date_observation DESC);

CREATE INDEX IF NOT EXISTS idx_t_device_date_creation
    ON t_device (date_creation DESC);

CREATE INDEX IF NOT EXISTS idx_t_device_filiale_filiale
    ON t_device_filiale (id_filiale, id_device);

-- C1 — pagination événements
CREATE INDEX IF NOT EXISTS idx_t_evenement_device_date
    ON t_evenement_device (date_evenement DESC, id DESC);
```

### Frontend C1

- Hook `hooks/usePaginatedData.js` : cache `Map<clé, page>`, clé =
  `page:page_size:params`.
- Page déjà visitée → affichage **instantané** (aucun fetch).
- Préchargement de la page N+1 en arrière-plan.
- `loading` vrai uniquement si la page n'est pas en cache.
- `Skeleton` local en bas de liste (pas de spinner global).
- Boutons Précédent/Suivant désactivés pendant le chargement
  (anti double-clic).
- `Pagination` est mémoïsé (`React.memo`).

## 6. Spécifications

- `page` ≥ 1, `page_size` par défaut 10 (le frontend propose 5 et 10).
- `total` calculé côté SQL via `COUNT(*) OVER()` sur la requête filtrée.
- Aucun filtre client-side : recherche, statut, type, filiale et dates
  sont envoyés en query parameters.
- Le SQL reste dans `repositories/` ; les services sérialisent et
  délèguent ; les controllers valident HTTP.
- Chargement progressif : les items déjà affichés ne sont pas vidés
  pendant le chargement (le state n'est remplacé qu'à la réponse).
- `/device/search` reste disponible (compatibilité), mais la page liste
  utilise désormais `recherche` sur `/device/liste`.

## 7. Critères d'acceptation

- [x] Filtres 100 % backend sur devices, événements, imprimantes,
      devices de filiale
- [x] Pagination `page` / `page_size` (5 ou 10) sur ces mêmes listes
- [x] Réponse `{ items, total, page, page_size, total_pages }`
- [x] Aucun filtre client-side restant sur les pages concernées
- [x] VIEWS rédigées et livrées (non exécutées par l'agent)
- [x] Build frontend OK

## 8. Tests réalisés (vérifications BDD §2.7, lecture seule)

Le SELECT des VIEWS a été exécuté **sans CREATE VIEW**, avec les
filtres et la pagination réels :

| Test | Résultat |
|---|---|
| `v_appareils_filtres` (SELECT seul) | 565 lignes, 26 colonnes |
| Devices sans filtre, page 1/5 | 5 lignes, total 565 |
| Devices `statut=ACTIVE`, page 2/5 | 5 lignes, total 560 |
| Devices `type_appareil=Chromebox Enterprise G4` | 5 lignes, total 522 |
| Devices `filiale=SOREDIM` | 5 lignes, total 73 |
| Devices `recherche=5CD5286V` | 5 lignes, total 380 |
| `v_evenements_avec_appareil` (SELECT seul) | 10 colonnes |
| Événements `type=CRASH_TYPE_EMBEDDED_CONTROLLER` | 5 lignes, total 4368 |
| Événements `filiale=PROPAIN` | 5 lignes, total 487 |
| Événements `recherche=propain` | 5 lignes, total 565 |
| Imprimantes page 1/5 | 5 lignes, total 15 |
| Imprimantes `recherche=HP` | 5 lignes, total 8 |
| `build_page(items, 23, 2, 10)` | `total_pages=3` |
| Build frontend (`npm run build`) | OK |

`py_compile` OK sur les 18 fichiers backend modifiés/créés.
Note : le nombre d'événements augmente pendant les tests car la
synchronisation automatique tourne en tâche de fond.

## 9. Risques / régressions

- **Bloquant tant que les VIEWS ne sont pas créées** : les endpoints
  `/device/liste`, `/evenement/liste` et `/filiale/{id}/devices`
  échouent. Les VIEWS sont fournies ci-dessus.
- `dashboard.jsx` continue de fonctionner : `getListeEvenement` et
  `getListeImprimante` appellent la pagination avec `page_size=10000`
  et renvoient un tableau (compatibilité temporaire, remplacée par
  l'AJUSTEMENT 8).
- Petites listes de référence non paginées : comportement inchangé.
- Un changement de filtre réinitialise la page à 1 (effet dédié).

## 10. Respect §2.4

Aucune fonction imbriquée Python, pas de closure, filtres construits
par des fonctions module-level (`_build_*_filter_clause`), services et
controllers courts.

## 11. C1 corrigé — préchargement sans cache persistant (retour utilisateur)

- Hook `hooks/usePaginatedData.js` réécrit : plus de `Map` persistante
  des pages déjà vues.
- Préchargement des pages **N+1 et N+2** en arrière-plan dans un buffer
  `prefetched` (one-shot).
- Au clic « Suivant » : si la page est déjà préchargée, elle est
  consommée immédiatement puis retirée du buffer (aucune latence).
- Revenir sur une page vue plus tard → nouvel appel (pas de cache).
- `loading` ne concerne que la page courante ; `Skeleton` local en bas
  de liste (pas de spinner global).

## 12. Pagination + cache — liste des filiales (même système que device/événements)

- Endpoint paginé dédié : `GET /filiale/liste/page?page=&page_size=&recherche=`
  → `{ items, total, page, page_size, total_pages }` (`FilialePageResponse`).
- `GET /filiale/liste` reste **complet** (non paginé) : il alimente les
  dropdowns de filiale.
- Repository : `find_filiales_paginated` (`COUNT(*) OVER()` + `LIMIT/OFFSET`).
- Service : `get_filiales_page` caché sous le préfixe `filiales:` (TTL 60 s),
  invalidé après `commit` de synchronisation.
- Frontend : `page/filiale/liste.jsx` utilise `usePaginatedData`
  (préchargement N+1/N+2) + composant `Pagination` (5/10).
- `/filiale/{id}/devices` (devices d'une filiale) avait déjà pagination +
  cache via `getDevicesPage` (clé `devices:`) : aucun changement requis.
