from backend.fonction.metier.repository.statut import ID_STATUT_RESOLUE

def get_evenement_by_id(cur,id):
    cur.execute(
        """
        SELECT * FROM t_evenement_device WHERE id = %s
        """,(id,)
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


def count_evenements_device_period(cur, id_device, jours):
    """Nombre d'evenements d'un device sur les `jours` derniers jours."""
    cur.execute(
        """
        SELECT COUNT(*)
        FROM t_evenement_device
        WHERE id_device = %s
          AND date_evenement >= NOW() - make_interval(days => %s)
        """,
        (id_device, jours),
    )
    row = cur.fetchone()
    return row[0] if row else 0


def create_evenement_device(cur,id_device,id_type_evenement,date_evenement,details):
    cur.execute(
        """
        INSERT INTO t_evenement_device (id_device, id_type_evenement, date_evenement, details)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (id_device, id_type_evenement, date_evenement)
        DO UPDATE SET
            details = EXCLUDED.details
        RETURNING id;
        """, (id_device,id_type_evenement,date_evenement,details)
    )
    row = cur.fetchone()
    return row[0] if row else None

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
                                   datetime_from=None, datetime_to=None,id_device=None,
                                   utilisateur_recent=None):
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
        clauses.append("serial_number ILIKE %s")
        params.append(f"%{recherche}%")
    if datetime_from is not None:
        clauses.append("date_evenement >= %s")
        params.append(datetime_from)
    if datetime_to is not None:
        clauses.append("date_evenement <= %s")
        params.append(datetime_to)
    if id_device is not None:
        clauses.append("id_device = %s"); params.append(id_device)
    if utilisateur_recent:
        # Recherche partielle (email) sur les utilisateurs récents du device
        clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM t_device_utilisateur_recent dur
                JOIN t_utilisateur ur ON ur.id = dur.id_utilisateur
                WHERE dur.id_device = v_evenements_avec_appareil.id_device
                  AND ur.email ILIKE %s
            )
            """
        )
        params.append(f"%{utilisateur_recent}%")

    return clauses, params


def find_evenements_paginated(cur, page=1, page_size=10, type_evenement=None,
                              id_filiale=None, filiale=None, recherche=None,
                              datetime_from=None, datetime_to=None,id_device=None,
                              utilisateur_recent=None):
    clauses, params = _build_evenement_filter_clause(
        type_evenement, id_filiale, filiale, recherche, datetime_from, datetime_to,id_device,
        utilisateur_recent
    )
    clauses.append("(id_statut IS NULL OR id_statut != %s)")
    params.append(ID_STATUT_RESOLUE)
    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    offset = (page - 1) * page_size

    cur.execute(
        f"SELECT COUNT(*) FROM v_evenements_avec_appareil {where}",
        tuple(params),
    )
    total = cur.fetchone()[0]

    cur.execute(
        f"""
        SELECT
            id, date_evenement, details, type_evenement, id_device,
            device_id, serial_number, modele, id_filiale, filiale
        FROM v_evenements_avec_appareil
        {where}
        ORDER BY date_evenement DESC, id DESC
        LIMIT %s OFFSET %s
        """,
        tuple(params + [page_size, offset])
    )
    return _rows_to_dicts(cur), total

def delete_evenements_avant(cur, date_limite):
    cur.execute(
        """
        DELETE FROM t_evenement_statut
        WHERE id_evenement IN (
            SELECT id FROM t_evenement_device WHERE date_evenement < %s
        )
        """,
        (date_limite,),
    )
    cur.execute(
        "DELETE FROM t_evenement_device WHERE date_evenement < %s",
        (date_limite,),
    )


def find_evenements_resolues_paginated(cur, page=1, page_size=10, type_evenement=None,
                                       id_filiale=None, filiale=None, recherche=None,
                                       datetime_from=None, datetime_to=None, id_device=None,
                                       utilisateur_recent=None):
    clauses, params = _build_evenement_filter_clause(
        type_evenement, id_filiale, filiale, recherche, datetime_from, datetime_to, id_device,
        utilisateur_recent
    )
    clauses.append("id_statut = %s")
    params.append(ID_STATUT_RESOLUE)
    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    offset = (page - 1) * page_size

    cur.execute(
        f"SELECT COUNT(*) FROM v_evenements_avec_appareil {where}",
        tuple(params),
    )
    total = cur.fetchone()[0]

    cur.execute(
        f"""
        SELECT
            id, date_evenement, details, type_evenement, id_device,
            device_id, serial_number, modele, id_filiale, filiale
        FROM v_evenements_avec_appareil
        {where}
        ORDER BY date_evenement DESC, id DESC
        LIMIT %s OFFSET %s
        """,
        tuple(params + [page_size, offset])
    )
    return _rows_to_dicts(cur), total

def get_evenement_detail_by_id(cur, event_id):
    cur.execute(
        """
        SELECT
            ed.id,
            ed.date_evenement,
            ed.details,
            te.type        AS type_evenement,
            d.id           AS id_device,
            d.device_id,
            d.serial_number,
            d.modele,
            f.org_unit_path AS filiale,
            (
                SELECT s.id_statut
                FROM t_evenement_statut s
                WHERE s.id_evenement = ed.id
                ORDER BY s.date DESC NULLS LAST, s.id DESC
                LIMIT 1
            ) AS id_statut
        FROM t_evenement_device ed
        LEFT JOIN t_type_evenement te ON te.id = ed.id_type_evenement
        LEFT JOIN t_device d          ON d.id  = ed.id_device
        LEFT JOIN t_device_filiale df ON df.id_device = d.id
        LEFT JOIN t_filiale f         ON f.id = df.id_filiale
        WHERE ed.id = %s
        LIMIT 1
        """,
        (event_id,),
    )
    row = cur.fetchone()
    if row is None:
        return None

    colonnes = [
        "id", "date_evenement", "details", "type_evenement",
        "id_device", "device_id", "serial_number", "modele", "filiale", "id_statut",
    ]
    return dict(zip(colonnes, row))
