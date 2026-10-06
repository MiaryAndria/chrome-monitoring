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
    INSERT INTO t_reseau(valeur) VALUES(%s) RETURNING id, valeur;
    """,(valeur,)
    )
    return cur.fetchone()

def get_or_create_reseau(cur, valeur):
    existing = get_reseau_by_valeur(cur, valeur)
    if existing:
        return existing[0]
    inserted = insert_reseau(cur, valeur)
    return inserted[0] if inserted else None