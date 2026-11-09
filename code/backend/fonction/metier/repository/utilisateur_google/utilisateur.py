

def get_utilisateur_by_id(cur, id):

    cur.execute("""
        SELECT * FROM t_utilisateur
        WHERE id = %s
    """, (id,))

    result = cur.fetchone()
    return result


def get_utilisateur_by_email(cur, email):

    cur.execute("""
        SELECT * FROM t_utilisateur
        WHERE email = %s
    """, (email,))

    result = cur.fetchone()
    return result


def create_utilisateur(cur, email):

    cur.execute("""
        INSERT INTO t_utilisateur (email)
        VALUES (%s)
    """, (email,))


def get_or_create_utilisateur(cur, email):

    utilisateur = get_utilisateur_by_email(cur, email)

    if utilisateur:
        return utilisateur[0]

    create_utilisateur(cur, email)

    created = get_utilisateur_by_email(cur, email)
    return created[0] if created else None


def find_utilisateurs_recent_paginated(cur, page=1, page_size=10, filiale=None, recherche=None):
    offset = (page - 1) * page_size
    clauses = []
    params = []

    if recherche:
        clauses.append("u.email ILIKE %s")
        params.append(f"%{recherche}%")

    if filiale:
        clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM t_filiale_utilisateur fu
                JOIN t_filiale f ON f.id = fu.id_filiale
                WHERE fu.id_utilisateur = u.id AND f.org_unit_path = %s
            )
            """
        )
        params.append(filiale)

    where = "WHERE " + " AND ".join(clauses) if clauses else ""

    cur.execute(
        f"""
        SELECT
            u.id,
            u.email,
            COUNT(DISTINCT dur.id_device) AS nb_devices,
            MAX(dur.date_observation) AS derniere_observation,
            COALESCE(
                (
                    SELECT array_agg(DISTINCT f.org_unit_path ORDER BY f.org_unit_path)
                    FROM t_filiale_utilisateur fu
                    JOIN t_filiale f ON f.id = fu.id_filiale
                    WHERE fu.id_utilisateur = u.id
                ), '{{}}'::text[]
            ) AS filiales,
            COUNT(*) OVER() AS total
        FROM t_utilisateur u
        JOIN t_device_utilisateur_recent dur ON dur.id_utilisateur = u.id
        {where}
        GROUP BY u.id, u.email
        ORDER BY MAX(dur.date_observation) DESC, u.email ASC
        LIMIT %s OFFSET %s
        """,
        tuple(params + [page_size, offset]),
    )
    return cur.fetchall()


def get_devices_by_utilisateur_recent(cur, id_utilisateur, limit=100):
    cur.execute(
        """
        SELECT d.id, d.device_id, d.serial_number, d.modele,
               MAX(dur.date_observation) AS derniere_observation
        FROM t_device_utilisateur_recent dur
        JOIN t_device d ON d.id = dur.id_device
        WHERE dur.id_utilisateur = %s
        GROUP BY d.id, d.device_id, d.serial_number, d.modele
        ORDER BY MAX(dur.date_observation) DESC
        LIMIT %s
        """,
        (id_utilisateur, limit),
    )
    return cur.fetchall()