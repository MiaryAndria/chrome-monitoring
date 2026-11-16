def get_liste_comparaison(cur):
    cur.execute(
        """
        SELECT id, id_device_a, id_device_b, id_type_comparaison,
               date_reference_a, date_reference_b, date_comparaison, resultat,
               version_a, version_b
        FROM t_comparaison
        ORDER BY date_comparaison DESC
        """
    )
    return cur.fetchall()


def find_comparaisons_paginated(cur, page=1, page_size=10, datetime_from=None, datetime_to=None):
    offset = (page - 1) * page_size
    where = ""
    params = []
    if datetime_from is not None:
        where += " WHERE date_comparaison >= %s"
        params.append(datetime_from)
        if datetime_to is not None:
            where += " AND date_comparaison <= %s"
            params.append(datetime_to)
    elif datetime_to is not None:
        where += " WHERE date_comparaison <= %s"
        params.append(datetime_to)

    cur.execute(f"SELECT COUNT(*) FROM v_comparaison{where}", tuple(params))
    total = cur.fetchone()[0]

    cur.execute(
        f"""
        SELECT id, id_device_a, id_device_b, id_type_comparaison,
               date_reference_a, date_reference_b, date_comparaison, resultat,
               version_a, version_b, device_a, device_b
        FROM v_comparaison
        {where}
        ORDER BY date_comparaison DESC, id DESC
        LIMIT %s OFFSET %s
        """,
        tuple(params + [page_size, offset]),
    )
    return cur.fetchall(), total


def get_comparaison_by_id(cur, id):
    cur.execute(
        """
        SELECT id, id_device_a, id_device_b, id_type_comparaison,
               date_reference_a, date_reference_b, date_comparaison, resultat,
               version_a, version_b, device_a, device_b
        FROM v_comparaison
        WHERE id = %s
        """,
        (id,),
    )
    return cur.fetchone()


def insert_comparaison(cur, id_device_a, id_device_b, date_reference_a, date_reference_b,
                       id_type_comparaison, version_a, version_b, resultat=None):
    cur.execute(
        """
        INSERT INTO t_comparaison
            (id_device_a, id_device_b, id_type_comparaison,
             date_reference_a, date_reference_b, version_a, version_b, resultat)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (id_device_a, id_device_b, id_type_comparaison,
         date_reference_a, date_reference_b, version_a, version_b, resultat)
    )
    row = cur.fetchone()
    return row[0] if row else None


def update_comparaison_resultat(cur, id_comparaison, resultat):
    cur.execute(
        """
        UPDATE t_comparaison SET resultat = %s WHERE id = %s
        """,
        (resultat, id_comparaison)
    )


def insert_comparaison_statut(cur, id_comparaison, id_statut):
    cur.execute(
        """
        INSERT INTO t_statut_comparaison (id_comparaison, id_statut, date)
        VALUES (%s, %s, NOW())
        """,
        (id_comparaison, id_statut)
    )
