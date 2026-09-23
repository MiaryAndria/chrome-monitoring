from backend.fonction.conn.connexion import get_connection
connexion = get_connection()
cur=connexion.cursor()

def get_liste_statut(cur):
    cur.execute("SELECT * FROM t_statut;")
    return cur.fetchall()

def get_statut_by_id(cur, id):
    cur.execute("SELECT * FROM t_statut WHERE id = %s;", (id,))
    return cur.fetchone()

def get_statut_by_name(cur, nom):
    cur.execute("SELECT * FROM t_statut WHERE nom = %s;", (nom,))
    return cur.fetchone()

def get_or_create_statut(cur, nom):
    statut = get_statut_by_name(cur, nom)
    if statut:
        return statut
    cur.execute(
        """
        INSERT INTO t_statut (nom)
        SELECT %s
        WHERE NOT EXISTS (SELECT 1 FROM t_statut WHERE nom = %s);
        """,
        (nom, nom)
    )
    return get_statut_by_name(cur, nom)

def insert_device_statut(cur, id_device, id_statut):
    cur.execute(
        """
        INSERT INTO t_device_statut (id_device, id_statut)
        VALUES (%s, %s);
        """,
        (id_device, id_statut)
    )

def get_status_actuel_device(cur, id_device):
    cur.execute(
        """
        SELECT s.nom 
        FROM t_device_statut ds
        JOIN t_statut s ON ds.id_statut = s.id
        WHERE ds.id_device = %s
        ORDER BY ds.date DESC
        LIMIT 1
        """,
        (id_device,)
    )
    result = cur.fetchone()
    return result[0] if result else "UNKNOWN"