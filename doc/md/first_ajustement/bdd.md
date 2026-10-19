# BDD — Rôle des VIEWS et des INDEX

> Ce fichier explique **à quoi sert chaque VIEW** et **chaque INDEX** du
> projet, et comment les exécuter. Il ne remplace pas
> `code/bdd/versionFinal.sql` (source de vérité des tables) ni
> `code/bdd/views.sql` (source unique des VIEWS).

## 1. Pourquoi des VIEWS ?

Une VIEW est une requête SQL nommée et stockée dans PostgreSQL. Elle
sert à :

1. **Encapsuler les jointures/agrégations complexes** (statut courant,
   filiale, CPU, disque, dernière détection…) hors du code Python.
2. **Éviter le SQL complexe dans les repositories** : le repository fait
   simplement `SELECT … FROM v_xxx WHERE …`.
3. **Centraliser la logique** : une seule définition partagée par
   plusieurs endpoints.
4. **Réduire les requêtes répétées** (N+1) : la VIEW calcule les
   informations « dernières » une seule fois.

> ⚠️ L'agent IA **ne crée jamais** les VIEWS. Elles sont rédigées dans
> `code/bdd/views.sql` et exécutées **manuellement** par l'utilisateur.

---

## 2. Les 4 VIEWS actives

| VIEW | Rôle principal | Tables sources | Consommateur (code) | Endpoint |
|---|---|---|---|---|
| `v_appareils_filtres` | Une ligne par device avec statut, filiale, utilisateur, CPU et disque courants | `t_device`, `t_device_statut`, `t_statut`, `t_utilisateur`, `t_device_utilisateur`, `t_device_utilisateur_recent`, `t_device_filiale`, `t_filiale`, `t_device_cpu`, `t_cpu`, `t_disk_device`, `t_disk`, `t_type_appareil` | `repository/devices/devices.py::find_devices_paginated` | `GET /device/liste`, `GET /filiale/{id}/devices` |
| `v_evenements_avec_appareil` | Une ligne par événement avec type, appareil et filiale | `t_evenement_device`, `t_type_evenement`, `t_device`, `t_device_filiale`, `t_filiale` | `repository/evenement/evenement_device.py::find_evenements_paginated` | `GET /evenement/liste` |
| `v_tableau_de_bord_resume` | Une seule ligne d'indicateurs agrégés | Toutes les tables du dashboard | `repository/dashboard/dashboard.py::get_summary` | `GET /dashboard/summary` (cache) |
| `v_imprimantes_filtrees` | Une ligne par imprimante avec sa dernière détection | `t_imprimante`, `t_imprimante_device` | `repository/imprimante/imprimante.py::find_imprimantes_paginated` | `GET /imprimante/liste` |

### 2.1 `v_appareils_filtres`

**Rôle** : exposer en une seule ligne toutes les informations utiles
d'un appareil pour la liste :

- identité : `id`, `device_id`, `serial_number`, `modele`,
  `type_appareil`, versions ChromeOS/Chrome, MAC, IP, date de création,
  RAM totale ;
- **dernier statut** (`dernier_statut`, `DISTINCT ON`) ;
- **utilisateur principal** et **utilisateurs récents** (tableau) ;
- **filiale courante** ;
- **dernier CPU** (modèle, fréquence, architecture) ;
- **dernier disque** (capacité, libre, utilisé, modèle, type).

**Pourquoi une VIEW** : la liste doit afficher ces champs pour
**565 devices**. Sans la VIEW, il faudrait une requête par device
(N+1) ou des `LATERAL` par ligne. La version actuelle utilise des
agrégats globaux (`DISTINCT ON` / `GROUP BY`) calculés **une seule
fois** : c'est ce qui fait passer la pagination d'environ **16 s à
~0,4 s** (avec les index).

**Filtres supportés** (appliqués dans le repository) :
`id_filiale`, `filiale`, `statut`, `type_appareil`, `recherche`,
`datetime_from` / `datetime_to` (sur `date_creation`).

**Consommateur** : `find_devices_paginated` →
`GET /device/liste` et `GET /filiale/{id}/devices`.

> La page **détail** d'un device (`GET /device/{id}`) n'utilise pas
> cette VIEW : elle appelle `_build_device_response` (requêtes ciblées
> sur un seul device).

### 2.2 `v_evenements_avec_appareil`

**Rôle** : exposer chaque événement avec son type, l'appareil associé et
la filiale, pour permettre des filtres 100 % backend :

- `type_evenement` (KERNEL, EC, etc.) ;
- `device_id`, `serial_number`, `modele` ;
- `id_filiale` et `filiale` ;
- `date_evenement` et `details` (JSONB brut).

**Pourquoi une VIEW** : la liste doit filtrer par type, filiale,
recherche textuelle et plage date+heure, puis paginer. La VIEW résout
la filiale **une fois** (`derniere_filiale`, `DISTINCT ON`) au lieu de
la recalculer pour chaque événement.

**Consommateur** : `find_evenements_paginated` →
`GET /evenement/liste`.

> `details` reste du JSONB : le service extrait `cause_class`,
> `last_user`, `incident_key`, etc. pour la réponse API.

### 2.3 `v_tableau_de_bord_resume`

**Rôle** : retourner **une seule ligne** contenant tous les indicateurs
du dashboard :

- `nb_total_appareils`, `nb_actifs`, `nb_indisponibles`,
  `nb_anomalie`, `nb_reparation` ;
- `nb_crashs`, `nb_incidents`, `nb_imprimantes` ;
- `repartition_statuts`, `repartition_types`, `repartition_evenements`
  (objets JSONB).

**Mapping métier** :

| Colonne | Calcul |
|---|---|
| `nb_actifs` | dernier statut = `ACTIVE` |
| `nb_indisponibles` | dernier statut `DISABLED` ou `DEPROVISIONED` |
| `nb_anomalie` | dernier statut `DELINQUENT` |
| `nb_reparation` | devices ayant au moins une alerte non `RESOLUE` |
| `nb_crashs` | nombre de lignes `t_evenement_device` |
| `nb_incidents` | nombre d'`incident_key` distincts |

**Pourquoi une VIEW** : le dashboard ne fait qu'**un seul appel API**
(`/dashboard/summary`) au lieu de plusieurs requêtes/endpoints. Le
service met le résultat en cache (`dashboard:summary`, TTL
`CACHE_TTL_SECONDS`).

**Consommateur** : `get_summary` → `GET /dashboard/summary`.

### 2.4 `v_imprimantes_filtrees`

**Rôle** : exposer chaque imprimante avec sa **dernière date de
détection** (`MAX(t_imprimante_device.date)`), pour permettre :

- la recherche par `vendor`, `nom`, `vid`, `pid` ;
- le filtre `datetime_from` / `datetime_to` sur la dernière détection ;
- la pagination.

**Pourquoi une VIEW** : la table `t_imprimante` ne contient pas de date ;
la date est portée par la relation `t_imprimante_device` (1-N). La VIEW
agrège cette relation une fois.

**Consommateur** : `find_imprimantes_paginated` →
`GET /imprimante/liste`.

---

## 3. VIEWS supprimées

| VIEW | Raison |
|---|---|
| `v_resume_plage_cpu` | Remplacée par `SUM(cpu_utiliser)` direct sur `t_device_cpu` (C4) |
| `v_resume_plage_ram` | Remplacée par `SUM(ram_utiliser)` direct sur `t_device_ram` (C4) |

Elles sont à supprimer via `code/bdd/drop_views.sql` (si elles avaient
déjà été créées).

---

## 4. Les INDEX et leur rôle

Les index n'ajoutent aucune donnée : ils accélèrent les **recherches,
tris, jointures et agrégations**. Ils sont définis dans
`code/bdd/indexes.sql` et exécutés manuellement.

| Index | Table | Colonnes | Rôle | Requête accélérée |
|---|---|---|---|---|
| `idx_t_device_reseau_device` | `t_device_reseau` | `(id_device)` | Retrouver rapidement les liaisons d'un device | `find_devices_without_network` (`NOT EXISTS`), synchro des réseaux |
| `idx_t_device_statut_device_date` | `t_device_statut` | `(id_device, date DESC, id DESC)` | Trouver le **dernier statut** d'un device sans tri complet | CTE `dernier_statut` de `v_appareils_filtres` et `v_tableau_de_bord_resume` |
| `idx_t_device_utilisateur_recent_device_date` | `t_device_utilisateur_recent` | `(id_device, date_observation DESC)` | Agréger les utilisateurs récents par device | CTE `utilisateurs_recents` de `v_appareils_filtres` |
| `idx_t_device_date_creation` | `t_device` | `(date_creation DESC)` | Filtrer les devices par date de création | `GET /device/liste?datetime_from=&datetime_to=` |
| `idx_t_device_filiale_filiale` | `t_device_filiale` | `(id_filiale, id_device)` | Lister les devices d'une filiale | `GET /filiale/{id}/devices`, filtre `id_filiale` |
| `idx_t_evenement_device_date` | `t_evenement_device` | `(date_evenement DESC, id DESC)` | Trier et filtrer les événements par date | `GET /evenement/liste` (`ORDER BY date_evenement DESC, id DESC`) |

### 4.1 Détail par index

#### `idx_t_device_reseau_device`
- **Rôle** : accélérer la recherche des liaisons d'un device.
- **Utilisé par** : `find_devices_without_network` (synchro C0,
  `NOT EXISTS (SELECT 1 FROM t_device_reseau dr WHERE dr.id_device = d.id)`),
  `get_by_device_and_reseau`.
- **Remarque** : la contrainte `uq_device_reseau UNIQUE (id_device,
  id_reseau)` crée déjà un index dont la **première colonne est
  `id_device`**. Cet index explicite est donc en grande partie
  redondant ; il reste inoffensif et explicite l'intention.

#### `idx_t_device_statut_device_date`
- **Rôle** : obtenir le dernier statut par device via un parcours
  d'index ordonné, sans trier les ~87 000 lignes de `t_device_statut`.
- **Utilisé par** : `dernier_statut` dans `v_appareils_filtres` et
  `derniers_statuts` dans `v_tableau_de_bord_resume`.
- **Sans lui** : `DISTINCT ON` + `ORDER BY date DESC` déclenche un tri
  complet (coût majeur de l'ancienne pagination à 16 s).

#### `idx_t_device_utilisateur_recent_device_date`
- **Rôle** : agréger les emails récents d'un device dans l'ordre
  chronologique.
- **Utilisé par** : `utilisateurs_recents` (`array_agg(... ORDER BY
  date_observation DESC)`) dans `v_appareils_filtres`.
- **Sans lui** : agrégation avec tri complet des ~154 000 lignes.

#### `idx_t_device_date_creation`
- **Rôle** : accélérer les bornes de date sur `date_creation`.
- **Utilisé par** : filtre `datetime_from` / `datetime_to` de
  `/device/liste` (colonne `date` de `v_appareils_filtres`).
- **Sans lui** : parcours complet de `t_device` pour la plage.

#### `idx_t_device_filiale_filiale`
- **Rôle** : retrouver les devices d'une filiale sans passer par
  l'index `(id_device, id_filiale)` existant (dont la première colonne
  est `id_device`).
- **Utilisé par** : `/filiale/{id}/devices`, et le filtre `id_filiale`
  de `/device/liste`.

#### `idx_t_evenement_device_date`
- **Rôle** : trier les événements par date décroissante et filtrer une
  plage date+heure sans tri complet.
- **Utilisé par** : `ORDER BY date_evenement DESC, id DESC` et
  `datetime_from`/`datetime_to` de `/evenement/liste`.
- **Sans lui** : tri de tous les événements à chaque page (~5 500+
  lignes actuellement, en croissance).

---

## 5. Ordre d'exécution manuel

Depuis le dossier `code/` (adapter le chemin de `psql` si besoin) :

```powershell
# 1. Mettre à jour / créer les 4 VIEWS
psql -U postgres -h localhost -d gt -f bdd\views.sql

# 2. Supprimer les 2 VIEWS de plage devenues inutiles
psql -U postgres -h localhost -d gt -f bdd\drop_views.sql

# 3. Créer les index (idempotent : IF NOT EXISTS)
psql -U postgres -h localhost -d gt -f bdd\indexes.sql
```

> `views.sql`, `drop_views.sql` et `indexes.sql` ne contiennent aucun
> `INSERT`/`UPDATE`/`DELETE` de données. Les `DROP VIEW` ne concernent
> que les 2 vues de plage.

---

## 6. Vérifications utiles

### Vérifier que les VIEWS sont à jour
```sql
SELECT viewname, definition ILIKE '%LATERAL%' AS ancienne_version
FROM pg_views
WHERE viewname IN ('v_appareils_filtres', 'v_evenements_avec_appareil');
-- ancienne_version = false pour les deux après ré-exécution
```

### Vérifier que les INDEX existent
```sql
SELECT indexname, indexdef
FROM pg_indexes
WHERE indexname LIKE 'idx_t_%'
ORDER BY indexname;
```

### Vérifier l'usage d'un index
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM v_appareils_filtres ORDER BY id LIMIT 10;
```

### Vérifier l'insertion des réseaux
```sql
SELECT COUNT(*) FROM t_device_reseau;                    -- attendu : 492
SELECT COUNT(*) FROM t_device d
WHERE NOT EXISTS (
    SELECT 1 FROM t_device_reseau dr WHERE dr.id_device = d.id
);                                                       -- attendu : 73 (sans IP)
```

---

## 7. Maintenance

- Après toute modification d'une VIEW : **ré-exécuter
  `code/bdd/views.sql`** (`CREATE OR REPLACE VIEW` met à jour sans
  supprimer).
- Les index utilisent `IF NOT EXISTS` : les ré-exécuter ne casse rien.
- Ne jamais supprimer une VIEW sans vérifier qu'aucun repository ne
  l'interroge (`grep v_xxx code/backend/`).
- Les VIEWS ne stockent aucune donnée : elles reflètent toujours l'état
  courant des tables.
