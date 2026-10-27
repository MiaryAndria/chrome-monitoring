def get_by_device_and_reseau(cur, device_id, reseau_id):
    cur.execute(
        """
        SELECT id, id_device, id_reseau, date
        FROM t_device_reseau
        WHERE id_device = %s AND id_reseau = %s
        LIMIT 1
        """,
        (device_id, reseau_id)
    )
    return cur.fetchone()


def insert_device_reseau(cur, device_id, reseau_id):
    cur.execute(
        """
        INSERT INTO t_device_reseau (id_device, id_reseau)
        VALUES (%s, %s)
        RETURNING id;
        """,
        (device_id, reseau_id)
    )
    row = cur.fetchone()
    return row[0] if row else None
