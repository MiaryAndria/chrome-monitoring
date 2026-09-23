from backend.fonction.conn.connexion import get_connection
connexion = get_connection()
cur = connexion.cursor()

def get_liste_reseau_filiale(cur):
    cur.execute(
    """
    SELECT * FROM t_reseau_filiale
    """,
    )
    result = cur.fetchall()
    return result 

def get_reseau_filiale_by_id(cur,id):
    cur.execute(
        """
        SELECT * FROM t_reseau_filiale WHERE id = %s
        """,(id,)
    )
    result = cur.fetchone()
    return result 

def get_reseau_by_filiale(cur,id_filiale):
    cur.execute(
    """
    SELECT * FROM t_reseau_filiale WHERE id_filiale =%s
    """,(id_filiale,)
    )
    result = cur.fetchone()
    return result 

def get_filiale_by_reseaux(cur,id_reseau):
    cur.execute(
    """
    SELECT * FROM t_reseau_filiale WHERE id_reseau = %s
    """,(id_reseau,)
    )
    result = cur.fetchone()
    return result 

def get_filiale_by_reseaux_and_filiale(cur,id_reseau,id_filiale):
    cur.execute(
        """
        SELECT * FROM t_reseau_filiale WHERE id_reseau =%s AND id_filiale=%s
        """,(id_reseau,id_filiale,)
    )
    result = cur.fetchone()
    return result 

def insert_into_reseau_filiale(cur,id_reseau,id_filiale):
    cur.execute(
    """
    INSERT INTO t_reseau_filiale(id_reseau,id_filiale) VALUES(%s , %s)
    """,(id_reseau,id_filiale,)
    )
    result = cur.fetchone()
    return result