def get_liste_device(cur):
    cur.execute(
        """
        SELECT d.id, d.device_id, d.serial_number, d.modele, d.id_type_appareil,
               v.chromeos_version, v.chromeos_version AS chrome_version, d.mac_adress, d.ip_adress,
               d.date_creation, d.ram_total, c.cpu_model, c.freq_max_proc,
               c.cpu_architecture
        FROM t_device d
        LEFT JOIN t_device_cpu dc ON d.id = dc.id_device AND dc.id = (SELECT MAX(id) FROM t_device_cpu WHERE id_device = d.id)
        LEFT JOIN t_cpu c ON c.id = dc.id_cpu
        LEFT JOIN LATERAL (
            SELECT dv.chromeos_version
            FROM t_device_version dv
            WHERE dv.id_device = d.id
            ORDER BY dv.date DESC, dv.id DESC
            LIMIT 1
        ) v ON TRUE
        ORDER BY d.id ASC
        """
    )
    result = cur.fetchall()
    return result


def get_device_by_id(cur,id):
    cur.execute(
        """
        SELECT d.id, d.device_id, d.serial_number, d.modele, d.id_type_appareil,
               v.chromeos_version, v.chromeos_version AS chrome_version, d.mac_adress, d.ip_adress,
               d.date_creation, d.ram_total, c.cpu_model, c.freq_max_proc,
               c.cpu_architecture
        FROM t_device d
        LEFT JOIN t_device_cpu dc ON d.id = dc.id_device AND dc.id = (SELECT MAX(id) FROM t_device_cpu WHERE id_device = d.id)
        LEFT JOIN t_cpu c ON c.id = dc.id_cpu
        LEFT JOIN LATERAL (
            SELECT dv.chromeos_version
            FROM t_device_version dv
            WHERE dv.id_device = d.id
            ORDER BY dv.date DESC, dv.id DESC
            LIMIT 1
        ) v ON TRUE
        WHERE d.id = %s
        """,(id,)
    )
    result = cur.fetchone()
    return result

def get_device_by_device_id(cur,device_id):
    cur.execute(
        """
        SELECT d.id, d.device_id, d.serial_number, d.modele, d.id_type_appareil,
               v.chromeos_version, v.chromeos_version AS chrome_version, d.mac_adress, d.ip_adress,
               d.date_creation, d.ram_total, c.cpu_model, c.freq_max_proc,
               c.cpu_architecture
        FROM t_device d
        LEFT JOIN t_device_cpu dc ON d.id = dc.id_device AND dc.id = (SELECT MAX(id) FROM t_device_cpu WHERE id_device = d.id)
        LEFT JOIN t_cpu c ON c.id = dc.id_cpu
        LEFT JOIN LATERAL (
            SELECT dv.chromeos_version
            FROM t_device_version dv
            WHERE dv.id_device = d.id
            ORDER BY dv.date DESC, dv.id DESC
            LIMIT 1
        ) v ON TRUE
        WHERE d.device_id = %s
        """,(device_id,)
    )
    result = cur.fetchone()
    return result

def get_device_by_serial_number(cur,serial_number):
    cur.execute(
        """
        SELECT d.id, d.device_id, d.serial_number, d.modele, d.id_type_appareil,
               v.chromeos_version, v.chromeos_version AS chrome_version, d.mac_adress, d.ip_adress,
               d.date_creation, d.ram_total, c.cpu_model, c.freq_max_proc,
               c.cpu_architecture
        FROM t_device d
        LEFT JOIN t_device_cpu dc ON d.id = dc.id_device AND dc.id = (SELECT MAX(id) FROM t_device_cpu WHERE id_device = d.id)
        LEFT JOIN t_cpu c ON c.id = dc.id_cpu
        LEFT JOIN LATERAL (
            SELECT dv.chromeos_version
            FROM t_device_version dv
            WHERE dv.id_device = d.id
            ORDER BY dv.date DESC, dv.id DESC
            LIMIT 1
        ) v ON TRUE
        WHERE d.serial_number = %s
        """,(serial_number,)
    )
    result = cur.fetchone()
    return result


def insert_device(cur, device_id, serial_number, modele, id_type_appareil,
    date_creation, ip_adress, mac_adress, ram_total=None):
    cur.execute(
        """
        INSERT INTO t_device (device_id, serial_number, modele, id_type_appareil,
            mac_adress, ram_total, ip_adress, date_creation)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """,
        (device_id, serial_number, modele, id_type_appareil,
         mac_adress, ram_total, ip_adress, date_creation)
    )
    row = cur.fetchone()
    return row[0] if row else None

def update_device(cur, device_id, serial_number, modele,
    ip_adress, mac_adress, ram_total=None):
    cur.execute(
        """
        UPDATE t_device SET
            serial_number = %s,
            modele = %s,
            ip_adress = %s,
            mac_adress = %s,
            ram_total = COALESCE(ram_total, %s)
        WHERE device_id = %s
        RETURNING id;
        """,
        (serial_number, modele, ip_adress, mac_adress, ram_total, device_id)
    )
    row = cur.fetchone()
    return row[0] if row else None

def insert_device_cpu(cur, cpu_id, device_id):
    """
    Les lignes vides de liaison CPU ne doivent plus être créées.
    La vraie mesure CPU est stockée dans t_device_cpu via l'insertion de
    cpu_utiliser, cpu_libre, cpu_total et date.
    """
    return None


def get_last_cpu_for_device(cur, device_id):
    cur.execute(
        """
        SELECT id_cpu FROM t_device_cpu
        WHERE id_device = %s
        ORDER BY id DESC LIMIT 1;
        """,
        (device_id,)
    )
    row = cur.fetchone()
    return row[0] if row else None


def update_device_ram_total(cur, device_id, ram_total):
    cur.execute(
        """
        UPDATE t_device
        SET ram_total = %s
        WHERE id = %s
        RETURNING id;
        """,
        (ram_total, device_id)
    )
    row = cur.fetchone()
    return row[0] if row else None


def insert_device_filiale(cur, id_device, id_filiale):
    cur.execute(
        """
        INSERT INTO t_device_filiale (id_device, id_filiale)
        SELECT %s, %s
        WHERE NOT EXISTS (
            SELECT 1 FROM t_device_filiale
            WHERE id_device = %s AND id_filiale = %s
        );
        """,
        (id_device, id_filiale, id_device, id_filiale)
    )


def get_last_version(cur, id_device):
    cur.execute(
        """
        SELECT chromeos_version FROM t_device_version
        WHERE id_device = %s
        ORDER BY date DESC, id DESC
        LIMIT 1
        """,
        (id_device,)
    )
    row = cur.fetchone()
    return row[0] if row else None


def insert_device_version(cur, id_device, chromeos_version):
    cur.execute(
        """
        INSERT INTO t_device_version (id_device, chromeos_version)
        VALUES (%s, %s)
        """,
        (id_device, chromeos_version)
    )

    
def delete_all(cur):
    cur.execute(
    """
    TRUNCATE TABLE
        t_device_alerte_statut,
        t_device_alerte,
        t_device_cpu,
        t_device_filiale,
        t_device_reseau,
        t_device_statut,
        t_device_utilisateur,
        t_device_utilisateur_recent,
        t_disk_device,
        t_device_ram,
        t_device_version,
        t_rapport_device,
        t_evenement_device,
        t_imprimante_device,
        t_imprimante_user,
        t_statut_comparaison,
        t_comparaison,
        t_filiale_utilisateur,
        t_reseau_filiale,
        t_statut_synchronisation,
        t_synchronisation_historique,
        t_device,
        t_imprimante,
        t_utilisateur,
        t_filiale,
        t_reseau,
        t_cpu,
        t_disk
    RESTART IDENTITY CASCADE;
    
    """,
    )
    

def _get_device_cpu_info(cur, device_id):
    cur.execute(
        """
        SELECT c.cpu_model, c.freq_max_proc, c.cpu_architecture
        FROM t_device d
        LEFT JOIN t_device_cpu dc ON d.id = dc.id_device AND dc.id = (SELECT MAX(id) FROM t_device_cpu WHERE id_device = d.id)
        LEFT JOIN t_cpu c ON c.id = dc.id_cpu
        WHERE d.id = %s
        """,
        (device_id,),
    )
    return cur.fetchone()

def get_map_devices(cur):
    cur.execute("SELECT device_id, id FROM t_device")
    map_devices = dict(cur.fetchall())
    return map_devices


def get_liste_modele(cur):
    cur.execute(
        """
        SELECT DISTINCT modele
        FROM t_device
        WHERE modele IS NOT NULL AND modele <> ''
        ORDER BY modele ASC
        """
    )
    return [r[0] for r in cur.fetchall()]


def get_all_device_stats(cur):
    cur.execute(
        """
        SELECT COUNT(*) AS total,
               COUNT(*) FILTER (WHERE st.id_statut = 1) AS actifs
        FROM t_device d
        LEFT JOIN LATERAL (
            SELECT ds.id_statut
            FROM t_device_statut ds
            WHERE ds.id_device = d.id
            ORDER BY ds.date DESC, ds.id DESC
            LIMIT 1
        ) st ON TRUE
        """
    )
    row = cur.fetchone()
    return {
        "total": row[0] if row else 0,
        "actifs": row[1] if row else 0,
    }


def _rows_to_dicts(cur):
    colonnes = [desc[0] for desc in cur.description]
    return [dict(zip(colonnes, row)) for row in cur.fetchall()]


_DEVICE_FILTER_JOINS = """
LEFT JOIN t_type_appareil ta ON ta.id = d.id_type_appareil
LEFT JOIN LATERAL (
    SELECT df.id_filiale
    FROM t_device_filiale df
    WHERE df.id_device = d.id
    ORDER BY df.id ASC
    LIMIT 1
) fi ON TRUE
LEFT JOIN t_filiale f ON f.id = fi.id_filiale
LEFT JOIN LATERAL (
    SELECT ds.id_statut, s.nom
    FROM t_device_statut ds
    JOIN t_statut s ON s.id = ds.id_statut
    WHERE ds.id_device = d.id
    ORDER BY ds.date DESC, ds.id DESC
    LIMIT 1
) st ON TRUE
"""

_DEVICE_DETAIL_QUERY = """
SELECT
    d.id, d.device_id, d.serial_number, d.modele, d.id_type_appareil,
    ta.nom AS type_appareil, v.chromeos_version, v.chromeos_version AS chrome_version,
    d.mac_adress, d.ip_adress, d.date_creation AS date, d.ram_total,
    du.id_utilisateur, du.email AS utilisateur_email,
    st.nom AS status, st.id_statut AS id_status,
    fi.id_filiale, fi.org_unit_path AS filiale,
    ru.emails AS utilisateurs_recents,
    cp.cpu_model, cp.freq_max_proc AS cpu_freq_max, cp.cpu_architecture,
    di.total_reel AS disk_total, di.disponible AS disk_free, di.total_utiliser AS disk_used,
    di.model AS disk_model, di.type AS disk_type
FROM t_device d
LEFT JOIN t_type_appareil ta ON ta.id = d.id_type_appareil
LEFT JOIN LATERAL (
    SELECT du.id_utilisateur, u.email
    FROM t_device_utilisateur du
    JOIN t_utilisateur u ON u.id = du.id_utilisateur
    WHERE du.id_device = d.id
    ORDER BY du.id ASC
    LIMIT 1
) du ON TRUE
LEFT JOIN LATERAL (
    SELECT ds.id_statut, s.nom
    FROM t_device_statut ds
    JOIN t_statut s ON s.id = ds.id_statut
    WHERE ds.id_device = d.id
    ORDER BY ds.date DESC, ds.id DESC
    LIMIT 1
) st ON TRUE
LEFT JOIN LATERAL (
    SELECT df.id_filiale, f.org_unit_path
    FROM t_device_filiale df
    JOIN t_filiale f ON f.id = df.id_filiale
    WHERE df.id_device = d.id
    ORDER BY df.id ASC
    LIMIT 1
) fi ON TRUE
LEFT JOIN LATERAL (
    SELECT array_agg(DISTINCT u2.email) AS emails
    FROM t_device_utilisateur_recent dur
    JOIN t_utilisateur u2 ON u2.id = dur.id_utilisateur
    WHERE dur.id_device = d.id
) ru ON TRUE
LEFT JOIN LATERAL (
    SELECT c.cpu_model, c.freq_max_proc, c.cpu_architecture
    FROM t_device_cpu dc
    JOIN t_cpu c ON c.id = dc.id_cpu
    WHERE dc.id_device = d.id
    ORDER BY dc.date DESC, dc.id DESC
    LIMIT 1
) cp ON TRUE
LEFT JOIN LATERAL (
    SELECT dd.total_reel, dd.disponible, dd.total_utiliser, dk.model, dk.type
    FROM t_disk_device dd
    JOIN t_disk dk ON dk.id = dd.id_disk
    WHERE dd.id_device = d.id
    ORDER BY dd.date DESC, dd.id DESC
    LIMIT 1
) di ON TRUE
LEFT JOIN LATERAL (
    SELECT dv.chromeos_version
    FROM t_device_version dv
    WHERE dv.id_device = d.id
    ORDER BY dv.date DESC, dv.id DESC
    LIMIT 1
) v ON TRUE
WHERE d.id = ANY(%s)
ORDER BY d.id ASC
"""


def _build_device_filter_clause(id_filiale=None, filiale=None, id_statut=None,
                                statut=None, type_appareil=None, recherche=None,
                                datetime_from=None, datetime_to=None, modele=None,
                                utilisateur_recent=None):
    clauses = []
    params = []
    if modele:
        clauses.append("d.modele = %s")
        params.append(modele)
    if id_filiale is not None:
        clauses.append("fi.id_filiale = %s")
        params.append(id_filiale)
    if filiale:
        clauses.append("f.org_unit_path = %s")
        params.append(filiale)
    if id_statut is not None:
        clauses.append("st.id_statut = %s")
        params.append(id_statut)
    elif statut:
        clauses.append("UPPER(st.nom) = UPPER(%s)")
        params.append(statut)
    if utilisateur_recent:
        clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM t_device_utilisateur_recent dur
                JOIN t_utilisateur ur ON ur.id = dur.id_utilisateur
                WHERE dur.id_device = d.id AND ur.email = %s
            )
            """
        )
        params.append(utilisateur_recent)
    if type_appareil:
        clauses.append("UPPER(ta.nom) = UPPER(%s)")
        params.append(type_appareil)
    if recherche:
        clauses.append("d.serial_number ILIKE %s")
        params.append(f"%{recherche}%")
    if datetime_from is not None:
        clauses.append("d.date_creation >= %s")
        params.append(datetime_from)
    if datetime_to is not None:
        clauses.append("d.date_creation <= %s")
        params.append(datetime_to)

    return clauses, params


def find_devices_paginated(cur, page=1, page_size=10, id_filiale=None,
                           filiale=None, id_statut=None, statut=None,
                           type_appareil=None, recherche=None,
                           datetime_from=None, datetime_to=None, modele=None,
                           utilisateur_recent=None):
    clauses, params = _build_device_filter_clause(
        id_filiale=id_filiale, filiale=filiale, id_statut=id_statut,
        statut=statut, type_appareil=type_appareil, recherche=recherche,
        datetime_from=datetime_from, datetime_to=datetime_to,
        modele=modele, utilisateur_recent=utilisateur_recent
    )
    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    offset = (page - 1) * page_size

    cur.execute(
        f"""
        SELECT d.id, COUNT(*) OVER() AS total
        FROM t_device d
        {_DEVICE_FILTER_JOINS}
        {where}
        ORDER BY d.id ASC
        LIMIT %s OFFSET %s
        """,
        tuple(params + [page_size, offset])
    )
    id_rows = cur.fetchall()
    if not id_rows:
        return []

    total = id_rows[0][1]
    ids = [row[0] for row in id_rows]

    cur.execute(_DEVICE_DETAIL_QUERY, (ids,))
    rows = _rows_to_dicts(cur)
    for row in rows:
        row["total"] = total
    return rows


def get_device_detail(cur, id_device):
    cur.execute(_DEVICE_DETAIL_QUERY, ([int(id_device)],))
    rows = _rows_to_dicts(cur)
    return rows[0] if rows else None


def get_liste_version_by_device(cur, id_device):
    """Toutes les versions d'un appareil (source de la liste déroulante)."""
    cur.execute(
        """
        SELECT id, chromeos_version, date
        FROM t_device_version
        WHERE id_device = %s
        ORDER BY date ASC, id ASC
        """,
        (id_device,)
    )
    return cur.fetchall()


def get_version_intervalle(cur, id_device, chromeos_version):
    cur.execute(
        """
        SELECT v.date AS debut,
               (SELECT MIN(dv.date)
                FROM t_device_version dv
                WHERE dv.id_device = v.id_device
                  AND dv.date > v.date) AS fin
        FROM t_device_version v
        WHERE v.id_device = %s AND v.chromeos_version = %s
        ORDER BY v.date ASC
        LIMIT 1
        """,
        (id_device, chromeos_version)
    )
    return cur.fetchone()
