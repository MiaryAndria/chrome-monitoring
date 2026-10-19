# AJUSTEMENT 10 — Durée de vie avant extinction

## 1. Contexte

Guide agent, §3 AJUSTEMENT 10. Question métier obligatoire posée avant
codage :

> « Durée de vie avant extinction = (a) batterie restante,
> (b) fin de support AUE, (c) temps depuis dernier événement ? »

**Réponse utilisateur : batterie restante ET temps depuis le dernier
événement.**

## 2. Fichiers existants vérifiés

- [x] `code/bdd/create/versionFinal.sql` — aucune table batterie dédiée ;
      la batterie est dans `t_rapport_device` (JSONB, type
      `BATTERY_STATUS`) ; les événements sont dans `t_evenement_device`
- [x] `repository/rapport/rapport_device.py` — pas de lecture
      « dernière batterie »
- [x] `repository/evenement/evenement_device.py` — pas de
      `get_last_event_date`
- [x] `service/import_service.py` — la synchro alimente bien
      `t_rapport_device` (BATTERY_STATUS) et `t_evenement_device`
- [x] `frontend/src/page/device/detail/general_tab.jsx` — page détail
      device (point d'affichage retenu)
- [x] L'AUE n'est stockée ni en base ni récupérée par `google_api/devices.py`
      (option (b) écartée, info manquante)

## 3. Décision : fichiers/fonctions identifiés

- Métrique 1 (batterie) : dernier rapport `BATTERY_STATUS`, échantillon
  `Discharging` le plus récent → `minutes_restantes =
  remainingCapacity / current × 60`.
- Métrique 2 (dernier événement) : `MAX(date_evenement)` par device →
  secondes écoulées.
- Aucun stockage supplémentaire : calcul à la volée dans le service à
  partir des données déjà persistées.

## 4. Fichiers créés / modifiés

| Ordre | Fichier | Nature |
|---|---|---|
| 1 | `repository/rapport/rapport_device.py` | `get_latest_battery_by_device` |
| 1 | `repository/rapport/__init__.py` | export |
| 1 | `repository/evenement/evenement_device.py` | `get_last_event_date` |
| 1 | `repository/evenement/__init__.py` | export |
| 2 | `service/life_service.py` | créé : calcul module-level |
| 3 | `controller/life_controller.py` | créé : `GET /life/{device_id}` |
| 3 | `main.py` | router `life` enregistré |
| 4 | `fonction/deviceFonction.js` | `getLifeRemaining` |
| 4 | `fonction/utils/util.js` | `formatDuration` |
| 4 | `page/device/detail/general_tab.jsx` | panneau « Durée de vie avant extinction » |

Endpoint : `GET /life/{device_id}` →
```json
{
  "device_id": 496,
  "batterie": {
    "etat": "Charging",
    "charge_rate": 100,
    "battery_health": "BATTERY_HEALTH_NORMAL",
    "cycle_count": 2,
    "minutes_restantes": 123.4,
    "estimation_batterie": { "minutes_restantes": 123.4, "charge_rate": 54.0, "report_time": "..." },
    "report_time": "..."
  },
  "dernier_evenement": "2026-10-19T10:38:12+00:00",
  "secondes_depuis_dernier_evenement": 2309
}
```

## 5. ⚠️ Views à créer — À exécuter manuellement par l'utilisateur

**Aucune nouvelle VIEW.** Rappel : les VIEWS des AJUSTEMENTS 3 et 8
restent à créer.

## 6. Spécifications

- `compute_battery_remaining(donnees)` (fonction plate) :
  - état = statut du sample le plus récent ;
  - `charge_rate`, `battery_health`, `cycle_count` ;
  - estimation = premier sample `Discharging` avec `current > 0` et
    `remainingCapacity` renseignés ; sinon `null` (ex. appareil en
    charge sans historique de décharge).
- `get_life_remaining(id_device)` :
  - lecture du dernier rapport batterie et du dernier événement ;
  - conversion UTC, calcul des secondes écoulées ;
  - retourne `batterie = null` pour les Chromebox / devices sans rapport.
- Frontend : panneau dans la page détail device affichant l'état, la
  charge, l'autonomie estimée, la santé, les cycles, et le temps écoulé
  depuis le dernier événement (`formatDuration`).

## 7. Critères d'acceptation

- [x] Question métier posée et réponse prise en compte (a + c)
- [x] Calcul batterie dans une fonction dédiée du service
- [x] Calcul « dernier événement » dans le service
- [x] Endpoint backend
- [x] Affichage page détail device
- [x] Aucun SQL hors repository
- [x] Build frontend OK

## 8. Tests réalisés (vérifications BDD §2.7, lecture seule)

| Vérification | Résultat |
|---|---|
| Devices avec rapport `BATTERY_STATUS` | 33 |
| Devices avec au moins un événement | 339 |
| Device 496 (en charge) | charge 100 %, santé NORMAL, 2 cycles, estimation 123,4 min (décharge 2720 mAh / 1322 mA) |
| Device 163 (toujours en charge) | estimation `null` (aucun sample Discharging) |
| Device 363 (Chromebox) | `batterie = null`, dernier événement il y a 2 309 s |
| Route OpenAPI | `/life/{device_id}` |
| Build frontend | OK |

`py_compile` OK sur les 7 fichiers backend modifiés/créés.

## 9. Risques / régressions

- L'estimation d'autonomie est approximative (basée sur le dernier
  échantillon de décharge, pas sur une consommation future).
- Un appareil en charge n'a pas d'estimation s'il n'a jamais été
  observé en décharge.
- 33 devices seulement ont un rapport batterie (les Chromebox n'en ont
  pas) : l'UI affiche « Aucune donnée batterie ».
- Aucune colonne ajoutée, aucune migration ; l'option AUE n'est pas
  implémentée (donnée non disponible).

## 10. Respect §2.4

`_to_float`, `_find_discharging_sample`, `compute_battery_remaining`,
`_to_utc` et `get_life_remaining` sont des fonctions plates au niveau
module ; une seule boucle par fonction, aucune fonction imbriquée.

## 11. C3 — Déplacement vers la page événements (POST_AJUSTEMENT)

### Changement

- La durée de vie n'est **plus affichée dans le détail device**.
- Elle est fusionnée dans le domaine **événement** (C7) et affichée
  dans un accordéon de la page événements.

### Backend

- `life_service.py` et `life_controller.py` **supprimés**.
- Logique déplacée dans `service/event_service.py` :
  `_to_float`, `_find_discharging_sample`, `compute_battery_remaining`,
  `_to_utc`, `_build_duree_vie`, `get_duree_vie_evenement`.
- `repository/evenement/__init__.py` exporte `get_evenement_by_id`.
- Le router `life` est retiré de `main.py`.
- Nouvel endpoint :
  `GET /evenement/{event_id}/duree-vie` →
  ```json
  {
    "duree_vie": 671.8,
    "unite": "minutes",
    "details": {
      "batterie": { "etat": "Discharging", "charge_rate": 66, "cycle_count": 116, "minutes_restantes": 671.8 },
      "dernier_evenement": "2026-10-19T08:01:26+00:00",
      "secondes_depuis_dernier_evenement": 15561
    }
  }
  ```
  `404` si l'événement n'existe pas.
- Métrique : décision utilisateur maintenue = **batterie restante +
  temps depuis le dernier événement** (l'AUE n'est pas stockée).

### Frontend

- `general_tab.jsx` : panneau « Durée de vie » et appel
  `getLifeRemaining` supprimés.
- `fonction/eventFonction.js` : `getDureeVieEvenement(eventId)`.
- `page/component/EvenementDureeVie.jsx` : composant dédié
  (fetch + skeleton + affichage autonomie / dernier événement).
- `component_event.jsx` : l'accordéon « Voir diagnostic » affiche la
  durée de vie ; l'état ouvert est contrôlé par le parent pour qu'une
  seule carte soit ouverte.
- `page/event/liste.jsx` : vue grille (accordéon) + vue tableau
  (bouton « Voir » et panneau sous le tableau), une seule ligne ouverte.
- `Skeleton` au dépliage.

### Tests

| Vérification | Résultat |
|---|---|
| Événement d'un Chromebox (15809) | `duree_vie=null`, dernier événement il y a 4 222 s |
| Événement d'un device avec batterie (14179) | `duree_vie=671.8` min, charge 66 %, 116 cycles |
| Événement inexistant | `None` → 404 |
| Routes | `/evenement/{event_id}/duree-vie` présente, plus aucune `/life` |
| Build frontend | OK |

### Risques

- Pour les événements de devices sans rapport batterie (Chromebox),
  `duree_vie` vaut `null` ; l'UI affiche « Non estimable ».
- Le détail device ne montre plus l'autonomie : elle est accessible via
  la page événements.
