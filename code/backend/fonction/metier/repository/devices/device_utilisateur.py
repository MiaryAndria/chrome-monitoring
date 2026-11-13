def insert_device_utilisateur(cur, id_device, id_utilisateur):
    cur.execute(
        """
        INSERT INTO t_device_utilisateur (id_device, id_utilisateur)
        VALUES (%s, %s)
        ON CONFLICT (id_device, id_utilisateur) DO NOTHING
        """, (id_device, id_utilisateur)
    )

