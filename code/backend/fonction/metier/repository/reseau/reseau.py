from backend.fonction.conn.connexion import get_connection

def get_liste_reseau(cur):
    cur.execute(
    """
    SELECT * FROM t_reseau
    """,
    )
    result=cur.fetchall()
    return result 

def get_reseau_by_id(cur,id):
    cur.execute(
    """
    SELECT * FROM t_reseau where id =%s
    """,(id,)
    )
    result = cur.fetchone()
    return result 

def get_reseau_by_valeur(cur,valeur):
    cur.execute(
    """
    SELECT * FROM t_reseau where valeur =%s
    """,(valeur,)
    )
    result = cur.fetchone()
    return result 

def insert_reseau(cur,valeur):
    cur.execute(
    """
    INSERT INTO t_reseau(valeur)VALUES(%s)
    """,(valeur,)
    )