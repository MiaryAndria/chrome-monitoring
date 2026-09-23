from backend.fonction.conn.connexion import get_connection


connexion = get_connection()
cur=connexion.cursor()

def get_liste_device_statut(cur):
    cur.execute(
        """
        SELECT * FROM t_device_statut
        """
    )
    result = cur.fetchall()
    return result

def get_device_statut_by_id(cur,id):
    cur.execute(
        """
        SELECT * FROM t_device_statut WHERE id = %s
        """,(id,)
    )
    result = cur.fetchone()
    return result

def get_statuts_by_device(cur,id_device):
    cur.execute(
        """
        SELECT * FROM t_device_statut WHERE id_device = %s
        ORDER BY date DESC
        """,(id_device,)
    )
    result = cur.fetchall()
    return result

def get_devices_by_statut(cur,id_statut):
    cur.execute(
        """
        SELECT * FROM t_device_statut WHERE id_statut = %s
        ORDER BY date DESC
        """,(id_statut,)
    )
    result = cur.fetchall()
    return result

def get_dernier_statut_device(cur,id_device):
    cur.execute(
        """
        SELECT * FROM t_device_statut
        WHERE id_device = %s
        ORDER BY date DESC
        LIMIT 1
        """,(id_device,)
    )
    result = cur.fetchone()
    return result

def get_historique_statut_device(cur,id_device):
    cur.execute(
        """
        SELECT * FROM t_device_statut
        WHERE id_device = %s
        ORDER BY date DESC
        """,(id_device,)
    )
    result = cur.fetchall()
    return result

def get_statuts_by_period(cur,id_device,date_debut,date_fin):
    cur.execute(
        """
        SELECT * FROM t_device_statut
        WHERE id_device = %s AND date BETWEEN %s AND %s
        ORDER BY date DESC
        """,(id_device,date_debut,date_fin,)
    )
    result = cur.fetchall()
    return result

def get_device_statut_by_device_and_statut(cur,id_device,id_statut):
    cur.execute(
        """
        SELECT * FROM t_device_statut
        WHERE id_device = %s AND id_statut = %s
        ORDER BY date DESC
        """,(id_device,id_statut,)
    )
    result = cur.fetchall()
    return result

def get_statuts_by_device_statut_and_period(cur,id_device,id_statut,date_debut,date_fin):
    cur.execute(
        """
        SELECT * FROM t_device_statut
        WHERE id_device = %s AND id_statut = %s AND date BETWEEN %s AND %s
        ORDER BY date DESC
        """,(id_device,id_statut,date_debut,date_fin,)
    )
    result = cur.fetchall()
    return result

