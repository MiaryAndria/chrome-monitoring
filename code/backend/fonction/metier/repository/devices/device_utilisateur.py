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

