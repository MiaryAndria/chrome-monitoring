# AJUSTEMENT 4 — Caching

## 1. Contexte

Guide agent, §3 AJUSTEMENT 4. Objectif : cache côté service, TTL
configurable via `.env`, invalidation après les écritures (synchro /
upserts). Le cache ne doit jamais vivre dans le repository.

## 2. Fichiers existants vérifiés

- [x] Aucun module de cache existant (`backend/core/` absent)
- [x] `service/device_service.py` — `getDevicesPage`
- [x] `service/event_service.py` — `get_events_page`
- [x] `service/imprimante_service.py` — `get_imprimantes_page`
- [x] `service/import_service.py` — `synchroniser_tout`, point d'écriture
      principal (devices, événements, imprimantes)
- [x] `code/.env` et `code/.env.example`

## 3. Décision : fichier/fonction identifiés

- Le guide indique `app/core/cache.py` ; l'équivalent réel dans ce dépôt
  est `backend/core/cache.py`.
- Seules les **lectures de liste coûteuses** sont mises en cache
  (devices, événements, imprimantes paginés). `getDeviceDetail` et les
  agrégations `MAX` restent non cachés.
- L'invalidation se fait par préfixe (`devices:`, `events:`,
  `imprimantes:`) après le `commit` de la synchronisation.

## 4. Fichiers créés / modifiés

| Ordre | Fichier | Nature |
|---|---|---|
| 1 | `backend/core/cache.py` | créé : cache dict + TTL |
| 1 | `backend/core/__init__.py` | créé (exports) |
| 2 | `service/device_service.py` | `_fetch_devices_page` + cache |
| 2 | `service/event_service.py` | `_fetch_events_page` + cache |
| 2 | `service/imprimante_service.py` | `_fetch_imprimantes_page` + cache |
| 3 | `service/import_service.py` | invalidation après `commit` |
| — | `code/.env`, `code/.env.example` | `CACHE_TTL_SECONDS=60` |

Fonctions module-level du cache :
`cache_get(key)`, `cache_set(key, value, ttl=None)`, `cache_invalidate(key)`,
`cache_invalidate_prefix(prefix)`, `cache_clear()`.

Clés de cache :
- `devices:{page}:{page_size}:{id_filiale}:{filiale}:{statut}:{type_appareil}:{recherche}`
- `events:{page}:{page_size}:{type_evenement}:{id_filiale}:{filiale}:{recherche}:{datetime_from}:{datetime_to}`
- `imprimantes:{page}:{page_size}:{recherche}`

## 5. ⚠️ Views à créer — À exécuter manuellement par l'utilisateur

**Aucune nouvelle VIEW.** Rappel : les VIEWS de l'AJUSTEMENT 3
(`v_appareils_filtres`, `v_evenements_avec_appareil`, voir
`03-filtres-backend-pagination.md`) doivent être créées pour que les
lectures cachées de devices et d'événements fonctionnent.

## 6. Spécifications

- `CACHE_TTL_SECONDS` lu dans `.env` (défaut : 60 s).
- Structure simple : `dict[key] = (value, expiration_timestamp)`,
  sans dépendance externe (conforme au guide : dict + timestamp).
- Le cache est un détail d'implémentation **du service** ; aucun
  repository ne connaît le cache.
- Invalidation : après `connexion.commit()` dans `synchroniser_tout`,
  les préfixes `devices:`, `events:` et `imprimantes:` sont purgés.
- Une entrée expirée est supprimée à la lecture (lazy expiration).

## 7. Critères d'acceptation

- [x] `backend/core/cache.py` avec get/set/invalidate
- [x] TTL configurable via `.env`
- [x] Cache appliqué aux lectures coûteuses (listes paginées)
- [x] Invalidation après synchronisation
- [x] Cache absent des repositories

## 8. Tests réalisés

| Test | Résultat |
|---|---|
| `cache_set` puis `cache_get` | valeur retournée |
| `cache_invalidate` | `None` ensuite |
| `cache_invalidate_prefix("events:")` | clés `events:*` supprimées, `imprimantes:a` conservée |
| TTL 0,05 s après 0,1 s | `None` (expiration OK) |
| `getDevicesPage` avec clé pré-remplie | sert le cache sans toucher la BDD |
| `get_imprimantes_page` appelé 2× | même objet retourné (`is` → `True`), total 15 |

`py_compile` OK sur les 6 fichiers modifiés/créés.

## 9. Risques / régressions

- Données périmées jusqu'à `CACHE_TTL_SECONDS` (60 s par défaut) entre
  deux synchronisations ; acceptable pour un monitoring.
- Le cache est local au processus : uvicorn multi-workers aurait un
  cache par worker (comportement voulu, pas de dépendance externe).
- Aucun changement de signature publique des services.

## 10. Respect §2.4

Aucune fonction imbriquée : chaque service expose une fonction
`_fetch_*` (accès BDD) et une fonction `get*` (cache), toutes au niveau
module. Pas de lambda, pas de closure.

## 11. Règle de cache corrigée (retour utilisateur)

- ✅ Cache UNIQUEMENT : listes paginées (device, événements, imprimantes,
  matériels), données stables (référentiels/labels).
- ❌ Jamais de cache sur : CPU/RAM/Disk/Batterie, sommes date+heure
  (chaque appel peut différer), détail device, événements récents,
  **dashboard summary** (les compteurs évoluent à chaque synchro).

Concrètement :

- `cache.py` reste appliqué uniquement aux lectures de listes paginées ;
  aucun repository n'est caché.
- `dashboard_service.get_summary()` n'utilise plus de cache : il
  recalcule les compteurs à chaque appel.
- Invalidation après `commit` de synchronisation : préfixes `devices:`,
  `events:` et `imprimantes:` purgés → une nouvelle imprimante/device/
  événement est visible dès le prochain appel de liste.
- Frontend : suppression du `sommeCache` (`Map`) dans `cpu_tab.jsx` et
  `ram_tab.jsx` (données changeantes).
- Le hook `usePaginatedData` ne stocke plus les pages déjà vues de façon
  persistante : voir `03-filtres-backend-pagination.md` §C1 corrigé
  (préchargement N+1/N+2 one-shot, pas de cache).
