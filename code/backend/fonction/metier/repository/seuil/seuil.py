from datetime import datetime

# Colonnes communes : id, id_type_seuil, type, categorie, valeur, date
# Une seule lecture du dernier statut par seuil (LEFT JOIN LATERAL) au lieu de
# deux sous-requetes correlees.
SEUIL_COLONNES = """
SELECT s.id, s.id_type_seuil, t.type, c.categorie, s.valeur, ds.date, t.sens
"""

SEUIL_FROM = """
FROM t_seuil s
JOIN t_type_seuil t ON t.id = s.id_type_seuil
JOIN t_categorie_type_seuil c ON c.id = t.id_categorie
LEFT JOIN LATERAL (
    SELECT ss.id_statut, ss.date
    FROM t_seuil_statut ss
    WHERE ss.id_seuil = s.id
    ORDER BY ss.date DESC, ss.id DESC
    LIMIT 1
) ds ON true
"""


def get_liste_seuil(cur):
    cur.execute(
        SEUIL_COLONNES
        + SEUIL_FROM
        + """
        WHERE ds.id_statut <> 14
        ORDER BY s.id ASC
        """
    )
    return cur.fetchall()


def find_seuils_paginated(cur, page=1, page_size=10, categorie=None):
    offset = (page - 1) * page_size
    query = (
        SEUIL_COLONNES
        + """,
               COUNT(*) OVER() AS total
        """
        + SEUIL_FROM
        + """
        WHERE ds.id_statut <> 14
        """
    )
    params = []
    if categorie:
        query += " AND c.categorie = %s"
        params.append(categorie)
    query += " ORDER BY s.id ASC LIMIT %s OFFSET %s"
    params.append(page_size)
    params.append(offset)
    cur.execute(query, tuple(params))
    return cur.fetchall()


def get_liste_archiver(cur):
    cur.execute(
        SEUIL_COLONNES
        + SEUIL_FROM
        + """
        WHERE ds.id_statut = 14
        ORDER BY s.id ASC
        """
    )
    return cur.fetchall()


def find_seuils_archived_paginated(cur, page=1, page_size=10):
    offset = (page - 1) * page_size
    cur.execute(
        SEUIL_COLONNES
        + """,
               COUNT(*) OVER() AS total
        """
        + SEUIL_FROM
        + """
        WHERE ds.id_statut = 14
        ORDER BY s.id ASC
        LIMIT %s OFFSET %s
        """,
        (page_size, offset),
    )
    return cur.fetchall()


def get_by_id_liste_archiver(cur, id_seuil):
    cur.execute(
        """
        SELECT s.id
        FROM t_seuil s
        WHERE s.id = %s
          AND (
              SELECT st.id_statut
              FROM t_seuil_statut st
              WHERE st.id_seuil = s.id
              ORDER BY st.date DESC, st.id DESC
              LIMIT 1
          ) = 14
        """,
        (id_seuil,),
    )
    return cur.fetchone()


def get_seuil_by_id(cur, id_seuil):
    cur.execute(
        SEUIL_COLONNES
        + SEUIL_FROM
        + """
        WHERE s.id = %s
        """,
        (id_seuil,),
    )
    return cur.fetchone()


def verifier_seuil_type_existe(cur, id_type_seuil):
    cur.execute(
        """
        SELECT id, valeur
        FROM t_seuil
        WHERE id_type_seuil = %s
        ORDER BY id ASC
        LIMIT 1
        """,
        (id_type_seuil,),
    )
    return cur.fetchone()


def insert_seuil(cur, id_type_seuil, valeur):
    cur.execute(
        """
        INSERT INTO t_seuil (id_type_seuil, valeur)
        VALUES (%s, %s)
        RETURNING id
        """,
        (id_type_seuil, valeur),
    )
    row = cur.fetchone()
    return row[0] if row else None


def insert_seuil_statut(cur, id_seuil, id_statut):
    cur.execute(
        """
        INSERT INTO t_seuil_statut (id_seuil, id_statut, date)
        VALUES (%s, %s, %s)
        """,
        (id_seuil, id_statut, datetime.utcnow()),
    )
    return True


def update_seuil(cur, id_seuil, valeur):
    cur.execute(
        """
        UPDATE t_seuil
        SET valeur = %s
        WHERE id = %s
        RETURNING id
        """,
        (valeur, id_seuil),
    )
    row = cur.fetchone()
    return row[0] if row else None


def delete_seuil(cur, id_seuil, id_statut=14, date=None):
    date_value = date or datetime.utcnow()
    cur.execute(
        """
        INSERT INTO t_seuil_statut (id_seuil, id_statut, date)
        VALUES (%s, %s, %s)
        """,
        (id_seuil, id_statut, date_value),
    )
    return True


def restore_seuil(cur, id_seuil, id_statut=16):
    cur.execute(
        """
        INSERT INTO t_seuil_statut (id_seuil, id_statut, date)
        VALUES (%s, %s, %s)
        """,
        (id_seuil, id_statut, datetime.utcnow()),
    )
    return True


def hard_delete_seuil(cur, id_seuil):
    cur.execute(
        "DELETE FROM t_seuil_statut WHERE id_seuil = %s",
        (id_seuil,),
    )
    cur.execute(
        "DELETE FROM t_seuil WHERE id = %s",
        (id_seuil,),
    )
    return cur.rowcount > 0


def get_type_seuil_by_categorie(cur, id_categorie):
    cur.execute(
        """
        SELECT id, type FROM t_type_seuil
        WHERE id_categorie = %s
        ORDER BY type ASC
        """,
        (id_categorie,),
    )
    return cur.fetchall()


def get_categorie_seuil(cur):
    cur.execute(
        """
        SELECT id, categorie FROM t_categorie_type_seuil
        ORDER BY id ASC
        """
    )
    return cur.fetchall()


def get_regles_seuil(cur):
    """Regles d'alerte lues en base : (type, type_alerte, metrique, sens, message)."""
    cur.execute(
        """
        SELECT t.type, t.type_alerte, t.metrique, t.sens, t.message
        FROM t_type_seuil t
        WHERE t.sens IS NOT NULL
          AND t.type_alerte IS NOT NULL
          AND t.metrique IS NOT NULL
        ORDER BY t.id ASC
        """
    )
    return cur.fetchall()


def update_sens_seuil(cur, id_seuil, sens):
    """Met a jour le sens ('>' ou '<') du type associe a un seuil."""
    cur.execute(
        """
        UPDATE t_type_seuil
        SET sens = %s
        WHERE id = (SELECT id_type_seuil FROM t_seuil WHERE id = %s)
        RETURNING id
        """,
        (sens, id_seuil),
    )
    row = cur.fetchone()
    return row[0] if row else None
