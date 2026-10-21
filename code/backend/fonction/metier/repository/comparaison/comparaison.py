from backend.fonction.conn.connexion import get_connection

connexion = get_connection()
cur=connexion.cursor()

def get_liste_comparaison(cur):
    cur.execute(
        """
        SELECT * FROM t_comparaison
        """
    )
    result = cur.fetchall()
    return result

def get_comparaison_by_id(cur,id):
    cur.execute(
        """
        SELECT * FROM t_comparaison WHERE id = %s
        """,(id,)
    )
    result = cur.fetchone()
    return result

def get_comparaison_by_device(cur,id_device):
    cur.execute(
        """
        SELECT * FROM t_comparaison
        WHERE id_device_a = %s OR id_device_b = %s
        ORDER BY date_comparaison DESC
        """,(id_device,id_device,)
    )
    result = cur.fetchall()
    return result

def get_comparaisons_device_a(cur,id_device_a):
    cur.execute(
        """
        SELECT * FROM t_comparaison WHERE id_device_a = %s
        ORDER BY date_comparaison DESC
        """,(id_device_a,)
    )
    result = cur.fetchall()
    return result

def get_comparaisons_device_b(cur,id_device_b):
    cur.execute(
        """
        SELECT * FROM t_comparaison WHERE id_device_b = %s
        ORDER BY date_comparaison DESC
        """,(id_device_b,)
    )
    result = cur.fetchall()
    return result

def get_comparaisons_between_devices(cur,id_device_a,id_device_b):
    cur.execute(
        """
        SELECT * FROM t_comparaison
        WHERE id_device_a = %s AND id_device_b = %s
        ORDER BY date_comparaison DESC
        """,(id_device_a,id_device_b,)
    )
    result = cur.fetchall()
    return result

def get_comparaisons_by_period(cur,date_debut,date_fin):
    cur.execute(
        """
        SELECT * FROM t_comparaison
        WHERE date_comparaison BETWEEN %s AND %s
        ORDER BY date_comparaison DESC
        """,(date_debut,date_fin,)
    )
    result = cur.fetchall()
    return result

def get_derniere_comparaison(cur,id_device_a,id_device_b):
    cur.execute(
        """
        SELECT * FROM t_comparaison
        WHERE id_device_a = %s AND id_device_b = %s
        ORDER BY date_comparaison DESC
        LIMIT 1
        """,(id_device_a,id_device_b,)
    )
    result = cur.fetchone()
    return result

def get_comparaisons_between_devices_by_period(cur,id_device_a,id_device_b,date_debut,date_fin):
    cur.execute(
        """
        SELECT * FROM t_comparaison
        WHERE id_device_a = %s AND id_device_b = %s AND date_comparaison BETWEEN %s AND %s
        ORDER BY date_comparaison DESC
        """,(id_device_a,id_device_b,date_debut,date_fin,)
    )
    result = cur.fetchall()
    return result

def get_comparaisons_device_a_by_period(cur,id_device_a,date_debut,date_fin):
    cur.execute(
        """
        SELECT * FROM t_comparaison
        WHERE id_device_a = %s AND date_comparaison BETWEEN %s AND %s
        ORDER BY date_comparaison DESC
        """,(id_device_a,date_debut,date_fin,)
    )
    result = cur.fetchall()
    return result

def get_comparaisons_device_b_by_period(cur,id_device_b,date_debut,date_fin):
    cur.execute(
        """
        SELECT * FROM t_comparaison
        WHERE id_device_b = %s AND date_comparaison BETWEEN %s AND %s
        ORDER BY date_comparaison DESC
        """,(id_device_b,date_debut,date_fin,)
    )
    result = cur.fetchall()
    return result

def insert_comparaison_simple(cur, id1, id2, date1, date2, resultat, id_type_comparaison):
    cur.execute(
        """
        INSERT INTO t_comparaison
            (id_device_a, id_device_b, date_reference_a, date_reference_b, resultat, id_type_comparaison)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id_comparaison
        """,
        (id1, id2, date1, date2, resultat, id_type_comparaison)
    )
    return cur.fetchone()

def insert_comparaison_double(cur, id1, id2, date1, date2, resultat, id_type_comparaison):
    cur.execute(
        """
        INSERT INTO t_comparaison
            (id_device_a, id_device_b, date_reference_a, date_reference_b, resultat, id_type_comparaison)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id_comparaison
        """,
        (id1, id2, date1, date2, resultat, id_type_comparaison)
    )
    return cur.fetchone()

def insert_comparaison_statut(cur,id_comparaison,id_statut):
    cur.execute(
    """
    INSERT INTO t_statut_comparaison(id_comparaison,id_statut)VALUES(%s,%s)
    """,(id_comparaison,id_statut)
    )