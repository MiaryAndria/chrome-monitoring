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

def get_device_by_utilisateur(cur,id_utilisateur):
    cur.execute(
        """
        SELECT d.id, d.device_id, d.serial_number, d.modele, d.id_type_appareil,
               d.chromeos_version, d.chrome_version, d.mac_adress, d.ip_adress, d.date_creation
        FROM t_device d
        JOIN t_device_utilisateur du ON d.id = du.id_device
        WHERE du.id_utilisateur = %s
        """,(id_utilisateur,)
    )
    result = cur.fetchall()
    return result

def get_device_by_filiale(cur,id_filiale):
    cur.execute(
        """
        SELECT d.id, d.device_id, d.serial_number, d.modele, d.id_type_appareil,
               d.chromeos_version, d.chrome_version, d.mac_adress, d.ip_adress, d.date_creation
        FROM t_device d
        JOIN t_device_filiale df ON d.id = df.id_device
        WHERE df.id_filiale = %s
        """,(id_filiale,)
    )
    result = cur.fetchall()
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

def get_device_by_type(cur,id_type_appareil):
    cur.execute(
        """
        SELECT * FROM t_device WHERE id_type_appareil = %s
        """,(id_type_appareil,)
    )
    result = cur.fetchall()
    return result

def get_device_by_statut(cur,id_statut):
    cur.execute(
        """
        SELECT d.* FROM t_device d
        JOIN t_device_statut ds ON d.id = ds.id_device
        WHERE ds.id_statut = %s
        AND ds.date = (SELECT MAX(ds2.date) FROM t_device_statut ds2 WHERE ds2.id_device = d.id)
        """,(id_statut,)
    )
    result = cur.fetchall()
    return result

def get_liste_chromebook(cur):
    cur.execute(
        """
        SELECT d.* FROM t_device d
        JOIN t_type_appareil ta ON d.id_type_appareil = ta.id
        WHERE ta.nom = 'Chromebook'
        """
    )
    result = cur.fetchall()
    return result

def get_liste_chromebox(cur):
    cur.execute(
        """
        SELECT d.* FROM t_device d
        JOIN t_type_appareil ta ON d.id_type_appareil = ta.id
        WHERE ta.nom = 'Chromebox'
        """
    )
    result = cur.fetchall()
    return result

def get_device_actif(cur):
    cur.execute(
        """
        SELECT d.* FROM t_device d
        JOIN t_device_statut ds ON d.id = ds.id_device
        JOIN t_statut s ON ds.id_statut = s.id
        WHERE s.nom = 'Actif'
        AND ds.date = (SELECT MAX(ds2.date) FROM t_device_statut ds2 WHERE ds2.id_device = d.id)
        """
    )
    result = cur.fetchall()
    return result

def get_device_hors_ligne(cur):
    cur.execute(
        """
        SELECT d.* FROM t_device d
        JOIN t_device_statut ds ON d.id = ds.id_device
        JOIN t_statut s ON ds.id_statut = s.id
        WHERE s.nom = 'Hors ligne'
        AND ds.date = (SELECT MAX(ds2.date) FROM t_device_statut ds2 WHERE ds2.id_device = d.id)
        """
    )
    result = cur.fetchall()
    return result

def get_device_en_reparation(cur):
    cur.execute(
        """
        SELECT d.* FROM t_device d
        JOIN t_device_statut ds ON d.id = ds.id_device
        JOIN t_statut s ON ds.id_statut = s.id
        WHERE s.nom = 'En réparation'
        AND ds.date = (SELECT MAX(ds2.date) FROM t_device_statut ds2 WHERE ds2.id_device = d.id)
        """
    )
    result = cur.fetchall()
    return result

def get_device_anomalie(cur):
    cur.execute(
        """
        SELECT d.* FROM t_device d
        JOIN t_device_statut ds ON d.id = ds.id_device
        JOIN t_statut s ON ds.id_statut = s.id
        WHERE s.nom = 'Anomalie'
        AND ds.date = (SELECT MAX(ds2.date) FROM t_device_statut ds2 WHERE ds2.id_device = d.id)
        """
    )
    result = cur.fetchall()
    return result

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

def get_nombre_device(cur):
    cur.execute(
        """
        SELECT COUNT(*) FROM t_device
        """
    )
    result = cur.fetchone()
    return result[0]

def get_nombre_chromebook(cur):
    cur.execute(
        """
        SELECT COUNT(*) FROM t_device d
        JOIN t_type_appareil ta ON d.id_type_appareil = ta.id
        WHERE ta.nom = 'Chromebook'
        """
    )
    result = cur.fetchone()
    return result

def get_nombre_chromebox(cur):
    cur.execute(
        """
        SELECT COUNT(*) FROM t_device d
        JOIN t_type_appareil ta ON d.id_type_appareil = ta.id
        WHERE ta.nom = 'Chromebox'
        """
    )
    result = cur.fetchone()
    return result

def get_nombre_device_actif(cur):
    cur.execute(
        """
        SELECT COUNT(*) FROM t_device d
        JOIN t_device_statut ds ON d.id = ds.id_device
        JOIN t_statut s ON ds.id_statut = s.id
        WHERE s.nom = 'Actif'
        AND ds.date = (SELECT MAX(ds2.date) FROM t_device_statut ds2 WHERE ds2.id_device = d.id)
        """
    )
    result = cur.fetchone()
    return result

def get_nombre_device_hors_ligne(cur):
    cur.execute(
        """
        SELECT COUNT(*) FROM t_device d
        JOIN t_device_statut ds ON d.id = ds.id_device
        JOIN t_statut s ON ds.id_statut = s.id
        WHERE s.nom = 'Hors ligne'
        AND ds.date = (SELECT MAX(ds2.date) FROM t_device_statut ds2 WHERE ds2.id_device = d.id)
        """
    )
    result = cur.fetchone()
    return result

def get_nombre_device_reparation(cur):
    cur.execute(
        """
        SELECT COUNT(*) FROM t_device d
        JOIN t_device_statut ds ON d.id = ds.id_device
        JOIN t_statut s ON ds.id_statut = s.id
        WHERE s.nom = 'En réparation'
        AND ds.date = (SELECT MAX(ds2.date) FROM t_device_statut ds2 WHERE ds2.id_device = d.id)
        """
    )
    result = cur.fetchone()
    return result

def get_nombre_device_anomalie(cur):
    cur.execute(
        """
        SELECT COUNT(*) FROM t_device d
        JOIN t_device_statut ds ON d.id = ds.id_device
        JOIN t_statut s ON ds.id_statut = s.id
        WHERE s.nom = 'Anomalie'
        AND ds.date = (SELECT MAX(ds2.date) FROM t_device_statut ds2 WHERE ds2.id_device = d.id)
        """
    )
    result = cur.fetchone()
    return result

def get_device_by_device_id_and_serial_number(cur,device_id,serial_number):
    cur.execute(
        """
        SELECT * FROM t_device WHERE device_id = %s AND serial_number = %s
        """,(device_id,serial_number,)
    )
    result = cur.fetchone()
    return result

def get_device_by_type_and_statut(cur,id_type_appareil,id_statut):
    cur.execute(
        """
        SELECT d.* FROM t_device d
        JOIN t_device_statut ds ON d.id = ds.id_device
        WHERE d.id_type_appareil = %s AND ds.id_statut = %s
        AND ds.date = (SELECT MAX(ds2.date) FROM t_device_statut ds2 WHERE ds2.id_device = d.id)
        """,(id_type_appareil,id_statut,)
    )
    result = cur.fetchall()
    return result

def get_device_by_utilisateur_and_type(cur,id_utilisateur,id_type_appareil):
    cur.execute(
        """
        SELECT d.* FROM t_device d
        JOIN t_device_utilisateur du ON d.id = du.id_device
        WHERE du.id_utilisateur = %s AND d.id_type_appareil = %s
        """,(id_utilisateur,id_type_appareil,)
    )
    result = cur.fetchall()
    return result

def get_device_by_filiale_and_type(cur,id_filiale,id_type_appareil):
    cur.execute(
        """
        SELECT d.* FROM t_device d
        JOIN t_device_filiale df ON d.id = df.id_device
        WHERE df.id_filiale = %s AND d.id_type_appareil = %s
        AND df.date_fin_affectation IS NULL
        """,(id_filiale,id_type_appareil,)
    )
    result = cur.fetchall()
    return result

def get_device_by_filiale_and_statut(cur,id_filiale,id_statut):
    cur.execute(
        """
        SELECT d.* FROM t_device d
        JOIN t_device_filiale df ON d.id = df.id_device
        JOIN t_device_statut ds ON d.id = ds.id_device
        WHERE df.id_filiale = %s AND ds.id_statut = %s
        AND df.date_fin_affectation IS NULL
        AND ds.date = (SELECT MAX(ds2.date) FROM t_device_statut ds2 WHERE ds2.id_device = d.id)
        """,(id_filiale,id_statut,)
    )
    result = cur.fetchall()
    return result

def get_device_by_filiale_and_utilisateur(cur,id_filiale,id_utilisateur):
    cur.execute(
        """
        SELECT d.* FROM t_device d
        JOIN t_device_filiale df ON d.id = df.id_device
        JOIN t_device_utilisateur du ON d.id = du.id_device
        WHERE df.id_filiale = %s AND du.id_utilisateur = %s
        AND df.date_fin_affectation IS NULL
        """,(id_filiale,id_utilisateur,)
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
    cur.execute(
        """
        INSERT INTO t_device_cpu (id_device, id_cpu)
        VALUES (%s, %s)
        RETURNING id;
        """,
        (device_id, cpu_id)
    )
    row = cur.fetchone()
    return row[0] if row else None

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
        t_device_alerte,
        t_device_utilisateur_recent,
        t_device_filiale,
        t_device_historique,
        t_device_statut,
        t_device_utilisateur,
        t_disk_device,
        t_rapport_device,
        t_version_report,
        t_evenement_device,
        t_imprimante_device,
        t_comparaison,
        t_filiale_utilisateur,
        t_reseau_filiale,
        t_device_cpu,
        t_device,
        t_imprimante,
        t_alerte,
        t_type_evenement,
        t_type_rapport,
        t_utilisateur,
        t_type_appareil,
        t_reseau,
        t_filiale,
        t_configuration,
        t_cpu,
        t_statut,
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