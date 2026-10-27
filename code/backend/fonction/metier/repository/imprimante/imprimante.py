def get_liste_imprimante(cur):
    cur.execute(
        """
        SELECT i.id, i.vid, i.pid, v.vendor, i.nom
        FROM t_imprimante i
        LEFT JOIN t_vendor v ON v.id = i.id_vendor
        ORDER BY i.id ASC
        """
    )
    return cur.fetchall()


def get_imprimante_by_id(cur, id):
    cur.execute(
        """
        SELECT i.id, i.vid, i.pid, v.vendor, i.nom
        FROM t_imprimante i
        LEFT JOIN t_vendor v ON v.id = i.id_vendor
        WHERE i.id = %s
        """, (id,)
    )
    return cur.fetchone()


def get_imprimante_by_vid(cur, vid):
    cur.execute(
        """
        SELECT i.id, i.vid, i.pid, v.vendor, i.nom
        FROM t_imprimante i
        LEFT JOIN t_vendor v ON v.id = i.id_vendor
        WHERE i.vid = %s
        """, (vid,)
    )
    return cur.fetchone()


def get_imprimante_by_pid(cur, pid):
    cur.execute(
        """
        SELECT i.id, i.vid, i.pid, v.vendor, i.nom
        FROM t_imprimante i
        LEFT JOIN t_vendor v ON v.id = i.id_vendor
        WHERE i.pid = %s
        """, (pid,)
    )
    return cur.fetchone()

def get_imprimante_by_vendor(cur, vendor):
    cur.execute(
        """
        SELECT i.id, i.vid, i.pid, v.vendor, i.nom
        FROM t_imprimante i
        JOIN t_vendor v ON v.id = i.id_vendor
        WHERE v.vendor = %s
        """, (vendor,)
    )
    return cur.fetchone()


def get_imprimante_by_nom(cur, nom):
    cur.execute(
        """
        SELECT i.id, i.vid, i.pid, v.vendor, i.nom
        FROM t_imprimante i
        LEFT JOIN t_vendor v ON v.id = i.id_vendor
        WHERE i.nom = %s
        """, (nom,)
    )
    return cur.fetchone()


def search_imprimante(cur, recherche):
    cur.execute(
        """
        SELECT i.id, i.vid, i.pid, v.vendor, i.nom
        FROM t_imprimante i
        LEFT JOIN t_vendor v ON v.id = i.id_vendor
        WHERE CAST(i.vid AS TEXT) ILIKE %s
           OR CAST(i.pid AS TEXT) ILIKE %s
           OR v.vendor ILIKE %s
           OR i.nom ILIKE %s
        """, (recherche, recherche, recherche, recherche)
    )
    return cur.fetchall()


def _rows_to_dicts(cur):
    colonnes = [desc[0] for desc in cur.description]
    return [dict(zip(colonnes, row)) for row in cur.fetchall()]


def find_imprimantes_paginated(cur, page=1, page_size=10, recherche=None,
                               vendor=None, datetime_from=None, datetime_to=None):
    clauses = []
    params = []

    if recherche:
        terme = f"%{recherche}%"
        clauses.append(
            "(vendor ILIKE %s OR nom ILIKE %s "
            "OR CAST(vid AS TEXT) ILIKE %s OR CAST(pid AS TEXT) ILIKE %s)"
        )
        params.extend([terme, terme, terme, terme])
    if vendor:
        clauses.append("vendor = %s")
        params.append(vendor)
    if datetime_from is not None:
        clauses.append("derniere_detection >= %s")
        params.append(datetime_from)
    if datetime_to is not None:
        clauses.append("derniere_detection <= %s")
        params.append(datetime_to)

    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    offset = (page - 1) * page_size

    cur.execute(
        f"""
        SELECT
            id, vid, pid, vendor, nom, derniere_detection,
            COUNT(*) OVER() AS total
        FROM v_imprimantes_filtrees
        {where}
        ORDER BY id ASC
        LIMIT %s OFFSET %s
        """,
        tuple(params + [page_size, offset])
    )
    return _rows_to_dicts(cur)


def get_liste_vendor(cur):
    cur.execute("SELECT vendor FROM t_vendor ORDER BY vendor ASC")
    return [r[0] for r in cur.fetchall()]


def get_nombre_imprimante(cur):
    cur.execute(
        """
        SELECT COUNT(*) FROM t_imprimante
        """
    )
    result = cur.fetchone()
    return result


def get_imprimante_by_vid_and_pid(cur, vid, pid):
    cur.execute(
        """
        SELECT i.id, i.vid, i.pid, v.vendor, i.nom
        FROM t_imprimante i
        LEFT JOIN t_vendor v ON v.id = i.id_vendor
        WHERE i.vid = %s AND i.pid = %s
        """, (vid, pid)
    )
    return cur.fetchall()


def get_imprimante_by_vendor_and_nom(cur, vendor, nom):
    cur.execute(
        """
        SELECT i.id, i.vid, i.pid, v.vendor, i.nom
        FROM t_imprimante i
        LEFT JOIN t_vendor v ON v.id = i.id_vendor
        WHERE v.vendor = %s AND i.nom = %s
        """, (vendor, nom)
    )
    return cur.fetchone()


def get_or_create_vendor(cur, vendor):
    nom_vendor = vendor or "UNKNOWN"
    cur.execute("SELECT id FROM t_vendor WHERE vendor = %s", (nom_vendor,))
    row = cur.fetchone()
    if row:
        return row[0]

    cur.execute(
        """
        INSERT INTO t_vendor (vendor) VALUES (%s)
        ON CONFLICT (vendor) DO NOTHING
        RETURNING id
        """,
        (nom_vendor,)
    )
    row = cur.fetchone()
    if row:
        return row[0]

    cur.execute("SELECT id FROM t_vendor WHERE vendor = %s", (nom_vendor,))
    row = cur.fetchone()
    return row[0] if row else None


def insert_imprimante(cur, vid, pid, vendor, nom):
    id_vendor = get_or_create_vendor(cur, vendor)
    cur.execute(
        """
        INSERT INTO t_imprimante (vid, pid, id_vendor, nom)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
        """,
        (vid, pid, id_vendor, nom)
    )
    row = cur.fetchone()
    return row[0] if row else None


def get_or_create_imprimante(cur, vid, pid, vendor, nom):
    imprimante = get_imprimante_by_vid_and_pid(cur, vid, pid)
    if not imprimante:
        insert_imprimante(cur, vid, pid, vendor, nom)
        imprimante = get_imprimante_by_vid_and_pid(cur, vid, pid)

    return imprimante
