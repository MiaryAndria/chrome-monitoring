import os
import psycopg2

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - compat environnement sans python-dotenv
    def load_dotenv(*args, **kwargs):
        return False

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "gt"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres")
}

def get_connection():
    try:
        connexion = psycopg2.connect(
            dbname=DB_CONFIG["dbname"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"]
        )
        print("Connexion réussie !",connexion)
        return connexion
        
    except Exception as erreur:
        print(f"Erreur de connexion : {erreur}")
        return None        
        
def close_connection(connexion):
    connexion.close()
    
    