# Chromebook Surveillance & Monitoring System

Application de **surveillance et de suivi d’un parc de Chromebooks** en entreprise. Elle permet de synchroniser et d’exploiter les données issues des **API Google Admin / Chrome (appareils, télémétrie, événements, utilisateurs, imprimantes)**, de les stocker en base **PostgreSQL**, et de les consulter/administrer via une **API REST FastAPI** et une **interface web React/Vite**.

Ce README sert de **guide d’installation, de configuration et de prise en main** pour un nouveau développeur ou un repreneur du projet.

> Guide dédié à l’assistant IA (clé Gemini) : [doc/guide_gemini_api.md](doc/guide_gemini_api.md)

---

## Sommaire

- [Présentation fonctionnelle](#présentation-fonctionnelle)
- [Architecture et structure du dépôt](#architecture-et-structure-du-dépôt)
- [Prérequis](#prérequis)
- [Installation et configuration](#installation-et-configuration)
  - [1. Récupération du projet](#1-récupération-du-projet)
  - [2. Base de données PostgreSQL](#2-base-de-données-postgresql)
  - [3. Backend (Python / FastAPI)](#3-backend-python--fastapi)
  - [4. Frontend (React / Vite)](#4-frontend-react--vite)
  - [5. Variables d’environnement (`code/.env`)](#5-variables-denvironnement-codeenv)
  - [6. Credentials Google Admin / Télémétrie](#6-credentials-google-admin--télémétrie)
  - [7. Clé API Gemini (Assistant IA / Messagerie)](#7-clé-api-gemini-assistant-ia--messagerie)
- [Lancement du projet](#lancement-du-projet)
- [Fonctionnalités principales (prise en main)](#fonctionnalités-principales-prise-en-main)
- [Dépendances et utilité](#dépendances-et-utilité)
- [Documentation complémentaire](#documentation-complémentaire)
- [Sécurité, bonnes pratiques et handover](#sécurité-bonnes-pratiques-et-handover)
- [Dépannage rapide](#dépannage-rapide)

---

## Présentation fonctionnelle

Le système couvre notamment :

- **Inventaire et suivi des appareils (devices)** : informations Chromebook, versions, statut, ressources (CPU/RAM/disque), utilisateurs récents, détails par appareil.
- **Filiales / unités organisationnelles** : rattachement et consultation des appareils par filiale.
- **Utilisateurs (annuaire synchronisé & comptes applicatifs)** : utilisateurs Google récents, comptes de l’application, rôles/permissions, archivage/restauration, mise à jour du mot de passe.
- **Événements & rapports** : événements/rapports liés aux appareils, consultation et analyses.
- **Alertes & seuils** : génération/suivi d’alertes, configuration de seuils.
- **Imprimantes & réseau** : données issues de la télémétrie (imprimantes, informations réseau).
- **Comparaisons & tableaux de bord** : vues de synthèse, comparaisons, indicateurs.
- **Configuration applicative** : paramètres métier/techniques stockés en base et modifiables via l’interface (selon droits).
- **Synchronisation** : import/synchronisation des données depuis Google (script/worker d’auto-synchronisation disponible).
- **Export** : export de données (selon modules).
- **Assistant IA / Messagerie** : aide et analyse contextuelle via l’API Gemini (nécessite une clé API valide).

L’accès à l’interface est protégé (authentification JWT/cookie). Certaines actions sont réservées aux administrateurs.

---

## Architecture et structure du dépôt

- `code/backend/` : API FastAPI, logique métier (`fonction/metier` : controllers/services/repositories/models), accès base/transactions, intégrations Google (`google_api/`), utilitaires, middlewares, sécurité.
- `code/frontend/` : application React + Vite (pages, composants, appels API, styles).
- `code/bdd/` : scripts/ressources liés à la base de données (schéma, vues/fonctions selon le contenu du projet).
- `code/.env.example` : modèle des variables d’environnement backend (et base frontend). **À copier en `code/.env`**.
- `code/doc/requirements.txt` : dépendances Python du backend.
- `credential/` : fichiers de credentials Google (OAuth client, token) — **à ne jamais commiter**.
- `doc/` : documentation technique (synchronisation, cache, sécurité, JWT, seuils, etc.) et guides.
- `export/`, `output/` : sorties/exports générés selon les usages.

---

## Prérequis

- **Python** 3.10+ (recommandé : version compatible avec les dépendances du projet) et `pip`.
- **Node.js** (LTS recommandé) et `npm`.
- **PostgreSQL** (serveur accessible) et une base initialisée avec le schéma attendu par l’application.
- **Accès Google Workspace / Admin** (pour la synchronisation) : projet Google Cloud configuré, API Admin SDK / Chrome/Telemetry activées selon besoins, et credentials OAuth (voir plus bas).
- **Clé API Gemini** (Google AI Studio) pour l’assistant IA/messagerie (optionnel si la fonctionnalité IA n’est pas utilisée, mais l’absence de clé empêchera son fonctionnement).

---

## Installation et configuration

### 1. Récupération du projet

```bash
git clone <url-du-depot>
cd chromebook_surveillance
```

> Adapter le nom du dossier racine si différent (`chrome-monitoring` selon votre environnement).

### 2. Base de données PostgreSQL

1. Créer une base de données (ex. `gt`) et un utilisateur PostgreSQL avec les droits nécessaires.
2. Initialiser le schéma/tables/vues/fonctions requis par l’application à partir des scripts fournis dans `code/bdd/` (et/ou selon la procédure interne du projet). Le backend s’appuie sur des tables/vues comme `t_configuration`, `v_configuration`, etc.
3. Renseigner les paramètres de connexion dans `code/.env` (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`).

### 3. Backend (Python / FastAPI)

> Les commandes ci-dessous sont à exécuter depuis le dossier **`code/`** (ou en ajustant les chemins). Le module applicatif est `backend.main:app`.

#### A. Créer et activer un environnement virtuel

**Windows (PowerShell) :**
```powershell
cd code
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS :**
```bash
cd code
python3 -m venv venv
source venv/bin/activate
```

#### B. Installer les dépendances Python

```bash
python -m pip install --upgrade pip
pip install -r doc/requirements.txt
```

> Le fichier de dépendances du backend est `code/doc/requirements.txt`. (Si votre environnement dispose d’un autre fichier `requirements.txt`, alignez-vous sur celui-ci.)  
> Le hachage des mots de passe utilise `pwdlib[argon2]` (inclus) ; `passlib[bcrypt]` est également listé pour compatibilité selon les environnements.

### 4. Frontend (React / Vite)

```bash
cd code/frontend
npm install
```

### 5. Variables d’environnement (`code/.env`)

1. Dupliquer le modèle :
   ```bash
   cp code/.env.example code/.env
   ```
   (Windows PowerShell : `Copy-Item code\.env.example code\.env`, depuis la racine ou en adaptant le chemin)

2. Compléter `code/.env` avec les valeurs de votre environnement. Principales variables :

| Variable | Description |
|---|---|
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Connexion PostgreSQL |
| `API_HOST`, `API_PORT` | Hôte/port d’écoute (information/configuration selon usage) |
| `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES` | Sécurité JWT / authentification |
| `CACHE_TTL_SECONDS` | Durée de cache applicatif (secondes) |
| `GOOGLE_CUSTOMER_ID` | Identifiant client Google Workspace (ex. `my_customer`) |
| `GOOGLE_TOKEN_PATH`, `GOOGLE_CREDENTIALS_PATH` | Chemins vers `token.json` et `credential.json` (relatifs au contexte d’exécution, ex. `../credential/...` depuis `code/`) |
| `GEMINI_API_KEY`, `GEMINI_MODEL` | Clé API et modèle pour l’assistant IA (voir [guide dédié](doc/guide_gemini_api.md)) |
| `VITE_API_BASE_URL` | URL de base de l’API consommée par le frontend (ex. `http://localhost:8000`) |

> `VITE_API_BASE_URL` est utilisé côté frontend (Vite) : après modification, relancer/redéployer le frontend si nécessaire.

### 6. Credentials Google Admin / Télémétrie

La synchronisation et les appels Google reposent sur des credentials OAuth placés dans le dossier `credential/` (non versionné), typiquement :
- `credential/credential.json` (client OAuth / identifiants d’application),
- `credential/token.json` (jeton d’accès/refresh généré lors de l’autorisation).

Étapes générales :
1. Créer/configurer un projet dans Google Cloud Console, activer les API nécessaires (Admin SDK, Chrome Management/Telemetry, etc. selon le périmètre du projet).
2. Créer des identifiants OAuth 2.0 (type adapté : application de bureau, etc.) et télécharger le fichier client en `credential/credential.json`.
3. Générer/rafraîchir `token.json` via le flux d’autorisation prévu par le projet (scripts/utilitaires dans `code/backend/google_api/` ou procédure interne) avec un compte disposant des droits d’administration requis.
4. Vérifier `GOOGLE_TOKEN_PATH` et `GOOGLE_CREDENTIALS_PATH` dans `code/.env`.

> Les jetons OAuth expirent et se renouvellent via le refresh token ; en cas d’erreur d’authentification Google, régénérer `token.json` selon la procédure du projet.

### 7. Clé API Gemini (Assistant IA / Messagerie)

L’assistant IA utilise **Google Gemini** via une **clé API** (`GEMINI_API_KEY`) configurée dans `code/.env` (et `GEMINI_MODEL` pour le modèle). Elle est lue par le backend au runtime (voir `code/backend/fonction/metier/service/ia_common.py`).

- **Obtenir / renouveler une clé** et la mettre dans `.env` : voici guide 
---

## 1. Prérequis

- Un compte Google.
- Accès à [Google AI Studio](https://aistudio.google.com/) (création/gestion de clés API) ou à la [Google Cloud Console](https://console.cloud.google.com/) selon la configuration du projet Google associé.
- Accès au fichier `code/.env` du projet (non versionné). Utiliser `code/.env.example` comme modèle.

---

## 2. Obtenir ou recréer une clé API Gemini

1. **Ouvrir Google AI Studio**  
   - Aller sur [https://aistudio.google.com/](https://aistudio.google.com/) et se connecter avec le compte Google prévu pour le projet.

2. **Accéder à la gestion des clés API**  
   - Menu **Get API key** / **Obtenir une clé API** (libellé pouvant varier selon l’interface).
   - Choisir le projet Google Cloud associé, ou en créer un si nécessaire.

3. **Créer une nouvelle clé**  
   - Cliquer sur **Create API key** / **Créer une clé API**.
   - Copier immédiatement la clé générée : elle ne pourra pas toujours être ré-affichée intégralement ensuite.

4. **(Optionnel mais recommandé) Sécuriser la clé**  
   - Dans Google Cloud Console > *APIs & Services* > *Credentials*, restreindre la clé (API autorisées, restrictions d’usage) selon la politique de l’organisation.
   - Vérifier que l’API Generative Language / Gemini utilisée est activée pour le projet et que la facturation/quota est conforme à l’usage.

> **Si l’ancienne clé a été exposée ou ne fonctionne plus** : révoquer/supprimer l’ancienne clé dans la console, en créer une nouvelle, puis mettre à jour `code/.env` (voir ci-dessous) et redémarrer le backend.

---

## 3. Renseigner la clé dans `code/.env`

1. Depuis la racine du projet, créer le fichier d’environnement si besoin :
   ```bash
   cp code/.env.example code/.env
   ```
   (Windows PowerShell : `Copy-Item code\.env.example code\.env`)

2. Ouvrir `code/.env` et renseigner au minimum :
   ```env
   # Assistant IA (Gemini)
   GEMINI_API_KEY=votre_nouvelle_cle_api
   GEMINI_MODEL=gemini-3.5-flash-lite
   ```
   - `GEMINI_API_KEY` : coller la clé copiée depuis AI Studio (sans guillemets, sans espaces).
   - `GEMINI_MODEL` : modèle utilisé par l’assistant (laisser la valeur par défaut du projet sauf besoin spécifique et compatibilité vérifiée).

3. **Ne jamais commiter `code/.env` ni partager la clé** (dépôt Git, captures, tickets publics). Le fichier `.env` est ignoré par Git ; partager uniquement la structure via `code/.env.example`.

4. **Redémarrer le backend** après modification : la clé est lue au premier usage et le client IA est mis en cache en mémoire dans le processus. Un changement de clé dans `.env` nécessite un redémarrage de `uvicorn` (et du worker si utilisé) pour être pris en compte.

---

## 4. Prise en main par une autre personne (handover)

Pour qu’un nouveau mainteneur fasse fonctionner l’assistant IA :

1. Récupérer les accès au **compte/projet Google** qui porte la clé (ou créer une clé sur son propre projet, selon l’organisation).
2. Créer sa propre clé API (étape 2) — **ne pas réutiliser une clé reçue par canal non sécurisé**.
3. Copier `code/.env.example` vers `code/.env` et renseigner `GEMINI_API_KEY`, `GEMINI_MODEL`, ainsi que les autres variables requises (base de données, JWT, Google Admin/télémétrie, etc.).
4. Installer les dépendances backend (`pip install -r doc/requirements.txt` depuis `code/` ou selon le README) : le client Gemini repose notamment sur `google-genai`.
5. Lancer le backend et tester la fonctionnalité de messagerie/assistant IA depuis le frontend.

---

## 5. La clé peut-elle “expirer” ou cesser de fonctionner ?

- Une **clé API** n’a généralement pas d’expiration courte comme un *access token* OAuth, mais elle peut **devenir inutilisable** si :
  - elle est **révoquée, supprimée ou régénérée** ;
  - le **projet Google** est désactivé ou mal configuré ;
  - la **facturation, le quota ou le free tier** est dépassé/bloqué ;
  - des **restrictions** de clé empêchent l’appel (API, référent, etc.).
- Dans ces cas, les appels IA échouent (erreurs typiques 401/403/429 selon le motif). Il faut alors vérifier la clé/projet/quotas dans AI Studio ou Google Cloud Console et, si nécessaire, créer une nouvelle clé et mettre à jour `code/.env`.
- Ce mécanisme est **différent** des jetons OAuth Google (ex. accès Google Admin/Directory du projet, gérés via `credential/` et refresh token), qui expirent et se renouvellent automatiquement selon le flux configuré.

---

## 6. Dépannage rapide

| Symptôme | Pistes |
|---|---|
| `GEMINI_API_KEY manquante dans le fichier .env` | Vérifier que `code/.env` existe, contient `GEMINI_API_KEY=...`, et que le backend est lancé depuis le bon contexte (le projet charge `.env` au démarrage du module IA). Redémarrer le backend. |
| Erreur 401/403 de l’API Gemini | Clé invalide/révoquée, API non activée, restrictions ou projet/facturation. Régénérer la clé et vérifier la console Google. |
| Erreur 429 / quota | Quota ou limite de débit atteint ; attendre, augmenter le quota ou ajuster le plan/facturation. |
| Changement de clé sans effet | Redémarrer le backend (client IA en cache en mémoire) et vérifier qu’il n’y a pas de doublon/override de variable d’environnement. |
| Réponse IA vide ou erreur modèle | Vérifier `GEMINI_MODEL` (modèle disponible pour votre clé/projet) et les logs backend. |

---

## 7. Références dans le projet

- Variables : `code/.env.example` (`GEMINI_API_KEY`, `GEMINI_MODEL`)
- Chargement/usage : `code/backend/fonction/metier/service/ia_common.py`
- Dépendance : `google-genai` (voir `doc/requirements.txt`)
- Documentation générale : `README.md` (section Assistant IA / configuration)

- **La clé peut-elle “ne plus marcher” ?** Une clé API n’expire pas comme un token de session court, mais peut devenir invalide (révoquée, quota/facturation, restrictions, projet désactivé). Voir le guide pour le diagnostic.
- **Remarque** : la clé n’est pas gérée depuis l’écran de configuration applicative (stockée en variables d’environnement) ; un changement nécessite une mise à jour de `code/.env` et un redémarrage du backend.

---

## Lancement du projet

### Backend (API FastAPI)

Depuis `code/`, avec l’environnement virtuel activé et `code/.env` configuré :

```bash
uvicorn backend.main:app --reload
```

- API : [http://127.0.0.1:8000](http://127.0.0.1:8000) (par défaut)
- Documentation interactive (si activée par FastAPI) : `/docs` (Swagger) et `/redoc`

### Frontend (React + Vite)

Depuis `code/frontend/` :

```bash
npm run dev
```

- Interface web : [http://localhost:5173](http://localhost:5173) (par défaut Vite)

### Autres commandes utiles

- **Tests / scripts backend** (selon disponibilité) :
  ```bash
  python -m backend.test
  ```
- **Worker / auto-synchronisation** (selon usage du projet) :
  ```bash
  python -m backend.worker
  ```
- **Build frontend (production)** :
  ```bash
  cd code/frontend
  npm run build
  npm run preview
  ```

---

## Fonctionnalités principales (prise en main)

1. **Connexion / inscription** : création de compte et authentification (JWT/cookie). Les droits dépendent du rôle.
2. **Tableau de bord** : vue synthétique de l’état du parc.
3. **Appareils** : liste (cartes/table), filtres, pagination, vue détaillée, informations système/réseau/utilisateurs récents.
4. **Filiales / utilisateurs / événements / imprimantes / alertes / seuils / configuration** : modules de consultation et d’administration selon les écrans disponibles dans le menu.
5. **Vues liste** : bascule carte/liste sur certains écrans ; la vue tableau permet d’afficher l’ensemble des résultats filtrés avec pagination côté client (par lots) selon les pages concernées.
6. **Messagerie / Assistant IA** : bouton d’accès à la messagerie pour poser des questions/analyser avec Gemini (clé API requise).
7. **Profil** : mise à jour du mot de passe via la page dédiée.
8. **Synchronisation & données** : les données proviennent des imports Google ; en l’absence de synchronisation/credentials valides, certaines vues peuvent être vides.

> Pour comprendre la logique de synchronisation, cache, seuils, comparaisons, JWT, etc., consulter les notes dans `doc/`.

---

## Dépendances et utilité

### Backend (Python) — `code/doc/requirements.txt`

| Package | Utilité / Rôle |
|---|---|
| `google-auth` | Authentification de base pour les services Google |
| `google-auth-oauthlib` | Flux OAuth 2.0 (credentials Google) |
| `google-auth-httplib2` | Transport HTTP pour les clients Google |
| `google-api-python-client` | Appels aux API Google (Admin SDK, etc.) |
| `google-genai` | Client Gemini (assistant IA) |
| `fastapi` | Framework API REST |
| `uvicorn` | Serveur ASGI pour FastAPI |
| `psycopg2-binary` | Connecteur PostgreSQL |
| `sqlalchemy` | Outils/ORM et accès base (selon usages du projet) |
| `pydantic-settings` | Gestion typée de la configuration |
| `python-dotenv` | Chargement des variables depuis `.env` |
| `python-jose[cryptography]` | JWT (authentification) |
| `python-multipart` | Gestion des formulaires/multipart |
| `pwdlib[argon2]`, `passlib[bcrypt]` | Hachage/vérification de mots de passe |
| `openpyxl` | Lecture/traitement de fichiers Excel (imports/exports/IA selon modules) |
| `reportlab` | Génération de PDF (exports/rapports selon modules) |

### Frontend (Node.js / React) — `code/frontend/package.json`

| Package | Utilité / Rôle |
|---|---|
| `react`, `react-dom` | Interface utilisateur |
| `vite`, `@vitejs/plugin-react` | Build et serveur de développement |
| `react-router-dom` | Routage des pages |
| `axios` | Client HTTP vers l’API backend |
| `lucide-react` | Icônes |
| `tailwindcss`, `@tailwindcss/vite`, `daisyui` | Styles et composants UI |
| `recharts` | Graphiques / visualisations |
| `eslint` (+ plugins) | Qualité de code (dev) |

---

## Documentation complémentaire

- **Assistant IA / clé Gemini** : [doc/guide_gemini_api.md](doc/guide_gemini_api.md)
- **Notes techniques (selon besoin)** : `doc/` (ex. `jwt_token.txt`, `auto_synchro.txt`, `caching.txt`, `security.txt`, `synchronisation_explain.txt`, `seuil.txt`, etc.)
- **Modèle d’environnement** : `code/.env.example`

---

## Sécurité, bonnes pratiques et handover

- **Ne jamais commiter** `code/.env`, le dossier `credential/`, ni aucune clé/token/mot de passe.
- Partager la configuration via `code/.env.example` et transmettre les secrets par un canal sécurisé.
- Pour la reprise du projet : fournir l’accès à la base, aux credentials Google, et (si utilisé) une **nouvelle clé Gemini** dédiée au repreneur (voir [doc/guide_gemini_api.md](doc/guide_gemini_api.md)).
- Limiter les droits des comptes/clé API (principe du moindre privilège) et surveiller les quotas/facturation Google.
- Après changement de dépendances, de `.env` ou de code backend, **redémarrer** les services concernés.

---

## Dépannage rapide

- **Backend ne démarre pas / erreur d’import** : vérifier l’activation du venv, `pip install -r doc/requirements.txt`, et lancer depuis `code/` (`uvicorn backend.main:app --reload`).
- **Erreur base de données** : vérifier `DB_*` dans `code/.env`, que PostgreSQL est accessible et le schéma initialisé.
- **401/erreurs d’authentification app** : vérifier `SECRET_KEY`/JWT, cookies/CORS selon environnement, et les comptes utilisateurs.
- **Synchronisation Google en échec** : vérifier `credential/`, `GOOGLE_*`, validité/refresh du `token.json` et les droits du compte.
- **Assistant IA indisponible** : vérifier `GEMINI_API_KEY`/`GEMINI_MODEL`, redémarrer le backend, consulter [doc/guide_gemini_api.md](doc/guide_gemini_api.md).
- **Frontend ne joint pas l’API** : vérifier `VITE_API_BASE_URL`, que le backend tourne, et les réglages CORS si applicable.
