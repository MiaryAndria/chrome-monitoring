# AJUSTEMENT 11 — CPU/RAM plage + somme + détail

## 1. Contexte

Guide agent, §3 AJUSTEMENT 11. Objectif : filtrer les relevés CPU/RAM
sur une plage de valeurs (ex. 6-7 %), afficher le **total cumulé** en
haut et le **détail par valeur** en bas, avec un squelette pendant le
chargement.

## 2. Fichiers existants vérifiés

- [x] `code/bdd/create/versionFinal.sql` — `t_device_cpu`
      (`cpu_utiliser NUMERIC(5,2)`) et `t_device_ram`
      (`ram_utiliser`, `ram_total` en octets)
- [x] `repository/cpu/device_cpu.py` — `get_latest_by_device` (AJUSTEMENT 6)
- [x] `repository/ram/ram.py` — `get_latest_by_device`, `get_max_total_ram`
- [x] `service/cpu_service.py`, `service/ram_service.py`
- [x] `controller/cpu_controller.py`, `controller/ram_controller.py`
- [x] `page/device/detail/cpu_tab.jsx`, `ram_tab.jsx`
- [x] Aucune VIEW de plage n'existait

## 3. Décision : fichiers/fonctions identifiés

- Deux VIEWS d'agrégation : `v_resume_plage_cpu` et
  `v_resume_plage_ram` (par device, valeur, jour).
- Pour la RAM, la « valeur » filtrée est le **pourcentage utilisé**
  (`ram_utiliser / ram_total × 100`) ; la « consommation » est la somme
  des octets utilisés.
- Pour le CPU, la valeur est `cpu_utiliser` (%) et la consommation la
  somme des pourcentages.
- Repository : `sum_range(...)` interroge la VIEW ; service : total +
  sérialisation ; controller : `?from=&to=` (+ bornes de date optionnelles).

## 4. Fichiers créés / modifiés

| Ordre | Fichier | Nature |
|---|---|---|
| — | `code/bdd/views.sql` | ajout des 2 VIEWS |
| 1 | `repository/cpu/device_cpu.py` | `sum_range` |
| 1 | `repository/ram/ram.py` | `sum_range` |
| 1 | `repository/{cpu,ram}/__init__.py` | exports |
| 2 | `service/cpu_service.py` | `get_cpu_range_summary` |
| 2 | `service/ram_service.py` | `get_ram_range_summary` |
| 3 | `controller/cpu_controller.py` | `GET /cpu/{id}/summary?from=&to=` |
| 3 | `controller/ram_controller.py` | `GET /ram/{id}/summary?from=&to=` |
| 4 | `fonction/deviceFonction.js` | `getCpuRangeSummary`, `getRamRangeSummary` |
| 4 | `page/device/detail/cpu_tab.jsx` | filtre plage + total + détail + skeleton |
| 4 | `page/device/detail/ram_tab.jsx` | idem |

Réponse API :
```json
{
  "device_id": 363,
  "from_value": 6,
  "to_value": 7,
  "total": 19.0,
  "breakdown": [
    { "value": 6.0, "consumption": 12.0, "samples": 2 },
    { "value": 7.0, "consumption": 7.0, "samples": 1 }
  ]
}
```

## 5. ⚠️ Views à créer — À exécuter manuellement par l'utilisateur

> **À exécuter dans `code/bdd/views.sql` puis sur la base PostgreSQL.**
> Sans elles, les endpoints `/cpu/{id}/summary` et `/ram/{id}/summary`
> échouent.

```sql
-- ------------------------------------------------------------
-- v_resume_plage_cpu
-- But : agréger les relevés CPU par device, valeur d'utilisation
--       et jour, pour les filtres de plage (ex. 6-7 %).
-- Colonnes : id_device, valeur (cpu_utiliser %), jour, nb_releves,
--            consommation (somme des utilisations de la plage)
-- Utilisée par : AJUSTEMENT 11 (plage + somme + détail)
-- À exécuter dans code/bdd/views.sql puis sur la base.
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_resume_plage_cpu AS
SELECT
    dc.id_device,
    dc.cpu_utiliser AS valeur,
    date_trunc('day', dc.date) AS jour,
    COUNT(*) AS nb_releves,
    SUM(dc.cpu_utiliser) AS consommation
FROM t_device_cpu dc
WHERE dc.cpu_utiliser IS NOT NULL
GROUP BY dc.id_device, dc.cpu_utiliser, date_trunc('day', dc.date);

-- ------------------------------------------------------------
-- v_resume_plage_ram
-- But : agréger les relevés RAM par device, pourcentage utilisé
--       et jour, pour les filtres de plage (ex. 6-7 %).
-- Colonnes : id_device, valeur (% utilisé), jour, nb_releves,
--            consommation (somme des octets utilisés)
-- Utilisée par : AJUSTEMENT 11 (plage + somme + détail)
-- À exécuter dans code/bdd/views.sql puis sur la base.
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_resume_plage_ram AS
SELECT
    dr.id_device,
    ROUND(dr.ram_utiliser::numeric * 100.0 / NULLIF(dr.ram_total, 0), 2) AS valeur,
    date_trunc('day', dr.date) AS jour,
    COUNT(*) AS nb_releves,
    SUM(dr.ram_utiliser) AS consommation
FROM t_device_ram dr
WHERE dr.ram_utiliser IS NOT NULL
  AND dr.ram_total IS NOT NULL
  AND dr.ram_total > 0
GROUP BY
    dr.id_device,
    ROUND(dr.ram_utiliser::numeric * 100.0 / NULLIF(dr.ram_total, 0), 2),
    date_trunc('day', dr.date);
```

## 6. Spécifications

- `sum_range(cur, id_device, from_val, to_val, datetime_from=None,
  datetime_to=None)` :
  - filtre `valeur BETWEEN %s AND %s` ;
  - bornes de date optionnelles sur `jour` ;
  - `GROUP BY valeur ORDER BY valeur`.
- Service : conversion `Decimal → float`, `total = Σ consumption`,
  réponse `{ device_id, from_value, to_value, total, breakdown }`.
- Controller : `from`/`to` exposés via des alias de query (mots
  réservés Python) + `datetime_from`/`datetime_to` optionnels.
- Frontend : deux champs `De (%)` / `À (%)` (0-100), bouton
  « Appliquer », total en haut, détail par valeur en bas, `Skeleton`
  pendant la requête. Aucun calcul lourd côté React.

## 7. Critères d'acceptation

- [x] VIEWS `v_resume_plage_cpu` / `v_resume_plage_ram` rédigées
- [x] `sum_range` dans les repositories CPU/RAM
- [x] Services délégation + total
- [x] Endpoints `?from=&to=`
- [x] Frontend plage + total + détail + skeleton
- [x] Aucun `CREATE VIEW` exécuté par l'agent
- [x] Build frontend OK

## 8. Tests réalisés (vérifications BDD §2.7, lecture seule)

Bodies des VIEWS exécutés **sans CREATE VIEW** :

| Vérification | Résultat |
|---|---|
| `v_resume_plage_cpu` (SELECT seul) | 8 724 lignes agrégées |
| `v_resume_plage_ram` (SELECT seul) | 2 216 lignes agrégées |
| CPU device 363, plage 0-100 | 13 valeurs, total 270 |
| CPU device 363, plage 6-7 | 2 valeurs (6 et 7), total 19, 3 relevés |
| CPU device 363, plage 90-100 | 0 valeur |
| RAM device 363, plage 0-100 | 6 valeurs (28,46 à ~75 %), total ~36,3 Go |
| RAM device 363, plage 30-40 | 0 valeur |
| Routes OpenAPI | `/cpu/{id}/summary`, `/ram/{id}/summary` présentes |
| Build frontend | OK |

`py_compile` OK sur les 8 fichiers backend modifiés.

## 9. Risques / régressions

- **Bloquant tant que les VIEWS ne sont pas créées** : les endpoints de
  plage échouent (500). Les blocs SQL sont fournis ci-dessus.
- L'agrégation par jour limite la granularité des bornes de date
  (filtrage au jour) ; suffisant pour le cas d'usage.
- Pour la RAM, la valeur filtrée est un pourcentage (pas des octets) ;
  c'est ce qui rend la plage 6-7 pertinente.

## 10. Respect §2.4

`sum_range` (repository) et `get_*_range_summary` / `_serialize_range_breakdown`
(service) sont des fonctions plates, sans fonction imbriquée ni closure.

## 11. C4 — Refonte : somme via filtres date+heure (POST_AJUSTEMENT)

### Changement demandé

- Suppression du champ « plage d'utilisation ».
- Utilisation des filtres **date début + date fin + heure** déjà présents.
- Calcul d'une **somme** sur la période via
  `get_cpu_device_date` / `get_ram_device_date`.
- Réponse : `{ somme, date_debut, date_fin }` (plus de breakdown).

### Backend

| Avant | Après |
|---|---|
| `sum_range(...)` sur `v_resume_plage_*` | `get_cpu_device_date(cur, id, date_debut, date_fin)` |
| `get_cpu_range_summary` / `get_ram_range_summary` | `get_cpu_device_date` / `get_ram_device_date` (service) |
| `GET /cpu/{id}/summary?from=&to=` | `GET /cpu/{id}/somme?date_debut=&date_fin=` |
| `GET /ram/{id}/summary?from=&to=` | `GET /ram/{id}/somme?date_debut=&date_fin=` |

- CPU : `SUM(cpu_utiliser)` entre `date_debut` et `date_fin`.
- RAM : `SUM(ram_utiliser)` (octets) entre `date_debut` et `date_fin`.
- Validation : `date_fin < date_debut` → **HTTP 400**.
- Aucune VIEW pour cette somme simple.

### SQL

- `v_resume_plage_cpu` et `v_resume_plage_ram` **retirées de**
  `code/bdd/views.sql`.
- Ajoutées à `code/bdd/drop_views.sql` (à exécuter manuellement si
  elles avaient déjà été créées) :

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

### Frontend

- `cpu_tab.jsx` / `ram_tab.jsx` : champs « De/À (%) » supprimés.
- Le filtre **interne** aux onglets est supprimé : les onglets
  reçoivent `datetimeFrom` / `datetimeTo` du filtre unique situé **en
  haut de la page détail device** (celui utilisé pour le filtrage de
  base des rapports).
- Appel `/somme` automatique dès que le filtre du haut est appliqué.
- Total en haut (`%` pour CPU, octets formatés pour RAM), pas de détail.
- Cache client `Map` par couple de bornes, `Skeleton` pendant le fetch.
- Sans filtre appliqué, le panneau affiche :
  « Appliquez le filtre date + heure en haut de la page ».

### Tests (lecture seule)

| Test | Résultat |
|---|---|
| Device 363 CPU, 2026-10-19 00:00 → 23:59:59 | `somme = 50.0` |
| Device 363 RAM, même période | `somme = 22 987 464 704` octets |
| Device inexistant | `0.0` / `0` |
| Routes | `/cpu/{id}/somme`, `/ram/{id}/somme` ; plus de `/summary` |
| Build frontend | OK |

### Risques

- Les VIEWS de plage peuvent encore exister en base : exécuter
  `code/bdd/drop_views.sql` si elles avaient été créées.
- La somme RAM est une somme d'octets sur des relevés successifs ;
  elle représente un cumul, pas une moyenne.
- Le total n'apparaît qu'après application d'une période.

## 12. C4 corrigé — total + détail + same_day (retour utilisateur)

Le total seul ne suffit pas : l'utilisateur veut **le total ET le détail**
sur la période, et aucun total quand début/fin sont le même jour.

Réponse de `GET /cpu/{id}/somme` et `GET /ram/{id}/somme` :

```json
// deux dates différentes
{ "total": 45.0, "same_day": false,
  "detail": [ { "date": "2026-10-15", "valeur": 2.0 },
              { "date": "2026-10-16", "valeur": 3.0 } ] }

// même jour
{ "total": null, "same_day": true,
  "detail": [ { "datetime": "2026-10-16T15:40:00", "valeur": 2.0 },
              { "datetime": "2026-10-16T15:41:00", "valeur": 3.0 } ] }
```

- Repository : `get_cpu_device_date` / `get_ram_device_date` retournent
  désormais les **relevés bruts** (`date`, `valeur`) au lieu d'une somme.
- Service : `_build_date_summary` (plat, sans fonction imbriquée) groupe
  par jour si `same_day = false`, sinon liste les mesures (`datetime`).
  `same_day = (date_debut.date() == date_fin.date())`.
- Controller : renvoie directement `{ total, same_day, detail }`.
- Frontend `cpu_tab.jsx` / `ram_tab.jsx` : total affiché uniquement si
  `!same_day` ; détail « par jour » ou « par mesure » en dessous.
- Aucune VIEW créée (règle C4.a inchangée).
- `t_device.ip_adress` (un seul « d ») inchangé.
- Détail multi-jours : `_group_by_day` génère **tous les jours** de la
  plage (date début → date fin). Les jours sans relevé renvoient
  `valeur: null` et le frontend affiche « Aucune donnée » au lieu de les
  masquer ; le total n'apparaît que si au moins une valeur existe.
