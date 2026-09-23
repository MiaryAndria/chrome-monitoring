from backend.fonction.conn.connexion import get_connection

def get_liste_type_appareil(cur):
    cur.execute(
        """
        SELECT * FROM t_type_appareil
        """
    )
    result = cur.fetchall()
    return result

def get_type_appareil_by_id(cur,id):
    cur.execute(
    """
    SELECT * FROM t_type_appareil WHERE id = %s 
    """,(id,)
    )
    result = cur.fetchone()
    return result 

def get_type_appareil_by_name(cur,name):
    cur.execute(
    """
    SELECT * FROM t_type_appareil WHERE nom = %s
    """,(name,)
    )
    result = cur.fetchone()
    return result 

def delete_appareil(cur,id):
    cur.execute(
    """
    DELETE FROM t_type_appareil WHERE id = %s
    """,(id,)
    )

def delete_all(cur):
    cur.execute(
        """
        TRUNCATE TABLE t_type_appareil RESTART IDENTITY CASCADE
        """,
    )

def insert_type_appareil(cur,type_device):
    cur.execute("SELECT 1 FROM t_type_appareil WHERE nom = %s", (type_device,))
    if cur.fetchone() is None:
        cur.execute("INSERT INTO t_type_appareil (nom) VALUES (%s)", (type_device,))
        
def get_or_create_type_appareil(cur, type_device):
    type_appareil = get_type_appareil_by_name(cur,type_device)
    if type_appareil:
        return type_appareil

    insert_type_appareil(cur, type_device)

    return get_type_appareil_by_name(
        cur,
        type_device
    )