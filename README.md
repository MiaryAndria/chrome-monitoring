# Chromebook Surveillance & Monitoring System

Système de surveillance et de suivi du parc Chromebook pour entreprise. Cette application permet de récupérer les télémétries, appareils, événements et utilisateurs via les API Google Admin, et de les gérer à travers un backend **FastAPI** et un frontend **React/Vite** connecté à une base de données **PostgreSQL**.

---

##  Installation et Configuration

### 1. Backend (Python / FastAPI)

#### A. Création et activation de l'environnement virtuel (venv)

* **Sur Windows :**
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```

* **Sur Linux / Ubuntu :**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

#### B. Mise à jour de pip & installation des dépendances

```bash
python -m pip install --upgrade pip
pip install -r code/requirements.txt
```

> **Remarque :** Pour installer manuellement la bibliothèque de hachage de mot de passe recommandée :
> ```bash
> pip install "pwdlib[argon2]"
> ```

#### C. Configuration des Variables d'Environnement

1. Dupliquer le fichier modèle `.env.example` dans le dossier `code/` :
   ```bash
   cp code/.env.example code/.env
   ```
2. Compléter `code/.env` avec vos identifiants (PostgreSQL, clé JWT, identifiants Google API).

---

### 2. Frontend (React / Vite)

#### Installation des dépendances Node.js

Se déplacer dans le dossier `code/frontend` et installer les packages :

```bash
cd code/frontend
npm install
```

---

## Lancement du Projet

### Lancer le Backend (FastAPI)

Depuis le dossier `code/`, exécuter :

```bash
uvicorn backend.main:app --reload
```

- **API REST :** [http://127.0.0.1:8000](http://127.0.0.1:8000)  


### Lancer le Frontend (React + Vite)

Depuis le dossier `code/frontend/`, exécuter :

```bash
npm run dev
```

- **Application Web :** [http://localhost:5173](http://localhost:5173)

### Autres commandes utiles

* **Exécution des tests backend :**
  ```bash
  python -m backend.test
  ```

* **Build de production frontend :**
  ```bash
  cd code/frontend
  npm run build
  ```

---

## Liste des Packages & Utilité

### Backend (Python)

| Package | Utilité / Rôle |
| :--- | :--- |
| **`google-auth`** | Authentification de base pour les services Google |
| **`google-auth-oauthlib`** | Flux OAuth 2.0 avec le Client ID Google |
| **`google-auth-httplib2`** | Transport et communication sécurisée HTTP avec Google |
| **`google-api-python-client`** | Client officiel d'appel des API Google Admin SDK & Telemetry |
| **`fastapi`** | Framework web haut de gamme pour l'API REST Backend |
| **`uvicorn`** | Serveur web ASGI ultra-rapide pour exécuter FastAPI |
| **`psycopg2-binary`** | Connecteur PostgreSQL pour Python |
| **`sqlalchemy`** | ORM et gestion de la base de données relationnelle |
| **`pydantic-settings`** | Gestion typée des configurations de l'application |
| **`python-dotenv`** | Chargement des variables d'environnement depuis le fichier `.env` |
| **`python-jose[cryptography]`** | Génération et vérification des jetons JWT pour l'authentification |
| **`python-multipart`** | Traitement des formulaires et données multipart |
| **`pwdlib[argon2]`** | Hachage sécurisé des mots de passe avec l'algorithme Argon2 |

### Frontend (Node.js / React)

| Package | Utilité / Rôle |
| :--- | :--- |
| **`react` & `react-dom`** | Bibliothèque d'interface utilisateur web |
| **`vite`** | Outil de build et serveur de développement ultra-rapide |
| **`react-router-dom`** | Gestion de la navigation et du routage des pages |
| **`axios`** | Client HTTP pour consommer l'API REST FastAPI |
| **`lucide-react`** | Collection d'icônes modernes pour l'interface |
| **`tailwindcss` & `daisyui`** | Frameworks CSS pour le design et les composants UI |

---

##  Sécurité & Bonnes Pratiques

- **Le fichier `.env` et le dossier `credential/` ne doivent jamais être commités sur Git.**
- Utilisez le fichier `.env.example` pour partager la structure des variables aux nouveaux collaborateurs.
