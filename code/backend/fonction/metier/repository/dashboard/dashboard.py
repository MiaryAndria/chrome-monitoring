def get_summary(cur):
    cur.execute(
        """
        SELECT nb_total_appareils, nb_actifs, nb_indisponibles,
               nb_anomalie, nb_reparation, nb_crashs, nb_incidents,
               nb_imprimantes, repartition_statuts, repartition_types,
               repartition_evenements
        FROM v_tableau_de_bord_resume
        """
    )
    row = cur.fetchone()
    if row is None:
        return None

    return {
        "nb_total_appareils": row[0],
        "nb_actifs": row[1],
        "nb_indisponibles": row[2],
        "nb_anomalie": row[3],
        "nb_reparation": row[4],
        "nb_crashs": row[5],
        "nb_incidents": row[6],
        "nb_imprimantes": row[7],
        "repartition_statuts": row[8] or {},
        "repartition_types": row[9] or {},
        "repartition_evenements": row[10] or {},
    }


__all__ = ["get_summary"]
