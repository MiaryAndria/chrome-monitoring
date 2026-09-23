from backend.fonction.conn.connexion import get_connection

connexion = get_connection()
cur=connexion.cursor()

def get_liste_device_alerte(cur):
    cur.execute(
        """
        SELECT * FROM t_device_alerte
        """
    )
    result = cur.fetchall()
    return result

def get_device_alerte_by_id(cur,id):
    cur.execute(
        """
        SELECT * FROM t_device_alerte WHERE id = %s
        """,(id,)
    )
    result = cur.fetchone()
    return result

def get_alertes_by_device(cur,id_device):
    cur.execute(
        """
        SELECT * FROM t_device_alerte WHERE id_device = %s
        ORDER BY date DESC
        """,(id_device,)
    )
    result = cur.fetchall()
    return result

def get_devices_by_alerte(cur,id_alerte):
    cur.execute(
        """
        SELECT * FROM t_device_alerte WHERE id_alerte = %s
        ORDER BY date DESC
        """,(id_alerte,)
    )
    result = cur.fetchall()
    return result

def get_alertes_actives_by_device(cur,id_device):
    cur.execute(
        """
        SELECT * FROM t_device_alerte
        WHERE id_device = %s AND date_resolution IS NULL
        ORDER BY date DESC
        """,(id_device,)
    )
    result = cur.fetchall()
    return result

def get_alertes_resolues_by_device(cur,id_device):
    cur.execute(
        """
        SELECT * FROM t_device_alerte
        WHERE id_device = %s AND date_resolution IS NOT NULL
        ORDER BY date DESC
        """,(id_device,)
    )
    result = cur.fetchall()
    return result

def get_alertes_by_period(cur,id_device,date_debut,date_fin):
    cur.execute(
        """
        SELECT * FROM t_device_alerte
        WHERE id_device = %s AND date BETWEEN %s AND %s
        ORDER BY date DESC
        """,(id_device,date_debut,date_fin,)
    )
    result = cur.fetchall()
    return result

def get_derniere_alerte_device(cur,id_device):
    cur.execute(
        """
        SELECT * FROM t_device_alerte
        WHERE id_device = %s
        ORDER BY date DESC
        LIMIT 1
        """,(id_device,)
    )
    result = cur.fetchone()
    return result

def get_nombre_alerte_active(cur):
    cur.execute(
        """
        SELECT COUNT(*) FROM t_device_alerte
        WHERE date_resolution IS NULL
        """
    )
    result = cur.fetchone()
    return result

def get_nombre_alerte_device(cur,id_device):
    cur.execute(
        """
        SELECT COUNT(*) FROM t_device_alerte
        WHERE id_device = %s
        """,(id_device,)
    )
    result = cur.fetchone()
    return result

def get_device_alerte_by_device_and_alerte(cur,id_device,id_alerte):
    cur.execute(
        """
        SELECT * FROM t_device_alerte
        WHERE id_device = %s AND id_alerte = %s
        ORDER BY date DESC
        """,(id_device,id_alerte,)
    )
    result = cur.fetchall()
    return result

def get_alertes_actives_by_device_and_period(cur,id_device,date_debut,date_fin):
    cur.execute(
        """
        SELECT * FROM t_device_alerte
        WHERE id_device = %s AND date_resolution IS NULL AND date BETWEEN %s AND %s
        ORDER BY date DESC
        """,(id_device,date_debut,date_fin,)
    )
    result = cur.fetchall()
    return result

def get_alertes_by_alerte_and_period(cur,id_alerte,date_debut,date_fin):
    cur.execute(
        """
        SELECT * FROM t_device_alerte
        WHERE id_alerte = %s AND date BETWEEN %s AND %s
        ORDER BY date DESC
        """,(id_alerte,date_debut,date_fin,)
    )
    result = cur.fetchall()
    return result
