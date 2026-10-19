Lis doc/md/AI_AGENT_GUIDE_MONITORING_PLATFORM.md en entier
et exécute les ajustements §3 dans l'ordre en respectant §2
(dont §2.5 : toutes les VIEWS dans sql/views.sql).

Rappels :
- Enchaîne automatiquement AJUSTEMENT 1 → 13 sans attendre ma validation,
  sauf blocage : ambiguïté métier (ex: AJUSTEMENT 10), info manquante
  dans sql/versionFinal.sql, choix architectural majeur.
- Après chaque ajustement terminé : crée le .md de suivi dans doc/md/
  (nomenclature §3.13) et produis un rapport court (5-10 lignes).
- Ne jamais écrire de SQL hors repositories/, ne jamais créer de
  fonction imbriquée (§2.4).

Commence par AJUSTEMENT 1.

# AI AGENT GUIDE — Monitoring ChromeOS & Imprimantes

> **Ce fichier est la SEULE source d'instructions.**
> L'agent IA le lit en entier, puis exécute les ajustements §3 dans l'ordre.
> Pour chaque ajustement terminé : créer le `.md` de suivi dans `doc/md/`
> puis **enchaîner automatiquement** sur le suivant (sauf blocage).

---

## 1. CONTEXTE PROJET

### 1.1 Objectif
Plateforme web de **monitoring centralisé** d'un parc :
- **Appareils ChromeOS** (Chromebooks + Chromebox)
- **Imprimantes gérées** détectées via Telemetry

Supervision : CPU, RAM, Disque, Réseau, événements, crashs, incidents,
états, alertes, comparaisons, statistiques, exports.

---

## 2. RÈGLES DE DÉVELOPPEMENT (à respecter ABSOLUMENT)

### 2.1 Source de vérité BDD
> **TOUJOURS lire `sql/versionFinal.sql` avant d'écrire une requête.**
> Ne jamais inventer un nom de colonne. Si une info manque → **demander**.

### 2.2 Workflow obligatoire
```
1. VÉRIFIER si le fichier existe déjà
        ├── OUI → RÉUTILISER
        └── NON → CRÉER

2. Créer dans CET ORDRE :
   Repository  →  Service  →  Controller  →  Model (si nécessaire)
```

**Chaîne d'appel :** `Controller → Service → Repository → PostgreSQL`

| Couche | ✅ Fait | ❌ Ne fait pas |
|---|---|---|
| Controller | Valider HTTP, appeler service, retourner schéma | SQL, logique métier |
| Service | Logique, cache, orchestration, Google API | SQL, session DB |
| Repository | SQL, filtres, pagination, upserts | Logique métier |
| Model | Tables SQLAlchemy + schémas Pydantic | Logique |

### 2.3 Arborescence
```
app/
├── controllers/    # routers FastAPI
├── services/       # logique métier
├── repositories/   # accès DB
├── models/         # SQLAlchemy
├── schemas/        # Pydantic
├── core/           # config, cache, db
└── jobs/           # sync, alertes
```

### 2.4 Style de code (OBLIGATOIRE)
- ❌ **Pas de fonction imbriquée** dans une autre fonction.
- ❌ **Pas de `for` imbriqués** dans une même fonction si ça nuit à la lisibilité.
- ✅ Une fonction = une seule chose, nom explicite, < ~30 lignes.
- ✅ Fonctions **au niveau module**, appelées séquentiellement.
- ✅ **Lire 2-3 fichiers voisins** avant d'écrire pour caler le style existant.
- ✅ Pas de lambda complexe, pas de closure.

**Bon exemple :**
```python
def get_missing_networks():
    return reseau_repository.find_devices_without_network(db.session)

def upsert_one_network(row):
    existing = reseau_repository.get_by_device_id(db.session, row.device_id)
    if existing and existing.network_info == row.network_info:
        return
    reseau_repository.upsert_network(db.session, row)

def sync_networks_for_all_devices():
    for row in get_missing_networks():
        upsert_one_network(row)
```

**Mauvais exemple :**
```python
def synchronisation_automatique():
    def insert_network(row):
        for x in row:
            for y in x:
                db.execute("INSERT ...")
    for r in data:
        insert_network(r)
```

### 2.5 PostgreSQL VIEWS — fichier dédié `sql/views.sql`

> **Toute requête de filtre, jointure ou agrégation complexe et/ou
> répétée doit être encapsulée dans une VIEW PostgreSQL.**
> **Toutes les VIEWS sont déclarées dans un fichier unique : `sql/views.sql`.**

**Règles :**
- ⚠️ **`sql/versionFinal.sql` reste la source de vérité des TABLES**
  (structure, colonnes, types, clés). Il ne contient **PAS** de VIEW.
- ⚠️ **`sql/views.sql` est la source unique des VIEWS.** Il contient
  **toutes** les VIEWS du projet, créées au fur et à mesure des ajustements.
- Le repository interroge la VIEW comme une table
  (`SELECT ... FROM v_xxx WHERE ...`). Aucun SQL complexe inline.

**⚠️ RÈGLE CRITIQUE — L'agent NE CRÉE PAS les VIEWS :**

> **L'agent IA ne doit JAMAIS exécuter de `CREATE VIEW` ni de
> `CREATE OR REPLACE VIEW` sur la base de données.**
>
> **À la place, l'agent :**
> 1. Rédige le **code SQL complet de la VIEW** (avec commentaires : but,
>    colonnes, ajustement lié).
> 2. Le **présente à l'utilisateur** dans le rapport de l'ajustement en
>    cours ET dans le `.md` de suivi (`doc/md/XX-....md`).
> 3. **Indique explicitement** : *"À exécuter manuellement par
>    l'utilisateur dans `sql/views.sql` puis sur la base."*
> 4. **Attend la confirmation** que la VIEW a été créée avant de coder
>    le repository qui l'interroge — OU code le repository en supposant
>    que la VIEW existera, en le signalant clairement.
>
> **C'est l'utilisateur qui exécute le SQL de création des VIEWS
> manuellement.**

**Quand créer une VIEW :**
- Jointure sur 2+ tables avec filtres multiples
- Agrégation récurrente (dashboard, statistiques, summary)
- Requête utilisée par plusieurs endpoints
- Filtres combinés (date + heure + type + statut + filiale…)
- Plage de valeurs (CPU/RAM range summary)

**Nommage des VIEWS — EN FRANÇAIS :**

> Toutes les VIEWS doivent avoir un nom **en français**, préfixé par `v_`.
> Format : `v_<usage_en_français>` (snake_case).

Exemples :
- `v_tableau_de_bord_resume` (dashboard summary)
- `v_appareils_filtres` (devices filtered)
- `v_evenements_avec_appareil` (events with device)
- `v_imprimantes_avec_evenements` (printers with events)
- `v_resume_plage_cpu` (CPU range summary)
- `v_resume_plage_ram` (RAM range summary)
- `v_materiels_liste` (materials list)
- `v_statistiques_periode` (period statistics)

**Format de livraison attendu (par l'agent) :**

L'agent fournit un bloc SQL prêt à copier, dans ce format exact :

```sql
-- ------------------------------------------------------------
-- v_tableau_de_bord_resume
-- But : indicateurs agrégés pour le dashboard (§7.3)
-- Colonnes : nb_total_appareils, nb_actifs, nb_indisponibles,
--            nb_anomalie, nb_reparation, nb_crashs,
--            nb_incidents, nb_imprimantes
-- Utilisée par : AJUSTEMENT 8 (dashboard rapide)
-- À exécuter manuellement par l'utilisateur dans sql/views.sql
-- puis sur la base PostgreSQL.
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_tableau_de_bord_resume AS
SELECT ... ;   -- SQL exact basé sur versionFinal.sql
```

Ce bloc doit être :
1. Inclus dans le `.md` de suivi de l'ajustement concerné
   (section « Views à créer — À exécuter manuellement »).
2. Reproduit dans `doc/md/00-RECAP.md` (section « Views à créer par
   l'utilisateur ») avec un statut `⏳ en attente` / `✅ créée` que
   **l'utilisateur met à jour lui-même**.

**Bon réflexe agent :** avant d'écrire un `SELECT` avec plusieurs
jointures ou filtres dans un repository → **rédiger la VIEW** (nom en
français), la **livrer à l'utilisateur**, puis interroger la VIEW depuis
le repository (en supposant qu'elle sera créée).

### 2.6 Ne rien casser
- Ne rien supprimer sans vérifier qu'aucun autre fichier ne l'utilise.
- Avant d'ajouter, chercher si une fonction équivalente existe déjà.

### 2.7 Vérification des données en base (accès en lecture seule autorisé)

> **L'agent IA est autorisé à se connecter à la base de données
> PostgreSQL du projet en LECTURE SEULE pour vérifier des données.**

**Autorisé :**
- ✅ `SELECT` (vérifications, comptages, contrôle des données réelles)
- ✅ `EXPLAIN` / `EXPLAIN ANALYZE` (analyse de requêtes)
- ✅ Vérifier l'existence d'une table, d'une colonne, d'une VIEW
  (via `information_schema` ou `pg_catalog`)
- ✅ Compter des lignes pour valider une hypothèse
  (ex: combien de devices sans réseau dans `t_device_reseau`)
- ✅ Exécuter le `SELECT` d'une future VIEW pour valider son résultat
  (mais **jamais** le `CREATE VIEW`)

**Interdit (STRICTEMENT) :**
- ❌ `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, `DROP`, `ALTER`
- ❌ `CREATE VIEW`, `CREATE OR REPLACE VIEW`, `CREATE TABLE`, etc.
- ❌ Toute modification de la structure ou des données
- ❌ Exécution de scripts SQL entiers
- ❌ Utilisation des credentials de production s'ils existent
  (utiliser la base de dev/démo uniquement)

**Comment l'agent se connecte :**
- Utiliser les credentials de `.env`
  (ex: `DATABASE_URL` ou variables `DB_HOST`, `DB_USER`, `DB_PASSWORD`,
  `DB_NAME`).
- Si le `.env` n'est pas disponible ou non lisible → **demander** à
  l'utilisateur la commande de connexion exacte.
- Ne **jamais** loguer le mot de passe.
- Préférer passer par le repository existant ou une commande
  `psql` en lecture seule si disponible.

**À quoi sert cette vérification :**
- Confirmer que les colonnes nommées dans `sql/versionFinal.sql`
  existent réellement.
- Vérifier que des données existent avant d'écrire une logique
  (ex: `t_device_reseau` vide au départ ? déjà partiellement remplie ?).
- Vérifier les doublons, les nulls, les formats de date réels.
- Comparer les résultats d'une nouvelle requête avec les données
  attendues.
- **Valider les VIEWS** proposées : l'agent peut exécuter le `SELECT`
  de la VIEW (pas le `CREATE VIEW`) pour vérifier que le résultat est
  correct, puis livrer le `CREATE VIEW` à l'utilisateur.

**Exemple de vérification autorisée :**

```bash
# L'agent peut lancer (lecture seule) :
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM t_device_reseau;"
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM t_device WHERE id NOT IN
  (SELECT device_id FROM t_device_reseau);"

# L'agent peut vérifier le SELECT de la future VIEW :
psql "$DATABASE_URL" -c "SELECT ... FROM ... ;"  # la requête de la VIEW
# mais NE DOIT PAS lancer :
# psql "$DATABASE_URL" -c "CREATE OR REPLACE VIEW v_xxx AS ... ;"  ❌
```

**Dans le rapport de chaque ajustement, l'agent indique :**
- Les vérifications BDD effectuées (requêtes + résultats).
- Les VIEWS rédigées (à créer manuellement par l'utilisateur).
- Les VIEWS dont l'utilisateur a confirmé la création (si applicable).

---

## 3. AJUSTEMENTS À RÉALISER (dans l'ordre)

> Pour chaque ajustement :
> 1. Lire `sql/versionFinal.sql`
> 2. Identifier l'existant (fichier + fonction réels, pas devinés)
> 3. Appliquer le workflow §2.2
> 4. Si requête complexe → **rédiger la VIEW** (nom en français, §2.5)
>    et la **livrer à l'utilisateur** — **ne pas exécuter le `CREATE VIEW`**
> 5. Créer le `.md` de suivi dans `doc/md/` (voir §3.13)
> 6. Rapport court, puis **enchaîner** sur le suivant

---

### AJUSTEMENT 1 — Réseaux manquants dans `t_device_reseau`

**But :** lors de la synchro, insérer les réseaux des devices déjà en base
mais absents de `t_device_reseau`. Idempotence : skip si identique.

**Étapes :**
1. Lire `t_device` et `t_device_reseau` dans `sql/versionFinal.sql`.
2. **Vérifier en BDD** (§2.7) : compter les devices sans réseau dans
   `t_device_reseau` pour confirmer le cas d'usage.
3. Identifier la fonction de synchro existante (chercher dans
   `app/jobs/`, `app/services/` — se fier au **comportement** :
   récupération devices Google + persistance DB).
4. Créer dans l'ordre :
   - `repositories/reseau_repository.py` :
     - `find_devices_without_network(session)`
     - `get_by_device_id(session, device_id)`
     - `upsert_network(session, payload)`
   - `services/reseau_service.py` :
     - `get_missing_networks()`
     - `upsert_network_for_device(row)` (compare + décide INSERT/UPDATE/skip)
   - Fonction dédiée `sync_networks_for_all_devices()` au niveau module,
     appelée depuis la fonction de synchro identifiée.
     `try/except` **par ligne** + `logger.error` + `continue` (§10).
   - Modèle SQLAlchemy si absent (basé sur `versionFinal.sql`).
5. Tests manuels : device sans réseau détecté · device identique non
   réinséré · exception isolée.
6. Créer `doc/md/01-sync-insertion-device-reseau.md` (voir §3.13).

**✅ Critères :** réseaux insérés · pas de doublons · erreur isolée · pas
de SQL dans service · pas de fonction imbriquée.

---

### AJUSTEMENT 2 — Graph RAM frontend : max total

**But :** afficher le **max total** agrégé (calculé backend), pas une
valeur partielle.

**Étapes :**
1. Lire `t_device_ram` dans `sql/versionFinal.sql`.
2. **Vérifier en BDD** (§2.7) : vérifier les valeurs réelles de RAM pour
   comprendre l'agrégation attendue.
3. Identifier le composant React existant (se fier au comportement).
4. Backend :
   - `ram_repository.get_max_total_ram(session, device_id, filters)`
   - `ram_service.get_max_total_ram(...)` (délégation)
   - `GET /api/ram/{device_id}/max-total`
5. Frontend : brancher sur l'endpoint, **aucun calcul lourd** côté React.
6. Créer `doc/md/02-ram-max-total.md`.

---

### AJUSTEMENT 3 — Filtres backend + pagination 5/10

**But :** tous les filtres traités backend + pagination configurable.

**Étapes :**
1. Lire `sql/versionFinal.sql` (tables des listes concernées).
2. Identifier TOUS les endpoints de liste existants.
3. Pour chacun :
   - **Si la requête est complexe (jointures + filtres multiples) →
     RÉDIGER la VIEW** (nom en français, §2.5) et la **livrer à
     l'utilisateur** dans le rapport + `.md` de suivi.
     **Ne pas exécuter le `CREATE VIEW`.** L'utilisateur la crée
     manuellement. L'agent peut exécuter le `SELECT` de la VIEW
     (lecture seule, §2.7) pour valider.
   - Repository : `WHERE` + `LIMIT` + `OFFSET` + filtres 100% backend.
     Si une VIEW est utilisée, interroger la VIEW (en supposant
     qu'elle sera créée par l'utilisateur).
   - Service : délégation.
   - Controller : `?page=&page_size=&filters...` → retour
     `{ items, total, page, page_size, total_pages }`.
4. Frontend :
   - Retirer tout filtre client-side.
   - Pagination 5 ou 10 (configurable).
   - Chargement progressif (données déjà affichées restent visibles).
   - Squelettes au lieu des spinners.
5. Créer `doc/md/03-filtres-backend-pagination.md`.

---

### AJUSTEMENT 4 — Caching

**But :** cache côté service, TTL configurable, invalidation sur writes.

**Étapes :**
1. Créer `app/core/cache.py` :
   - `cache_get(key)`, `cache_set(key, value)`, `cache_invalidate(key)`
   - TTL via `.env` (`CACHE_TTL_SECONDS=60` défaut)
   - Fonctions **au niveau module** (dict + timestamp simple).
2. Services : wrapper les lectures coûteuses (ex: `get_devices_cached`).
   Le cache **vit dans le service**, jamais dans le repository.
3. Invalidation après sync/upsert (sur les clés concernées).
4. Créer `doc/md/04-caching.md`.

---

### AJUSTEMENT 5 — Skeleton UI

**But :** remplacer tous les spinners par des squelettes.

**Étapes :**
1. Composant `Skeleton` réutilisable.
2. Squelettes dédiés : `DeviceListSkeleton`, `EventListSkeleton`,
   `PrinterListSkeleton`, `DashboardSkeleton`, `CpuRamChartSkeleton`.
3. Remplacer TOUS les spinners.
4. Squelette visible **uniquement sur les zones non chargées**.
5. Créer `doc/md/05-skeleton-ui.md`.

---

### AJUSTEMENT 6 — CPU/RAM directs depuis `t_device_cpu` / `t_device_ram`

**But :** valeurs CPU/RAM lues directement en DB (via backend), zéro
calcul côté front.

**Étapes :**
1. Lire `t_device_cpu` et `t_device_ram` dans `sql/versionFinal.sql`.
2. **Vérifier en BDD** (§2.7) : lire quelques lignes réelles pour
   confirmer la structure et les valeurs.
3. Backend :
   - `cpu_repository.get_latest_by_device(session, device_id)`
   - `ram_repository.get_latest_by_device(session, device_id)`
   - services : délégation
   - `GET /api/devices/{id}/cpu/latest` et `.../ram/latest`
4. Frontend : consommer, retirer tout calcul CPU/RAM.
5. Créer `doc/md/06-cpu-ram-direct-db.md`.

---

### AJUSTEMENT 7 — Vérifier `t_disk_device`

**But :** `t_disk_device` exploitée comme CPU/RAM.

**Étapes :**
1. Lire `t_disk_device` dans `sql/versionFinal.sql`.
2. **Vérifier en BDD** (§2.7) : compter les lignes, vérifier que la table
   est alimentée.
3. Vérifier que la synchro alimente la table. Si non → corriger via le
   service de synchro (jamais de SQL inline).
4. Backend :
   - `disk_repository.get_latest_by_device(session, device_id)`
   - service : délégation
   - `GET /api/devices/{id}/disk/latest`
5. Frontend : brancher sur l'endpoint.
6. Créer `doc/md/07-disk-verification.md`.

---

### AJUSTEMENT 8 — Dashboard rapide

**But :** dashboard chargé en **1 seul appel** et rapide (<500ms avec cache).

**Étapes :**
1. Lire `sql/versionFinal.sql` (toutes tables concernées).
2. **RÉDIGER le SQL de la VIEW `v_tableau_de_bord_resume`** (§2.5)
   qui agrège : nb devices, actifs, indisponibles, anomalie,
   réparation, crashs, incidents, imprimantes.
   **Livrer le bloc à l'utilisateur** dans le rapport + `.md` de
   suivi (section « Views à créer — À exécuter manuellement »).
   **Ne pas exécuter le `CREATE VIEW`.** L'utilisateur la crée.
   L'agent peut exécuter le `SELECT` de la VIEW (lecture seule,
   §2.7) pour valider.
3. Backend :
   - `dashboard_repository.get_summary(session)` → `SELECT * FROM v_tableau_de_bord_resume`
   - `dashboard_service.get_summary()` + cache
   - `GET /api/dashboard/summary`
4. Frontend :
   - **UN SEUL** appel API
   - `DashboardSkeleton` au chargement
   - retirer tous les appels séparés
5. Créer `doc/md/08-dashboard-perf.md`.

---

### AJUSTEMENT 9 — Format date/heure `t_evenements`

**But :** dates stockées en `TIMESTAMPTZ` UTC + affichage formaté.

**Étapes :**
1. Lire `t_evenements` dans `sql/versionFinal.sql`.
2. **Vérifier en BDD** (§2.7) : regarder quelques lignes réelles pour
   voir le format actuel des dates.
3. **Insertion** : parser les dates Google (RFC3339) → UTC dans le
   **service** (pas le repository).
4. **Affichage** : helper `formatDateTime` plat, au niveau module
   (`dd/MM/yyyy HH:mm:ss` + timezone admin).
5. Créer `doc/md/09-events-datetime-format.md`.

---

### AJUSTEMENT 10 — Durée de vie avant extinction ⚠️

**⚠️ QUESTION OBLIGATOIRE avant de coder :**
> "Durée de vie avant extinction = (a) batterie restante,
> (b) fin de support AUE, (c) temps depuis dernier événement ?"

Poser la question, attendre la réponse, **puis** :

1. Lire les tables concernées dans `sql/versionFinal.sql`.
2. **Vérifier en BDD** (§2.7) : regarder les données disponibles pour
   la métrique retenue.
3. Calcul dans une fonction dédiée au niveau module, **dans le service**.
4. Stockage via repository si nécessaire.
5. Affichage : page détail device (+ liste évènements / CPU-RAM si pertinent).
6. Créer `doc/md/10-life-remaining.md`.

---

### AJUSTEMENT 11 — CPU/RAM plage + somme + détail

**But :** filtre plage (ex: 6-7) → total en haut + détail par valeur en bas.

**Étapes :**
1. Lire `t_device_cpu` / `t_device_ram` dans `sql/versionFinal.sql`.
2. **RÉDIGER les SQL des VIEWS `v_resume_plage_cpu` et
   `v_resume_plage_ram`** (§2.5, noms en français) pour agréger par
   valeur + total.
   **Livrer les blocs à l'utilisateur** dans le rapport + `.md` de
   suivi. **Ne pas exécuter le `CREATE VIEW`.** L'utilisateur les
   crée manuellement.
3. Backend :
   - repo : `sum_range(session, device_id, from_val, to_val, period)`
     → interroge la view
   - service : délégation
   - `GET /api/devices/{id}/cpu/summary?from=6&to=7`
   - `GET /api/devices/{id}/ram/summary?from=6&to=7`
   - réponse : `{ total, breakdown: [{value, consumption}] }`
4. Frontend : filtre plage + total en haut + détail en bas + skeleton.
5. Créer `doc/md/11-cpu-ram-range-sum.md`.

---

### AJUSTEMENT 12 — Filtres date + heure partout

**But :** tous les filtres date acceptent **date + heure combinés**.

**Étapes :**
1. Lire `sql/versionFinal.sql` (toutes colonnes date/heure).
2. Backend : `datetime_from` / `datetime_to` en ISO 8601 pour tous les
   endpoints de liste. **Si plusieurs filtres se cumulent → RÉDIGER
   la VIEW** (§2.5, nom en français) et la **livrer à l'utilisateur**
   (pas de `CREATE VIEW` exécuté par l'agent).
3. Frontend : composant date+heure unifié, envoie ISO.
4. Endpoints minimum : évènements, devices, imprimantes, statistiques,
   alertes, CPU/RAM/disk history.
5. Créer `doc/md/12-datetime-filters.md`.

---

### AJUSTEMENT 13 — Documentation de suivi

**Dossier :** `doc/md/`

**Nomenclature :**
```
00-RECAP.md
01-sync-insertion-device-reseau.md
02-ram-max-total.md
03-filtres-backend-pagination.md
04-caching.md
05-skeleton-ui.md
06-cpu-ram-direct-db.md
07-disk-verification.md
08-dashboard-perf.md
09-events-datetime-format.md
10-life-remaining.md
11-cpu-ram-range-sum.md
12-datetime-filters.md
```

**Contenu imposé de chaque `.md` (sections) :**
1. Contexte (lien §7.x cahier des charges)
2. Fichiers existants vérifiés (checklist)
3. Décision : fichier/fonction identifiés
4. Fichiers créés/modifiés (repo → service → controller → model)
5. **⚠️ Views à créer — À exécuter manuellement par l'utilisateur**
   (bloc SQL prêt à copier, avec commentaires but/colonnes, nom de la
   VIEW en français, et la mention *"À exécuter dans `sql/views.sql`
   puis sur la base"*)
6. Spécifications (renvoi `sql/versionFinal.sql`, pas de SQL inline)
7. Critères d'acceptation (checklist)
8. Tests réalisés (inclure les vérifications BDD §2.7)
9. Risques / régressions
10. Respect §2.4 (aucune fonction imbriquée)

**`00-RECAP.md` :** tableau de tous les ajustements avec statut
(fait / partiel / bloqué), questions ouvertes, fichiers touchés.

**Section obligatoire dans `00-RECAP.md` — Views à créer par l'utilisateur :**

```markdown
## Views à créer par l'utilisateur (manuel)

| View (nom français) | Ajustement | Statut | Bloc SQL |
|---|---|---|---|
| v_tableau_de_bord_resume | AJUSTEMENT 8 | ⏳ en attente | voir `08-dashboard-perf.md` |
| v_resume_plage_cpu | AJUSTEMENT 11 | ⏳ en attente | voir `11-cpu-ram-range-sum.md` |
| v_resume_plage_ram | AJUSTEMENT 11 | ⏳ en attente | voir `11-cpu-ram-range-sum.md` |
| ... | ... | ... | ... |
```

> Le statut `⏳ en attente` / `✅ créée` est **mis à jour par
> l'utilisateur lui-même**, pas par l'agent.

---

## 4. CHECKLIST FINALE (avant chaque commit)

- [ ] Workflow §2.2 respecté
- [ ] `sql/versionFinal.sql` consulté (§2.1)
- [ ] Aucune requête SQL hors `repositories/`
- [ ] Aucune logique métier dans `controllers/`
- [ ] Credentials Google dans `.env` uniquement
- [ ] Idempotence respectée
- [ ] Gestion erreurs §10 (erreur device isolée)
- [ ] Skeleton UI partout
- [ ] Cache appliqué sur lectures coûteuses
- [ ] Pagination 5/10 sur toutes les listes
- [ ] Filtres 100% backend
- [ ] Date + heure combinés partout
- [ ] **Aucun `CREATE VIEW` exécuté par l'agent** (§2.5)
- [ ] **Toutes les VIEWS rédigées sont livrées à l'utilisateur** dans
      le `.md` de suivi + `00-RECAP.md` (§2.5)
- [ ] **Noms des VIEWS en français** (§2.5)
- [ ] **Vérifications BDD effectuées en lecture seule uniquement**
      (§2.7 — aucun `INSERT`/`UPDATE`/`DELETE`/`CREATE`/`ALTER`/`DROP`)
- [ ] Style cohérent avec l'existant (§2.4)
- [ ] **Aucune fonction imbriquée** (§2.4)
- [ ] `.md` de suivi créé dans `doc/md/`

---

## 5. RÈGLES D'ENCHAÎNEMENT

- Enchaîner **automatiquement** AJUSTEMENT 1 → 13, sans validation.
- **Sauf** si :
  - ambiguïté métier bloquante (ex: AJUSTEMENT 10)
  - info manquante dans `sql/versionFinal.sql`
  - choix architectural majeur
- **Si un ajustement dépend d'une VIEW que l'utilisateur n'a pas
  encore créée :**
  - l'agent **code quand même** le repository en supposant que la VIEW
    existera,
  - il **signale clairement** dans le rapport : *"⚠️ Cette VIEW doit
    être créée par l'utilisateur avant que l'endpoint fonctionne."*
  - il **continue** sur l'ajustement suivant (pas de blocage).
- À chaque étape : rapport court (5-10 lignes) + passer à la suivante.
- **Commencer par AJUSTEMENT 1 dès maintenant.**