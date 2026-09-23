## commande d'installation 
pip install -r requirements.txt

## commande de test
python -m backend.test 

## création environnement virtuel comme ça installer juste pour projet 
python -m venv venv

## création environnement ubuntu 
python3 -m venv venv

## activation venv
venv\Scripts\activate

## mise à jour python
python -m pip install --upgrade pip

## lancement uvicorn
uvicorn backend.main:app --reload
http://127.0.0.1:8000

## Package	Utilisation
google-auth	                    Authentification Google
google-auth-oauthlib	        OAuth 2.0 avec ton Client ID
google-auth-httplib2	        Communication authentifiée avec Google
google-api-python-client	    Appel des APIs Google
fastapi	                        Backend / API REST
uvicorn	                        Serveur pour FastAPI
psycopg2-binary	                Connexion PostgreSQL
sqlalchemy	                    Gestion de la base de données
pydantic-settings	            Configuration de l'application
python-dotenv	                Lecture du .env
python-jose[cryptography]	    JWT / authentification
passlib[bcrypt]	                Hashage des mots de passe
python-multipart	            Formulaires et données multipart
pip install "pwdlib[argon2]"        Haschage mdp


## synchronisation toutes les 30 minutes 
probleme ko token misy expiration 
mettre à jour json dans dossier credential token 
-> on stock toujours on base on fait pas update fa stockerna fona comme ça on pourra avoir historique 

## compilation
# petit test 
python nom_fichier.py

# fichier contenant des dependances ailleurs
cd racines du code global 
python -m dossier.fichier_python
ou uvicorn backend.main:app --reload

# Petit script indépendant
        ↓
python test.py

# Fichier faisant partie d'un projet structuré
        ↓
python -m package.test
-m sert à exécuter un module en respectant la structure des packages du projet.

# lancement serveur
uvicorn main:app --reload

cd "C:\Users\miary\Etude\finalisation s6\projet\chromebook_surveillance\chrome-monitoring"

# for A, B in dictionnaire.items():
    # A → clé
    # B → valeur