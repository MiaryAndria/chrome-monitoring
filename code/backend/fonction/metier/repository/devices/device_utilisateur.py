def insert_device_utilisateur(cur, id_device, id_utilisateur):
    cur.execute(
        """
        INSERT INTO t_device_utilisateur (id_device, id_utilisateur)
        VALUES (%s, %s)
        ON CONFLICT (id_device, id_utilisateur) DO NOTHING
        """, (id_device, id_utilisateur)
    )

def get_utilisateurs_by_device(cur, id_device):
    cur.execute(
        """
        SELECT u.* FROM t_utilisateur u
        JOIN t_device_utilisateur du ON u.id = du.id_utilisateur
        WHERE du.id_device = %s
        """, (id_device,)
    )
    result = cur.fetchall()
    return result

def get_devices_by_utilisateur(cur, id_utilisateur):
    cur.execute(
        """
        SELECT d.* FROM t_device d
        JOIN t_device_utilisateur du ON d.id = du.id_device
        WHERE du.id_utilisateur = %s
        """, (id_utilisateur,)
    )
    result = cur.fetchall()
    return result

def get_device_utilisateur_by_device_and_utilisateur(cur, id_device, id_utilisateur):
    cur.execute(
        """
        SELECT * FROM t_device_utilisateur
        WHERE id_device = %s AND id_utilisateur = %s
        """, (id_device, id_utilisateur)
    )
    result = cur.fetchone()
    return result
