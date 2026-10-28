from datetime import datetime

# Occurrence ACTIVE / RESOLUE, déterminée par le dernier t_device_alerte_statut
DERNIER_STATUT_SQL = """
    (
        SELECT s.id_statut
        FROM t_device_alerte_statut s
        WHERE s.id_device_alerte = da.id
        ORDER BY s.date DESC NULLS LAST, s.id DESC
        LIMIT 1
    )
"""


def get_liste_device_alerte(cur):
    cur.execute(
        """
        SELECT id, id_device, id_alerte, message, date
        FROM t_device_alerte
        ORDER BY date DESC, id DESC
        """
    )
    return cur.fetchall()


def get_liste_device_alerte_by_date(cur, date_debut=None, date_fin=None):
    """Alertes ACTIVE enrichies (série, type, utilisateur), filtrées par date si fournies."""
    query = f"""
        SELECT da.id, da.id_device, d.serial_number, tr.type,
               da.message, da.date,
               (
                   SELECT u.email
                   FROM t_device_utilisateur_recent ur
                   JOIN t_utilisateur u ON u.id = ur.id_utilisateur
                   WHERE ur.id_device = da.id_device
                   ORDER BY ur.date_observation DESC
                   LIMIT 1
               ) AS utilisateur_recent
        FROM t_device_alerte da
        JOIN t_device d ON d.id = da.id_device
        JOIN t_alerte tr ON tr.id = da.id_alerte
        WHERE {DERNIER_STATUT_SQL} = 1
    """
    params = []
    if date_debut is not None:
        query += " AND da.date >= %s"
        params.append(date_debut)
    if date_fin is not None:
        query += " AND da.date <= %s"
        params.append(date_fin)
    query += " ORDER BY da.date DESC, da.id DESC"

    cur.execute(query, tuple(params))
    return cur.fetchall()

def get_liste_device_alerte_by_date_resolue(cur, date_debut=None, date_fin=None):
    query = f"""
        SELECT da.id, da.id_device, d.serial_number, tr.type,
               da.message, da.date,
               (
                   SELECT u.email
                   FROM t_device_utilisateur_recent ur
                   JOIN t_utilisateur u ON u.id = ur.id_utilisateur
                   WHERE ur.id_device = da.id_device
                   ORDER BY ur.date_observation DESC
                   LIMIT 1
               ) AS utilisateur_recent
        FROM t_device_alerte da
        JOIN t_device d ON d.id = da.id_device
        JOIN t_alerte tr ON tr.id = da.id_alerte
        WHERE {DERNIER_STATUT_SQL} = 15
    """
    params = []
    if date_debut is not None:
        query += " AND da.date >= %s"
        params.append(date_debut)
    if date_fin is not None:
        query += " AND da.date <= %s"
        params.append(date_fin)
    query += " ORDER BY da.date DESC, da.id DESC"

    cur.execute(query, tuple(params))
    return cur.fetchall()

def get_device_alerte_by_id(cur, id_device_alerte):
    cur.execute(
        """
        SELECT id, id_device, id_alerte, message, date
        FROM t_device_alerte
        WHERE id = %s
        """,
        (id_device_alerte,),
    )
    return cur.fetchone()


def get_alertes_by_device(cur, id_device):
    cur.execute(
        """
        SELECT id, id_device, id_alerte, message, date
        FROM t_device_alerte
        WHERE id_device = %s
        ORDER BY date DESC, id DESC
        """,
        (id_device,),
    )
    return cur.fetchall()


def get_devices_by_alerte(cur, id_alerte):
    cur.execute(
        """
        SELECT id, id_device, id_alerte, message, date
        FROM t_device_alerte
        WHERE id_alerte = %s
        ORDER BY date DESC, id DESC
        """,
        (id_alerte,),
    )
    return cur.fetchall()


def get_alertes_actives_by_device(cur, id_device):
    cur.execute(
        f"""
        SELECT da.id, da.id_device, da.id_alerte, da.message, da.date
        FROM t_device_alerte da
        WHERE da.id_device = %s AND {DERNIER_STATUT_SQL} = 1
        ORDER BY da.date DESC, da.id DESC
        """,
        (id_device,),
    )
    return cur.fetchall()


def get_alertes_resolues_by_device(cur, id_device):
    cur.execute(
        f"""
        SELECT da.id, da.id_device, da.id_alerte, da.message, da.date
        FROM t_device_alerte da
        WHERE da.id_device = %s AND {DERNIER_STATUT_SQL} = 15
        ORDER BY da.date DESC, da.id DESC
        """,
        (id_device,),
    )
    return cur.fetchall()



def get_derniere_alerte_device(cur, id_device):
    cur.execute(
        """
        SELECT id, id_device, id_alerte, message, date
        FROM t_device_alerte
        WHERE id_device = %s
        ORDER BY date DESC, id DESC
        LIMIT 1
        """,
        (id_device,),
    )
    return cur.fetchone()


def get_nombre_alerte_active(cur):
    cur.execute(
        f"""
        SELECT COUNT(*)
        FROM t_device_alerte da
        WHERE {DERNIER_STATUT_SQL} = 1
        """
    )
    row = cur.fetchone()
    return row[0] if row else 0

def get_nombre_alerte_resolue(cur):
    cur.execute(
        f"""
        SELECT COUNT(*)
        FROM t_device_alerte da
        WHERE {DERNIER_STATUT_SQL} = 15
        """
    )
    row = cur.fetchone()
    return row[0] if row else 0


def get_nombre_alerte_device(cur, id_device):
    cur.execute(
        "SELECT COUNT(*) FROM t_device_alerte WHERE id_device = %s",
        (id_device,),
    )
    row = cur.fetchone()
    return row[0] if row else 0


def get_device_alerte_by_device_and_alerte(cur, id_device, id_alerte):
    cur.execute(
        """
        SELECT id, id_device, id_alerte, message, date
        FROM t_device_alerte
        WHERE id_device = %s AND id_alerte = %s
        ORDER BY date DESC, id DESC
        """,
        (id_device, id_alerte),
    )
    return cur.fetchall()


def get_device_alerte_active_by_device_and_alerte(cur, id_device, id_alerte):
    """Occurrence ACTIVE (dernier statut = 1) pour un couple (device, alerte), sinon None."""
    cur.execute(
        f"""
        SELECT da.id, da.id_device, da.id_alerte, da.message, da.date
        FROM t_device_alerte da
        WHERE da.id_device = %s AND da.id_alerte = %s AND {DERNIER_STATUT_SQL} = 1
        ORDER BY da.date DESC, da.id DESC
        LIMIT 1
        """,
        (id_device, id_alerte),
    )
    return cur.fetchone()


def get_alertes_actives_by_device_and_period(cur, id_device, date_debut, date_fin):
    cur.execute(
        f"""
        SELECT da.id, da.id_device, da.id_alerte, da.message, da.date
        FROM t_device_alerte da
        WHERE da.id_device = %s
          AND da.date BETWEEN %s AND %s
          AND {DERNIER_STATUT_SQL} = 1
        ORDER BY da.date DESC, da.id DESC
        """,
        (id_device, date_debut, date_fin),
    )
    return cur.fetchall()


def get_alertes_by_alerte_and_period(cur, id_alerte, date_debut, date_fin):
    cur.execute(
        """
        SELECT id, id_device, id_alerte, message, date
        FROM t_device_alerte
        WHERE id_alerte = %s AND date BETWEEN %s AND %s
        ORDER BY date DESC, id DESC
        """,
        (id_alerte, date_debut, date_fin),
    )
    return cur.fetchall()


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
    """Les `limit` dernières alertes dont le dernier statut est ACTIVE (1)."""
    cur.execute(
        f"""
        SELECT da.id, da.id_device, d.serial_number, tr.type,
               da.message, da.date,
               (
                   SELECT u.email
                   FROM t_device_utilisateur_recent ur
                   JOIN t_utilisateur u ON u.id = ur.id_utilisateur
                   WHERE ur.id_device = da.id_device
                   ORDER BY ur.date_observation DESC
                   LIMIT 1
               ) AS utilisateur_recent
        FROM t_device_alerte da
        JOIN t_device d ON d.id = da.id_device
        JOIN t_alerte tr ON tr.id = da.id_alerte
        WHERE {DERNIER_STATUT_SQL} = 1
        ORDER BY da.date DESC, da.id DESC
        LIMIT %s
        """,
        (limit,),
    )
    return cur.fetchall()

def find_device_alertes_paginated(cur, page=1, page_size=10, date_debut=None, date_fin=None, type_alerte=None,search_params=None):
    """Alertes ACTIVE paginées (série, type, utilisateur)."""
    offset = (page - 1) * page_size
    query = f"""
        SELECT da.id, da.id_device, d.serial_number, tr.type,
               da.message, da.date,
               (
                   SELECT u.email
                   FROM t_device_utilisateur_recent ur
                   JOIN t_utilisateur u ON u.id = ur.id_utilisateur
                   WHERE ur.id_device = da.id_device
                   ORDER BY ur.date_observation DESC
                   LIMIT 1
               ) AS utilisateur_recent,
               COUNT(*) OVER() AS total
        FROM t_device_alerte da
        JOIN t_device d ON d.id = da.id_device
        JOIN t_alerte tr ON tr.id = da.id_alerte
        WHERE {DERNIER_STATUT_SQL} = 1
    """
    params = []
    if date_debut is not None:
        query += " AND da.date >= %s"
        params.append(date_debut)
    if date_fin is not None:
        query += " AND da.date <= %s"
        params.append(date_fin)
    if type_alerte is not None:          # ← ajout
        query += " AND tr.type = %s"     # ← ajout
        params.append(type_alerte)
    if search_params:
        motif = f"%{search_params}%"
        query += """ AND (
            d.serial_number ILIKE %s
            OR da.message ILIKE %s
            OR tr.type ILIKE %s
        )"""
        params.extend([motif, motif, motif])
    query += " ORDER BY da.date DESC, da.id DESC LIMIT %s OFFSET %s"
    params.extend([page_size, offset])

    cur.execute(query, tuple(params))
    return cur.fetchall()



def find_device_alertes_resolues_paginated(cur, page=1, page_size=10, date_debut=None, date_fin=None,type_alerte=None,search_params=None):
    """Alertes RESOLUE paginées (série, type, utilisateur)."""
    offset = (page - 1) * page_size
    query = f"""
        SELECT da.id, da.id_device, d.serial_number, tr.type,
               da.message, da.date,
               (
                   SELECT u.email
                   FROM t_device_utilisateur_recent ur
                   JOIN t_utilisateur u ON u.id = ur.id_utilisateur
                   WHERE ur.id_device = da.id_device
                   ORDER BY ur.date_observation DESC
                   LIMIT 1
               ) AS utilisateur_recent,
               COUNT(*) OVER() AS total
        FROM t_device_alerte da
        JOIN t_device d ON d.id = da.id_device
        JOIN t_alerte tr ON tr.id = da.id_alerte
        WHERE {DERNIER_STATUT_SQL} = 15
    """
    params = []
    if date_debut is not None:
        query += " AND da.date >= %s"
        params.append(date_debut)
    if date_fin is not None:
        query += " AND da.date <= %s"
        params.append(date_fin)
    if type_alerte is not None:          # ← ajout
        query += " AND tr.type = %s"     # ← ajout
        params.append(type_alerte)       # ← ajout
    if search_params:
        motif = f"%{search_params}%"
        query += """ AND (
            d.serial_number ILIKE %s
            OR da.message ILIKE %s
            OR tr.type ILIKE %s
        )"""
        params.extend([motif, motif, motif])
    query += " ORDER BY da.date DESC, da.id DESC LIMIT %s OFFSET %s"
    params.extend([page_size, offset])

    cur.execute(query, tuple(params))
    return cur.fetchall()


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
    query = f"""
        SELECT COUNT(*)
        FROM t_device_alerte da
        JOIN t_alerte tr ON tr.id = da.id_alerte
        WHERE tr.type = %s
          AND {DERNIER_STATUT_SQL} = %s
    """
    params = [type_alerte, id_statut]
    if date_debut is not None:
        query += " AND da.date >= %s"
        params.append(date_debut)
    if date_fin is not None:
        query += " AND da.date <= %s"
        params.append(date_fin)

    cur.execute(query, tuple(params))
    row = cur.fetchone()
    return row[0] if row else 0

