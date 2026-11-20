from datetime import datetime

def insert_evenement_statut(cur, id_evenement, id_statut, date=None):
    date_value = date or datetime.now()
    cur.execute(
        """
        INSERT INTO t_evenement_statut (id_evenement, id_statut, date)
        VALUES (%s, %s, %s)
        """,
        (id_evenement, id_statut, date_value),
    )
    return True



def get_statut_evenement(cur, id_evenement):
    cur.execute(
        """
        SELECT *
        FROM t_evenement_statut
        WHERE id_evenement = %s
        ORDER BY id DESC
        LIMIT 1
        """,
        (id_evenement,)
    )
    return cur.fetchone()