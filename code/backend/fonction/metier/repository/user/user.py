def get_user_by_email(cur, email):
    cur.execute(
        """
        SELECT id, nom, email, mdp, id_role FROM t_user WHERE email = %s
        """,
        (email,),
    )
    return cur.fetchone()


def create_user(cur, nom, email, mdp, id_role):
    cur.execute(
        """
        INSERT INTO t_user (nom, email, mdp, id_role)
        VALUES (%s, %s, %s, %s)
        RETURNING id, nom, email, id_role
        """,
        (nom, email, mdp, id_role),
    )
    return cur.fetchone()


def get_role(cur):
    cur.execute(
        """
        SELECT id, role FROM t_role ORDER BY id ASC
        """
    )
    return cur.fetchall()


def list_users(cur):
    cur.execute(
        """
        SELECT u.id, u.nom, u.email, u.id_role, r.role
        FROM t_user u
        JOIN t_role r ON r.id = u.id_role
        ORDER BY u.id ASC
        """
    )
    return cur.fetchall()


def role_exists(cur, id_role):
    cur.execute("SELECT 1 FROM t_role WHERE id = %s", (id_role,))
    return cur.fetchone() is not None


def set_user_role(cur, id_user, id_role):
    cur.execute(
        """
        UPDATE t_user SET id_role = %s WHERE id = %s
        RETURNING id, nom, email, id_role
        """,
        (id_role, id_user),
    )
    return cur.fetchone()


def get_user_by_id(cur, id_user):
    cur.execute(
        """
        SELECT u.id, u.nom, u.email, u.id_role, r.role
        FROM t_user u
        JOIN t_role r ON r.id = u.id_role
        WHERE u.id = %s
        """,
        (id_user,),
    )
    return cur.fetchone()


def get_user_archived(cur, id_user, id_statut_supprime):
    cur.execute(
        """
        SELECT u.id, u.nom, u.email, u.id_role, r.role
        FROM t_user u
        JOIN t_role r ON r.id = u.id_role
        WHERE u.id = %s
          AND (
              SELECT us.id_statut
              FROM t_user_statut us
              WHERE us.id_user = u.id
              ORDER BY us.date DESC, us.id DESC
              LIMIT 1
          ) = %s
        """,
        (id_user, id_statut_supprime),
    )
    return cur.fetchone()


def find_users_paginated(cur, id_statut_supprime, page=1, page_size=10):
    offset = (page - 1) * page_size
    cur.execute(
        """
        SELECT u.id, u.nom, u.email, u.id_role, r.role,
               (
                   SELECT us.date
                   FROM t_user_statut us
                   WHERE us.id_user = u.id
                   ORDER BY us.date DESC, us.id DESC
                   LIMIT 1
               ) AS date,
               COUNT(*) OVER() AS total
        FROM t_user u
        JOIN t_role r ON r.id = u.id_role
        WHERE COALESCE(
            (
                SELECT us.id_statut
                FROM t_user_statut us
                WHERE us.id_user = u.id
                ORDER BY us.date DESC, us.id DESC
                LIMIT 1
            ), -1
        ) <> %s
        ORDER BY u.id ASC
        LIMIT %s OFFSET %s
        """,
        (id_statut_supprime, page_size, offset),
    )
    return cur.fetchall()


def find_users_archived_paginated(cur, id_statut_supprime, page=1, page_size=10):
    offset = (page - 1) * page_size
    cur.execute(
        """
        SELECT u.id, u.nom, u.email, u.id_role, r.role,
               (
                   SELECT us.date
                   FROM t_user_statut us
                   WHERE us.id_user = u.id
                   ORDER BY us.date DESC, us.id DESC
                   LIMIT 1
               ) AS date,
               COUNT(*) OVER() AS total
        FROM t_user u
        JOIN t_role r ON r.id = u.id_role
        WHERE (
            SELECT us.id_statut
            FROM t_user_statut us
            WHERE us.id_user = u.id
            ORDER BY us.date DESC, us.id DESC
            LIMIT 1
        ) = %s
        ORDER BY u.id ASC
        LIMIT %s OFFSET %s
        """,
        (id_statut_supprime, page_size, offset),
    )
    return cur.fetchall()


def insert_user_statut(cur, id_user, id_statut):
    cur.execute(
        """
        INSERT INTO t_user_statut (id_user, id_statut)
        VALUES (%s, %s)
        """,
        (id_user, id_statut),
    )
    return True
