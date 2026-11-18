def get_liste_device(cur):
    cur.execute("SELECT id FROM t_device ORDER BY id ASC")
    return cur.fetchall()

def get_device_type(cur,id_device):
    cur.execute(
        """
        SELECT t_device.* , t_type_appareil.*
        FROM t_device
        LEFT JOIN t_type_appareil ON t_type_appareil.id = t_device.id_type_appareil
        WHERE id_device = %s
        """,(id_device)
    )
    return cur.fetchone()

def get_device_by_id(cur, id):
    cur.execute(
        """
        SELECT id, device_id, serial_number, modele, id_type_appareil,
               chromeos_version, chrome_version, mac_adress, ip_adress,
               date, ram_total, cpu_model, cpu_freq_max, cpu_architecture
        FROM v_device_detail
        WHERE id = %s
        """,
        (id,),
    )
    return cur.fetchone()


def get_device_by_device_id(cur, device_id):
    cur.execute(
        """
        SELECT id, device_id, serial_number, modele, id_type_appareil,
               chromeos_version, chrome_version, mac_adress, ip_adress,
               date, ram_total, cpu_model, cpu_freq_max, cpu_architecture
        FROM v_device_detail
        WHERE device_id = %s
        """,
        (device_id,),
    )
    return cur.fetchone()


def get_device_by_serial_number(cur, serial_number):
    cur.execute(
        """
        SELECT id, device_id, serial_number, modele, id_type_appareil,
               chromeos_version, chrome_version, mac_adress, ip_adress,
               date, ram_total, cpu_model, cpu_freq_max, cpu_architecture
        FROM v_device_detail
        WHERE serial_number = %s
        """,
        (serial_number,),
    )
    return cur.fetchone()


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
        "SELECT cpu_model, cpu_freq_max, cpu_architecture FROM v_device_detail WHERE id = %s",
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
    result = []
    for r in cur.fetchall():
        result.append(r[0])
    return result


def get_all_device_stats(cur):
    cur.execute(
        """
        SELECT COUNT(*) AS total,
               COUNT(*) FILTER (
                   WHERE (
                       SELECT ds.id_statut
                       FROM t_device_statut ds
                       WHERE ds.id_device = d.id
                       ORDER BY ds.date DESC, ds.id DESC
                       LIMIT 1
                   ) = 1
               ) AS actifs
        FROM t_device d
        """
    )
    row = cur.fetchone()
    return {
        "total": row[0] if row else 0,
        "actifs": row[1] if row else 0,
    }


def _rows_to_dicts(cur):
    colonnes = [desc[0] for desc in cur.description]
    result = []
    for row in cur.fetchall():
        result.append(dict(zip(colonnes, row)))
    return result


def _build_device_filter_clause(id_filiale=None, filiale=None, id_statut=None,
                                statut=None, type_appareil=None, recherche=None,
                                datetime_from=None, datetime_to=None, modele=None,
                                utilisateur_recent=None):
    clauses = []
    params = []
    if modele:
        clauses.append("modele = %s")
        params.append(modele)
    if id_filiale is not None:
        clauses.append("id_filiale = %s")
        params.append(id_filiale)
    if filiale:
        clauses.append("filiale = %s")
        params.append(filiale)
    if id_statut is not None:
        clauses.append("id_status = %s")
        params.append(id_statut)
    elif statut:
        clauses.append("UPPER(status) = UPPER(%s)")
        params.append(statut)
    if utilisateur_recent:
        clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM t_device_utilisateur_recent dur
                JOIN t_utilisateur ur ON ur.id = dur.id_utilisateur
                WHERE dur.id_device = v_device_detail.id AND ur.email = %s
            )
            """
        )
        params.append(utilisateur_recent)
    if type_appareil:
        clauses.append("UPPER(type_appareil) = UPPER(%s)")
        params.append(type_appareil)
    if recherche:
        clauses.append("serial_number ILIKE %s")
        params.append(f"%{recherche}%")
    if datetime_from is not None:
        clauses.append("date >= %s")
        params.append(datetime_from)
    if datetime_to is not None:
        clauses.append("date <= %s")
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

    cur.execute(f"SELECT COUNT(*) FROM v_device_detail {where}", tuple(params))
    total = cur.fetchone()[0]

    cur.execute(
        f"""
        SELECT *
        FROM v_device_detail
        {where}
        ORDER BY id ASC
        LIMIT %s OFFSET %s
        """,
        tuple(params + [page_size, offset])
    )
    return _rows_to_dicts(cur), total


def get_device_detail(cur, id_device):
    cur.execute("SELECT * FROM v_device_detail WHERE id = %s", (id_device,))
    rows = _rows_to_dicts(cur)
    return rows[0] if rows else None


def get_liste_version_by_device(cur, id_device):
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
