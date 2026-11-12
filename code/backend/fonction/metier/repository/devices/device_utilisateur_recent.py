from backend.fonction.metier.repository.utilisateur_google.utilisateur import get_utilisateur_by_id

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

def insert_device_utilisateur_recent(cur, id_device, id_utilisateur):
    cur.execute(
        """
        INSERT INTO t_device_utilisateur_recent (id_device, id_utilisateur)
        VALUES (%s, %s)
        ON CONFLICT (id_device, id_utilisateur) DO NOTHING
        """, (id_device, id_utilisateur)
    )

def _get_recent_users(cur, device_id):
    """
    Retourne la liste des emails des utilisateurs récents observés sur ce device.
    Une seule requête agrégée au lieu d'un SELECT par ligne d'historique.
    """
    cur.execute(
        """
        SELECT DISTINCT u.email
        FROM t_device_utilisateur_recent dur
        JOIN t_utilisateur u ON u.id = dur.id_utilisateur
        WHERE dur.id_device = %s
          AND u.email IS NOT NULL
        ORDER BY u.email
        """,
        (device_id,),
    )
    return [row[0] for row in cur.fetchall()]


def get_utilisateur_recent_by_device(cur, device_id):
    """
    Retourne l'objet utilisateur (id, email) le plus récemment observé sur ce device.
    Retourne None si aucun utilisateur trouvé.
    """
    dernier = get_dernier_utilisateur_device(cur, device_id)
    if not dernier or not dernier[2]:
        return None
    return get_utilisateur_by_id(cur, dernier[2])

