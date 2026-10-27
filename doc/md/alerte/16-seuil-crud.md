# 16 — CRUD Seuil (create / update / liste / archive)

## Objectif
Créer une gestion complète des **seuils** (entité `t_seuil`), sur le **même modèle que la
Configuration** (`t_configuration`) : mêmes couches, même journalisation par statut, même
pagination + cache backend-side, même structure de pages frontend.

Un `seuil` est une **règle de déclenchement** (`cle` + `valeur` entière), concept distinct
d'une configuration (paramètre applicatif texte). Les deux tables ont donc leur propre CRUD.

## Base de données (déjà en place — aucune modif SQL requise)
- `t_seuil (id, cle UNIQUE NOT NULL, valeur INT NOT NULL)` — **pas** de colonne `date`.
- `t_seuil_statut (id, id_seuil, id_statut, date)` — historique daté des changements.

Statuts utilisés (confirmés sur la BDD) :
`12 = CREER`, `13 = MODIFIER`, `14 = SUPPRIMER` (archive), `16 = RESTAURER`.

La date affichée dans les listes provient du **dernier `t_seuil_statut`** (car `t_seuil` n'a
pas de colonne `date`).

## Fichiers créés / modifiés

### Backend
- `code/backend/fonction/metier/repository/seuil/seuil.py` — requêtes SQL (couche repository uniquement).
- `code/backend/fonction/metier/repository/seuil/__init__.py` — exports explicites (pas de `__all__`).
- `code/backend/fonction/metier/models/seuil.py` — `SeuilData`, `SeuilResponse`, `SeuilPageResponse`.
- `code/backend/fonction/metier/service/seuil_service.py` — orchestration + cache `seuils:`.
- `code/backend/fonction/metier/controller/seuil_controller.py` — routes FastAPI.
- `code/backend/main.py` — router enregistré sous `prefix="/seuil"` (protégé).

### Frontend
- `code/frontend/src/fonction/seuilFonction.js` — appels API.
- `code/frontend/src/page/seuil/create.jsx` — création.
- `code/frontend/src/page/seuil/liste.jsx` — liste (cache + pagination + prefetch).
- `code/frontend/src/page/seuil/update.jsx` — modification.
- `code/frontend/src/page/seuil/archived.jsx` — archive + restauration.
- `code/frontend/src/App.jsx` — 4 routes ajoutées.
- `code/frontend/src/components/Navbar.jsx` — dropdown **Seuil** (liste / créer / archive).

CSS réutilisé : `css/configuration.css` (classes `config-*`), aucune nouvelle feuille.

## Endpoints (`/seuil`, protégés par cookie)
| Méthode | Route | Rôle |
|---|---|---|
| GET | `/seuil/liste` | liste non archivée |
| GET | `/seuil/liste/page` | liste paginée (cache `seuils:{page}:{size}`) |
| POST | `/seuil/create` | création (statut 12) |
| GET | `/seuil/{id}` | détail |
| PUT | `/seuil/{id}/update` | modification (statut 13) |
| POST | `/seuil/{id}/delete` | archivage (statut 14) |
| GET | `/seuil/liste/archiver` | liste archivée |
| GET | `/seuil/liste/archiver/page` | liste archivée paginée (cache `seuils:archive:{page}:{size}`) |
| POST | `/seuil/{id}/restaurer` | restauration (statut 16) |

Cache invalidé (`seuils:`) après chaque écriture.

## Routes frontend
`/creer/seuil`, `/liste/seuil`, `/liste/seuil/archive`, `/update/seuil/:id`.

## Validations effectuées
- `python -m compileall` sur les nouveaux modules backend : OK.
- Import de `backend.main` avec le venv : OK, router `/seuil` enregistré.
- `npm run build` (frontend) : OK.
- Requête SELECT paginée des seuils exécutée en lecture seule sur la BDD : OK (0 ligne, pas d'erreur).

## Correctifs
- **Suppression inopérante** : `delete_seuil` insérait une ligne `t_seuil_statut` avec
  `date = NULL`, or la colonne est `NOT NULL` → violation → rollback → le seuil restait
  visible. Corrigé dans `repository/seuil/seuil.py` : `date_value = date or datetime.utcnow()`
  (aligné sur `insert_seuil_statut`). La Configuration n'a pas ce souci car son controller
  passe explicitement `date=datetime.now()`.

## À faire ensuite (actions manuelles — côté utilisateur)
1. **Aucune migration SQL** : `t_seuil` et `t_seuil_statut` existent déjà (vérifié).
2. Redémarrer le backend FastAPI (uvicorn) pour charger le nouveau router.
3. Redémarrer le frontend (`npm run dev`) ou servir le build.
4. Optionnel : insérer des seuils de démarrage (ex. `('STOCKAGE', 80)`), via l'UI
   « Créer seuil » ou un `INSERT` manuel.
