from datetime import datetime
def get_liste_configuration(cur):
    cur.execute(
        """
        SELECT c.id, c.type, c.valeur, c.date
        FROM t_configuration c
        WHERE c.id = (
            SELECT cs.id_configuration
            FROM t_configuration_statut cs
            WHERE cs.id_configuration = c.id
            ORDER BY cs.date DESC, cs.id DESC
            LIMIT 1
        )
        AND (
            SELECT cs2.id_statut
            FROM t_configuration_statut cs2
            WHERE cs2.id_configuration = c.id
            ORDER BY cs2.date DESC, cs2.id DESC
            LIMIT 1
        ) <> 14
        ORDER BY c.id ASC
        """
    )
    return cur.fetchall()


def find_configurations_paginated(cur, page=1, page_size=10):
    offset = (page - 1) * page_size
    cur.execute(
        """
        SELECT c.id, c.type, c.valeur, c.date, COUNT(*) OVER() AS total
        FROM t_configuration c
        WHERE c.id = (
            SELECT cs.id_configuration
            FROM t_configuration_statut cs
            WHERE cs.id_configuration = c.id
            ORDER BY cs.date DESC, cs.id DESC
            LIMIT 1
        )
        AND (
            SELECT cs2.id_statut
            FROM t_configuration_statut cs2
            WHERE cs2.id_configuration = c.id
            ORDER BY cs2.date DESC, cs2.id DESC
            LIMIT 1
        ) <> 14
        ORDER BY c.id ASC
        LIMIT %s OFFSET %s
        """,
        (page_size, offset),
    )
    return cur.fetchall()


def get_liste_archiver(cur):
    cur.execute(
        """
        SELECT c.id, c.type, c.valeur, c.date
        FROM t_configuration c
        WHERE c.id = (
            SELECT cs.id_configuration
            FROM t_configuration_statut cs
            WHERE cs.id_configuration = c.id
            ORDER BY cs.date DESC, cs.id DESC
            LIMIT 1
        )
        AND (
            SELECT cs2.id_statut
            FROM t_configuration_statut cs2
            WHERE cs2.id_configuration = c.id
            ORDER BY cs2.date DESC, cs2.id DESC
            LIMIT 1
        ) = 14
        ORDER BY c.id ASC
        """
    )
    return cur.fetchall()


def find_configurations_archived_paginated(cur, page=1, page_size=10):
    offset = (page - 1) * page_size
    cur.execute(
        """
        SELECT c.id, c.type, c.valeur, c.date, COUNT(*) OVER() AS total
        FROM t_configuration c
        WHERE c.id = (
            SELECT cs.id_configuration
            FROM t_configuration_statut cs
            WHERE cs.id_configuration = c.id
            ORDER BY cs.date DESC, cs.id DESC
            LIMIT 1
        )
        AND (
            SELECT cs2.id_statut
            FROM t_configuration_statut cs2
            WHERE cs2.id_configuration = c.id
            ORDER BY cs2.date DESC, cs2.id DESC
            LIMIT 1
        ) = 14
        ORDER BY c.id ASC
        LIMIT %s OFFSET %s
        """,
        (page_size, offset),
    )
    return cur.fetchall()


def get_by_id_liste_archiver(cur, id_configuration):
    cur.execute(
        """
        SELECT c.id, c.type, c.valeur, c.date
        FROM t_configuration c
        WHERE c.id = %s
          AND (
              SELECT cs.id_statut
              FROM t_configuration_statut cs
              WHERE cs.id_configuration = c.id
              ORDER BY cs.date DESC, cs.id DESC
              LIMIT 1
          ) = 14
        """,
        (id_configuration,),
    )
    return cur.fetchone()


def get_configuration_by_id(cur, id):
    cur.execute(
        "SELECT c.id, c.type, c.valeur, c.date FROM t_configuration c WHERE c.id = %s",
        (id,),
    )
    return cur.fetchone()


def get_historique_by_type(cur, type_):
    cur.execute(
        "SELECT * FROM t_configuration WHERE type = %s ORDER BY id DESC",
        (type_,),
    )
    return cur.fetchall()


def get_valeur_configuration(cur, type_):
    cur.execute(
        """
        SELECT c.valeur
        FROM t_configuration c
        WHERE c.type = %s
          AND (
              SELECT cs.id_statut
              FROM t_configuration_statut cs
              WHERE cs.id_configuration = c.id
              ORDER BY cs.date DESC, cs.id DESC
              LIMIT 1
          ) <> 14
        ORDER BY c.id DESC
        LIMIT 1
        """,
        (type_,),
    )
    return cur.fetchone()


def get_dernier_statut(cur, id_configuration):
    cur.execute(
        """
        SELECT id_statut
        FROM t_configuration_statut
        WHERE id_configuration = %s
        ORDER BY date DESC, id DESC
        LIMIT 1
        """,
        (id_configuration,),
    )
    result = cur.fetchone()
    return result[0] if result else None


def insert_configuration(cur, type_, valeur, date=None):
    date_value = date or datetime.utcnow()
    cur.execute(
        """
        INSERT INTO t_configuration (type, valeur, date)
        VALUES (%s, %s, %s)
        RETURNING id
        """,
        (type_, valeur, date_value),
    )
    row = cur.fetchone()
    return row[0] if row else None


def insert_configuration_statut(cur, id_configuration, id_statut):
    cur.execute(
        """
        INSERT INTO t_configuration_statut (id_configuration, id_statut, date)
        VALUES (%s, %s, %s)
        """,
        (id_configuration, id_statut, datetime.utcnow()),
    )
    return True


def update_configuration(cur, id_configuration, type_, valeur, date=None):
    date_value = date or datetime.utcnow()
    cur.execute(
        """
        UPDATE t_configuration
        SET type = %s,
            valeur = %s,
            date = %s
        WHERE id = %s
        RETURNING id
        """,
        (type_, valeur, date_value, id_configuration),
    )
    row = cur.fetchone()
    return row[0] if row else None


def delete_configuration(cur, id_configuration, id_statut=14, date=None):
    cur.execute(
        """
        INSERT INTO t_configuration_statut (id_configuration, id_statut, date)
        VALUES (%s, %s, %s)
        """,
        (id_configuration, id_statut, date),
    )
    return True


def restore_configuration(cur, id_configuration, id_statut=16):
    cur.execute(
        """
        INSERT INTO t_configuration_statut (id_configuration, id_statut, date)
        VALUES (%s, %s, %s)
        """,
        (id_configuration, id_statut, datetime.now()),
    )
    return True

