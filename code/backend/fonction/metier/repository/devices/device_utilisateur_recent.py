from backend.fonction.conn.connexion import get_connection

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
