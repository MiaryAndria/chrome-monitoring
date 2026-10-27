# 18 — Guide : service d'alerte (catalogue + moteur d'évaluation)

> Aucune modification de BDD dans cette étape : le code a été aligné sur le schéma **existant**.

## 1. Le schéma réel (vérifié en base)

| Table | Colonnes | Rôle |
|---|---|---|
| `t_alerte` | `id`, `type` (UNIQUE) | **Catalogue** des types d'alerte. **Pas de `message`, pas de `date`.** |
| `t_alerte_statut` | `id`, `id_alerte`, `id_statut`, `date` | Cycle de vie du **catalogue** |
| `t_device_alerte` | `id`, `id_device`, `id_alerte`, `message`, `date` | **Occurrence** par device (le message est ici) |
| `t_device_alerte_statut` | `id`, `id_device_alerte`, `id_statut`, `date` (nullable) | Cycle de vie de l'**occurrence** |

**Deux cycles de vie distincts** (statuts de `t_statut`) :
- Catalogue (`t_alerte_statut`) : `12 CREER`, `13 MODIFIER`, `14 SUPPRIMER` (archive), `16 RESTAURER`.
- Occurrence (`t_device_alerte_statut`) : `1 ACTIVE`, `15 RESOLUE`.

⚠️ Pièges corrigés : `t_device_alerte` **n'a pas** de `date_resolution` (elle a été supprimée), et la table s'appelle `t_device_alerte_statut` (pas `t_device_alerte_status`).

## 2. Corrections apportées à ta maquette de service

| Ligne de ta maquette | Problème | Correction |
|---|---|---|
| `getDeviceList()` | `return result` était **dans** la boucle (1 seul device) ; appelait `get_utilisateur_recent_by_device(id)` sans `cur` | **Complétée** : `cur` passé, `return` hors boucle (565 devices OK) |
| `getListeDeviceAlerteDate()` / `getAllDeviceAlerte()` | `cur`/`id_device` non définis, pas de `return` | **Complétées** : `get_liste_device_alerte_by_date(cur, …)` / alias de `getListeDeviceAlerte()` |
| `createAlerte` → `insertIntoAlerte(type,date)` | fonction inexistante | `insert_alerte(cur, type)` (get_or_create via `ON CONFLICT`) |
| `createAlerte` → `insertIntoAlerteStatus` | inexistante ; mélangeait `status_id=12` du catalogue | `insert_alerte_statut(cur, id_alerte, 12)` |
| `updateAlerte` → `updateAlerte(cur,...)` | **récursion infinie** ; `cur` non défini | `update_alerte(cur, id_alerte, type)` |
| `getListeArchiveAlerte()` | **`:` manquant** (erreur de syntaxe) | `get_liste_alerte_archive(cur)` |
| `reActiverAlerte` → `restoreAlerte` | inexistante | `restore_alerte(cur, id, 16)` + vérif archive |
| `getNombreAlerte` → `getCountAlerte` | SQL cassé (`t_device_alerte_status`, `id_status`) | `get_nombre_alerte_active(cur)` (dernier statut = 1) |
| `insertAlerte` → `seuil = getSeuil` | fonction inexistante, pas d'appel | `_seuils_actifs(cur)` = `{cle: valeur}` des seuils non archivés |
| `if l.cpu > seuil.cpu` | compare la **liste** `l` et des attributs inexistants | `_metriques_device(cur, id)` par device + comparaison au seuil |
| `insertIntoDeviceAlerte(...)` | `cur.fetchone()` après INSERT **sans `RETURNING`** → None | `insert_device_alerte(... RETURNING id)` |
| `insertIntoDeviceAlerteStatuts` | typo + inexistante | `insert_device_alerte_statut(cur, id_device_alerte, id_statut)` |
| `insertIntoTDevcieAlerteStatus` | typo | idem |
| `insertAlerte` (engine) | indentation cassée, pas de commit/rollback | boucle propre + `commit`/`rollback` + retour `{creations, resolutions}` |

Bugs **repo** corrigés : `=(...)` au lieu de `IN`, `&` au lieu de `AND`, `id_status`/`date_resolution` inexistants, `insert_into_alerte` sans `RETURNING` et sans paramètre `cur`, connexion ouverte au niveau module.

## 3. Repository — complété (`repository/alerte/`)

Rien n'est supprimé : toutes les fonctions existantes sont **conservées et corrigées**.

- `alerte.py` (catalogue) : `get_liste_alerte`, `find_alertes_paginated`, `get_liste_alerte_archive`, `find_alertes_archived_paginated`, `get_alerte_by_id`, `get_alerte_by_type`, `get_alerte_archivee_by_id`, `insert_alerte` (get_or_create `RETURNING id`), `update_alerte`, `delete_alerte`, `restore_alerte`, `get_alertes_actives`, `get_alertes_resolues`, `getCountAlerte` (complété), `get_temperature_max_device`.
- `alerte_statut.py` : `insert_alerte_statut`, `get_statuts_alerte`, `get_dernier_statut_alerte` (le fichier était vide, désormais implémenté).
- `device_alerte.py` (occurrences) : `get_liste_device_alerte`, `get_liste_device_alerte_by_date` (`&`→`AND`), `get_device_alerte_by_id`, `get_alertes_by_device`, `get_devices_by_alerte`, `get_alertes_actives_by_device`, `get_alertes_resolues_by_device`, `get_alertes_by_period`, `get_derniere_alerte_device`, `get_nombre_alerte_active`, `get_nombre_alerte_device`, `get_device_alerte_by_device_and_alerte`, `get_device_alerte_active_by_device_and_alerte`, `get_alertes_actives_by_device_and_period`, `get_alertes_by_alerte_and_period`, `insert_device_alerte` (`RETURNING id`), `insert_device_alerte_statut`.
- Les **actives/résolues** sont calculées via le dernier `t_device_alerte_statut` (plus de `date_resolution`, qui n'existe plus en base) ; constante partagée `DERNIER_STATUT_SQL`.

## 4. Service (`service/alerte_service.py`)

- Devices : `getDeviceList()`.
- Catalogue : `getListeAlerte`, `getAlertesPage`, `getListeArchiveAlerte`, `getAlertesArchivePage`, `getDetailAlerte`, `createAlerte`, `updateAlerte`, `deleteAlerte`, `reActiverAlerte`.
- Occurrences : `getNombreAlerte`, `getListeDeviceAlerte`, `getListeDeviceAlerteDate`, `getAlertesByDevice`.
- Moteur : `insertAlerte()`.

**Plus aucun id codé en dur** :
- Statuts : on garde les **noms** (`NOM_STATUT_*`) et `_id_statut(cur, nom)` résout l'id via `t_statut` (repository statut).
- Seuils : les noms de clés (`SEUIL_CPU`…) restent la référence métrique → seuil ; les **valeurs** viennent de la base via le repository seuil (`get_liste_seuil`, seuils non archivés).
- Les helpers `updateAlerteStatutToActive/ToResolue` ont été retirés : le moteur écrit les statuts directement dans sa transaction (`insert_device_alerte_statut`).

Cache : clés `alertes:` (liste + archive), invalidées à chaque écriture. Pagination via `build_page`.

## 5. Le moteur `insertAlerte()` — logique

```
seuils actifs (t_seuil non archivés)  = {seuil_utilisation_cpu, seuil_utilisation_ram, seuil_capteur_cpu}
pour chaque device :
    métriques = dernière CPU % (t_device_cpu)
                dernière RAM % (t_device_ram, via usage_percent)
                température max capteurs (t_rapport_device CPU_STATUS)
    pour chaque seuil présent :
        dépassé  → si aucune occurrence ACTIVE : INSERT t_device_alerte + statut ACTIVE
        repassé  → si une occurrence ACTIVE existe : nouveau statut RESOLUE
```
Les ids ACTIVE/RESOLUE sont résolus en base par nom (`t_statut`), pas codés en dur.

- **Sens** : ici tous les seuils sont « au-dessus = alerte ».
- **Anti-doublon** : on ne crée pas une 2ᵉ occurrence si une ACTIVE existe déjà pour (device, alerte).
- **Résolution automatique** quand la valeur repasse sous le seuil.
- Le type d'alerte du catalogue est créé à la volée (`ALERTE_CPU`, `ALERTE_RAM`, `ALERTE_TEMPERATURE`) **seulement si le seuil correspondant existe**.

Où l'appeler : à la fin de la synchro (`import_service`), **en passant le curseur de la
transaction** : `insertAlerte(cur)`. Comme ça le moteur voit les métriques tout juste
insérées (avant le commit) et écrit dans la même transaction.

- `insertAlerte(cur)` → tourne dans la transaction de l'appelant (recommandé depuis la synchro).
- `insertAlerte()` → ouvre sa propre connexion (usage manuel/standalone), commit et ferme.

⚠️ **Important** : ne jamais appeler `insertAlerte()` (sans `cur`) depuis `synchroniser_tout`,
car une seconde connexion ne voit pas les lignes non commitées de la transaction en cours
(le moteur évaluerait le sync précédent).

⚠️ Performance : le moteur fait quelques requêtes par device (≈ 565 devices). Correct pour un run périodique ; optimisable plus tard en un seul SQL « dernière métrique par device ».

## 6. Reste à faire (non fait ici)

1. **Controller + models + routes** `/alerte` (CRUD catalogue, liste occurrences, nombre d'alertes) sur le modèle configuration/seuil.
2. **Appel du moteur** dans `import_service` après la synchro.
3. **Frontend** : page alertes (catalogue + occurrences actives) — optionnel.
4. **Barème/décisions métier** : seuil global vs par device ; sens pour la batterie (`<`) ; réouverture après résolution.

## 7. Validations effectuées (lecture seule)

- `compileall` repository + service : OK.
- Import du service (venv) + appels lecture seule :
  - `get_temperature_max_device(1) = 65`
  - `_seuils_actifs = {ram: 80, cpu: 75, capteur: 75}`
  - `_metriques_device(1) = {cpu: 3.0, ram: 95.7, temperature: 65}`
  - `getDeviceList()` → 565 devices (1er : `{device_id: 1, serial_number: '5CD5286VM3', modele: 'Chromebox Enterprise G4'}`)
  - `getNombreAlerte() = 0`, `getListeAlerte() = []`, `getListeDeviceAlerte() = []`, `getListeDeviceAlerteDate(...) = []`
  - Toutes les fonctions repo (statuts, actives/résolues, by-period, by-device…) répondent sans erreur SQL.
  - Résolution des statuts (`_id_statut`) : `ACTIVE→1`, `RESOLUE→15`, `CREER→12`, `MODIFIER→13`, `SUPPRIMER→14`, `RESTAURER→16`.
- Aucune écriture BDD effectuée (le moteur n'a pas été lancé).
