# AJUSTEMENT 13 — Import Google, auto-synchronisation et stockage des données

Ce document explique **comment les données sont importées depuis Google**, comment
fonctionne **l'auto-synchronisation**, et **comment Google stocke (ou non) les
rapports**, pour comprendre pourquoi certaines données (RAM) sont irrécupérables
alors que d'autres (CPU) le sont.

---

## 1. Vue d'ensemble du flux d'import

```
worker.py
  └─ demarrer_auto_synchronisation()          (backend/google_api/auto_synch.py)
        └─ boucle toutes les 2 min : executer_synchronisation()
              ├─ calcule la fenêtre [fenetre_debut, fenetre_fin]
              ├─ enregistre la synchro (t_synchronisation_historique + statuts)
              └─ synchroniser_tout(fenetre_debut, fenetre_fin, suivi)
                    (backend/fonction/metier/service/import_service.py)
                    ├─ get_credential()
                    ├─ _recuperer_donnees_google(credential, debut, etapes)   → 3 appels en parallèle
                    │     ├─ get_devices(credential)                 → liste des appareils
                    │     ├─ get_telemetry_devices(credential, debut) → télémétrie (CPU, RAM, disque…)
                    │     └─ fetch_crash_sources(credential, debut)   → crashs / événements
                    ├─ build_crash_incidents(...)                     → enrichissement des crashs
                    └─ _importer_en_bdd(cur, …, filtre_debut, etapes)
                          ├─ insertion_device(...)      → t_device, filiale, réseau, statut, utilisateurs
                          ├─ insert_telemetry(...)      → t_device_cpu, t_device_ram, t_disk_device, t_rapport_device
                          ├─ insert_imprimante(...)     → t_imprimante_device, t_imprimante_user
                          └─ insert_event(...)          → t_evenement_device
                    └─ commit + invalidation du cache
```

Fichiers clés :
- `backend/worker.py` : lance le thread d'auto-synchro.
- `backend/google_api/auto_synch.py` : boucle, verrou, calcul de la fenêtre.
- `backend/google_api/devices.py` : appels API Google (`get_devices`, `get_telemetry_devices`).
- `backend/fonction/metier/service/import_service.py` : orchestration + insertion en base.

---

## 2. `auto_synch.py` — l'auto-synchronisation

### 2.1 Constantes

| Constante | Valeur | Rôle |
|---|---|---|
| `INTERVALLE_SECONDE` | `2 * 60` (2 min) | délai entre deux tentatives de synchro |
| `MARGE_1h` | 1 h | recouvrement si une synchro a déjà été faite **le même jour** |
| `MARGE_72h` | 72 h | recouvrement si la dernière synchro date d'un **autre jour** |
| `PREMIERE_SYNCHRO` | 90 jours | fenêtre initiale quand aucune synchro n'existe |
| `TZ_LOCAL` | UTC+3 | fuseau utilisé pour « déjà fait aujourd'hui » |

### 2.2 Verrou

`_verrou = threading.Lock()` : `executer_synchronisation()` fait
`if not _verrou.acquire(blocking=False): return False`. **Une seule synchro à la
fois** ; si deux workers tournent, le second est ignoré tant que le premier tient
le verrou.

### 2.3 Calcul de la fenêtre

```python
dernier = get_derniere_fenetre_fin_by_source(cur, "google")
# = MAX(fenetre_fin) des synchros ayant le statut TERMINER

if dernier is None:
    fenetre_debut = lancement - PREMIERE_SYNCHRO      # 90 jours
else:
    deja_fait_aujourdhui = dernier.date(TZ_LOCAL) == lancement.date(TZ_LOCAL)
    marge = MARGE_1h if deja_fait_aujourdhui else MARGE_72h
    fenetre_debut = dernier - marge

fenetre_fin = lancement
```

Conséquences :
- Une synchro **continue le même jour** → fenêtre de **1 h** seulement.
- Première synchro d'un **nouveau jour** → fenêtre de **72 h** avant la dernière
  synchro.
- `fenetre_fin` = maintenant.

La fenêtre sert **deux fois** :
1. au niveau de l'API : `get_telemetry_devices(credential, debut)` envoie
   `filter='reports_timestamp>="<fenetre_debut>"'` ;
2. au niveau de l'insertion : `insert_telemetry` ignore tout relevé dont
   `reportTime < fenetre_debut`.

> ⚠️ La fenêtre ne peut **pas** « remonter dans le temps » au-delà de
> `dernier − marge`. En synchro continue (1 h), une donnée d'il y a 2 jours est
> donc exclue côté requête **et** côté insertion.

### 2.4 Enregistrement de la synchro

Pour chaque exécution, une ligne est ajoutée dans `t_synchronisation_historique`
(`source`, `date_debut`, `fenetre_debut`, `fenetre_fin`) et des statuts sont
posés dans `t_statut_synchronisation` : `COMMENCER` → `EN_COURS` → `TERMINER`
(ou `ECHEC`), avec `nb_lignes` et `message`.

---

## 3. `import_service.py` — l'import et l'insertion

### 3.1 Récupération (parallèle)

`_recuperer_donnees_google(credential, debut, etapes)` lance 3 tâches en
`ThreadPoolExecutor` :
- `get_devices(credential)` : liste des appareils (Admin SDK).
- `get_telemetry_devices(credential, debut)` : télémétrie ChromeOS.
- `fetch_crash_sources(credential, debut)` : sources de crashs.

### 3.2 Insertion

`_importer_en_bdd(cur, dvc_list, telemetry_devices_list, crashes_data, filtre_debut, etapes)` :

| Étape | Fonction | Tables alimentées |
|---|---|---|
| appareils | `insertion_device` | `t_device`, `t_filiale`, `t_device_filiale`, `t_reseau`, `t_reseau_filiale`, `t_device_reseau`, `t_statut`, `t_device_statut`, `t_utilisateur`, `t_device_utilisateur`, `t_device_utilisateur_recent`, `t_filiale_utilisateur` |
| télémétrie | `insert_telemetry` | `t_device_cpu`, `t_device_ram`, `t_disk`, `t_disk_device`, `t_cpu`, `t_rapport_device` |
| imprimantes | `insert_imprimante` | `t_imprimante`, `t_imprimante_device`, `t_imprimante_user` |
| événements | `insert_event` | `t_evenement_device`, `t_type_evenement` |

Puis `connexion.commit()` et invalidation des caches de listes :
`devices:`, `events:`, `imprimantes:`, `filiales:`.

### 3.3 `insert_telemetry` en détail

1. `init_default_types_rapport` + `get_liste_type_rapport` → 13 types
   (`CPU_STATUS`, `MEMORY_STATUS`, `STORAGE_STATUS`, …) avec leur clé API
   (`cpuStatusReport`, `memoryStatusReport`, …).
2. Pour chaque appareil de télémétrie, pour chaque type, pour chaque relevé :
   - `date_releve = reportTime`
   - **filtre** : `if debut is not None and date_releve < debut: continue`
   - `MEMORY_STATUS` → `t_device_ram` (`ram_total`, `ram_utiliser`, `ram_libre`)
   - `CPU_STATUS` → `t_device_cpu` (`cpu_utiliser`, `cpu_libre`, `cpu_total`)
   - `STORAGE_STATUS` → `t_disk_device`
   - **toujours** → une ligne brute dans `t_rapport_device`
     (`id_device`, `id_type_rapport`, `report_time`, `donnees` JSONB).

---

## 4. `get_telemetry_devices` — l'appel API et son filtre

```python
def get_telemetry_devices(credentials, debut=None):
    service.customers().telemetry().devices().list(
        parent="customers/my_customer",
        filter=(
            f'reports_timestamp>="{debut.isoformat()}"'
            if debut is not None else "reports_timestamp>=0"
        ),
        readMask="name,customer,orgUnitId,deviceId,serialNumber,cpuInfo,cpuStatusReport,"
                 "memoryInfo,memoryStatusReport,...",
        pageSize=1000,
        pageToken=page_token,
    ).execute()
```

D'après la documentation Google :

> **`filter`** — « Requests that don't specify a `reports_timestamp` value will
> default to returning only **recent reports**. Specify `"reports_timestamp>=0"`
> to get **all report data**. »

Donc :
- avant le correctif (pas de `filter`) → l'API ne renvoyait que les
  **rapports récents** ;
- avec `filter='reports_timestamp>="<fenetre_debut>"'` → on demande **tout ce que
  Google conserve** depuis la borne.

⚠️ Ce filtre sélectionne les **appareils** ayant des rapports après la borne,
mais **ce que Google renvoie par type de rapport reste limité par ce qu'il
conserve** (voir §5).

---

## 5. Comment Google stocke les rapports (et pourquoi tout n'est pas récupérable)

### 5.1 Ce qui est documenté (par type de rapport)

| Rapport | Fréquence de collecte | Remontée par défaut | Cache si hors-ligne |
|---|---|---|---|
| `cpuStatusReport` | toutes les **10 min** | toutes les 3 h | **Non** |
| `memoryStatusReport` | **uniquement à l'upload** (`systemRamFreeBytes` toutes les 10 min) | toutes les 3 h | **Non** |
| `storageStatusReport` | uniquement à l'upload | toutes les 3 h | **Non** |
| `networkStatusReport` | 60 min | 3 h | Oui |
| `osUpdateStatus` | uniquement à l'upload | 3 h | Non |
| `heartbeatStatusReport` | 2 min | 2 min | N/A |

Points importants :
- Il n'y a **pas de cache hors-ligne** pour CPU / mémoire / stockage : un appareil
  hors-ligne ne « rattrape » pas ses rapports manqués.
- Google **ne publie pas** de durée de rétention serveur explicite.

### 5.2 Ce qu'on observe réellement via l'API

Requête faite avec le filtre le plus large (`reports_timestamp>="2026-10-21"`,
560 appareils), le 23/10 :

| Type | 21/10 | 22/10 | 23/10 |
|---|---|---|---|
| **MEMORY_STATUS** | **10** | **55** | 353 |
| **STORAGE_STATUS** | **10** | **55** | 353 |
| **CPU_STATUS** | 9 192 | 9 587 | 1 103 |

Interprétation :
- `cpuStatusReport[]` renvoie un **historique long** par appareil (des milliers de
  relevés/jour) → le CPU est **rejouable**.
- `memoryStatusReport[]` / `storageStatusReport[]` ne renvoient, par appareil,
  **quasiment que le dernier relevé** :
  - 353 appareils ont leur dernier rapport mémoire sur le 23/10 (en ligne),
  - 55 sur le 22/10 (hors-ligne depuis),
  - 10 sur le 21/10.
  → dès qu'un appareil remonte un nouveau rapport mémoire, l'ancien n'est plus
  exposé par l'API. **L'historique RAM n'est donc pas rejouable.**

> **Même avec `reports_timestamp>=0`** (le filtre le plus large), l'historique
> mémoire/stockage n'est pas récupérable : le filtre élargit la *demande*, mais
> l'API ne renvoie toujours qu'un nombre très limité de rapports mémoire par
> appareil (essentiellement le dernier).

### 5.3 Conséquence pratique : CPU récupérable, RAM non

- **CPU** : long historique → un rattrapage (fenêtre 72 h) récupère les jours
  manqués.
- **RAM / stockage** : seul le dernier point par appareil est disponible → si la
  synchro ne tourne pas au moment de la remontée, **le point est perdu
  définitivement**. Un rattrapage ne le récupère pas.

---

## 6. Exemple concret (incident 21–22/10)

1. Les synchros se sont arrêtées le **21/10 à 11:58** et ont repris le
   **23/10 à 08:24** (aucune synchro le 22/10).
2. Au redémarrage, `dernier` (dernière `fenetre_fin`) n'était pas du jour →
   marge **72 h** → `fenetre_debut = 18/10 11:58`.
3. Résultat en base :
   - CPU : ~6 120 relevés le 22/10 (quasi normal) → **récupéré**.
   - RAM : 87 relevés le 22/10, quasi rien le 21 après-midi → **non récupéré**.
4. Vérification directe de l'API : elle ne renvoie que **55 rapports mémoire**
   pour le 22/10 et **10** pour le 21/10 → la donnée n'est plus disponible côté
   Google, indépendamment du code.

---

## 7. Pourquoi des données ne sont (ou ne seront) pas récupérables

1. **Pas de synchro = pas d'insertion.** L'application ne « lit » pas un
   historique complet : elle capture ce que l'API renvoie à l'instant de la
   synchro.
2. **Fenêtre d'insertion.** `insert_telemetry` ignore `reportTime < fenetre_debut`.
   En synchro continue (1 h), tout relevé plus ancien est écarté.
3. **Disponibilité côté Google.** Pour la mémoire/stockage, l'API n'expose que le
   dernier relevé par appareil → l'historique est perdu dès qu'un nouveau relevé
   arrive.
4. **Pas de cache hors-ligne** (CPU/mémoire/stockage) : un appareil hors-ligne ne
   rattrape pas.
5. **Rétention non publiée** : impossible de garantir un « X jours » ; en pratique
   la RAM doit être captée en quasi temps réel.

---

## 8. Bonnes pratiques / recommandations

- **Garder `backend.worker` en continu** (synchro toutes les 2 min) : c'est la
  seule façon fiable de capter la RAM.
- Pour **plus de points RAM**, augmenter la fréquence de remontée via la policy
  ChromeOS **`ReportDeviceMemoryInfo`** (Admin console), pas via le code.
- Pour un **rattrapage ciblé** (CPU surtout), lancer une synchro avec un `debut`
  explicite, worker arrêté pour éviter les écritures concurrentes :
  ```python
  from backend.google_api.devices import get_credential
  from backend.fonction.metier.service.import_service import synchroniser_tout
  synchroniser_tout(debut=<datetime UTC>, fin=<datetime UTC>)
  ```
  Cela ne récupérera la RAM que si Google l'expose encore.
- Éviter deux workers simultanés (le verrou `_verrou` ignore la seconde synchro,
  mais deux processus = deux caches et deux boucles).

---

## 9. Rappel cache (lié aux listes)

Le cache serveur (`backend/core/cache.py`, TTL 60 s) est invalidé après le
`commit` de la synchro pour : `devices:`, `events:`, `imprimantes:`, `filiales:`.
Les caches `configurations:` / `configurations:archive:` sont invalidés lors des
opérations CRUD de configuration.

Le cache **ne concerne que les listes paginées**, jamais les relevés CPU/RAM/
disque, ni les sommes date+heure, ni les détails d'appareil.

---

## 10. Fichiers concernés

| Fichier | Rôle |
|---|---|
| `backend/worker.py` | lance le thread d'auto-synchro |
| `backend/google_api/auto_synch.py` | boucle, verrou, fenêtre, statuts |
| `backend/google_api/devices.py` | `get_devices`, `get_telemetry_devices` (filtre `reports_timestamp`) |
| `backend/fonction/metier/service/import_service.py` | `synchroniser_tout`, `insertion_device`, `insert_telemetry`, `insert_imprimante`, `insert_event` |
| `backend/fonction/metier/repository/synchronisation/` | historique + statuts de synchro |
| `backend/core/cache.py` | cache mémoire TTL + invalidation |

---

## 11. Sources (documentation Google)

- [Chrome Management Telemetry API](https://developers.google.com/chrome/management/guides/telemetry_api)
- [REST Resource: customers.telemetry.devices](https://developers.google.com/chrome/management/reference/rest/v1/customers.telemetry.devices)
- [Method: customers.telemetry.devices.list](https://developers.google.com/chrome/management/reference/rest/v1/customers.telemetry.devices/list)
- [Use Chrome Management Telemetry API to monitor devices](https://support.google.com/chrome/a/answer/11230542)
