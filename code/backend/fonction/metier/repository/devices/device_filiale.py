from backend.fonction.conn.connexion import get_connection

connexion = get_connection()
cur=connexion.cursor()

def get_liste_device_filiale(cur):
    cur.execute(
        """
        SELECT * FROM t_device_filiale
        """
    )
    result = cur.fetchall()
    return result

def get_device_filiale_by_id(cur,id):
    cur.execute(
        """
        SELECT * FROM t_device_filiale WHERE id = %s
        """,(id,)
    )
    result = cur.fetchone()
    return result

def get_filiales_by_device(cur,id_device):
    cur.execute(
        """
        SELECT * FROM t_device_filiale WHERE id_device = %s
        ORDER BY date_affectation DESC
        """,(id_device,)
    )
    result = cur.fetchall()
    return result

def get_devices_by_filiale(cur,id_filiale):
    cur.execute(
        """
        SELECT * FROM t_device_filiale WHERE id_filiale = %s
        ORDER BY date_affectation DESC
        """,(id_filiale,)
    )
    result = cur.fetchall()
    return result

def get_affectation_actuelle_device(cur,id_device):
    cur.execute(
        """
        SELECT * FROM t_device_filiale
        WHERE id_device = %s AND date_fin_affectation IS NULL
        ORDER BY date_affectation DESC
        LIMIT 1
        """,(id_device,)
    )
    result = cur.fetchone()
    return result

def get_historique_affectation_device(cur,id_device):
    cur.execute(
        """
        SELECT * FROM t_device_filiale
        WHERE id_device = %s
        ORDER BY date_affectation DESC
        """,(id_device,)
    )
    result = cur.fetchall()
    return result

def get_device_filiale_by_device_and_filiale(cur,id_device,id_filiale):
    cur.execute(
        """
        SELECT * FROM t_device_filiale
        WHERE id_device = %s AND id_filiale = %s
        ORDER BY date_affectation DESC
        """,(id_device,id_filiale,)
    )
    result = cur.fetchall()
    return result

def get_affectation_actuelle_by_device_and_filiale(cur,id_device,id_filiale):
    cur.execute(
        """
        SELECT * FROM t_device_filiale
        WHERE id_device = %s AND id_filiale = %s AND date_fin_affectation IS NULL
        """,(id_device,id_filiale,)
    )
    result = cur.fetchone()
    return result
