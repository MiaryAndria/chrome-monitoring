from backend.fonction.conn.transaction import transaction
from backend.fonction.metier.repository.devices import delete_all
from backend.core.cache import cache_clear

def reset_data():
    with transaction() as cur:
        if cur is None:
            print("Connexion BDD impossible")
            return None
        delete_all(cur)
    cache_clear()
    return True
