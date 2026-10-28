def get_summary(cur):
    cur.execute(
        """
        SELECT nb_total_appareils, nb_actifs, nb_indisponibles,
               nb_anomalie, nb_reparation, nb_crashs, nb_incidents,
               nb_imprimantes, repartition_statuts, repartition_types,
               repartition_evenements, total_alerte, alerte_active, alerte_resolue
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
        "total_alerte": row[11] if row[11] is not None else 0,
        "alerte_active": row[12] if row[12] is not None else 0,
        "alerte_resolue": row[13] if row[13] is not None else 0,
    }
