from backend.fonction.conn.connexion import get_connection
def get_liste_device(cur):
    cur.execute(
        """
        SELECT * FROM t_device
        """
    )
    result = cur.fetchall()
    return result


def get_device_by_id(cur,id):
    cur.execute(
        """
        SELECT * FROM t_device WHERE id = %s
        """,(id,)
    )
    result = cur.fetchone()
    return result

def get_device_by_device_id(cur,device_id):
    cur.execute(
        """
        SELECT * FROM t_device WHERE device_id = %s
        """,(device_id,)
    )
    result = cur.fetchone()
    return result

def get_device_by_serial_number(cur,serial_number):
    cur.execute(
        """
        SELECT * FROM t_device WHERE serial_number = %s
        """,(serial_number,)
    )
    result = cur.fetchone()
    return result

def get_device_by_utilisateur(cur,id_utilisateur):
    cur.execute(
        """
        SELECT * FROM t_device WHERE id_utilisateur = %s
        """,(id_utilisateur,)
    )
    result = cur.fetchall()
    return result

def get_device_by_filiale(cur,id_filiale):
    cur.execute(
        """
        SELECT d.id, d.device_id, d.serial_number, d.modele, d.id_type_appareil,
               d.id_utilisateur, d.chromeos_version, d.chrome_version, d.date_creation,
               d.ip_adress, d.mac_adress
        FROM t_device d
        JOIN t_device_filiale df ON d.id = df.id_device
        WHERE df.id_filiale = %s
        """,(id_filiale,)
    )
    result = cur.fetchall()
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

def search_device(cur,recherche):
    cur.execute(
        """
        SELECT d.*, u.email AS email_utilisateur, ta.nom AS type_appareil,
               s.nom AS statut, f.nom AS filiale
        FROM t_device d
        LEFT JOIN t_utilisateur u ON d.id_utilisateur = u.id
        LEFT JOIN t_type_appareil ta ON d.id_type_appareil = ta.id
        LEFT JOIN t_device_statut ds ON d.id = ds.id_device
            AND ds.date = (SELECT MAX(ds2.date) FROM t_device_statut ds2 WHERE ds2.id_device = d.id)
        LEFT JOIN t_statut s ON ds.id_statut = s.id
        LEFT JOIN t_device_filiale df ON d.id = df.id_device AND df.date_fin_affectation IS NULL
        LEFT JOIN t_filiale f ON df.id_filiale = f.id
        WHERE d.device_id ILIKE %s
           OR d.serial_number ILIKE %s
           OR d.modele ILIKE %s
           OR u.email ILIKE %s
           OR ta.nom ILIKE %s
           OR s.nom ILIKE %s
           OR f.nom ILIKE %s
        """,(recherche,recherche,recherche,recherche,recherche,recherche,recherche,)
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
    return result

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
        SELECT * FROM t_device WHERE id_utilisateur = %s AND id_type_appareil = %s
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
        WHERE df.id_filiale = %s AND d.id_utilisateur = %s
        AND df.date_fin_affectation IS NULL
        """,(id_filiale,id_utilisateur,)
    )
    result = cur.fetchall()
    return result

def insert_device(cur, device_id, serial_number, modele, id_type_appareil, id_utilisateur,
    chromeos_version, chrome_version, date_creation, ip_adress, mac_adress):
    cur.execute(
        """
        INSERT INTO t_device (device_id, serial_number, modele, id_type_appareil, id_utilisateur,
            chromeos_version, chrome_version, date_creation, ip_adress, mac_adress)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """,
        (device_id, serial_number, modele, id_type_appareil, id_utilisateur,
         chromeos_version, chrome_version, date_creation, ip_adress, mac_adress)
    )
    row = cur.fetchone()
    return row[0] if row else None

def update_device(cur, device_id, serial_number, modele,
    chromeos_version, chrome_version, ip_adress, mac_adress):
    cur.execute(
        """
        UPDATE t_device SET
            serial_number = %s,
            modele = %s,
            chromeos_version = %s,
            chrome_version = %s,
            ip_adress = %s,
            mac_adress = %s
        WHERE device_id = %s
        RETURNING id;
        """,
        (serial_number, modele, chromeos_version, chrome_version,
         ip_adress, mac_adress, device_id)
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
        t_rapport_device,
        t_version_report,
        t_evenement_device,
        t_imprimante_device,
        t_comparaison,
        t_filiale_utilisateur,
        t_reseau_filiale,
        t_device,
        t_imprimante,
        t_alerte,
        t_type_evenement,
        t_type_rapport,
        t_statut,
        t_utilisateur,
        t_type_appareil,
        t_reseau,
        t_filiale,
        t_configuration
    RESTART IDENTITY CASCADE;
    
    """,
    )