from backend.fonction.conn.connexion import get_connection

def get_liste_evenement_device(cur):
    cur.execute(
        """
        SELECT * FROM t_evenement_device
        """
    )
    result = cur.fetchall()
    return result

def get_evenement_by_id(cur,id):
    cur.execute(
        """
        SELECT * FROM t_evenement_device WHERE id = %s
        """,(id,)
    )
    result = cur.fetchone()
    return result

def get_evenements_by_device(cur,id_device):
    cur.execute(
        """
        SELECT * FROM t_evenement_device WHERE id_device = %s
        ORDER BY date_evenement DESC
        """,(id_device,)
    )
    result = cur.fetchall()
    return result

def get_evenements_by_type(cur,id_type_evenement):
    cur.execute(
        """
        SELECT * FROM t_evenement_device WHERE id_type_evenement = %s
        ORDER BY date_evenement DESC
        """,(id_type_evenement,)
    )
    result = cur.fetchall()
    return result

def get_evenements_by_period(cur,date_debut,date_fin):
    cur.execute(
        """
        SELECT * FROM t_evenement_device
        WHERE date_evenement BETWEEN %s AND %s
        ORDER BY date_evenement DESC
        """,(date_debut,date_fin,)
    )
    result = cur.fetchall()
    return result

def get_evenements_device_by_period(cur,id_device,date_debut,date_fin):
    cur.execute(
        """
        SELECT * FROM t_evenement_device
        WHERE id_device = %s AND date_evenement BETWEEN %s AND %s
        ORDER BY date_evenement DESC
        """,(id_device,date_debut,date_fin,)
    )
    result = cur.fetchall()
    return result

def get_dernier_evenement_device(cur,id_device):
    cur.execute(
        """
        SELECT * FROM t_evenement_device
        WHERE id_device = %s
        ORDER BY date_evenement DESC
        LIMIT 1
        """,(id_device,)
    )
    result = cur.fetchone()
    return result

def get_nombre_evenement(cur):
    cur.execute(
        """
        SELECT COUNT(*) FROM t_evenement_device
        """
    )
    result = cur.fetchone()
    return result

def get_nombre_evenement_device(cur,id_device):
    cur.execute(
        """
        SELECT COUNT(*) FROM t_evenement_device WHERE id_device = %s
        """,(id_device,)
    )
    result = cur.fetchone()
    return result

def get_nombre_evenement_type(cur,id_type_evenement):
    cur.execute(
        """
        SELECT COUNT(*) FROM t_evenement_device WHERE id_type_evenement = %s
        """,(id_type_evenement,)
    )
    result = cur.fetchone()
    return result

def get_evenements_by_device_and_type(cur,id_device,id_type_evenement):
    cur.execute(
        """
        SELECT * FROM t_evenement_device
        WHERE id_device = %s AND id_type_evenement = %s
        ORDER BY date_evenement DESC
        """,(id_device,id_type_evenement,)
    )
    result = cur.fetchall()
    return result

def get_evenements_by_device_type_and_period(cur,id_device,id_type_evenement,date_debut,date_fin):
    cur.execute(
        """
        SELECT * FROM t_evenement_device
        WHERE id_device = %s AND id_type_evenement = %s AND date_evenement BETWEEN %s AND %s
        ORDER BY date_evenement DESC
        """,(id_device,id_type_evenement,date_debut,date_fin,)
    )
    result = cur.fetchall()
    return result

def get_evenements_by_type_and_period(cur,id_type_evenement,date_debut,date_fin):
    cur.execute(
        """
        SELECT * FROM t_evenement_device
        WHERE id_type_evenement = %s AND date_evenement BETWEEN %s AND %s
        ORDER BY date_evenement DESC
        """,(id_type_evenement,date_debut,date_fin,)
    )
    result = cur.fetchall()
    return result

def create_evenement_device(cur,id_device,id_type_evenement,date_evenement,details):
    cur.execute(
        """
        INSERT INTO t_evenement_device (id_device, id_type_evenement, date_evenement, details)
        VALUES (%s, %s, %s, %s);
        """, (id_device,id_type_evenement,date_evenement,details)
    )