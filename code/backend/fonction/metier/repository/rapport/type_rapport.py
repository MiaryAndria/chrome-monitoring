from backend.fonction.conn.connexion import get_connection


def get_liste_type_rapport(cur):
    cur.execute(
        """
        SELECT * FROM t_type_rapport
        """
    )
    result = cur.fetchall()
    return result

def get_type_rapport_by_id(cur,id):
    cur.execute(
        """
        SELECT * FROM t_type_rapport WHERE id = %s
        """,(id,)
    )
    result = cur.fetchone()
    return result

def get_type_rapport_by_type(cur,type):
    cur.execute(
        """
        SELECT * FROM t_type_rapport WHERE type = %s
        """,(type,)
    )
    result = cur.fetchone()
    return result

def create_type_rapport(cur,type):
    cur.execute(
        """
        INSERT INTO t_type_rapport (type) VALUES (%s)
        ON CONFLICT (type) DO UPDATE SET type = EXCLUDED.type
        RETURNING id;
    """, (type,)
    )
    result = cur.fetchone()
    return result 
