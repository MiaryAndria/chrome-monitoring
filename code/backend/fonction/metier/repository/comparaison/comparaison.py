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
    result = cur.fetchall()
    return result


def find_comparaisons_paginated(cur, page=1, page_size=10, datetime_from=None, datetime_to=None):
    offset = (page - 1) * page_size
    query = """
        SELECT c.id, c.id_device_a, c.id_device_b, c.id_type_comparaison,
               c.date_reference_a, c.date_reference_b, c.date_comparaison, c.resultat,
               c.version_a, c.version_b,
               da.serial_number AS device_a,
               db.serial_number AS device_b,
               COUNT(*) OVER() AS total
        FROM t_comparaison c
        LEFT JOIN t_device da ON da.id = c.id_device_a
        LEFT JOIN t_device db ON db.id = c.id_device_b
    """
    clauses = []
    params = []
    if datetime_from is not None:
        clauses.append("c.date_comparaison >= %s")
        params.append(datetime_from)
    if datetime_to is not None:
        clauses.append("c.date_comparaison <= %s")
        params.append(datetime_to)
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY c.date_comparaison DESC, c.id DESC LIMIT %s OFFSET %s"
    params.extend([page_size, offset])
    cur.execute(query, tuple(params))
    return cur.fetchall()


def get_comparaison_by_id(cur, id):
    cur.execute(
        """
        SELECT c.id, c.id_device_a, c.id_device_b, c.id_type_comparaison,
               c.date_reference_a, c.date_reference_b, c.date_comparaison, c.resultat,
               c.version_a, c.version_b,
               da.serial_number AS device_a,
               db.serial_number AS device_b
        FROM t_comparaison c
        LEFT JOIN t_device da ON da.id = c.id_device_a
        LEFT JOIN t_device db ON db.id = c.id_device_b
        WHERE c.id = %s
        """,
        (id,)
    )
    return cur.fetchone()


def insert_comparaison(cur, id_device_a, id_device_b, date_reference_a, date_reference_b,
                       id_type_comparaison, version_a, version_b, resultat=None):
    """
    Insère une comparaison (resultat NULL au départ) et retourne son id.
    La colonne PK réelle de t_comparaison est `id` (pas `id_comparaison`).
    """
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
