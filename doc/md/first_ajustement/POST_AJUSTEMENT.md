# POST_AJUSTEMENT — Corrections après AJUSTEMENTS 1→13

> **Contexte :** les AJUSTEMENTS 1→13 du guide
> `doc/md/AI_AGENT_GUIDE_MONITORING_PLATFORM.md` ont déjà été exécutés.
> Ce fichier liste les **corrections à apporter** suite aux retours
> utilisateur. Il ne remplace pas le guide principal — il le complète.
>
> **Règles générales (rappel du guide principal) :**
> - §2.2 : workflow Repository → Service → Controller → Model
> - §2.4 : pas de fonction imbriquée, code plat et lisible
> - §2.5 : les VIEWS sont **rédigées et livrées** à l'utilisateur,
>   **jamais créées par l'agent**
> - §2.7 : accès BDD en **lecture seule** autorisé
> - Ne rien supprimer sans vérifier les usages (grep dans le repo)
> - **Avant de créer un fichier → vérifier s'il existe déjà.**
>   Si oui : l'étendre. Si non : le créer.
> - **L'agent n'écrit pas d'`ALTER TABLE ADD CONSTRAINT`.**

---

## TABLE DES CORRECTIONS

| # | Correction | Priorité |
|---|---|---|
| C0 | Insertion dans `t_device_reseau` lors de la synchro + audit doublons | **Haute** |
| C1 | Performance pagination `liste_device` + `evenements` | Haute |
| C2 | Dashboard : redirections cassées + cartes cliquables | Haute |
| C3 | Life remaining : déplacé vers page évènements (accordéon) | Moyenne |
| C4 | CPU/RAM : refonte du calcul de somme via filtres date+heure | Haute |
| C5 | Filtre calendrier : ajout du champ heure partout | Moyenne |
| C6 | Suppression de VIEWS inutiles : `sql/drop_views.sql` | Basse |
| C7 | Audit et consolidation des controllers/services/repositories | Basse |

---

## STATUT D'EXÉCUTION (mis à jour par l'agent)

| # | Statut | Résumé |
|---|---|---|
| C0 | ✅ fait | `t_device.id_reseau` absent → fallback `t_device.ip_adress` ; `get_reseau_id_by_ip`, `get_by_device_and_reseau`, `insert_device_reseau` ; index + audit livrés. **Audit tranché : sous-réseaux partagés autorisés, 0 doublon interne par filiale, aucun DELETE.** |
| C1 | ✅ code fait | Pagination devices 15,9 s → ~380 ms après réécriture des VIEWS. **Ré-exécuter `code/bdd/views.sql`** (les VIEWS en base ont encore l'ancienne définition LATERAL). Index livrés. Cache client + prefetch + skeleton local. |
| C2 | ✅ fait | `/liste/imprimante` → `/imprimantes` ; sous-cartes événements cliquables (`?type=`). |
| C3 | ✅ fait | `life_*` fusionnés dans `evenement_*` ; `GET /evenement/{id}/duree-vie` ; affichage en accordéon dans les événements. |
| C4 | ✅ fait | Champ plage supprimé ; `get_*_device_date` + `/somme` ; VIEWS de plage retirées de `views.sql` et ajoutées à `drop_views.sql`. |
| C5 | ✅ fait | `DateHeureFilter` unique (aucun doublon) ; validation backend 400 si `datetime_to < datetime_from`. |
| C6 | ✅ fait | `code/bdd/drop_views.sql` créé ; 2 VIEWS candidates listées. |
| C7 | ✅ fait | `statistique_service` → `dashboard_service` ; `life_*` déjà fusionné ; `ram/__init.__.py` supprimé. |

### Actions manuelles restantes

1. **Ré-exécuter** `v_appareils_filtres` et `v_evenements_avec_appareil`
   depuis `code/bdd/views.sql` (`CREATE OR REPLACE VIEW`) pour activer
   l'optimisation C1.
2. **Exécuter** `code/bdd/drop_views.sql` pour supprimer les VIEWS de
   plage devenues inutiles.
3. **Exécuter** `code/bdd/indexes.sql` (index C0 + C1 livrés,
   non exécutés par l'agent).
4. **C0 — audit `t_reseau_filiale`** : ✅ **validé** — un réseau peut
   appartenir à plusieurs filiales ; aucun `DELETE`, aucune contrainte
   supplémentaire. Aucun doublon interne par filiale.

---

## C0 — Insertion dans `t_device_reseau` lors de la synchro

### Problème constaté
> *"Lors de `synchronisation_automatique` il n'y a pas d'insertion alors verifie fonction synchroniser_tout et ajuste là dedans
> device dans `t_device_reseau`. J'aimerais récupérer les informations
> des devices et réseaux et les insérer dans `t_device_reseau`. Et si
> existe déjà, à chaque synchro on n'insère plus."*

### Structure de la table (source de vérité)

```sql
CREATE TABLE t_device_reseau (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),
    id_reseau INT NOT NULL REFERENCES t_reseau(id),
    date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (id_device, id_reseau)
);
```

**Points importants :**
- `UNIQUE (id_device, id_reseau)` garantit déjà l'absence de doublons.
- `date` remplie automatiquement par `DEFAULT NOW()`.
- `IntegrityError` sur UNIQUE = doublon → **skip** (pas log critique).

### ⚠️ RÈGLE — Source du `id_reseau`

> **Si le réseau existe déjà dans `t_device` (colonne `id_reseau`
> renseignée), on utilise JUSTE `t_device.id_reseau` directement.**
>
> On **ne recherche PAS** dans `t_reseau` par IP. On **ne crée PAS** de
> nouvelle ligne `t_reseau`. On prend l'id existant.
>
> **Fallback uniquement** : si `t_device.id_reseau` est NULL → on
> recherche dans `t_reseau` via l'IP. Si l'IP n'existe pas → skip + warning.

**Ordre de résolution du `id_reseau` :**
1. **Priorité 1** : `t_device.id_reseau` (si non NULL).
2. **Priorité 2** : recherche dans `t_reseau` via `t_device.adresse_ip`.
3. **Sinon** : skip + warning.

### Diagnostic à faire

1. **Lire `sql/versionFinal.sql`** :
   - `t_device` : identifier **quelle colonne contient le réseau**
     (`id_reseau`, `adresse_ip`, `network_id`, etc.).
   - `t_reseau` : `id`, `valeur` (IP).
   - `t_reseau_filiale` : `id_reseau`, `id_filiale`.

2. **Vérifier en BDD** (§2.7, lecture seule) :

```sql
-- Colonnes de t_device (identifier la source réseau)
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 't_device'
ORDER BY ordinal_position;

-- Devices sans ligne dans t_device_reseau
SELECT COUNT(*) FROM t_device d
WHERE NOT EXISTS (
    SELECT 1 FROM t_device_reseau dr WHERE dr.id_device = d.id
);
```

3. **Rapporter** : structure réelle de `t_device` (colonne réseau),
   nombre de devices sans réseau.

### ✅ Audit `t_reseau_filiale` — décision et résultat

> **Réponse utilisateur (validée) : NORMAL** — un même réseau **peut**
> appartenir à 2 filiales (sous-réseau partagé).
> → **Aucun script `DELETE`**, **aucune contrainte `UNIQUE`
> supplémentaire**, données conservées telles quelles.

L'audit demandé porte sur les **doublons internes à chaque filiale**
(et non sur les réseaux partagés entre filiales) :

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
- 30 filiales contrôlées ;
- **0 filiale** avec `total <> distincts` ;
- **0 ligne** retournée par `HAVING COUNT(*) > 1` ;
- contrainte `UNIQUE (id_reseau, id_filiale)` présente.

→ **Aucun doublon interne, aucun script de nettoyage nécessaire.**

Constat complémentaire : `172.22.64.*` = 49 liaisons SODIREX
(filiale 2), 0 SOREDIM (filiale 1) ; 3 réseaux partagés entre
2 filiales (autres sous-réseaux), ce qui est **normal**.
La colonne IP réelle est **`t_device.ip_adress`** (un seul « d »).

### Corrections backend

#### C0.a — Repository — `repositories/reseau_repository.py`

```python
def find_devices_without_network(session):
    """
    Retourne les devices (id, id_reseau, adresse_ip) qui n'ont AUCUNE
    ligne dans t_device_reseau.
    """
    ...

def get_reseau_id_by_ip(session, ip):
    """Fallback : id de t_reseau pour une IP, ou None."""
    ...

def get_by_device_and_reseau(session, device_id, reseau_id):
    """Ligne t_device_reseau pour ce couple, ou None."""
    ...

def insert_device_reseau(session, device_id, reseau_id):
    """INSERT dans t_device_reseau (date = DEFAULT NOW())."""
    ...
```

#### C0.b — Service — `services/reseau_service.py`

```python
def get_missing_networks():
    return reseau_repository.find_devices_without_network(db.session)


def resolve_id_reseau(device_row):
    """
    Priorité 1 : device_row.id_reseau (déjà renseigné dans t_device).
    Priorité 2 : recherche dans t_reseau via device_row.adresse_ip.
    Sinon : None.
    """
    if device_row.id_reseau is not None:
        return device_row.id_reseau
    if device_row.adresse_ip:
        return reseau_repository.get_reseau_id_by_ip(
            db.session, device_row.adresse_ip
        )
    return None


def upsert_network_for_device(device_row):
    """
    Idempotence :
    - resolve_id_reseau.
    - Si None → skip + warning.
    - Si couple existe → skip.
    - Sinon → INSERT, catch IntegrityError → skip.
    """
    reseau_id = resolve_id_reseau(device_row)

    if reseau_id is None:
        logger.warning(
            f"[sync] device {device_row.id} : aucun réseau résolu, skip"
        )
        return

    existing = reseau_repository.get_by_device_and_reseau(
        db.session, device_row.id, reseau_id
    )
    if existing is not None:
        return

    try:
        reseau_repository.insert_device_reseau(
            db.session, device_row.id, reseau_id
        )
    except IntegrityError:
        db.session.rollback()
        logger.info(
            f"[sync] device {device_row.id} réseau {reseau_id} déjà inséré"
        )
```

#### C0.c — Orchestration — `services/sync_service.py`

```python
def sync_networks_for_all_devices():
    missing = reseau_service.get_missing_networks()
    for row in missing:
        try:
            reseau_service.upsert_network_for_device(row)
        except Exception as e:
            logger.error(f"[sync] device {row.id} network failed: {e}")
            continue
```

#### C0.d — Intégration dans la synchro existante

À la fin de la fonction de synchronisation automatique (identifiée en
lisant `app/jobs/` ou `app/services/`), après la persistance des
devices :

```python
sync_networks_for_all_devices()
```

#### C0.e — Controller — **rien à créer**

Pas d'endpoint demandé → pas de `reseau_controller.py` (règle C7).

#### C0.f — Modèle SQLAlchemy

Vérifier si `t_device_reseau` a déjà un modèle dans `app/models/`.
Sinon :

```python
class DeviceReseau(Base):
    __tablename__ = "t_device_reseau"

    id = Column(Integer, primary_key=True)
    id_device = Column(Integer, ForeignKey("t_device.id"), nullable=False)
    id_reseau = Column(Integer, ForeignKey("t_reseau.id"), nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("id_device", "id_reseau", name="uq_device_reseau"),
    )
```

### SQL à livrer (à exécuter par l'utilisateur)

> **Note :** Aucune contrainte `ALTER TABLE ... ADD CONSTRAINT UNIQUE`
> n'est proposée. L'ajout de contraintes `UNIQUE` est un choix métier
> qui revient à l'utilisateur.

**Index (exemple, 1 bloc) :**

```sql
-- Index pour accélérer la synchro des réseaux
-- À exécuter manuellement par l'utilisateur.
CREATE INDEX IF NOT EXISTS idx_t_device_reseau_device
    ON t_device_reseau (id_device);
```

**Audit doublons (exemple, 1 requête) :**

```sql
-- Doublons dans t_reseau_filiale
SELECT id_reseau, COUNT(*) AS nb_filiales
FROM t_reseau_filiale
GROUP BY id_reseau
HAVING COUNT(*) > 1;
```

### Tests manuels

- [ ] Device avec `id_reseau` renseigné → INSERT direct.
- [ ] Device sans `id_reseau` mais avec IP → recherche dans `t_reseau`.
- [ ] Device sans réseau → warning loggé, skip.
- [ ] Couple déjà présent → **skip** (aucun log critique).
- [ ] Exception sur un device → boucle continue.
- [ ] `SELECT COUNT(*) FROM t_device_reseau;` avant/après.

### ✅ Critères d'acceptation C0

- [ ] `t_device.id_reseau` utilisé **en priorité**.
- [ ] Fallback `t_reseau.valeur` si `id_reseau` NULL.
- [ ] `UNIQUE (id_device, id_reseau)` respectée.
- [ ] Réseau/IP absent → **loggé** et **skippé**.
- [ ] Erreur device → n'interrompt pas la synchro.
- [ ] Aucun `INSERT` en double.
- [ ] Aucune requête SQL dans le service.
- [ ] Aucune fonction imbriquée.
- [ ] `CREATE INDEX` et audit **livrés** (pas exécutés).
- [ ] `doc/md/01-sync-insertion-device-reseau.md` mis à jour.

### Fichiers à créer/modifier (C0)

- Backend : `reseau_repository.py`, `reseau_service.py`,
  `sync_service.py`, modèle `DeviceReseau`
- Documentation : `doc/md/01-sync-insertion-device-reseau.md`

---

## C1 — Performance pagination `liste_device` + `evenements`

### Symptôme
> *"Quand j'appuie sur le bouton 3 ou suivant, ça prend du temps et ça
> bug un peu avant d'afficher le suivant. Il faut que ce soit rapide.
> Pour évènements aussi c'est pareil."*

### Diagnostic à faire avant de corriger
1. **Ouvrir** les composants React `liste_device` et `evenements`.
2. **Identifier** :
   - Comment le `page` state est géré.
   - Est-ce que **tout le composant** re-render au changement de page ?
   - Est-ce qu'un spinner global s'affiche ?
   - Est-ce que le `useEffect` dépend de trop de variables ?
3. **Ouvrir** l'endpoint backend.
4. **Vérifier en BDD** (§2.7) : nombre de lignes, index existants.
5. **Rapporter** : lignes totales, colonnes sans index, comportement front.

### Corrections backend

#### C1.a — Requête paginée efficace
- Colonnes utiles uniquement (pas de `SELECT *`).
- Total dans la même requête (`COUNT(*) OVER()` en PostgreSQL).
- Tri sur colonne indexée.

```python
def find_paginated(session, page, page_size, filters):
    # WHERE + COUNT(*) OVER() + LIMIT/OFFSET
    # Retourner (items, total)
    ...
```

#### C1.b — Index manquants (à livrer, pas à exécuter)

> **L'agent ne crée PAS les index.** Il **rédige** et **livre** dans
> le rapport + `03-filtres-backend-pagination.md`.

Exemple (1 bloc) :

```sql
-- Index pour la pagination liste_device (C1)
CREATE INDEX IF NOT EXISTS idx_<table>_date_creation
    ON <table> (date_creation DESC);
```

Répéter pour `evenements`.

#### C1.c — Controller inchangé
Format `{ items, total, page, page_size, total_pages }` si déjà respecté.

### Corrections frontend

#### C1.d — Supprimer le re-render global
- Cache client `Map<pageNumber, items[]>`.
- **Skeleton en bas** (pas de spinner global).
- Bouton "suivant" **désactivé** pendant le fetch.
- Throttle des clics rapides.

#### C1.e — Préchargement page N+1
Dès l'affichage de la page N : fetch N+1 en arrière-plan, stocker dans
le cache.

#### C1.f — Composant pagination stable
Dépend uniquement de `total` et `page_size`. Isolé du parent.

### ✅ Critères d'acceptation C1
- [ ] Clic "suivant" / numéro → affichage **sans bug**
- [ ] Pas de spinner global → **skeleton local**
- [ ] Pages déjà visitées → **instantané** (cache client)
- [ ] Préchargement N+1
- [ ] Aucun re-render du parent
- [ ] Index SQL **livrés** (pas exécutés)
- [ ] Même corrections sur `evenements`

### Fichiers à créer/modifier (C1)
- Repository : requête optimisée
- Frontend : liste + pagination + hook cache client
- Documentation : `03-filtres-backend-pagination.md`

---

## C2 — Dashboard : redirections cassées

### Symptôme
> *"Dans dashboard, quand j'appuie sur imprimante, redirection vers
> page imprimante avec erreur. Et pour les évènements, fais en sorte
> que ce soit cliquable."*

### Diagnostic à faire
1. Ouvrir le composant dashboard React.
2. Identifier les cartes / tuiles cliquables ou non.
3. Ouvrir la page cible (imprimantes) → noter l'erreur console.
4. Rapporter l'erreur exacte.

### Corrections frontend

#### C2.a — Rendre toutes les cartes cliquables
- Curseur pointer, hover.
- `navigate('/<route>')` via `useNavigate`.
- Route **existante et valide**.

#### C2.b — Corriger la page cible `imprimantes`
- Aucun paramètre de route manquant.
- Aucun state initial non défini.
- Appels API au montage gèrent `loading` et `error`.
- Si 500 backend → corriger le backend aussi.

#### C2.c — Rendre la carte évènements cliquable
`navigate('/evenements')`, route valide, page cible OK.

### ✅ Critères d'acceptation C2
- [ ] Toutes les cartes cliquables
- [ ] Redirection `/imprimantes` **sans erreur**
- [ ] Redirection `/evenements` **sans erreur**
- [ ] Aucune erreur console au montage
- [ ] Aucun changement visuel non demandé

### Fichiers à créer/modifier (C2)
- Frontend dashboard : cartes cliquables
- Frontend pages imprimantes + évènements : correction du montage
- Documentation : `08-dashboard-perf.md`

---

## C3 — Life remaining : déplacé vers page évènements

### Changement demandé
> *"Life remaining on n'affiche pas dans détails device mais dans page
> évènements. Genre quand on appuie sur liste déroulante dans
> évènements, c'est là que ça s'affiche."*

### Diagnostic à faire
1. Localiser `life_controller.py`, `life_service.py`,
   `life_repository.py` et le composant React dans le détail device.
2. Vérifier les endpoints existants liés.
3. Rapporter : ce qui existe, où c'est appelé.

### Corrections backend

#### C3.a — Fusionner dans `evenement_*` (voir C7)
- Supprimer `life_*` si créés.
- Déplacer la logique dans `evenement_service.py` /
  `evenement_repository.py` / `evenement_controller.py`.

#### C3.b — Endpoint exposé via `evenement_controller`
```
GET /api/evenements/{id}/duree-vie
```
Retourne `{ duree_vie, unite, details }`.

> **⚠️ Question métier toujours en suspens :**
> Durée de vie = (a) batterie restante, (b) AUE, (c) temps depuis
> dernier évènement ? **Demander avant d'implémenter.**

### Corrections frontend

#### C3.c — Retirer du détail device
Supprimer section « durée de vie » + appel API associé.

#### C3.d — Ajouter dans page évènements (accordéon)
- Chaque ligne → accordéon.
- Clic → fetch `/duree-vie`.
- Affiche durée + détails.
- **Skeleton** pendant le fetch.
- Une seule ligne ouverte à la fois.

### ✅ Critères d'acceptation C3
- [ ] Aucune mention dans le détail device
- [ ] Durée dans l'accordéon évènements
- [ ] Endpoint dans `evenement_controller`
- [ ] Skeleton au dépliage
- [ ] Fichiers `life_*` supprimés/fusionnés

### Fichiers à créer/modifier (C3)
- Backend : `evenement_*` (ajout logique life)
- Backend : suppression `life_*` (voir C7)
- Frontend : détail device (retirer), évènements (accordéon)
- Documentation : `10-life-remaining.md`

---

## C4 — CPU/RAM : refonte du calcul de somme via filtres date+heure

### Changement demandé
> *"Pour plage dans RAM et CPU, on ne crée pas un champ pour insérer
> plage d'utilisation. On utilise filtre date début et date fin en haut
> et c'est valeurs de ces deux sommes qu'on fait somme et affiche.
> Genre une fonction `get_ram_device_date` et argument date et CPU, et
> on traite somme ensuite, et on return."*

### Diagnostic à faire
1. Identifier ce qui a été créé pour l'AJUSTEMENT 11 :
   - Champ "plage" → à supprimer.
   - VIEWS `v_resume_plage_cpu` / `v_resume_plage_ram` → à retirer +
     ajouter à `sql/drop_views.sql`.
   - Endpoints `/cpu/summary?from=&to=` et `/ram/summary?from=&to=`
     → à remplacer.
2. Rapporter ce qui existe.

### Corrections backend

#### C4.a — Nouvelles fonctions de repository
```python
# repositories/cpu_repository.py
def get_cpu_device_date(session, device_id, date_debut, date_fin):
    # SELECT SUM(<colonne_valeur>)
    # FROM t_device_cpu
    # WHERE <colonne_device_id> = :device_id
    #   AND <colonne_date> BETWEEN :date_debut AND :date_fin
    ...

# repositories/ram_repository.py
def get_ram_device_date(session, device_id, date_debut, date_fin):
    # idem sur t_device_ram
    ...
```

> **⚠️ Ne PAS créer de VIEW** pour cette somme simple.

#### C4.b — Service de délégation
```python
# services/cpu_service.py
def get_cpu_device_date(device_id, date_debut, date_fin):
    return cpu_repository.get_cpu_device_date(
        db.session, device_id, date_debut, date_fin
    )

# services/ram_service.py
def get_ram_device_date(device_id, date_debut, date_fin):
    return ram_repository.get_ram_device_date(
        db.session, device_id, date_debut, date_fin
    )
```

#### C4.c — Controller : remplacer les endpoints
- **Supprimer** :
  - `GET /api/devices/{id}/cpu/summary?from=&to=`
  - `GET /api/devices/{id}/ram/summary?from=&to=`
- **Créer** :
  - `GET /api/devices/{id}/cpu/somme?date_debut=&date_fin=`
  - `GET /api/devices/{id}/ram/somme?date_debut=&date_fin=`
- Réponse : `{ "somme": 123.45, "date_debut": "...", "date_fin": "..." }`
- Validation : `date_fin < date_debut` → HTTP 400.

### Corrections frontend

#### C4.d — Pages CPU et RAM
- Supprimer le champ "plage".
- Conserver uniquement les filtres **date début + date fin + heure**
  (composant C5).
- Au changement → appel `/somme`.
- Total en haut.
- Pas de breakdown.
- Skeleton + cache client.

### Corrections SQL

#### C4.e — Supprimer les VIEWS plage
Si `v_resume_plage_cpu` / `v_resume_plage_ram` ont été rédigées :
1. Retirer de `sql/views.sql`.
2. Ajouter dans `sql/drop_views.sql` (voir C6 pour le format).

### ✅ Critères d'acceptation C4
- [ ] Plus de champ "plage"
- [ ] `get_cpu_device_date` / `get_ram_device_date` créées
- [ ] Endpoints `/somme` fonctionnels
- [ ] Total = somme réelle sur la période
- [ ] Validation `date_fin >= date_debut`
- [ ] VIEWS plage retirées + ajoutées à `sql/drop_views.sql`
- [ ] Skeleton + cache client

### Fichiers à créer/modifier (C4)
- Backend : `cpu_*` et `ram_*`
- Frontend : pages CPU et RAM
- SQL : `sql/views.sql`, `sql/drop_views.sql`
- Documentation : `11-cpu-ram-range-sum.md`

---

## C5 — Filtre calendrier : ajout du champ heure partout

### Changement demandé
> *"Ce filtre calendrier là, ajoute possibilité de faire filtre avec
> heure aussi."*

### ⚠️ RÈGLE — Vérifier AVANT de créer

> - **1 composant existant** → **l'étendre** (pas de nouveau).
> - **Plusieurs** → **unifier** (choisir le plus utilisé, étendre,
>   remplacer les autres, supprimer après grep propre).
> - **Aucun** → **le créer**.

### Diagnostic à faire AVANT toute action
1. Chercher dans `src/` : `type="date"`, `DatePicker`, `DateRange`,
   `Calendar`, `FiltreDate`, `DateFilter`, etc.
2. Lister : nom, pages qui l'utilisent, présence d'un champ heure.
3. Décider : étendre / unifier / créer.
4. Rapporter la décision.

### Corrections frontend

#### C5.a — Étendre le composant existant
- Ajouter `<input type="time">` à côté du `<input type="date">`.
- Conserver l'API actuelle.
- Format de sortie : `YYYY-MM-DDTHH:mm:ss`.
- Rétrocompatibilité : heure absente → `00:00` (début) / `23:59:59` (fin).
- Adapter les pages qui consommaient l'ancien format.

#### C5.b — Unifier les doublons
- Choisir le plus utilisé comme base.
- L'étendre (comme C5.a).
- Remplacer les usages des autres.
- Supprimer les anciens après grep propre.
- Signaler dans le rapport.

#### C5.c — Créer un composant (aucun trouvé)
- `src/components/DateTimeFilter.jsx` (ou équivalent selon le style).
- Date + heure côte à côte.
- Callback renvoie ISO 8601 complet.
- Si date remplie, heure vide → `00:00` par défaut.

#### C5.d — Comportement (dans tous les cas)
- Renvoie au parent une valeur ISO 8601 complète.
- Gère les bornes début/fin avec heure.
- Valide : date fin < date début → avertissement visuel.
- Propage l'heure (`00:00:00` début, `23:59:59` fin par défaut).

### Corrections backend

#### C5.e — Endpoints acceptent ISO 8601 avec heure
```
?datetime_from=YYYY-MM-DDTHH:mm:ss&datetime_to=YYYY-MM-DDTHH:mm:ss
```
- Parser en `datetime` côté controller.
- Valider `datetime_to >= datetime_from`.
- Repository applique le `WHERE`.

#### C5.f — VIEWS si nécessaire
Endpoint combinant date+heure + plusieurs filtres → **rédiger la VIEW**
(§2.5) et la **livrer**.

### ✅ Critères d'acceptation C5
- [ ] Vérification d'existence **AVANT** création
- [ ] Composant existant → étendu
- [ ] Doublons → unifiés
- [ ] Aucun → créé
- [ ] Envoie ISO 8601 complet
- [ ] Utilisé partout où un filtre date existait
- [ ] Backend valide et filtre
- [ ] Test `10/01/2024 08:30 → 17:45` fonctionne

### Fichiers à créer/modifier (C5)
- Frontend : composant existant étendu (ou créé), tous les `<input type="date">`
- Backend : tous les controllers/services/repositories avec filtre date
- Documentation : `12-datetime-filters.md`

---

## C6 — Script de suppression des VIEWS : `sql/drop_views.sql`

### Changement demandé
> *"Créer script pour suppression VIEW s'il y a des VIEWS qu'on
> n'aurait pas besoin."*

### Action

#### C6.a — Créer `sql/drop_views.sql` s'il n'existe pas
> Vérifier d'abord si le fichier existe. Si oui → étendre. Si non → créer.

Format :
```sql
-- ============================================================
-- SUPPRESSION DES VIEWS DEVENUES INUTILES
-- À exécuter manuellement par l'utilisateur.
-- Ajouter une ligne quand une VIEW n'est plus utilisée.
-- Ne rien supprimer des autres lignes sans vérifier.
-- ============================================================

-- (aucune VIEW à supprimer pour l'instant)
```

#### C6.b — Recenser les VIEWS candidates
1. Lister toutes les VIEWS (`sql/views.sql` + `information_schema.views`).
2. Identifier celles qui ne sont **plus utilisées** :
   - grep dans `app/repositories/` : aucune référence.
   - Ou remplacées par une autre VIEW.
3. Rapporter dans le rapport + `00-RECAP.md`.

#### C6.c — Ajouter les `DROP VIEW` correspondants
Exemple (1 bloc) :
```sql
-- v_ancienne_view
-- Raison : remplacée par v_nouvelle_view (C4)
-- Date : YYYY-MM-DD
DROP VIEW IF EXISTS v_ancienne_view;
```

**Ne pas exécuter** — c'est l'utilisateur.

### ✅ Critères d'acceptation C6
- [ ] `sql/drop_views.sql` existe (créé ou étendu)
- [ ] VIEWS inutiles identifiées et listées
- [ ] Chaque `DROP VIEW IF EXISTS` commenté (raison + date)
- [ ] Aucun `DROP VIEW` exécuté par l'agent
- [ ] `00-RECAP.md` mis à jour

### Fichiers à créer/modifier (C6)
- SQL : `sql/drop_views.sql`
- Documentation : `00-RECAP.md`

---

## C7 — Audit et consolidation des controllers/services/repositories

### Changement demandé
> *"Comme par exemple t'as créé `life_controller`, celui-ci pouvait
> être combiné avec `evenement_controller`. Alors vérifie les
> controllers etc. qui peuvent être ensemble avant de créer. Et ajuste
> ce que t'as créé tout à l'heure pour être avec fichier qui peuvent
> être ensemble, et si ils peuvent pas être ensemble alors c'est là
> qu'on crée fichier."*

### Règle de consolidation
> **Avant de créer un nouveau fichier** (`*_controller.py`,
> `*_service.py`, `*_repository.py`), **vérifier** si la fonctionnalité
> peut être **fusionnée** dans un fichier existant du **même domaine
> métier**.

**Règle de décision :**
- Même entité principale (ex: life = propriété d'un évènement) → **fusionner**.
- Fonctionnalité transverse (cache global, auth) → fichier dédié légitime.
- Fonctionnalité isolée sans parent naturel → fichier dédié.

**Exemples de fusion :**
- `life_*` → `evenement_*`
- `ram_stats_*` → `ram_*`
- `cpu_stats_*` → `cpu_*`
- `printer_events_*` → `printer_*`
- `device_network_*` → `device_*` ou `reseau_*` selon le cas

### Diagnostic à faire

#### C7.a — Lister tous les fichiers existants
- `app/controllers/`
- `app/services/`
- `app/repositories/`

#### C7.b — Identifier les candidats à la fusion
Tableau à produire dans le rapport :

| Fichier existant | Peut être fusionné dans | Raison |
|---|---|---|
| `life_controller.py` | `evenement_controller.py` | life = propriété évènement |
| ... | ... | ... |

#### C7.c — Proposer les fusions
Proposer dans le rapport **AVANT** de modifier. Attendre confirmation
si la fusion n'est pas évidente.

### Corrections

#### C7.d — Fusionner les fichiers identifiés
1. **Backend** :
   - Déplacer les fonctions du source vers la cible.
   - Adapter les imports (grep).
   - Supprimer le source **seulement** après grep propre.
   - Vérifier que les **URLs exposées restent identiques**.
2. **Backend — Router** :
   - Fusionner dans le router cible.
   - Vérifier que `main.py` n'importe plus le source.
3. **Documentation** :
   - Mettre à jour `00-RECAP.md` (liste des fusions).
   - Mettre à jour le `.md` de suivi concerné.

#### C7.e — Ne PAS fusionner ce qui n'a pas à l'être
Exemple : `device_controller` et `printer_controller` restent séparés.

### ✅ Critères d'acceptation C7
- [ ] Liste des fichiers existants produite
- [ ] Candidats identifiés et documentés
- [ ] Fusions confirmées effectuées
- [ ] Aucun import cassé (grep propre)
- [ ] Aucune route cassée
- [ ] `00-RECAP.md` mis à jour

### Fichiers à créer/modifier (C7)
- Backend : sources à supprimer, cibles à enrichir, `main.py`, routers
- Documentation : `00-RECAP.md`, `.md` de suivi concernés

---

## LIVRABLES ATTENDUS (fin de POST_AJUSTEMENT)

### Documentation
- [x] `POST_AJUSTEMENT.md` (ce fichier, mis à jour)
- [x] `00-RECAP.md` (Views à créer, Views à supprimer, Fusions effectuées)
- [x] `bdd.md` — rôle détaillé des VIEWS et des INDEX
- [x] `01-sync-insertion-device-reseau.md` (C0)
- [x] `03-filtres-backend-pagination.md` (C1)
- [x] `08-dashboard-perf.md` (C2)
- [x] `10-life-remaining.md` (C3)
- [x] `11-cpu-ram-range-sum.md` (C4)
- [x] `12-datetime-filters.md` (C5)

### SQL livré (pas exécuté)
- [x] Bloc `CREATE INDEX` pour la pagination (C1) — `code/bdd/indexes.sql`
- [x] Index pour `t_device_reseau` (C0) — `code/bdd/indexes.sql`
- [x] Requête d'audit doublons `t_reseau_filiale` (C0)
- [x] `code/bdd/drop_views.sql` mis à jour (C4, C6)

### Code
- [x] Corrections C0 → C7 appliquées
- [x] Aucun fichier orphelin (imports cassés)
- [x] Aucune fonction imbriquée (§2.4)
- [x] Aucun SQL hors `repositories/` (§2.2)
- [x] **Aucun `ALTER TABLE ADD CONSTRAINT` rédigé**

---

## RAPPORT FINAL ATTENDU

L'agent produit un rapport court (15-20 lignes) couvrant :

1. **C0** : fonction synchro identifiée + `resolve_id_reseau`
   (priorité `t_device.id_reseau`) + audit doublons + index livrés
2. **C1** : bug pagination identifié + corrections + index livrés
3. **C2** : cause exacte redirection + corrections
4. **C3** : `life_*` fusionnés (ou supprimés) + emplacement final
5. **C4** : anciennes fonctions plage supprimées +
   `get_*_device_date` créées + VIEWS plage retirées de
   `sql/views.sql` + ajoutées à `sql/drop_views.sql`
6. **C5** : composant trouvé et étendu (ou créé) + pages mises à jour
7. **C6** : `sql/drop_views.sql` créé + VIEWS candidates listées
8. **C7** : tableau des fusions + grep propre
9. **Questions ouvertes** (ex: métrique life remaining, doublons
   `t_reseau_filiale` `id_filiale=2`)
10. **Points à vérifier manuellement**

---

## RÈGLES D'EXÉCUTION

- Traiter les corrections **dans l'ordre C0 → C7**.
- Entre chaque correction : rapport court (5-10 lignes) puis suivante.
- **Ne pas exécuter** : `CREATE VIEW`, `CREATE INDEX`, `DROP VIEW`,
  `ALTER`, `INSERT`, `UPDATE`, `DELETE`.
- **Oui** : `SELECT`, `EXPLAIN`, `information_schema` (§2.7).
- **Ne pas rédiger** de bloc `ALTER TABLE ADD CONSTRAINT UNIQUE`.
- Si ambiguïté métier (ex: C3, C0 audit doublons) → poser la question,
  faire les autres parties, ne pas bloquer.
- Si une correction nécessite une VIEW → rédiger et livrer.
- **Commencer par C0 dès maintenant.**