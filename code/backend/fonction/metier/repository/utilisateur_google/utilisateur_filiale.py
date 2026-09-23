from backend.fonction.conn.connexion import get_connection
connexion = get_connection()
cur=connexion.cursor()

def get_liste_filiale_utilisateur (cur):
    cur.execute(
    """
    SELECT * FROM t_filiale_utilisateur
    """,
    )
    result = cur.fetchall()
    return result 

def get_filiale_utilisateur_by_id(cur,id):
    cur.execute(
    """
    SELECT * FROM t_filiale_utilisateur WHERE id=%s
    """,(id,)
    )
    result = cur.fetchone()
    return result 

def get_utilisateurs_by_filiale(cur,id_filiale):
    cur.execute(
    """
    SELECT * FROM t_filiale_utilisateur WHERE id_filiale=%s
    """,(id_filiale,)
    )
    result = cur.fetchone()
    return result 

def get_filiales_by_utilisateur(cur,id_utilisteur):
    cur.execute(
    """
    SELECT * FROM t_filiale_utilisateur WHERE id_utilisateur = %s
    """,(id_utilisteur,)
    )
    result = cur.fetchone()
    return result

def get_filiale_by_utilisateur_and_filiale(cur,id_utilisateur,id_filiale):
    cur.execute(
    """
    SELECT * FROM t_filiale_utilisateur WHERE id_utilisateur =%s AND id_filiale=%s
    """,(id_utilisateur,id_filiale,)
    )
    result = cur.fetchone()
    return result 

def insert_filiale_utilisateur(cur,id_filiale,id_utilisateur):
    cur.execute(
        """
        INSERT INTO t_filiale_utilisateur(id_filiale,id_utilisateur)VALUES(%s,%s)
        """,(id_filiale,id_utilisateur)
    )

def get_or_create_filiale_utilisateur(cur,id_filiale,id_utilisateur):
    filiale_utilisateur = get_filiale_by_utilisateur_and_filiale(cur,id_utilisateur,id_filiale)
    if filiale_utilisateur:
        return filiale_utilisateur
    else:
        insert_filiale_utilisateur(cur,id_filiale,id_utilisateur)