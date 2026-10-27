# AJUSTEMENT 6 — CPU/RAM directs depuis `t_device_cpu` / `t_device_ram`

## 1. Contexte

Guide agent, §3 AJUSTEMENT 6. Objectif : lire les valeurs CPU/RAM
**directement en base via le backend**, sans recalcul côté React.
Les endpoints renvoient le dernier relevé stocké.

## 2. Fichiers existants vérifiés

- [x] `code/bdd/create/versionFinal.sql` —
      `t_device_cpu` (`id_device`, `id_cpu`, `cpu_utiliser` NUMERIC(5,2),
      `cpu_libre`, `cpu_total`, `date`) et
      `t_device_ram` (`id_device`, `ram_total`, `ram_utiliser`,
      `ram_libre`, `date`)
- [x] `repository/cpu/device_cpu.py` — seulement `insert_cpu_device`
- [x] `repository/ram/ram.py` — `insert_into_device_ram`,
      `get_max_total_ram` (AJUSTEMENT 2)
- [x] `service/ram_service.py` — `get_max_total_ram`
- [x] `controller/ram_controller.py` — `GET /ram/{device_id}/max-total`
- [x] Frontend : `cpu_tab.jsx`, `ram_tab.jsx`, `general_tab.jsx`
      (valeurs dérivées des rapports JSONB via `extractCpuSummary` /
      `extractRamSummary`)

## 3. Décision : fichiers/fonctions identifiés

- Ajout de `get_latest_by_device` dans les repositories CPU et RAM
  (jointure `t_cpu` pour le modèle).
- Nouveau service `cpu_service.py`, extension de `ram_service.py`.
- Nouveaux endpoints sous des routers dédiés (`/cpu`, `/ram`).
- Le frontend privilégie la valeur `latest` backend ; l'historique et
  les températures (absentes des tables) restent issus des rapports.

## 4. Fichiers créés / modifiés

| Ordre | Fichier | Nature |
|---|---|---|
| 1 | `repository/cpu/device_cpu.py` | `get_latest_by_device` |
| 1 | `repository/ram/ram.py` | `get_latest_by_device` |
| 1 | `repository/cpu/__init__.py`, `repository/ram/__init__.py` | exports |
| 2 | `service/cpu_service.py` | créé : `get_latest_cpu` |
| 2 | `service/ram_service.py` | `get_latest_ram` |
| 3 | `controller/cpu_controller.py` | créé : `GET /cpu/{device_id}/latest` |
| 3 | `controller/ram_controller.py` | `GET /ram/{device_id}/latest` |
| 3 | `main.py` | router `cpu` enregistré |
| 4 | `fonction/deviceFonction.js` | `getCpuLatest`, `getRamLatest` |
| 4 | `page/device/detail/cpu_tab.jsx` | utilisation backend |
| 4 | `page/device/detail/ram_tab.jsx` | utilisation backend |
| 4 | `page/device/detail/general_tab.jsx` | cartes CPU/RAM backend |

Endpoints (équivalents réels de `/api/devices/{id}/cpu|ram/latest`,
le projet n'utilisant pas de préfixe `/api`) :
- `GET /cpu/{device_id}/latest` → `{ device_id, latest: { cpu_model,
  freq_max_proc, cpu_architecture, cpu_utiliser, cpu_libre, cpu_total,
  date } }`
- `GET /ram/{device_id}/latest` → `{ device_id, latest: { ram_total,
  ram_utiliser, ram_libre, date } }`

## 5. ⚠️ Views à créer — À exécuter manuellement par l'utilisateur

**Aucune nouvelle VIEW.** Ces lectures sont des `SELECT ... ORDER BY
date DESC LIMIT 1` sur une seule table (+ `t_cpu`), sans filtre
multiple. Rappel : les VIEWS de l'AJUSTEMENT 3 restent à créer.

## 6. Spécifications

- Repository : `ORDER BY date DESC, id DESC LIMIT 1`, aucun SQL ailleurs.
- Service : conversion des `NUMERIC` (`Decimal`) en `float` et des
  dates en ISO 8601, délégation uniquement.
- Controller : valide `device_id`, renvoie `latest = null` si aucun
  relevé (pas de 404 pour un device sans télémétrie).
- Frontend : `latest.cpu_utiliser` / `latest.ram_libre` remplacent les
  valeurs dérivées des rapports ; `extractCpuSummary` /
  `extractRamSummary` ne servent plus qu'à l'historique et aux
  températures.
- Aucun calcul lourd côté React (le pourcentage CPU vient déjà de la DB).

## 7. Critères d'acceptation

- [x] `get_latest_by_device` CPU et RAM
- [x] Délégation services
- [x] `GET /cpu/{id}/latest` et `GET /ram/{id}/latest`
- [x] Frontend branché, valeurs CPU/RAM issues de la DB
- [x] Build frontend OK

## 8. Tests réalisés (vérifications BDD §2.7, lecture seule)

| Vérification | Résultat |
|---|---|
| `COUNT(*)` / devices sur `t_device_cpu` | 22 642 lignes / 464 devices |
| Dernier relevé CPU (device 363) | i3-1315U, `cpu_utiliser=2.00`, `100`, date 2026-10-19 13:38 |
| Dernier relevé RAM (device 363) | total 8 Go, utilisé 2,44 Go, libre 6,14 Go |
| Device inexistant | `None` pour CPU et RAM |
| Routes OpenAPI | `/cpu/{device_id}/latest`, `/ram/{device_id}/latest`, `/ram/{device_id}/max-total` |
| Build frontend | OK |

`py_compile` OK sur les 9 fichiers backend modifiés/créés.

## 9. Risques / régressions

- Si un device n'a jamais remonté de télémétrie, `latest` vaut `null` et
  le frontend retombe sur les rapports JSONB existants.
- Les températures CPU ne sont pas dans `t_device_cpu` : elles restent
  lues dans les rapports, ce qui est hors périmètre de cet ajustement.
- Aucun endpoint existant modifié/supprimé.

## 10. Respect §2.4

Fonctions module-level uniquement ; le service CPU ajoute un
sérialiseur plat `_serialize_latest_cpu`, sans fonction imbriquée ni
closure.
