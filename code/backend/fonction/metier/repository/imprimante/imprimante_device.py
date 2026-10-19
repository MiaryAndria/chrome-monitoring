def get_liste_imprimante_device(cur):
    cur.execute(
        """
        SELECT * FROM t_imprimante_device
        """
    )
    result = cur.fetchall()
    return result

def get_imprimante_device_by_id(cur,id):
    cur.execute(
        """
        SELECT * FROM t_imprimante_device WHERE id = %s
        """,(id,)
    )
    result = cur.fetchone()
    return result

def get_devices_by_imprimante(cur,id_imprimante):
    cur.execute(
        """
        SELECT * FROM t_imprimante_device WHERE id_imprimante = %s
        ORDER BY derniere_detection DESC
        """,(id_imprimante,)
    )
    result = cur.fetchall()
    return result

def get_imprimante_device_by_id_imprimante(cur,id_imprimante):
    cur.execute (
    """
    SELECT * FROM t_imprimante_device where id_imprimante =%s
    """,(id_imprimante)
    )
    result = cur.fetchone()
    return result

def get_imprimantes_by_device(cur,id_device):
    cur.execute(
        """
        SELECT * FROM t_imprimante_device WHERE id_device = %s
        ORDER BY derniere_detection DESC
        """,(id_device,)
    )
    result = cur.fetchall()
    return result

def get_imprimantes_actuelles_by_device(cur,id_device):
    cur.execute(
        """
        SELECT * FROM t_imprimante_device
        WHERE id_device = %s
        ORDER BY derniere_detection DESC
        """,(id_device,)
    )
    result = cur.fetchall()
    return result

def get_liste_imprimante_device_by_id_device_id_imprimante(cur,id_imprimante,id_device):
    cur.execute(
    """
    SELECT * FROM t_imprimante_device WHERE id_imprimante = %s AND id_device = %s 
    """,(id_imprimante,id_device)
    )
    
    result = cur.fetchone()
    return result 

def get_devices_actuels_by_imprimante(cur,id_imprimante):
    cur.execute(
        """
        SELECT * FROM t_imprimante_device
        WHERE id_imprimante = %s
        ORDER BY derniere_detection DESC
        """,(id_imprimante,)
    )
    result = cur.fetchall()
    return result

def get_historique_imprimante_device(cur,id_imprimante,id_device):
    cur.execute(
        """
        SELECT * FROM t_imprimante_device
        WHERE id_imprimante = %s AND id_device = %s
        ORDER BY premiere_detection DESC
        """,(id_imprimante,id_device,)
    )
    result = cur.fetchall()
    return result

def insert_imprimante_device(cur, id_imprimante, id_device, date):
    cur.execute("""
        INSERT INTO t_imprimante_device (id_imprimante, id_device, date)
        VALUES (%s, %s, %s)
        ON CONFLICT (id_imprimante, id_device, date) DO NOTHING
        RETURNING id
    """, (id_imprimante, id_device, date))
    return cur.fetchone() is not None  


def get_devices_by_imprimante(cur, id_imprimante):
    """
    Retourne la liste des devices sur lesquels une imprimante a été détectée.
    Chaque device est retourné avec sa dernière date de détection.
    """
    cur.execute("""
        SELECT DISTINCT ON (d.id)
            d.id                AS id_device,
            d.device_id         AS device_uuid,
            d.serial_number,
            d.modele,
            d.ip_adress,
            d.mac_adress,
            d.chromeos_version,
            idv.date            AS derniere_detection
        FROM t_imprimante_device idv
        JOIN t_device d ON d.id = idv.id_device
        WHERE idv.id_imprimante = %s
        ORDER BY d.id, idv.date DESC
    """, (id_imprimante,))

    rows = cur.fetchall()
    return [
        {
            "id_device": r[0],
            "device_id": r[1],
            "serial_number": r[2],
            "modele": r[3],
            "ip_adress": r[4],
            "mac_adress": r[5],
            "chromeos_version": r[6],
            "derniere_detection": r[7],
        }
        for r in rows
    ]