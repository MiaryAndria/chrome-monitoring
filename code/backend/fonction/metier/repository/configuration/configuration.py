from backend.fonction.conn.connexion import get_connection

connexion = get_connection()
cur=connexion.cursor()

def get_liste_configuration(cur):
    cur.execute(
        """
        SELECT * FROM t_configuration
        """
    )
    result = cur.fetchall()
    return result

def get_configuration_by_id(cur,id):
    cur.execute(
        """
        SELECT * FROM t_configuration WHERE id = %s
        """,(id,)
    )
    result = cur.fetchone()
    return result

def get_configuration_by_type(cur,type):
    cur.execute(
        """
        SELECT * FROM t_configuration WHERE type = %s
        """,(type,)
    )
    result = cur.fetchone()
    return result

def get_valeur_configuration(cur,type):
    cur.execute(
        """
        SELECT valeur FROM t_configuration WHERE type = %s
        """,(type,)
    )
    result = cur.fetchone()
    return result
