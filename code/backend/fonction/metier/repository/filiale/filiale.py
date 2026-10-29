def get_liste_filiale(cur):
    cur.execute("SELECT * FROM t_filiale;")
    return cur.fetchall()


def get_filiale_by_org_unit(cur, unit_path):
    cur.execute("SELECT * FROM t_filiale WHERE org_unit_path = %s;", (unit_path,))
    return cur.fetchone()

def insert_filiale(cur, org_unit_path):
    cur.execute(
        """
        INSERT INTO t_filiale (org_unit_path) VALUES (%s)
        ON CONFLICT (org_unit_path) DO NOTHING
        RETURNING id;
        """,
        (org_unit_path,)
    )
    return cur.fetchone()

def get_or_create_filiale(cur, org_unit_path):
    filiale = get_filiale_by_org_unit(cur, org_unit_path)
    if filiale:
        return filiale[0]

    insert_filiale(cur, org_unit_path)
    created = get_filiale_by_org_unit(cur, org_unit_path)
    return created[0] if created else None


def _rows_to_dicts(cur):
    colonnes = [desc[0] for desc in cur.description]
    return [dict(zip(colonnes, row)) for row in cur.fetchall()]


def find_filiales_paginated(cur, page=1, page_size=10, recherche=None):
    clauses = []
    params = []

    if recherche:
        clauses.append("org_unit_path ILIKE %s")
        params.append(f"%{recherche}%")

    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    offset = (page - 1) * page_size

    cur.execute(
        f"""
        SELECT
            id, org_unit_path,
            COUNT(*) OVER() AS total
        FROM t_filiale
        {where}
        ORDER BY id ASC
        LIMIT %s OFFSET %s
        """,
        tuple(params + [page_size, offset])
    )
    return _rows_to_dicts(cur)