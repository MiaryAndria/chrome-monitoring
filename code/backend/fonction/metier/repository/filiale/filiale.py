from backend.fonction.conn.connexion import get_connection

def get_liste_filiale(cur):
    cur.execute("SELECT * FROM t_filiale;")
    return cur.fetchall()

def get_filiale_by_id(cur, id):
    cur.execute("SELECT * FROM t_filiale WHERE id = %s;", (id,))
    return cur.fetchone()

def get_filiale_by_org_unit(cur, unit_path):
    cur.execute("SELECT * FROM t_filiale WHERE org_unit_path = %s;", (unit_path,))
    return cur.fetchone()

def insert_filiale(cur, org_unit_path):
    cur.execute(
        """
        INSERT INTO t_filiale (org_unit_path) VALUES (%s)
        ON CONFLICT (org_unit_path) DO NOTHING
        RETURNING id;
        """,
        (org_unit_path,)
    )
    return cur.fetchone()

def get_or_create_filiale(cur, org_unit_path):
    filiale = get_filiale_by_org_unit(cur, org_unit_path)
    if filiale:
        return filiale

    insert_filiale(cur, org_unit_path)
    return get_filiale_by_org_unit(cur, org_unit_path)