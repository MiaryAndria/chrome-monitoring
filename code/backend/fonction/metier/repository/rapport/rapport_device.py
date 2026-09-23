from backend.fonction.conn.connexion import get_connection


def get_liste_rapport_device(cur):
    cur.execute(
        """
        SELECT * FROM t_rapport_device
        """
    )
    result = cur.fetchall()
    return result

def get_rapport_device_by_id(cur,id):
    cur.execute(
        """
        SELECT * FROM t_rapport_device WHERE id = %s
        """,(id,)
    )
    result = cur.fetchone()
    return result

def get_rapport_by_device(cur,id_device):
    cur.execute(
        """
        SELECT * FROM t_rapport_device WHERE id_device = %s
        ORDER BY report_time DESC
        """,(id_device,)
    )
    result = cur.fetchall()
    return result

def get_rapport_by_type(cur,id_type_rapport):
    cur.execute(
        """
        SELECT * FROM t_rapport_device WHERE id_type_rapport = %s
        ORDER BY report_time DESC
        """,(id_type_rapport,)
    )
    result = cur.fetchall()
    return result

def get_rapport_device_by_period(cur,id_device,date_debut,date_fin):
    cur.execute(
        """
        SELECT * FROM t_rapport_device
        WHERE id_device = %s AND report_time BETWEEN %s AND %s
        ORDER BY report_time DESC
        """,(id_device,date_debut,date_fin,)
    )
    result = cur.fetchall()
    return result

def get_dernier_rapport_device(cur,id_device):
    cur.execute(
        """
        SELECT * FROM t_rapport_device
        WHERE id_device = %s
        ORDER BY report_time DESC
        LIMIT 1
        """,(id_device,)
    )
    result = cur.fetchone()
    return result

def get_rapport_by_device_and_type(cur,id_device,id_type_rapport):
    cur.execute(
        """
        SELECT * FROM t_rapport_device
        WHERE id_device = %s AND id_type_rapport = %s
        ORDER BY report_time DESC
        """,(id_device,id_type_rapport,)
    )
    result = cur.fetchall()
    return result

def get_rapport_by_device_date(cur,id_device,date):
    cur.execute(
        """
        SELECT * FROM t_rapport_device
        WHERE id_device = %s AND DATE(report_time) = %s
        ORDER BY report_time DESC
        """,(id_device,date,)
    )
    result = cur.fetchall()
    return result

def get_rapport_by_type_and_period(cur,id_type_rapport,date_debut,date_fin):
    cur.execute(
        """
        SELECT * FROM t_rapport_device
        WHERE id_type_rapport = %s AND report_time BETWEEN %s AND %s
        ORDER BY report_time DESC
        """,(id_type_rapport,date_debut,date_fin,)
    )
    result = cur.fetchall()
    return result

def get_rapport_by_device_type_and_period(cur,id_device,id_type_rapport,date_debut,date_fin):
    cur.execute(
        """
        SELECT * FROM t_rapport_device
        WHERE id_device = %s AND id_type_rapport = %s AND report_time BETWEEN %s AND %s
        ORDER BY report_time DESC
        """,
        (id_device,id_type_rapport,date_debut,date_fin,)
    )
    result = cur.fetchall()
    return result

def create_rapport_device(cur,device_id,id_type_rapport,date_releve,data):
    cur.execute(
    """
    INSERT INTO t_rapport_device (id_device, id_type_rapport, report_time, donnees)
    VALUES (%s, %s, %s, %s);
    """, 
    (device_id, id_type_rapport, date_releve, data)
    )