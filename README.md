#  Chromebook Surveillance & Monitoring System

Système de surveillance et de suivi du parc Chromebook pour entreprise. Cette application permet de récupérer les télémétries, appareils, événements et utilisateurs via les API Google Admin, et de les gérer à travers un backend **FastAPI** et un frontend **React/Vite** connecté à une base de données **PostgreSQL**.

---

##  Guide d'Installation et Configuration

### 1. Création de l'Environnement Virtuel (venv)

Créer un environnement virtuel isolé pour le projet :

* **Sur Windows :**
  ```bash
  python -m venv venv
  ```

* **Sur Linux / Ubuntu :**
  ```bash
  python3 -m venv venv
  ```

### 2. Activation de l'Environnement Virtuel

* **Sur Windows (PowerShell / CMD) :**
  ```bash
  venv\Scripts\activate
  ```

* **Sur Linux / Ubuntu :**
  ```bash
  source venv/bin/activate
  ```

---

### 3. Mise à jour de pip & Installation des Dépendances

Mettre à jour le gestionnaire de paquets `pip` :

```bash
python -m pip install --upgrade pip
```

Installer toutes les dépendances requises à partir du fichier `requirements.txt` :

```bash
pip install -r code/requirements.txt
```

> **Remarque :** Pour installer manuellement la bibliothèque de hachage de mot de passe recommandée :
> ```bash
> pip install "pwdlib[argon2]"
> ```

---

### 4. Configuration des Variables d'Environnement

1. Dupliquer le fichier modèle `.env.example` situé dans le dossier `code/` :
   ```bash
   cp code/.env.example code/.env
   ```
2. Compléter le fichier `code/.env` avec vos identifiants réels (base de données PostgreSQL, clé secrète JWT, identifiants Google API).

---

## Lancement du Projet

### Lancer le serveur Backend (FastAPI)

Dans le dossier `code/`, exécuter :

```bash
uvicorn backend.main:app --reload
```

L'API sera accessible sur : [http://127.0.0.1:8000](http://127.0.0.1:8000)  
La documentation interactive Swagger est disponible sur : [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Exécution des tests

Pour exécuter les modules de test du backend :

```bash
python -m backend.test
```

---

##  Liste des Packages & Utilité

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

---

## Sécurité & Bonnes Pratiques

- **Le fichier `.env` et le dossier `credential/` ne doivent jamais être commités sur Git.**
- Utilisez le fichier `.env.example` pour partager la structure des variables aux nouveaux collaborateurs.
