# AJUSTEMENT 1 / C0 — Réseaux manquants dans `t_device_reseau`

## 1. Contexte

Guide `AI_AGENT_GUIDE_MONITORING_PLATFORM.md` §3 AJUSTEMENT 1, complété
par `POST_AJUSTEMENT.md` C0 : lors de la synchronisation, insérer les
réseaux des devices absents de `t_device_reseau`, de façon idempotente.

## 2. Fichiers existants vérifiés

- [x] `code/bdd/create/versionFinal.sql` — `t_device`, `t_reseau`,
      `t_device_reseau`
- [x] `repository/reseau/reseau.py` — `get_or_create_reseau`,
      `get_reseau_by_valeur`
- [x] `repository/reseau/reseau_device.py` — logique AJUSTEMENT 1
- [x] `service/reseau_service.py` — logique AJUSTEMENT 1
- [x] `service/import_service.py` — `synchroniser_tout` (fonction de
      synchro identifiée, appelée par `google_api/auto_synch.py`)
- [x] `google_api/auto_synch.py` — boucle `synchronisation_automatique`

## 3. Décision : fichiers/fonctions identifiés

- **Schéma réel** : `t_device` ne contient **pas** de colonne
  `id_reseau`. Colonnes : `id, device_id, serial_number, modele,
  id_type_appareil, chromeos_version, chrome_version, date_creation,
  ip_adress, mac_adress, ram_total`.
  → La priorité 1 (« `t_device.id_reseau` ») est **inapplicable** ;
  seule la priorité 2 (recherche dans `t_reseau` via l'IP) est utilisée.
  La priorité 1 reste implémentée dans `resolve_id_reseau` (elle
  fonctionnera si la colonne est ajoutée un jour).
- Le réseau n'est **jamais créé** dans `t_reseau` : si l'IP est inconnue
  → skip + warning.
- Aucun nouveau fichier `sync_service.py` : l'orchestration
  `sync_networks_for_all_devices` vit dans `reseau_service.py` et est
  appelée par `import_service.synchroniser_tout` (règle C7).
- Aucun `reseau_controller.py` (pas d'endpoint demandé, règle C7).
- Aucun modèle SQLAlchemy : le projet utilise psycopg2 brut (pas
  d'ORM), donc `DeviceReseau` n'est pas créé.

## 4. Fichiers créés / modifiés

| Ordre | Fichier | Nature |
|---|---|---|
| 1 | `repository/reseau/reseau_device.py` | `find_devices_without_network`, `get_reseau_id_by_ip`, `get_by_device_and_reseau`, `insert_device_reseau` + savepoints |
| 1 | `repository/reseau/__init__.py` | exports |
| 2 | `service/reseau_service.py` | `resolve_id_reseau`, `upsert_network_for_device`, `sync_network_row`, `sync_networks_for_all_devices` |
| 3 | `service/import_service.py` | appel après l'ingestion des devices (étape `db_reseaux`) |

Résolution du `id_reseau` :
1. `device_row.id_reseau` si non NULL (colonne absente aujourd'hui) ;
2. sinon `t_reseau.id` via `device_row.adresse_ip` (`ip_adress`) ;
3. sinon warning + skip.

Idempotence :
- `get_by_device_and_reseau` → skip si le couple existe ;
- `INSERT` simple + `SAVEPOINT` par ligne ;
- `IntegrityError` (UNIQUE) → rollback du savepoint + log info ;
- autre exception → rollback du savepoint + `logger.error` + continue.

## 5. ⚠️ Views à créer — À exécuter manuellement par l'utilisateur

**Aucune VIEW pour C0.**

Rappel : les VIEWS des AJUSTEMENTS 3, 8, 11 et 12 restent à créer
(`code/bdd/views.sql`).

## 6. Spécifications

- `find_devices_without_network(cur)` retourne
  `(id_device, id_reseau, adresse_ip)` pour tout device sans aucune
  ligne dans `t_device_reseau` (565 actuellement).
- `insert_device_reseau` insère uniquement `(id_device, id_reseau)` ;
  `date` est remplie par `DEFAULT NOW()`.
- Aucun SQL dans le service ; tout est dans le repository.
- L'erreur d'un device n'interrompt pas la boucle de synchro.

## 7. SQL à exécuter manuellement (index + audit)

> **Aucun `ALTER TABLE ADD CONSTRAINT UNIQUE` n'est proposé** (choix
> métier utilisateur). La contrainte `uq_device_reseau` existe déjà en
> base.

```sql
-- Index pour accélérer la synchro des réseaux (C0)
-- À exécuter manuellement par l'utilisateur
-- (également présent dans code/bdd/indexes.sql).
CREATE INDEX IF NOT EXISTS idx_t_device_reseau_device
    ON t_device_reseau (id_device);
```

```sql
-- Audit des réseaux associés à plusieurs filiales (C0)
-- À exécuter manuellement par l'utilisateur (lecture seule).
SELECT id_reseau, COUNT(DISTINCT id_filiale) AS nb_filiales
FROM t_reseau_filiale
GROUP BY id_reseau
HAVING COUNT(DISTINCT id_filiale) > 1;
```

Aucun `CREATE INDEX` / `DROP` / `ALTER` n'a été exécuté par l'agent.

## 8. Tests réalisés (vérifications BDD §2.7, lecture seule)

| Vérification | Résultat |
|---|---|
| Colonnes réelles de `t_device` | aucune colonne `id_reseau` |
| `SELECT COUNT(*) FROM t_device` | 565 |
| `SELECT COUNT(*) FROM t_device_reseau` | 0 |
| Devices sans liaison réseau | 565 |
| `get_reseau_id_by_ip('172.22.64.103')` | 2 |
| `get_reseau_id_by_ip('200.0.0.1')` | `None` |
| `resolve_id_reseau` priorité 1 (id=7) | 7 |
| `resolve_id_reseau` fallback IP | 2 |
| `resolve_id_reseau` sans IP | `None` |
| Couple déjà présent | skip |
| Nouveau couple | insert |
| Réseau introuvable | skip + warning |
| `IntegrityError` | skip (rollback savepoint), pas de log critique |
| Autre exception | `logger.error` + continue |

`py_compile` OK sur les 4 fichiers backend modifiés.

### Audit `t_reseau_filiale` — doublons INTERNES par filiale

**Décision métier (validée par l'utilisateur)** : un même réseau **peut
légitimement** appartenir à 2 filiales (sous-réseau partagé).
→ **Aucun script `DELETE`**, **aucune contrainte `UNIQUE`
supplémentaire**, données conservées telles quelles.

Audit demandé : pour **chaque filiale**, y a-t-il des `id_reseau` en
double ?

```sql
-- Doublons internes par filiale (aucune ligne attendue)
SELECT id_filiale, id_reseau, COUNT(*) AS nb
FROM t_reseau_filiale
GROUP BY id_filiale, id_reseau
HAVING COUNT(*) > 1
ORDER BY id_filiale, id_reseau;

-- Totaux vs distincts par filiale
SELECT id_filiale, COUNT(*) AS total, COUNT(DISTINCT id_reseau) AS distincts
FROM t_reseau_filiale
GROUP BY id_filiale
HAVING COUNT(*) <> COUNT(DISTINCT id_reseau);
```

Résultat réel (lecture seule) :

| Vérification | Résultat |
|---|---|
| Filiales contrôlées | 30 |
| Filiales avec `total <> distincts` | **0** |
| Lignes retournées par `HAVING COUNT(*) > 1` | **0** |
| Contrainte existante | `UNIQUE (id_reseau, id_filiale)` |

**Aucun doublon interne par filiale → aucun script de nettoyage
nécessaire.**

### Constat complémentaire (doublons inter-filiales)

| Constat | Résultat |
|---|---|
| Liaisons `172.22.64.*` | 54 |
| dont `id_filiale=1` (SOREDIM) | **0** |
| dont `id_filiale=2` (SODIREX) | **49** |
| Réseaux associés à plusieurs filiales | 3 (192.168.88.22, 172.25.57.18, 192.168.88.21) |
| Paires strictement dupliquées `(id_reseau, id_filiale)` | **0** |

Ces 3 réseaux partagés sont **normaux** (sous-réseaux partagés) et sont
conservés.

### Colonne IP

La colonne réelle de `t_device` est **`ip_adress`** (un seul « d »).
Le fallback de résolution utilise bien `d.ip_adress` dans
`find_devices_without_network` ; aucune référence à `adresse_ip`
n'existe dans le code.

## 9. Risques / régressions

- 73 devices sans IP seront loggés en warning à chaque synchro (comportement
  demandé : « réseau/IP absent → loggé et skippé »).
- Tant que `t_device.id_reseau` n'existe pas, la priorité 1 est
  inactive ; la résolution par IP est le seul chemin.
- Aucune modification du schéma, aucune contrainte ajoutée.

## 10. Respect §2.4

Fonctions plates au niveau module : `find_devices_without_network`,
`get_reseau_id_by_ip`, `get_by_device_and_reseau`,
`insert_device_reseau`, `resolve_id_reseau`,
`upsert_network_for_device`, `sync_network_row`,
`sync_networks_for_all_devices`. Aucune fonction imbriquée, aucune
closure.
