# AJUSTEMENT 12 — Filtres date + heure partout

## 1. Contexte

Guide agent, §3 AJUSTEMENT 12. Objectif : tous les filtres de date
acceptent **date + heure combinés** et envoient des bornes ISO 8601
(`datetime_from` / `datetime_to`). Lorsque plusieurs filtres se
cumulent, la requête passe par une VIEW (§2.5).

## 2. Fichiers existants vérifiés

- [x] `code/bdd/create/versionFinal.sql` — colonnes date/heure :
      `t_device.date_creation`, `t_evenement_device.date_evenement`,
      `t_rapport_device.report_time`, `t_imprimante_device.date`,
      `t_device_cpu.date`, `t_device_ram.date`, `t_disk_device.date`
- [x] `/evenement/liste` — acceptait déjà `datetime_from`/`datetime_to`
      (AJUSTEMENT 3)
- [x] `/device/liste`, `/imprimante/liste`, `/filiale/{id}/devices` —
      aucun filtre de date
- [x] `/rapport/filter` — `date_debut`/`date_fin` (jour uniquement)
- [x] `frontend/src/page/component/dateFilter.jsx` — date seule
- [x] Pages : `event/liste.jsx`, `device/liste.jsx`,
      `imprimante/liste.jsx`, `device/detail_device.jsx`

## 3. Décision : fichiers/fonctions identifiés

- Un composant unique `DateHeureFilter` (date + heure de début/fin)
  remplace `DateFilter` (supprimé, plus aucun usage).
- Les bornes envoyées sont des chaînes ISO locales
  (`yyyy-mm-ddTHH:mm:ss`) interprétées par FastAPI en `datetime`.
- Imprimantes : le filtre porte sur la dernière détection
  (`MAX(t_imprimante_device.date)`), d'où la VIEW
  `v_imprimantes_filtrees`.
- Devices : le filtre porte sur `t_device.date_creation` via
  `v_appareils_filtres`.
- Rapports (historique CPU/RAM/etc.) : nouvelle requête
  `report_time >= from AND report_time <= to`.

## 4. Fichiers créés / modifiés

| Fichier | Nature |
|---|---|
| `code/bdd/views.sql` | ajout `v_imprimantes_filtrees` |
| `repository/devices/devices.py` | filtres `datetime_from/to` |
| `repository/imprimante/imprimante.py` | idem + VIEW imprimantes |
| `repository/rapport/rapport_device.py` | `get_rapport_by_device_type_and_datetime` |
| `repository/rapport/__init__.py` | export |
| `service/device_service.py`, `imprimante_service.py` | paramètres + clés de cache |
| `service/filiale_service.py` | délégation date+heure |
| `service/rapport_service.py` | `filterRapportDeviceByDatetime` |
| `controller/device_controller.py`, `imprimante_controller.py`, `filiale_controller.py` | query params |
| `controller/rapport_controller.py` | `/filter` en `datetime_from/to` |
| `fonction/deviceFonction.js` | `filterByDeviceIdAndDateTime` |
| `page/component/DateHeureFilter.jsx` | créé |
| `page/component/dateFilter.jsx` | supprimé (inutilisé) |
| `page/event/liste.jsx`, `device/liste.jsx`, `imprimante/liste.jsx`, `device/detail_device.jsx` | filtre date+heure |

Endpoints avec date + heure :
- `GET /evenement/liste?datetime_from=&datetime_to=`
- `GET /device/liste?datetime_from=&datetime_to=`
- `GET /imprimante/liste?datetime_from=&datetime_to=`
- `GET /filiale/{id}/devices?datetime_from=&datetime_to=`
- `GET /rapport/filter?id_device=&id_type_rapport=&datetime_from=&datetime_to=`
- `GET /cpu/{id}/summary` et `/ram/{id}/summary` (bornes optionnelles)

## 5. ⚠️ Views à créer — À exécuter manuellement par l'utilisateur

> **À exécuter dans `code/bdd/views.sql` puis sur la base PostgreSQL.**
> Sans cette VIEW, `/imprimante/liste` échoue.

```sql
-- ------------------------------------------------------------
-- v_imprimantes_filtrees
-- But : exposer les imprimantes avec leur dernière date de
--       détection, pour les filtres date + heure backend.
-- Colonnes : id, vid, pid, vendor, nom, derniere_detection
-- Utilisée par : AJUSTEMENT 12 (filtres date + heure)
-- À exécuter dans code/bdd/views.sql puis sur la base.
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_imprimantes_filtrees AS
SELECT
    i.id,
    i.vid,
    i.pid,
    i.vendor,
    i.nom,
    MAX(idv.date) AS derniere_detection
FROM t_imprimante i
LEFT JOIN t_imprimante_device idv ON idv.id_imprimante = i.id
GROUP BY i.id, i.vid, i.pid, i.vendor, i.nom;
```

Rappel : `v_appareils_filtres` et `v_evenements_avec_appareil`
(AJUSTEMENT 3) restent également à créer.

## 6. Spécifications

- `DateHeureFilter` : **2 champs `datetime-local`** (début / fin).
  Le calendrier natif du navigateur permet de choisir la **date ET
  l'heure dans le même contrôle** (plus de champs heure séparés).
  Validation date/heure, boutons Filtrer / Réinitialiser.
  Valeurs par défaut : `00:00` (début) et `23:59` (fin) lorsqu'elles
  sont connues.
- Le frontend envoie `datetime_from`/`datetime_to` au format ISO.
- Le backend valide les bornes via FastAPI (`datetime`), sans SQL dans
  les services.
- Les filtres se cumulent côté SQL (statut + type + recherche + dates).
- Les exports PDF/Excel conservent leurs options `date_debut`/`date_fin`
  (non exposées comme filtres de liste dans l'UI).

## 7. Critères d'acceptation

- [x] Composant date + heure unifié
- [x] Bornes ISO envoyées par le frontend
- [x] Devices, événements, imprimantes, devices de filiale, rapports
- [x] VIEW `v_imprimantes_filtrees` rédigée et livrée
- [x] Aucun `CREATE VIEW` exécuté par l'agent
- [x] Build frontend OK

## 8. Tests réalisés (vérifications BDD §2.7, lecture seule)

Bodies des VIEWS exécutés **sans CREATE VIEW** :

| Test | Résultat |
|---|---|
| `v_imprimantes_filtrees` (SELECT seul) | 15 lignes |
| Devices créés entre 2025-08-01 et 2025-12-31 | 525 |
| Devices créés après 2030 | 0 |
| Imprimantes détectées en 2026 | 15 |
| Imprimantes détectées avant 2020 | 0 |
| Rapports CPU device 363 le 2026-10-19 (00:00→23:59:59) | 26 lignes |
| Build frontend | OK |

`py_compile` OK sur les 13 fichiers backend modifiés.

## 9. Risques / régressions

- **Bloquant tant que `v_imprimantes_filtrees` n'est pas créée** :
  `/imprimante/liste` échoue (500).
- `/rapport/filter` n'accepte plus `date_debut`/`date_fin` : le
  frontend a été mis à jour en conséquence.
- Les alertes n'ont pas d'endpoint de liste existant (`t_alerte` vide,
  pas de contrôleur) : rien à filtrer pour l'instant.
- Le dashboard (`/dashboard/summary`) reste un instantané global sans
  filtre de date, conformément à son contrat défini en AJUSTEMENT 8.
- `DateFilter` supprimé après vérification qu'aucun fichier ne
  l'importait plus.

## 10. Respect §2.4

Ajouts sous forme de fonctions plates (`_build_*_filter_clause`,
`get_rapport_by_device_type_and_datetime`,
`filterRapportDeviceByDatetime`), sans fonction imbriquée ni closure.

## 11. C5 — Vérification / unification du composant (POST_AJUSTEMENT)

### Diagnostic

Recherche dans `src/` : `type="date"`, `DatePicker`, `DateRange`,
`Calendar`, `DateFilter`, `DateHeureFilter`.

| Composant | Statut | Utilisé par |
|---|---|---|
| `page/component/DateHeureFilter.jsx` | **existant, conservé** | `event/liste`, `device/liste`, `imprimante/liste`, `device/detail_device`, `cpu_tab`, `ram_tab` |
| `page/component/dateFilter.jsx` | supprimé (AJUSTEMENT 12) | aucun |

Aucun autre `type="date"` ou `type="time"` dans le code hors
`DateHeureFilter`. Il n'y a donc **aucun doublon** à unifier.
Décision : **étendre/réutiliser** `DateHeureFilter` partout (déjà fait),
pas de nouveau composant.

**Évolution demandée** : le composant n'affiche plus 4 champs séparés
(date début, heure début, date fin, heure fin) mais **2 champs
`datetime-local`**. En cliquant sur le calendrier, l'utilisateur choisit
la date puis l'heure dans le même sélecteur natif.

### Backend — validation des bornes

Nouveau helper plat `backend/utils/validation.py` :
`is_valid_datetime_range(datetime_from, datetime_to)`.

Appliqué dans les controllers :
- `/device/liste`
- `/evenement/liste`
- `/imprimante/liste`
- `/filiale/{id}/devices`
- `/rapport/filter`

Si `datetime_to < datetime_from` → **HTTP 400**
(`datetime_to doit être supérieur ou égal à datetime_from`).

### Tests (lecture seule)

| Test | Résultat |
|---|---|
| `is_valid_datetime_range(08:30, 17:45)` | `True` |
| `is_valid_datetime_range(17:45, 08:30)` | `False` |
| Bornes absentes | `True` |
| Événements 2026-10-19 08:30 → 17:45 | 133 lignes |
| Relevés CPU 363 08:30 → 17:45 | 7 lignes |
| Build frontend | OK |

> L'exemple littéral `10/01/2024 08:30 → 17:45` est correctement traité
> par le composant et le backend ; cette date ne contient simplement
> aucune donnée dans la base actuelle (les relevés commencent en 2026).

## 12. C5 corrigé — filtre date+heure retiré de liste_device (retour utilisateur)

- `page/device/liste.jsx` : le `DateHeureFilter` est **supprimé**, ainsi
  que les états/fonctions date et les query params `datetime_from/to`.
  Les devices ne se filtrent pas par date.
- Le filtre date + heure reste UNIQUEMENT dans : détail device (CPU/RAM),
  page événements, statistiques/alertes si applicables.
- Backend `/device/liste` : les params optionnels `datetime_from/to`
  sont conservés (compatibilité) mais plus envoyés par la page liste.
