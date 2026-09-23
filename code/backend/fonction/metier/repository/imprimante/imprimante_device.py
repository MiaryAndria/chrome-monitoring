from backend.fonction.conn.connexion import get_connection

connexion = get_connection()
cur=connexion.cursor()

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
