from backend.fonction.conn.connexion import get_connection

connexion = get_connection()
cur=connexion.cursor()

def get_liste_alerte(cur):
    cur.execute(
        """
        SELECT * FROM t_alerte
        """
    )
    result = cur.fetchall()
    return result

def get_alerte_by_id(cur,id):
    cur.execute(
        """
        SELECT * FROM t_alerte WHERE id = %s
        """,(id,)
    )
    result = cur.fetchone()
    return result

def get_alerte_by_type(cur,type):
    cur.execute(
        """
        SELECT * FROM t_alerte WHERE type = %s
        """,(type,)
    )
    result = cur.fetchone()
    return result

def get_alertes_actives(cur):
    cur.execute(
        """
        SELECT a.* FROM t_alerte a
        JOIN t_device_alerte da ON a.id = da.id_alerte
        WHERE da.date_resolution IS NULL
        GROUP BY a.id
        """
    )
    result = cur.fetchall()
    return result

def get_alertes_resolues(cur):
    cur.execute(
        """
        SELECT a.* FROM t_alerte a
        JOIN t_device_alerte da ON a.id = da.id_alerte
        WHERE da.date_resolution IS NOT NULL
        GROUP BY a.id
        """
    )
    result = cur.fetchall()
    return result
