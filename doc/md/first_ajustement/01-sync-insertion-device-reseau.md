# AJUSTEMENT 1 / C0 — Insertion des réseaux dans `t_device_reseau`

## 1. Contexte

Guide `AI_AGENT_GUIDE_MONITORING_PLATFORM.md` §3 AJUSTEMENT 1, complété
par `POST_AJUSTEMENT.md` C0 : lors de la synchronisation, insérer les
liaisons device ↔ réseau dans `t_device_reseau`, de façon idempotente.

## 2. Fichiers vérifiés

- [x] `code/bdd/create/versionFinal.sql` — `t_device`, `t_reseau`,
      `t_device_reseau`
- [x] `repository/reseau/reseau.py` — `get_or_create_reseau`
- [x] `repository/reseau/reseau_filiale.py` — `insert_into_reseau_filiale`
- [x] `service/import_service.py` — `insertion_device`,
      `synchroniser_tout` (fonction de synchro)
- [x] `google_api/auto_synch.py` — boucle `synchronisation_automatique`
- [x] `t_device` ne contient **pas** de colonne `id_reseau` ; la colonne
      IP réelle est **`ip_adress`** (un seul « d »)

## 3. Fonctionnement final

L'insertion se fait **directement pendant l'ingestion des devices**,
dans `import_service.insertion_device` :

```python
if ip_adresse:
    id_reseau = get_or_create_reseau(cur, ip_adresse)
    if id_reseau is not None:
        insert_into_reseau_filiale(cur, id_reseau, id_filiale)
        lien_existant = get_by_device_and_reseau(cur, db_device_id, id_reseau)
        if lien_existant is None:
            insert_device_reseau(cur, db_device_id, id_reseau)
```

Étapes :
1. `ip_adresse` provient de `lastKnownNetwork[0].ipAddress` (Google).
2. `get_or_create_reseau` récupère ou crée le réseau dans `t_reseau`
   (comportement existant de l'ingestion).
3. `insert_into_reseau_filiale` associe le réseau à la filiale
   (`ON CONFLICT DO NOTHING`).
4. `get_by_device_and_reseau` vérifie si la liaison device ↔ réseau
   existe déjà.
5. Si absente → `insert_device_reseau` insère dans `t_device_reseau`.

**Idempotence** : grâce au pré-check `get_by_device_and_reseau`, une
2ᵉ synchro ne réinsère rien. Sans ce pré-check, l'`INSERT` violerait
`UNIQUE (id_device, id_reseau)`, l'exception serait attrapée par le
`try` global du device et la mise à jour du statut + des utilisateurs
récents serait sautée.

## 4. Fichiers créés / modifiés / supprimés

| Fichier | Nature |
|---|---|
| `repository/reseau/reseau_device.py` | `get_by_device_and_reseau`, `insert_device_reseau` |
| `repository/reseau/__init__.py` | exports |
| `service/import_service.py` | insertion directe dans `insertion_device` |
| `service/reseau_service.py` | **supprimé** (plus de second passage) |

Supprimés car plus utilisés ailleurs :
- `find_devices_without_network`
- `get_reseau_id_by_ip`
- `create_savepoint_ligne_reseau` / `rollback_savepoint_ligne_reseau`
- `sync_networks_for_all_devices`, `resolve_id_reseau`,
  `upsert_network_for_device`, `sync_network_row` (fichier
  `reseau_service.py`)

## 5. ⚠️ Views à créer — À exécuter manuellement par l'utilisateur

**Aucune VIEW pour C0.**

## 6. Spécifications

- `t_device_reseau` : `INSERT (id_device, id_reseau)` ; `date` est
  remplie par `DEFAULT NOW()`.
- `UNIQUE (id_device, id_reseau)` garantit l'absence de doublons.
- Aucun SQL dans le service : tout est dans `repositories/reseau/`.
- L'erreur d'un device reste isolée par le `try/except` de
  `insertion_device`.

## 7. SQL à exécuter manuellement

> **Aucun `ALTER TABLE ADD CONSTRAINT UNIQUE` n'est proposé** (choix
> métier utilisateur). La contrainte `uq_device_reseau` existe déjà.

**Aucun index dédié n'est nécessaire** : la recherche
`get_by_device_and_reseau` (`WHERE id_device = ... AND id_reseau = ...`)
est déjà couverte par l'index unique `uq_device_reseau
(id_device, id_reseau)`, dont la première colonne est `id_device`.

L'ancien `idx_t_device_reseau_device` était donc redondant. Il a été
retiré de `code/bdd/indexes.sql` et sa suppression est livrée dans
`code/bdd/drop_indexes.sql` :

```sql
-- À exécuter manuellement par l'utilisateur (facultatif : l'index est
-- redondant, mais inoffensif).
DROP INDEX IF EXISTS idx_t_device_reseau_device;
```

```sql
-- Audit des réseaux associés à plusieurs filiales (lecture seule).
SELECT id_reseau, COUNT(DISTINCT id_filiale) AS nb_filiales
FROM t_reseau_filiale
GROUP BY id_reseau
HAVING COUNT(DISTINCT id_filiale) > 1;
```

Aucun `CREATE INDEX` / `DROP` / `ALTER` n'a été exécuté par l'agent.

## 8. Tests réalisés (vérifications BDD §2.7, lecture seule)

| Vérification | Résultat |
|---|---|
| Colonnes réelles de `t_device` | aucune colonne `id_reseau` ; `ip_adress` |
| Devices | 565 |
| Devices avec IP | 492 |
| Devices dont l'IP existe dans `t_reseau` | 492 |
| Devices avec IP absente de `t_reseau` | 0 |
| Liaisons dans `t_device_reseau` | **492** |
| Doublons `(id_device, id_reseau)` | **0** |
| Devices sans liaison | 73 (tous sans IP → skip normal) |
| Devices sans liaison mais avec IP | **0** |

`py_compile` OK, tests unitaires 5/5 OK.

### Audit `t_reseau_filiale` — doublons internes par filiale

**Décision métier validée** : un même réseau **peut** appartenir à
2 filiales (sous-réseau partagé). Aucun `DELETE`, aucune contrainte
`UNIQUE` supplémentaire.

```sql
-- Doublons internes par filiale (aucune ligne attendue)
SELECT id_filiale, id_reseau, COUNT(*) AS nb
FROM t_reseau_filiale
GROUP BY id_filiale, id_reseau
HAVING COUNT(*) > 1
ORDER BY id_filiale, id_reseau;
```

Résultat : 30 filiales contrôlées, **0 doublon interne**,
`total = distincts` pour chacune. Contrainte
`UNIQUE (id_reseau, id_filiale)` présente.

Constat : `172.22.64.*` = 49 liaisons SODIREX (filiale 2), 0 SOREDIM
(filiale 1) ; 3 réseaux partagés au total (autres sous-réseaux), ce qui
est normal.

## 9. Risques / régressions

- **Suppression du second passage** (`sync_networks_for_all_devices`) :
  seuls les devices présents dans la réponse Google sont traités. Un
  device déjà en base mais absent de la liste Google ne sera pas lié
  automatiquement s'il n'a pas de liaison. État actuel : 492/492 devices
  avec IP sont liés, donc aucun impact immédiat.
- 73 devices sans IP ne sont pas liés (attendu).
- `get_or_create_reseau` peut créer une ligne `t_reseau` pour une
  nouvelle IP (comportement existant de l'ingestion, inchangé).

## 10. Respect §2.4

Fonctions plates au niveau module (`get_by_device_and_reseau`,
`insert_device_reseau`, `insertion_device`). Aucune fonction imbriquée,
aucune closure.
