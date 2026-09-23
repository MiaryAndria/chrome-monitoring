from backend.fonction.conn.connexion import get_connection

connexion = get_connection()
cur=connexion.cursor()

def get_liste_version_report(cur):
    cur.execute(
        """
        SELECT * FROM t_version_report
        """
    )
    result = cur.fetchall()
    return result

def get_version_report_by_id(cur,id):
    cur.execute(
        """
        SELECT * FROM t_version_report WHERE id = %s
        """,(id,)
    )
    result = cur.fetchone()
    return result

def get_version_by_device(cur,id_device):
    cur.execute(
        """
        SELECT * FROM t_version_report WHERE id_device = %s
        ORDER BY date_observation DESC
        """,(id_device,)
    )
    result = cur.fetchall()
    return result

def get_version_by_period(cur,id_device,date_debut,date_fin):
    cur.execute(
        """
        SELECT * FROM t_version_report
        WHERE id_device = %s AND date_observation BETWEEN %s AND %s
        ORDER BY date_observation DESC
        """,(id_device,date_debut,date_fin,)
    )
    result = cur.fetchall()
    return result

def get_derniere_version_device(cur,id_device):
    cur.execute(
        """
        SELECT * FROM t_version_report
        WHERE id_device = %s
        ORDER BY date_observation DESC
        LIMIT 1
        """,(id_device,)
    )
    result = cur.fetchone()
    return result

def get_devices_by_chromeos_version(cur,version):
    cur.execute(
        """
        SELECT * FROM t_version_report WHERE chromeos_version = %s
        ORDER BY date_observation DESC
        """,(version,)
    )
    result = cur.fetchall()
    return result

def get_devices_by_chrome_version(cur,version):
    cur.execute(
        """
        SELECT * FROM t_version_report WHERE chrome_version = %s
        ORDER BY date_observation DESC
        """,(version,)
    )
    result = cur.fetchall()
    return result

def get_version_by_device_and_chromeos(cur,id_device,chromeos_version):
    cur.execute(
        """
        SELECT * FROM t_version_report
        WHERE id_device = %s AND chromeos_version = %s
        ORDER BY date_observation DESC
        """,(id_device,chromeos_version,)
    )
    result = cur.fetchall()
    return result

def get_version_by_device_and_chrome(cur,id_device,chrome_version):
    cur.execute(
        """
        SELECT * FROM t_version_report
        WHERE id_device = %s AND chrome_version = %s
        ORDER BY date_observation DESC
        """,(id_device,chrome_version,)
    )
    result = cur.fetchall()
    return result

def get_version_by_chromeos_and_chrome(cur,chromeos_version,chrome_version):
    cur.execute(
        """
        SELECT * FROM t_version_report
        WHERE chromeos_version = %s AND chrome_version = %s
        ORDER BY date_observation DESC
        """,(chromeos_version,chrome_version,)
    )
    result = cur.fetchall()
    return result

