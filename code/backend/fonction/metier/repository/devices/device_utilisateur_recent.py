from backend.fonction.conn.connexion import get_connection
from backend.fonction.metier.repository.utilisateur_google.utilisateur import get_utilisateur_by_id

def get_liste_device_utilisateur_recent(cur):
    cur.execute(
        """
        SELECT * FROM t_device_utilisateur_recent
        """
    )
    result = cur.fetchall()
    return result

def get_utilisateurs_recents_by_device(cur,id_device):
    cur.execute(
        """
        SELECT * FROM t_device_utilisateur_recent
        WHERE id_device = %s
        ORDER BY date_observation DESC
        """,(id_device,)
    )
    result = cur.fetchall()
    return result

def get_devices_by_utilisateur_recent(cur,id_utilisateur):
    cur.execute(
        """
        SELECT * FROM t_device_utilisateur_recent
        WHERE id_utilisateur = %s
        ORDER BY date_observation DESC
        """,(id_utilisateur,)
    )
    result = cur.fetchall()
    return result

def get_dernier_utilisateur_device(cur,id_device):
    cur.execute(
        """
        SELECT * FROM t_device_utilisateur_recent
        WHERE id_device = %s
        ORDER BY date_observation DESC
        LIMIT 1
        """,(id_device,)
    )
    result = cur.fetchone()
    return result

def get_historique_utilisateurs_device(cur,id_device):
    cur.execute(
        """
        SELECT * FROM t_device_utilisateur_recent
        WHERE id_device = %s
        ORDER BY date_observation DESC
        """,(id_device,)
    )
    result = cur.fetchall()
    return result

def get_device_utilisateur_recent_by_device_and_utilisateur(cur,id_device,id_utilisateur):
    cur.execute(
        """
        SELECT * FROM t_device_utilisateur_recent
        WHERE id_device = %s AND id_utilisateur = %s
        ORDER BY date_observation DESC
        """,(id_device,id_utilisateur,)
    )
    result = cur.fetchall()
    return result

def insert_device_utilisateur_recent(cur, id_device, id_utilisateur):
    cur.execute(
        """
        INSERT INTO t_device_utilisateur_recent (id_device, id_utilisateur)
        VALUES (%s, %s)
        """, (id_device, id_utilisateur)
    )

def _get_recent_users(cur, device_id):
    """
    Retourne la liste des emails des utilisateurs récents observés sur ce device.
    Attendu par le modèle Pydantic (list[str]).
    """
    utilisateurs_recents = []
    historique = get_historique_utilisateurs_device(cur, device_id) or []
    for ur in historique:
        if not ur or not ur[2]:
            continue
        ur_u = get_utilisateur_by_id(cur, ur[2])
        if ur_u and ur_u[1] and ur_u[1] not in utilisateurs_recents:
            utilisateurs_recents.append(ur_u[1])
    return utilisateurs_recents


def get_utilisateur_recent_by_device(cur, device_id):
    """
    Retourne l'objet utilisateur (id, email) le plus récemment observé sur ce device.
    Retourne None si aucun utilisateur trouvé.
    """
    dernier = get_dernier_utilisateur_device(cur, device_id)
    if not dernier or not dernier[2]:
        return None
    return get_utilisateur_by_id(cur, dernier[2])