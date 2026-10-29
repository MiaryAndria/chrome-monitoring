def get_liste_device(cur):
    cur.execute(
        """
        SELECT d.id, d.device_id, d.serial_number, d.modele, d.id_type_appareil,
               d.chromeos_version, d.chrome_version, d.mac_adress, d.ip_adress,
               d.date_creation, d.ram_total, c.cpu_model, c.freq_max_proc,
               c.cpu_architecture
        FROM t_device d
        LEFT JOIN t_device_cpu dc ON d.id = dc.id_device AND dc.id = (SELECT MAX(id) FROM t_device_cpu WHERE id_device = d.id)
        LEFT JOIN t_cpu c ON c.id = dc.id_cpu
        ORDER BY d.id ASC
        """
    )
    result = cur.fetchall()
    return result


def get_device_by_id(cur,id):
    cur.execute(
        """
        SELECT d.id, d.device_id, d.serial_number, d.modele, d.id_type_appareil,
               d.chromeos_version, d.chrome_version, d.mac_adress, d.ip_adress,
               d.date_creation, d.ram_total, c.cpu_model, c.freq_max_proc,
               c.cpu_architecture
        FROM t_device d
        LEFT JOIN t_device_cpu dc ON d.id = dc.id_device AND dc.id = (SELECT MAX(id) FROM t_device_cpu WHERE id_device = d.id)
        LEFT JOIN t_cpu c ON c.id = dc.id_cpu
        WHERE d.id = %s
        """,(id,)
    )
    result = cur.fetchone()
    return result

def get_device_by_device_id(cur,device_id):
    cur.execute(
        """
        SELECT d.id, d.device_id, d.serial_number, d.modele, d.id_type_appareil,
               d.chromeos_version, d.chrome_version, d.mac_adress, d.ip_adress,
               d.date_creation, d.ram_total, c.cpu_model, c.freq_max_proc,
               c.cpu_architecture
        FROM t_device d
        LEFT JOIN t_device_cpu dc ON d.id = dc.id_device AND dc.id = (SELECT MAX(id) FROM t_device_cpu WHERE id_device = d.id)
        LEFT JOIN t_cpu c ON c.id = dc.id_cpu
        WHERE d.device_id = %s
        """,(device_id,)
    )
    result = cur.fetchone()
    return result

def get_device_by_serial_number(cur,serial_number):
    cur.execute(
        """
        SELECT d.id, d.device_id, d.serial_number, d.modele, d.id_type_appareil,
               d.chromeos_version, d.chrome_version, d.mac_adress, d.ip_adress,
               d.date_creation, d.ram_total, c.cpu_model, c.freq_max_proc,
               c.cpu_architecture
        FROM t_device d
        LEFT JOIN t_device_cpu dc ON d.id = dc.id_device AND dc.id = (SELECT MAX(id) FROM t_device_cpu WHERE id_device = d.id)
        LEFT JOIN t_cpu c ON c.id = dc.id_cpu
        WHERE d.serial_number = %s
        """,(serial_number,)
    )
    result = cur.fetchone()
    return result


def get_filiale_by_device(cur, id_device):
    cur.execute(
        """
        SELECT f.id, f.org_unit_path
        FROM t_filiale f
        JOIN t_device_filiale df ON f.id = df.id_filiale
        WHERE df.id_device = %s
        LIMIT 1
        """, (id_device,)
    )
    result = cur.fetchone()
    return result


STATUTS_AUTORISES = ('ACTIVE', 'DELINQUENT', 'DISABLED', 'DEPROVISIONED')


def recherche_multicritere(cur, recherche):
    terme = f"%{recherche}%"
    cur.execute(
        """
        SELECT DISTINCT d.id, d.device_id, d.serial_number, d.modele, d.id_type_appareil,
               d.chromeos_version, d.chrome_version, d.mac_adress, d.ip_adress,
               d.date_creation, ta.nom AS type_appareil, s.nom AS statut,
               f.org_unit_path AS filiale
        FROM t_device d
        LEFT JOIN t_device_utilisateur du ON d.id = du.id_device
        LEFT JOIN t_utilisateur u ON du.id_utilisateur = u.id
        LEFT JOIN t_device_utilisateur_recent dur ON d.id = dur.id_device
        LEFT JOIN t_utilisateur ur ON dur.id_utilisateur = ur.id
        LEFT JOIN t_type_appareil ta ON d.id_type_appareil = ta.id
        LEFT JOIN t_device_statut ds ON d.id = ds.id_device
            AND ds.date = (
                SELECT MAX(ds2.date)
                FROM t_device_statut ds2
                WHERE ds2.id_device = d.id
            )
        LEFT JOIN t_statut s ON ds.id_statut = s.id
        LEFT JOIN t_device_filiale df ON d.id = df.id_device
        LEFT JOIN t_filiale f ON df.id_filiale = f.id
        WHERE d.device_id ILIKE %s
           OR d.serial_number ILIKE %s
           OR d.modele ILIKE %s
           OR u.email ILIKE %s
           OR ur.email ILIKE %s
           OR ta.nom ILIKE %s
           OR s.nom ILIKE %s
           OR f.org_unit_path ILIKE %s
        ORDER BY d.id ASC
        """, (terme, terme, terme, terme, terme, terme, terme, terme)
    )

    result = cur.fetchall()
    return result


def insert_device(cur, device_id, serial_number, modele, id_type_appareil,
    chromeos_version, chrome_version, date_creation, ip_adress, mac_adress, ram_total=None):
    cur.execute(
        """
        INSERT INTO t_device (device_id, serial_number, modele, id_type_appareil,
            chromeos_version, chrome_version, mac_adress, ram_total, ip_adress, date_creation)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """,
        (device_id, serial_number, modele, id_type_appareil,
         chromeos_version, chrome_version, mac_adress, ram_total, ip_adress, date_creation)
    )
    row = cur.fetchone()
    return row[0] if row else None

def update_device(cur, device_id, serial_number, modele,
    chromeos_version, chrome_version, ip_adress, mac_adress, ram_total=None):
    cur.execute(
        """
        UPDATE t_device SET
            serial_number = %s,
            modele = %s,
            chromeos_version = %s,
            chrome_version = %s,
            ip_adress = %s,
            mac_adress = %s,
            ram_total = COALESCE(ram_total, %s)
        WHERE device_id = %s
        RETURNING id;
        """,
        (serial_number, modele, chromeos_version, chrome_version,
         ip_adress, mac_adress, ram_total, device_id)
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
    

def _get_last_disk_info(cur, device_id):
    cur.execute(
        """
        SELECT dd.total_reel, dd.total_formater, dd.disponible, dd.total_utiliser,
               d.model, d.type
        FROM t_disk_device dd
        JOIN t_disk d ON d.id = dd.id_disk
        WHERE dd.id_device = %s
        ORDER BY dd.date DESC, dd.id DESC
        LIMIT 1
        """,
        (device_id,),
    )
    return cur.fetchone()


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
        FROM v_appareils_filtres
        WHERE modele IS NOT NULL AND modele <> ''
        ORDER BY modele ASC
        """
    )
    return [r[0] for r in cur.fetchall()]


def _rows_to_dicts(cur):
    colonnes = [desc[0] for desc in cur.description]
    return [dict(zip(colonnes, row)) for row in cur.fetchall()]


def _build_device_filter_clause(id_filiale=None, filiale=None, statut=None,
                                type_appareil=None, recherche=None,
                                datetime_from=None, datetime_to=None,modele=None):
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
    if statut:
        clauses.append("UPPER(status) = UPPER(%s)")
        params.append(statut)
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
                           filiale=None, statut=None, type_appareil=None,
                           recherche=None, datetime_from=None,
                           datetime_to=None,modele=None):
    clauses, params = _build_device_filter_clause(
        id_filiale, filiale, statut, type_appareil, recherche,
        datetime_from, datetime_to,modele
    )
    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    offset = (page - 1) * page_size

    cur.execute(
        f"""
        SELECT
            id, device_id, serial_number, modele, id_type_appareil,
            type_appareil, chromeos_version, chrome_version, mac_adress,
            ip_adress, date, ram_total, id_utilisateur, utilisateur_email,
            status, id_filiale, filiale, utilisateurs_recents, cpu_model,
            cpu_freq_max, cpu_architecture, disk_total, disk_free, disk_used,
            disk_model, disk_type,
            COUNT(*) OVER() AS total
        FROM v_appareils_filtres
        {where}
        ORDER BY id ASC
        LIMIT %s OFFSET %s
        """,
        tuple(params + [page_size, offset])
    )
    return _rows_to_dicts(cur)
