from datetime import datetime

# Colonnes communes : id, id_type_configuration, type, categorie, valeur, date
# Une seule lecture du dernier statut par configuration (LEFT JOIN LATERAL).
CONFIG_COLONNES = """
SELECT c.id, c.id_type_configuration, t.type, cat.categorie, c.valeur, ds.date
"""

CONFIG_FROM = """
FROM t_configuration c
JOIN t_type_configuration t ON t.id = c.id_type_configuration
JOIN t_categorie_type_configuration cat ON cat.id = t.id_categorie
LEFT JOIN LATERAL (
    SELECT cs.id_statut, cs.date
    FROM t_configuration_statut cs
    WHERE cs.id_configuration = c.id
    ORDER BY cs.date DESC, cs.id DESC
    LIMIT 1
) ds ON true
"""


def get_liste_configuration(cur):
    cur.execute(
        CONFIG_COLONNES
        + CONFIG_FROM
        + """
        WHERE ds.id_statut <> 14
        ORDER BY c.id ASC
        """
    )
    return cur.fetchall()


def find_configurations_paginated(cur, page=1, page_size=10, categorie=None):
    offset = (page - 1) * page_size
    query = (
        CONFIG_COLONNES
        + """,
               COUNT(*) OVER() AS total
        """
        + CONFIG_FROM
        + """
        WHERE ds.id_statut <> 14
        """
    )
    params = []
    if categorie:
        query += " AND cat.categorie = %s"
        params.append(categorie)
    query += " ORDER BY c.id ASC LIMIT %s OFFSET %s"
    params.append(page_size)
    params.append(offset)
    cur.execute(query, tuple(params))
    return cur.fetchall()


def get_liste_archiver(cur):
    cur.execute(
        CONFIG_COLONNES
        + CONFIG_FROM
        + """
        WHERE ds.id_statut = 14
        ORDER BY c.id ASC
        """
    )
    return cur.fetchall()


def find_configurations_archived_paginated(cur, page=1, page_size=10):
    offset = (page - 1) * page_size
    cur.execute(
        CONFIG_COLONNES
        + """,
               COUNT(*) OVER() AS total
        """
        + CONFIG_FROM
        + """
        WHERE ds.id_statut = 14
        ORDER BY c.id ASC
        LIMIT %s OFFSET %s
        """,
        (page_size, offset),
    )
    return cur.fetchall()


def get_by_id_liste_archiver(cur, id_configuration):
    cur.execute(
        """
        SELECT c.id
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
        CONFIG_COLONNES
        + CONFIG_FROM
        + """
        WHERE c.id = %s
        """,
        (id,),
    )
    return cur.fetchone()


def get_valeur_configuration(cur, type_):
    cur.execute(
        """
        SELECT c.valeur
        """
        + CONFIG_FROM
        + """
        WHERE t.type = %s
          AND ds.id_statut <> 14
        ORDER BY c.id DESC
        LIMIT 1
        """,
        (type_,),
    )
    return cur.fetchone()


def get_valeur_configuration_by_id(cur, id_configuration):
    cur.execute(
        """
        SELECT c.valeur
        FROM t_configuration c
        WHERE c.id = %s
        """,
        (id_configuration,),
    )
    return cur.fetchone()


def verifier_configuration_type_existe(cur, id_type_configuration):
    cur.execute(
        """
        SELECT id, valeur
        FROM t_configuration
        WHERE id_type_configuration = %s
        ORDER BY id ASC
        LIMIT 1
        """,
        (id_type_configuration,),
    )
    return cur.fetchone()


def insert_configuration(cur, id_type_configuration, valeur):
    cur.execute(
        """
        INSERT INTO t_configuration (id_type_configuration, valeur)
        VALUES (%s, %s)
        RETURNING id
        """,
        (id_type_configuration, valeur),
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


def update_configuration(cur, id_configuration, valeur):
    cur.execute(
        """
        UPDATE t_configuration
        SET valeur = %s
        WHERE id = %s
        RETURNING id
        """,
        (valeur, id_configuration),
    )
    row = cur.fetchone()
    return row[0] if row else None


def delete_configuration(cur, id_configuration, id_statut=14, date=None):
    date_value = date or datetime.utcnow()
    cur.execute(
        """
        INSERT INTO t_configuration_statut (id_configuration, id_statut, date)
        VALUES (%s, %s, %s)
        """,
        (id_configuration, id_statut, date_value),
    )
    return True


def restore_configuration(cur, id_configuration, id_statut=16):
    cur.execute(
        """
        INSERT INTO t_configuration_statut (id_configuration, id_statut, date)
        VALUES (%s, %s, %s)
        """,
        (id_configuration, id_statut, datetime.utcnow()),
    )
    return True


def hard_delete_configuration(cur, id_configuration):
    cur.execute(
        "DELETE FROM t_configuration_statut WHERE id_configuration = %s",
        (id_configuration,),
    )
    cur.execute(
        "DELETE FROM t_configuration WHERE id = %s",
        (id_configuration,),
    )
    return cur.rowcount > 0


def get_categorie_configuration(cur):
    cur.execute(
        """
        SELECT id, categorie FROM t_categorie_type_configuration
        ORDER BY id ASC
        """
    )
    return cur.fetchall()


def get_type_configuration_by_categorie(cur, id_categorie):
    cur.execute(
        """
        SELECT id, type FROM t_type_configuration
        WHERE id_categorie = %s
        ORDER BY type ASC
        """,
        (id_categorie,),
    )
    return cur.fetchall()
