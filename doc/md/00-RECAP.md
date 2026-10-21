# 00 — RÉCAPITULATIF DES AJUSTEMENTS

Sources d'instructions : `doc/md/first_ajustement/`
(guide `AI_AGENT_GUIDE_MONITORING_PLATFORM_FIRST_CORRECTION.md` +
`POST_AJUSTEMENT.md`).

## Convention de chemins

- Le guide parle de `sql/versionFinal.sql` et `sql/views.sql` ; le dépôt
  ne contient pas de dossier `sql/`. Équivalent réel :
  - tables : `code/bdd/create/versionFinal.sql` (source de vérité)
  - views : **`code/bdd/views.sql`**
  - suppression de views : **`code/bdd/drop_views.sql`**
- Arborescence réelle :
  `code/backend/fonction/metier/{repository,service,controller,models}`
  (et non `app/`).
- Les endpoints du guide préfixés `/api/...` sont exposés sans `/api`.

## Tableau de suivi — AJUSTEMENTS 1 → 13

| # | Ajustement | Statut | Doc |
|---|---|---|---|
| 1 | Réseaux manquants `t_device_reseau` | ✅ fait (C0 inclus) | `01-sync-insertion-device-reseau.md` |
| 2 | Graph RAM frontend : max total | ✅ fait | `02-ram-max-total.md` |
| 3 | Filtres backend + pagination 5/10 | ✅ fait (C1 inclus) | `03-filtres-backend-pagination.md` |
| 4 | Caching | ✅ fait | `04-caching.md` |
| 5 | Skeleton UI | ✅ fait | `05-skeleton-ui.md` |
| 6 | CPU/RAM directs depuis la DB | ✅ fait | `06-cpu-ram-direct-db.md` |
| 7 | Vérifier `t_disk_device` | ✅ fait | `07-disk-verification.md` |
| 8 | Dashboard rapide | ✅ fait (C2 inclus) | `08-dashboard-perf.md` |
| 9 | Format date/heure `t_evenements` | ✅ fait | `09-events-datetime-format.md` |
| 10 | Durée de vie avant extinction | ✅ fait (C3 inclus) | `10-life-remaining.md` |
| 11 | CPU/RAM plage + somme + détail | ✅ fait (C4 inclus) | `11-cpu-ram-range-sum.md` |
| 12 | Filtres date + heure partout | ✅ fait (C5 inclus) | `12-datetime-filters.md` |
| 13 | Documentation de suivi | ✅ fait | ce fichier |

## Tableau de suivi — POST_AJUSTEMENT C0 → C7

| # | Correction | Statut | Notes |
|---|---|---|---|
| C0 | Insertion `t_device_reseau` + audit doublons | ✅ fait | liaison insérée dans `insertion_device` (pré-check `get_by_device_and_reseau`) ; `reseau_service` supprimé ; audit validé |
| C1 | Performance pagination devices/événements | ✅ code fait | VIEWS réécrites **à ré-exécuter** ; index livrés |
| C2 | Dashboard : redirections + cartes cliquables | ✅ fait | `/liste/imprimante` → `/imprimantes` |
| C3 | Life remaining → page événements | ✅ fait | `life_*` fusionnés dans `evenement_*` |
| C4 | CPU/RAM : somme via date+heure | ✅ fait | VIEWS de plage retirées → `drop_views.sql` |
| C5 | Filtre calendrier avec heure | ✅ fait | `DateHeureFilter` unique + validation 400 |
| C6 | `drop_views.sql` + recensement | ✅ fait | 2 VIEWS de plage à supprimer |
| C7 | Audit / consolidation | ✅ fait | `statistique_service` fusionné |

## Bilan

- **13 ajustements + 8 corrections POST_AJUSTEMENT livrés.**
- Aucun `CREATE VIEW`, `CREATE INDEX`, `DROP VIEW`, `ALTER`, `INSERT`,
  `UPDATE`, `DELETE` exécuté par l'agent.
- Aucun `ALTER TABLE ADD CONSTRAINT UNIQUE` rédigé.
- Aucun SQL hors `repositories/`, aucune fonction imbriquée.
- Vérifications BDD uniquement en lecture seule (§2.7).

## Views — état réel (vérifié en base, lecture seule)

Les VIEWS existent déjà en base. **Attention** : `v_appareils_filtres`
et `v_evenements_avec_appareil` ont encore l'**ancienne définition
LATERAL** (performance C1 non active).

| View (nom français) | Ajustement | Statut en base | Action |
|---|---|---|---|
| v_appareils_filtres | 3 / C1 | existe (ancienne version) | **ré-exécuter** le bloc de `code/bdd/views.sql` |
| v_evenements_avec_appareil | 3 / C1 | existe (ancienne version) | **ré-exécuter** le bloc de `code/bdd/views.sql` |
| v_tableau_de_bord_resume | 8 | existe | à jour |
| v_imprimantes_filtrees | 12 | existe | à jour |
| v_resume_plage_cpu | 11 / C4 | existe | **supprimer** (`drop_views.sql`) |
| v_resume_plage_ram | 11 / C4 | existe | **supprimer** (`drop_views.sql`) |

> `CREATE OR REPLACE VIEW` et `DROP VIEW` sont à exécuter
> **manuellement par l'utilisateur**, depuis `code/bdd/views.sql` et
> `code/bdd/drop_views.sql`.

## Views à supprimer (`code/bdd/drop_views.sql`)

```sql
-- v_resume_plage_cpu
-- Raison : remplacée par la somme date+heure sur t_device_cpu (C4)
-- Date : 2026-10-19
DROP VIEW IF EXISTS v_resume_plage_cpu;

-- v_resume_plage_ram
-- Raison : remplacée par la somme date+heure sur t_device_ram (C4)
-- Date : 2026-10-19
DROP VIEW IF EXISTS v_resume_plage_ram;
```

## Endpoints ajoutés / modifiés

| Endpoint | Ajustement |
|---|---|
| `GET /ram/{device_id}/max-total` | 2 |
| `GET /device/liste` (pagination + filtres + date/heure) | 3, 12 |
| `GET /evenement/liste` (pagination + filtres + date/heure) | 3, 12 |
| `GET /imprimante/liste` (pagination + filtres + date/heure) | 3, 12 |
| `GET /filiale/{id}/devices` (pagination + filtres + date/heure) | 3, 12 |
| `GET /cpu/{device_id}/latest` | 6 |
| `GET /ram/{device_id}/latest` | 6 |
| `GET /disk/{device_id}/latest` | 7 |
| `GET /dashboard/summary` | 8 |
| `GET /evenement/{event_id}/duree-vie` | 10, C3 |
| `GET /cpu/{device_id}/somme?date_debut=&date_fin=` | 11, C4 |
| `GET /ram/{device_id}/somme?date_debut=&date_fin=` | 11, C4 |
| `GET /rapport/filter?datetime_from=&datetime_to=` | 12 |

Endpoints supprimés : `/life/{id}`, `/cpu/{id}/summary`,
`/ram/{id}/summary`.

## Fusions effectuées (C7)

| Source | Cible | Raison |
|---|---|---|
| `life_service.py` + `life_controller.py` | `event_service.py` + `evenement_controller.py` | la durée de vie est une propriété de l'événement/device |
| `statistique_service.py` | `dashboard_service.py` | mêmes agrégats dashboard |
| `repository/ram/__init.__.py` (typo) | supprimé | fichier orphelin, jamais importé |
| `sum_range` / `get_*_range_summary` | `get_*_device_date` | simplification C4 |
| `service/reseau_service.py` | supprimé | insertion directe dans `insertion_device` ; plus de second passage |

Non fusionnés (domaines distincts, légitimes) : `cpu_*`, `ram_*`,
`disk_*`, `device_*`, `imprimante_*`, `rapport_*`, `reseau_*`,
`configuration_*`, `filiale_*`, `user_*`.

## Fichiers transverses créés

- `backend/core/cache.py` — cache TTL
- `backend/utils/pagination.py` — enveloppe `{items, total, …}`
- `backend/utils/validation.py` — validation des bornes date/heure (C5)
- `frontend/src/components/Skeleton.jsx` + `components/skeletons/`
- `frontend/src/components/Pagination.jsx`
- `frontend/src/hooks/usePaginatedData.js` — cache client + prefetch (C1)
- `frontend/src/page/component/DateHeureFilter.jsx`
- `frontend/src/page/component/EvenementDureeVie.jsx` (C3)
- `code/bdd/views.sql`, `code/bdd/drop_views.sql`,
  `code/bdd/indexes.sql` (C0/C1, à exécuter manuellement)
- `doc/md/first_ajustement/bdd.md` — rôle détaillé de chaque VIEW et
  de chaque INDEX

## Questions ouvertes

- **AJUSTEMENT 10** : tranché — batterie restante + temps depuis le
  dernier événement.
- **C0 — audit `t_reseau_filiale`** : ✅ tranché par l'utilisateur —
  un réseau **peut** appartenir à plusieurs filiales (sous-réseau
  partagé). Aucun `DELETE`, aucune contrainte `UNIQUE`
  supplémentaire. Audit interne par filiale : **0 doublon**
  (total = distincts pour les 30 filiales).
- `versionFinal.sql` contient deux virgules manquantes avant des
  contraintes `UNIQUE` (`t_device_reseau`, `t_seuil_statut`) ; la base
  réelle est corrigée via `alter_table.sql`.

## Checklist finale

- [x] Workflow Repository → Service → Controller → Model
- [x] `versionFinal.sql` consulté
- [x] Aucun SQL hors `repositories/`
- [x] Aucune logique métier dans les controllers
- [x] Idempotence (réseaux, rapports, événements, disques)
- [x] Gestion d'erreurs par device isolée
- [x] Skeleton UI sur les zones de contenu
- [x] Cache service + cache client pagination
- [x] Pagination 5/10 sur les listes métier
- [x] Filtres 100 % backend
- [x] Date + heure combinés partout
- [x] Aucun `CREATE VIEW` / `CREATE INDEX` / `DROP VIEW` exécuté
- [x] VIEWS et index livrés dans les `.md` + ce fichier
- [x] Noms des VIEWS en français
- [x] Vérifications BDD en lecture seule
- [x] Aucune fonction imbriquée
- [x] Aucun `ALTER TABLE ADD CONSTRAINT`
- [x] `.md` de suivi créé/mis à jour pour chaque étape
