from backend.fonction.conn.connexion import get_connection

def get_liste_type_evenement(cur):
    cur.execute(
        """
        SELECT * FROM t_type_evenement
        """
    )
    result = cur.fetchall()
    return result

def get_type_evenement_by_id(cur,id):
    cur.execute(
        """
        SELECT * FROM t_type_evenement WHERE id = %s
        """,(id,)
    )
    result = cur.fetchone()
    return result

def get_type_evenement_by_type(cur,type):
    cur.execute(
        """
        SELECT * FROM t_type_evenement WHERE type = %s
        """,(type,)
    )
    result = cur.fetchone()
    return result

def create_type_evenement(cur, type_evenement):
    cur.execute(
        """
        INSERT INTO t_type_evenement (type) VALUES (%s)
        ON CONFLICT (type) DO UPDATE SET type = EXCLUDED.type
        RETURNING id;
        """,
        (type_evenement,)
    )
    return cur.fetchone()
    
