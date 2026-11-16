from datetime import datetime

from backend.fonction.metier.repository.statut import (
    ID_STATUT_ACTIVE,
    ID_STATUT_RESOLUE,
)


def get_liste_device_alerte_by_date(cur, date_debut=None, date_fin=None):
    cur.execute(
        f"""
        SELECT id, id_device, serial_number, type, message, date, utilisateur_recent
        FROM v_device_alerte
        WHERE id_statut = %s
          AND (%s IS NULL OR date >= %s)
          AND (%s IS NULL OR date <= %s)
        ORDER BY date DESC, id DESC
        """,
        (ID_STATUT_ACTIVE, date_debut, date_debut, date_fin, date_fin),
    )
    return cur.fetchall()


def get_liste_device_alerte_by_date_resolue(cur, date_debut=None, date_fin=None):
    cur.execute(
        f"""
        SELECT id, id_device, serial_number, type, message, date, utilisateur_recent
        FROM v_device_alerte
        WHERE id_statut = %s
          AND (%s IS NULL OR date >= %s)
          AND (%s IS NULL OR date <= %s)
        ORDER BY date DESC, id DESC
        """,
        (ID_STATUT_RESOLUE, date_debut, date_debut, date_fin, date_fin),
    )
    return cur.fetchall()


def get_nombre_alerte_active(cur):
    cur.execute(
        "SELECT COUNT(*) FROM v_device_alerte WHERE id_statut = %s",
        (ID_STATUT_ACTIVE,),
    )
    row = cur.fetchone()
    return row[0] if row else 0


def get_nombre_alerte_resolue(cur):
    cur.execute(
        "SELECT COUNT(*) FROM v_device_alerte WHERE id_statut = %s",
        (ID_STATUT_RESOLUE,),
    )
    row = cur.fetchone()
    return row[0] if row else 0


def get_device_alerte_active_by_device_and_alerte(cur, id_device, id_alerte):
    cur.execute(
        f"""
        SELECT id, id_device, id_alerte, message, date
        FROM (
            SELECT da.id, da.id_device, da.id_alerte, da.message, da.date,
                   da.id_statut
            FROM (
                SELECT da.id, da.id_device, da.id_alerte, da.message, da.date,
                       (
                           SELECT s.id_statut
                           FROM t_device_alerte_statut s
                           WHERE s.id_device_alerte = da.id
                           ORDER BY s.date DESC NULLS LAST, s.id DESC
                           LIMIT 1
                       ) AS id_statut
                FROM t_device_alerte da
            ) da
        ) da
        WHERE da.id_device = %s
          AND da.id_alerte = %s
          AND da.id_statut = %s
        ORDER BY da.date DESC, da.id DESC
        LIMIT 1
        """,
        (id_device, id_alerte, ID_STATUT_ACTIVE),
    )
    return cur.fetchone()


def insert_device_alerte(cur, id_device, id_alerte, message):
    cur.execute(
        """
        INSERT INTO t_device_alerte (id_device, id_alerte, message)
        VALUES (%s, %s, %s)
        RETURNING id
        """,
        (id_device, id_alerte, message),
    )
    row = cur.fetchone()
    return row[0] if row else None


def get_dernieres_alertes(cur, limit):
    cur.execute(
        f"""
        SELECT id, id_device, serial_number, type, message, date, utilisateur_recent
        FROM v_device_alerte
        WHERE id_statut = %s
        ORDER BY date DESC, id DESC
        LIMIT %s
        """,
        (ID_STATUT_ACTIVE, limit),
    )
    return cur.fetchall()


def find_device_alertes_paginated(cur, page=1, page_size=10, date_debut=None, date_fin=None, type_alerte=None, search_params=None):
    offset = (page - 1) * page_size
    motif = f"%{search_params}%" if search_params else None

    cur.execute(
        f"""
        SELECT COUNT(*)
        FROM v_device_alerte
        WHERE id_statut = %s
          AND (%s IS NULL OR date >= %s)
          AND (%s IS NULL OR date <= %s)
          AND (%s IS NULL OR type = %s)
          AND (%s IS NULL OR serial_number ILIKE %s OR message ILIKE %s OR type ILIKE %s)
        """,
        (
            ID_STATUT_ACTIVE,
            date_debut, date_debut,
            date_fin, date_fin,
            type_alerte, type_alerte,
            motif, motif, motif, motif,
        ),
    )
    total = cur.fetchone()[0]

    cur.execute(
        f"""
        SELECT id, id_device, serial_number, type, message, date, utilisateur_recent
        FROM v_device_alerte
        WHERE id_statut = %s
          AND (%s IS NULL OR date >= %s)
          AND (%s IS NULL OR date <= %s)
          AND (%s IS NULL OR type = %s)
          AND (%s IS NULL OR serial_number ILIKE %s OR message ILIKE %s OR type ILIKE %s)
        ORDER BY date DESC, id DESC
        LIMIT %s OFFSET %s
        """,
        (
            ID_STATUT_ACTIVE,
            date_debut, date_debut,
            date_fin, date_fin,
            type_alerte, type_alerte,
            motif, motif, motif, motif,
            page_size, offset,
        ),
    )
    return cur.fetchall(), total


def find_device_alertes_resolues_paginated(cur, page=1, page_size=10, date_debut=None, date_fin=None, type_alerte=None, search_params=None):
    offset = (page - 1) * page_size
    motif = f"%{search_params}%" if search_params else None

    cur.execute(
        f"""
        SELECT COUNT(*)
        FROM v_device_alerte
        WHERE id_statut = %s
          AND (%s IS NULL OR date >= %s)
          AND (%s IS NULL OR date <= %s)
          AND (%s IS NULL OR type = %s)
          AND (%s IS NULL OR serial_number ILIKE %s OR message ILIKE %s OR type ILIKE %s)
        """,
        (
            ID_STATUT_RESOLUE,
            date_debut, date_debut,
            date_fin, date_fin,
            type_alerte, type_alerte,
            motif, motif, motif, motif,
        ),
    )
    total = cur.fetchone()[0]

    cur.execute(
        f"""
        SELECT id, id_device, serial_number, type, message, date, utilisateur_recent
        FROM v_device_alerte
        WHERE id_statut = %s
          AND (%s IS NULL OR date >= %s)
          AND (%s IS NULL OR date <= %s)
          AND (%s IS NULL OR type = %s)
          AND (%s IS NULL OR serial_number ILIKE %s OR message ILIKE %s OR type ILIKE %s)
        ORDER BY date DESC, id DESC
        LIMIT %s OFFSET %s
        """,
        (
            ID_STATUT_RESOLUE,
            date_debut, date_debut,
            date_fin, date_fin,
            type_alerte, type_alerte,
            motif, motif, motif, motif,
            page_size, offset,
        ),
    )
    return cur.fetchall(), total


def insert_device_alerte_statut(cur, id_device_alerte, id_statut, date=None):
    date_value = date or datetime.now()
    cur.execute(
        """
        INSERT INTO t_device_alerte_statut (id_device_alerte, id_statut, date)
        VALUES (%s, %s, %s)
        """,
        (id_device_alerte, id_statut, date_value),
    )
    return True


def _compter_alertes(cur, type_alerte, id_statut, date_debut=None, date_fin=None):
    cur.execute(
        """
        SELECT COUNT(*)
        FROM v_device_alerte
        WHERE type = %s
          AND id_statut = %s
          AND (%s IS NULL OR date >= %s)
          AND (%s IS NULL OR date <= %s)
        """,
        (type_alerte, id_statut, date_debut, date_debut, date_fin, date_fin),
    )
    row = cur.fetchone()
    return row[0] if row else 0


def get_nombre_alerte_nouvelle(cur, date_depuis):
    cur.execute("SELECT COUNT(*) FROM t_device_alerte WHERE date >= %s", (date_depuis,))
    row = cur.fetchone()
    return row[0] if row else 0


def get_alertes_nouvelles(cur, date_depuis, limit):
    cur.execute(
        f"""
        SELECT id, id_device, serial_number, type, message, date, utilisateur_recent
        FROM v_device_alerte
        WHERE date >= %s
        ORDER BY date DESC, id DESC
        LIMIT %s
        """,
        (date_depuis, limit),
    )
    return cur.fetchall()
