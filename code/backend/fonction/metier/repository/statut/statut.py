from backend.fonction.metier.repository.statut.constants import IDS_STATUTS_DEVICE

def get_liste_statut(cur):
    cur.execute(
        """
        SELECT id, nom
        FROM t_statut
        WHERE id = ANY(%s)
        ORDER BY id ASC
        """,
        (list(IDS_STATUTS_DEVICE),)
    )
    return cur.fetchall()


def get_statut_by_id(cur, id_statut):
    cur.execute("SELECT id, nom FROM t_statut WHERE id = %s;", (id_statut,))
    return cur.fetchone()


def get_statut_by_name(cur, nom):
    cur.execute("SELECT * FROM t_statut WHERE nom = %s;", (nom,))
    return cur.fetchone()

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


def get_id_status_actuel_device(cur, id_device):
    cur.execute(
        """
        SELECT ds.id_statut
        FROM t_device_statut ds
        WHERE ds.id_device = %s
        ORDER BY ds.date DESC, ds.id DESC
        LIMIT 1
        """,
        (id_device,)
    )
    result = cur.fetchone()
    return result[0] if result else None


def get_liste_statut_all(cur):
    cur.execute(
        """
        SELECT id, nom
        FROM t_statut
        ORDER BY id ASC
        """
    )
    return cur.fetchall()


def find_statuts_paginated(cur, page=1, page_size=10):
    offset = (page - 1) * page_size
    cur.execute(
        """
        SELECT id, nom, COUNT(*) OVER() AS total
        FROM t_statut
        ORDER BY id ASC
        LIMIT %s OFFSET %s
        """,
        (page_size, offset)
    )
    return cur.fetchall()


def update_statut(cur, id_statut, nom):
    cur.execute(
        """
        UPDATE t_statut
        SET nom = %s
        WHERE id = %s
        RETURNING id
        """,
        (nom, id_statut)
    )
    row = cur.fetchone()
    return row[0] if row else None

