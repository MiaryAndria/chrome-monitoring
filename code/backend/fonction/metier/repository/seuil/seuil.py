from datetime import datetime

def get_liste_seuil(cur):
    cur.execute(
        """
        SELECT s.id, s.cle, s.valeur,
               (
                   SELECT ss.date
                   FROM t_seuil_statut ss
                   WHERE ss.id_seuil = s.id
                   ORDER BY ss.date DESC, ss.id DESC
                   LIMIT 1
               ) AS date
        FROM t_seuil s
        WHERE (
            SELECT st.id_statut
            FROM t_seuil_statut st
            WHERE st.id_seuil = s.id
            ORDER BY st.date DESC, st.id DESC
            LIMIT 1
        ) <> 14
        ORDER BY s.id ASC
        """
    )
    return cur.fetchall()


def find_seuils_paginated(cur, page=1, page_size=10):
    offset = (page - 1) * page_size
    cur.execute(
        """
        SELECT s.id, s.cle, s.valeur,
               (
                   SELECT ss.date
                   FROM t_seuil_statut ss
                   WHERE ss.id_seuil = s.id
                   ORDER BY ss.date DESC, ss.id DESC
                   LIMIT 1
               ) AS date,
               COUNT(*) OVER() AS total
        FROM t_seuil s
        WHERE (
            SELECT st.id_statut
            FROM t_seuil_statut st
            WHERE st.id_seuil = s.id
            ORDER BY st.date DESC, st.id DESC
            LIMIT 1
        ) <> 14
        ORDER BY s.id ASC
        LIMIT %s OFFSET %s
        """,
        (page_size, offset),
    )
    return cur.fetchall()


def get_liste_archiver(cur):
    cur.execute(
        """
        SELECT s.id, s.cle, s.valeur,
               (
                   SELECT ss.date
                   FROM t_seuil_statut ss
                   WHERE ss.id_seuil = s.id
                   ORDER BY ss.date DESC, ss.id DESC
                   LIMIT 1
               ) AS date
        FROM t_seuil s
        WHERE (
            SELECT st.id_statut
            FROM t_seuil_statut st
            WHERE st.id_seuil = s.id
            ORDER BY st.date DESC, st.id DESC
            LIMIT 1
        ) = 14
        ORDER BY s.id ASC
        """
    )
    return cur.fetchall()


def find_seuils_archived_paginated(cur, page=1, page_size=10):
    offset = (page - 1) * page_size
    cur.execute(
        """
        SELECT s.id, s.cle, s.valeur,
               (
                   SELECT ss.date
                   FROM t_seuil_statut ss
                   WHERE ss.id_seuil = s.id
                   ORDER BY ss.date DESC, ss.id DESC
                   LIMIT 1
               ) AS date,
               COUNT(*) OVER() AS total
        FROM t_seuil s
        WHERE (
            SELECT st.id_statut
            FROM t_seuil_statut st
            WHERE st.id_seuil = s.id
            ORDER BY st.date DESC, st.id DESC
            LIMIT 1
        ) = 14
        ORDER BY s.id ASC
        LIMIT %s OFFSET %s
        """,
        (page_size, offset),
    )
    return cur.fetchall()


def get_by_id_liste_archiver(cur, id_seuil):
    cur.execute(
        """
        SELECT s.id, s.cle, s.valeur
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
        """
        SELECT s.id, s.cle, s.valeur,
               (
                   SELECT ss.date
                   FROM t_seuil_statut ss
                   WHERE ss.id_seuil = s.id
                   ORDER BY ss.date DESC, ss.id DESC
                   LIMIT 1
               ) AS date
        FROM t_seuil s
        WHERE s.id = %s
        """,
        (id_seuil,),
    )
    return cur.fetchone()


def get_seuil_by_cle(cur, cle):
    cur.execute(
        "SELECT id, cle, valeur FROM t_seuil WHERE cle = %s",
        (cle,),
    )
    return cur.fetchone()


def insert_seuil(cur, cle, valeur):
    cur.execute(
        """
        INSERT INTO t_seuil (cle, valeur)
        VALUES (%s, %s)
        RETURNING id
        """,
        (cle, valeur),
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


def update_seuil(cur, id_seuil, cle, valeur):
    cur.execute(
        """
        UPDATE t_seuil
        SET cle = %s,
            valeur = %s
        WHERE id = %s
        RETURNING id
        """,
        (cle, valeur, id_seuil),
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
        (id_seuil, id_statut, datetime.now()),
    )
    return True
