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


def insert_evenement_statut_si_absent(cur, id_evenement, id_statut, date=None):
    """Insère un statut uniquement si l'événement n'a encore aucun historique.
    Évite de rouvrir un événement résolu ou de dupliquer un statut lors des re-sync."""
    date_value = date or datetime.now()
    cur.execute(
        """
        INSERT INTO t_evenement_statut (id_evenement, id_statut, date)
        SELECT %s, %s, %s
        WHERE NOT EXISTS (
            SELECT 1 FROM t_evenement_statut WHERE id_evenement = %s
        )
        """,
        (id_evenement, id_statut, date_value, id_evenement),
    )
    return True

