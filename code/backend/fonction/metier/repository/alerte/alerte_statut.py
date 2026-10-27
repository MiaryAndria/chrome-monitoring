from datetime import datetime


def insert_alerte_statut(cur, id_alerte, id_statut, date=None):
    date_value = date or datetime.utcnow()
    cur.execute(
        """
        INSERT INTO t_alerte_statut (id_alerte, id_statut, date)
        VALUES (%s, %s, %s)
        """,
        (id_alerte, id_statut, date_value),
    )
    return True


def get_statuts_alerte(cur, id_alerte):
    cur.execute(
        """
        SELECT id, id_alerte, id_statut, date
        FROM t_alerte_statut
        WHERE id_alerte = %s
        ORDER BY date DESC, id DESC
        """,
        (id_alerte,),
    )
    return cur.fetchall()


def get_dernier_statut_alerte(cur, id_alerte):
    cur.execute(
        """
        SELECT id_statut
        FROM t_alerte_statut
        WHERE id_alerte = %s
        ORDER BY date DESC, id DESC
        LIMIT 1
        """,
        (id_alerte,),
    )
    row = cur.fetchone()
    return row[0] if row else None
