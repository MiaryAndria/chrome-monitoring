def get_liste_evenement_device(cur):
    cur.execute(
        """
        SELECT * FROM t_evenement_device
        """
    )
    result = cur.fetchall()
    return result

def get_evenement_by_id(cur,id):
    cur.execute(
        """
        SELECT * FROM t_evenement_device WHERE id = %s
        """,(id,)
    )
    result = cur.fetchone()
    return result

def get_evenements_by_device(cur,id_device):
    cur.execute(
        """
        SELECT * FROM t_evenement_device WHERE id_device = %s
        ORDER BY date_evenement DESC
        """,(id_device,)
    )
    result = cur.fetchall()
    return result

def get_evenements_by_type(cur,id_type_evenement):
    cur.execute(
        """
        SELECT * FROM t_evenement_device WHERE id_type_evenement = %s
        ORDER BY date_evenement DESC
        """,(id_type_evenement,)
    )
    result = cur.fetchall()
    return result

def get_evenements_by_period(cur,date_debut,date_fin):
    cur.execute(
        """
        SELECT * FROM t_evenement_device
        WHERE date_evenement BETWEEN %s AND %s
        ORDER BY date_evenement DESC
        """,(date_debut,date_fin,)
    )
    result = cur.fetchall()
    return result

def get_evenements_device_by_period(cur,id_device,date_debut,date_fin):
    cur.execute(
        """
        SELECT * FROM t_evenement_device
        WHERE id_device = %s AND date_evenement BETWEEN %s AND %s
        ORDER BY date_evenement DESC
        """,(id_device,date_debut,date_fin,)
    )
    result = cur.fetchall()
    return result

def get_dernier_evenement_device(cur,id_device):
    cur.execute(
        """
        SELECT * FROM t_evenement_device
        WHERE id_device = %s
        ORDER BY date_evenement DESC
        LIMIT 1
        """,(id_device,)
    )
    result = cur.fetchone()
    return result


def get_last_event_date(cur, id_device):
    cur.execute(
        """
        SELECT MAX(date_evenement)
        FROM t_evenement_device
        WHERE id_device = %s
        """,
        (id_device,)
    )
    row = cur.fetchone()
    return row[0] if row else None

def get_nombre_evenement(cur):
    cur.execute(
        """
        SELECT COUNT(*) FROM t_evenement_device
        """
    )
    result = cur.fetchone()
    return result

def get_nombre_evenement_device(cur,id_device):
    cur.execute(
        """
        SELECT COUNT(*) FROM t_evenement_device WHERE id_device = %s
        """,(id_device,)
    )
    result = cur.fetchone()
    return result

def get_nombre_evenement_type(cur,id_type_evenement):
    cur.execute(
        """
        SELECT COUNT(*) FROM t_evenement_device WHERE id_type_evenement = %s
        """,(id_type_evenement,)
    )
    result = cur.fetchone()
    return result

def get_evenements_by_device_and_type(cur,id_device,id_type_evenement):
    cur.execute(
        """
        SELECT * FROM t_evenement_device
        WHERE id_device = %s AND id_type_evenement = %s
        ORDER BY date_evenement DESC
        """,(id_device,id_type_evenement,)
    )
    result = cur.fetchall()
    return result

def get_evenements_by_device_type_and_period(cur,id_device,id_type_evenement,date_debut,date_fin):
    cur.execute(
        """
        SELECT * FROM t_evenement_device
        WHERE id_device = %s AND id_type_evenement = %s AND date_evenement BETWEEN %s AND %s
        ORDER BY date_evenement DESC
        """,(id_device,id_type_evenement,date_debut,date_fin,)
    )
    result = cur.fetchall()
    return result

def get_evenements_by_type_and_period(cur,id_type_evenement,date_debut,date_fin):
    cur.execute(
        """
        SELECT * FROM t_evenement_device
        WHERE id_type_evenement = %s AND date_evenement BETWEEN %s AND %s
        ORDER BY date_evenement DESC
        """,(id_type_evenement,date_debut,date_fin,)
    )
    result = cur.fetchall()
    return result

def create_evenement_device(cur,id_device,id_type_evenement,date_evenement,details):
    cur.execute(
        """
        INSERT INTO t_evenement_device (id_device, id_type_evenement, date_evenement, details)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (id_device, id_type_evenement, date_evenement)
        DO UPDATE SET
            details = EXCLUDED.details;
        """, (id_device,id_type_evenement,date_evenement,details)
    )


def get_liste_evenement_avec_details(cur):
    cur.execute(
        """
        SELECT DISTINCT ON (ed.id)
            ed.id,
            ed.date_evenement,
            ed.details,
            te.type       AS type_evenement,
            d.device_id,
            d.serial_number,
            d.modele,
            f.org_unit_path AS filiale
        FROM t_evenement_device ed
        LEFT JOIN t_type_evenement te  ON te.id = ed.id_type_evenement
        LEFT JOIN t_device         d   ON d.id  = ed.id_device
        LEFT JOIN t_device_filiale df  ON df.id_device = d.id
        LEFT JOIN t_filiale        f   ON f.id = df.id_filiale
        ORDER BY ed.id, ed.date_evenement DESC
        """
    )
    return cur.fetchall()


def _rows_to_dicts(cur):
    colonnes = [desc[0] for desc in cur.description]
    return [dict(zip(colonnes, row)) for row in cur.fetchall()]


def _build_evenement_filter_clause(type_evenement=None, id_filiale=None,
                                   filiale=None, recherche=None,
                                   datetime_from=None, datetime_to=None):
    clauses = []
    params = []

    if type_evenement:
        clauses.append("type_evenement = %s")
        params.append(type_evenement)
    if id_filiale is not None:
        clauses.append("id_filiale = %s")
        params.append(id_filiale)
    if filiale:
        clauses.append("filiale = %s")
        params.append(filiale)
    if recherche:
        terme = f"%{recherche}%"
        clauses.append(
            "(type_evenement ILIKE %s OR device_id ILIKE %s "
            "OR serial_number ILIKE %s OR modele ILIKE %s "
            "OR filiale ILIKE %s OR COALESCE(details->>'cause_class', '') ILIKE %s "
            "OR COALESCE(details->>'last_user', '') ILIKE %s)"
        )
        params.extend([terme] * 7)
    if datetime_from is not None:
        clauses.append("date_evenement >= %s")
        params.append(datetime_from)
    if datetime_to is not None:
        clauses.append("date_evenement <= %s")
        params.append(datetime_to)

    return clauses, params


def find_evenements_paginated(cur, page=1, page_size=10, type_evenement=None,
                              id_filiale=None, filiale=None, recherche=None,
                              datetime_from=None, datetime_to=None):
    clauses, params = _build_evenement_filter_clause(
        type_evenement, id_filiale, filiale, recherche, datetime_from, datetime_to
    )
    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    offset = (page - 1) * page_size

    cur.execute(
        f"""
        SELECT
            id, date_evenement, details, type_evenement, id_device,
            device_id, serial_number, modele, id_filiale, filiale,
            COUNT(*) OVER() AS total
        FROM v_evenements_avec_appareil
        {where}
        ORDER BY date_evenement DESC, id DESC
        LIMIT %s OFFSET %s
        """,
        tuple(params + [page_size, offset])
    )
    return _rows_to_dicts(cur)

