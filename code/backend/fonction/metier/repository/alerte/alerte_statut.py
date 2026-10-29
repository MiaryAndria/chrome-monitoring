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


