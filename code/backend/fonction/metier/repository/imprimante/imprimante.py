def get_liste_imprimante(cur):
    cur.execute(
        """
        SELECT * FROM t_imprimante
        """
    )
    result = cur.fetchall()
    return result

def get_imprimante_by_id(cur,id):
    cur.execute(
        """
        SELECT * FROM t_imprimante WHERE id = %s
        """,(id,)
    )
    result = cur.fetchone()
    return result

def get_imprimante_by_vid(cur,vid):
    cur.execute(
        """
        SELECT * FROM t_imprimante WHERE vid = %s
        """,(vid,)
    )
    result = cur.fetchone()
    return result

def get_imprimante_by_pid(cur,pid):
    cur.execute(
        """
        SELECT * FROM t_imprimante WHERE pid = %s
        """,(pid,)
    )
    result = cur.fetchone()
    return result

def get_imprimante_by_vendor(cur,vendor):
    cur.execute(
        """
        SELECT * FROM t_imprimante WHERE vendor = %s
        """,(vendor,)
    )
    result = cur.fetchone()
    return result

def get_imprimante_by_nom(cur,nom):
    cur.execute(
        """
        SELECT * FROM t_imprimante WHERE nom = %s
        """,(nom,)
    )
    result = cur.fetchone()
    return result

def search_imprimante(cur,recherche):
    cur.execute(
        """
        SELECT * FROM t_imprimante
        WHERE CAST(vid AS TEXT) ILIKE %s
           OR CAST(pid AS TEXT) ILIKE %s
           OR vendor ILIKE %s
           OR nom ILIKE %s
        """,(recherche,recherche,recherche,recherche,)
    )
    result = cur.fetchall()
    return result


def _rows_to_dicts(cur):
    colonnes = [desc[0] for desc in cur.description]
    return [dict(zip(colonnes, row)) for row in cur.fetchall()]


def find_imprimantes_paginated(cur, page=1, page_size=10, recherche=None,
                               datetime_from=None, datetime_to=None):
    clauses = []
    params = []

    if recherche:
        terme = f"%{recherche}%"
        clauses.append(
            "(vendor ILIKE %s OR nom ILIKE %s "
            "OR CAST(vid AS TEXT) ILIKE %s OR CAST(pid AS TEXT) ILIKE %s)"
        )
        params.extend([terme, terme, terme, terme])
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

def get_nombre_imprimante(cur):
    cur.execute(
        """
        SELECT COUNT(*) FROM t_imprimante
        """
    )
    result = cur.fetchone()
    return result

def get_imprimante_by_vid_and_pid(cur,vid,pid):
    cur.execute(
        """
        SELECT * FROM t_imprimante WHERE vid = %s AND pid = %s
        """,(vid,pid,)
    )
    result = cur.fetchall()
    return result

def get_imprimante_by_vendor_and_nom(cur,vendor,nom):
    cur.execute(
        """
        SELECT * FROM t_imprimante WHERE vendor = %s AND nom = %s
        """,(vendor,nom,)
    )
    result = cur.fetchone()
    return result

def insert_imprimante(cur, vid, pid, vendor, nom):
    cur.execute(
        """
        INSERT INTO t_imprimante (vid, pid, vendor, nom)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
        """,
        (vid, pid, vendor, nom)
    )

def get_or_create_imprimante(cur,vid,pid,vendor,nom):
    imprimante = get_imprimante_by_vid_and_pid(cur,vid,pid)
    if not imprimante :
        insert_imprimante(cur,vid,pid,vendor,nom)
        imprimante = get_imprimante_by_vid_and_pid(cur,vid,pid)
        
    return imprimante 

