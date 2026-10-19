# AJUSTEMENT 2 — Graph RAM frontend : max total

## 1. Contexte

Guide agent, §3 AJUSTEMENT 2. L'onglet RAM affichait une valeur totale
issue d'un seul rapport (`totalRamBytes` du premier relevé), donc
partielle ou incohérente. Objectif : afficher le **max total agrégé**,
calculé par le backend sur `t_device_ram`.

## 2. Fichiers existants vérifiés

- [x] `code/bdd/create/versionFinal.sql` — `t_device_ram`
      (`id_device`, `ram_total`, `ram_utiliser`, `ram_libre`, `date`)
- [x] `repository/ram/ram.py` — seul `insert_into_device_ram` existait
- [x] `service/rapport_service.py` — `getRamRaport` (JSONB `MEMORY_STATUS`)
- [x] `controller/rapport_controller.py` — `GET /rapport/ram/{id}` existant
- [x] `frontend/src/page/device/detail/ram_tab.jsx` — composant React
      identifié (onglet « Mémoire RAM »)
- [x] `frontend/src/fonction/deviceFonction.js` — `getDetailRam`,
      `extractRamSummary`
- [x] Aucun `ram_controller.py` ni `ram_service.py` n'existait

## 3. Décision : fichier/fonction identifiés

- Le composant est `RamTab` (`ram_tab.jsx`), branché sur
  `GET /rapport/ram/{id}`.
- Le calcul `MAX(ram_total)` doit se faire en SQL, pas dans React.
- Nouveau module backend dédié RAM, sans toucher à l'endpoint JSONB
  existant (aucune régression).

## 4. Fichiers créés / modifiés

| Ordre | Fichier | Nature |
|---|---|---|
| 1 | `repository/ram/ram.py` | modifié : `get_max_total_ram` |
| 1 | `repository/ram/__init__.py` | créé (exports) |
| 2 | `service/ram_service.py` | créé : `get_max_total_ram` |
| 3 | `controller/ram_controller.py` | créé : `GET /ram/{device_id}/max-total` |
| 3 | `main.py` | modifié : router `ram` enregistré |
| 4 | `frontend/src/fonction/deviceFonction.js` | modifié : `getRamMaxTotal` |
| 4 | `frontend/src/page/device/detail/ram_tab.jsx` | modifié : consommation de l'endpoint |

Endpoint exposé : `GET /ram/{device_id}/max-total[?datetime_from=&datetime_to=]`
→ `{ "device_id": 363, "max_total": 8589934592 }`.

> Le guide écrit `/api/ram/...` ; ce projet n'utilise aucun préfixe `/api`
> (tous les routers sont montés à la racine, ex. `/rapport`, `/device`).
> L'équivalent réel est donc `/ram/...`.

## 5. ⚠️ Views à créer — À exécuter manuellement par l'utilisateur

**Aucune VIEW nécessaire.** La requête est une agrégation simple sur une
seule table (`SELECT MAX(ram_total) FROM t_device_ram WHERE id_device = %s`).

## 6. Spécifications

- Source de vérité : `t_device_ram` dans `versionFinal.sql`.
- `get_max_total_ram(cur, id_device, datetime_from=None, datetime_to=None)` :
  `MAX(ram_total)` avec bornes `date >=` / `date <=` optionnelles.
- Le service délègue, le controller valide le HTTP et retourne le schéma.
- Frontend : un seul appel à l'endpoint au montage / changement de device,
  `maxTotal` remplace la valeur partielle issue du premier rapport.
  Aucun calcul lourd côté React (le maximum est déjà agrégé en SQL).

## 7. Critères d'acceptation

- [x] `get_max_total_ram` dans le repository RAM
- [x] Délégation dans le service (pas de SQL)
- [x] `GET /ram/{device_id}/max-total` opérationnel
- [x] Frontend branché sur l'endpoint, pas de calcul lourd
- [x] Valeur totale prioritaire = max agrégé backend

## 8. Tests réalisés (vérifications BDD §2.7, lecture seule)

| Vérification | Résultat |
|---|---|
| `COUNT(*)`, `COUNT(DISTINCT id_device)` sur `t_device_ram` | 2120 lignes, 465 devices |
| `MIN/MAX(ram_total)` | 8 589 934 592 / 17 179 869 184 |
| Colonnes réelles | `id_device, ram_total, ram_utiliser, ram_libre, date` |

Appels réels au service (lecture seule) :
- device 363 → `8589934592` (8 Go) ;
- device inexistant → `None` ;
- avec bornes `datetime_from` / `datetime_to` → `8589934592`.

`py_compile` OK sur les 5 fichiers backend modifiés/créés.

## 9. Risques / régressions

- L'endpoint `/rapport/ram/{id}` (JSONB) n'est pas modifié.
- Un device sans relevé RAM renvoie `{ "max_total": null }` : le frontend
  retombe sur `summary.total` puis `device.ram_total`.
- Le maximum peut masquer une valeur aberrante haute ; c'est le
  comportement explicitement demandé (max total agrégé).

## 10. Respect §2.4

Aucune fonction imbriquée côté Python, fonctions module-level courtes,
service sans SQL, controller sans logique métier.
