def insert_synchronisation_statut(cur, id_statut, id_synchronisation, date):
    cur.execute(
        """
        INSERT INTO t_statut_synchronisation (id_statut, id_synchronisation, date)
        VALUES (%s, %s, %s);
        """,
        (id_statut, id_synchronisation, date),
    )


# Compatibilité avec l'ancien nom
insert_synchronisaton_statut = insert_synchronisation_statut
