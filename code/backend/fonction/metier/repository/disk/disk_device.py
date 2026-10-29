def insert_disk_device(cur, id_device, id_disk, disponible=None,disponible_formater=None,total_reel=None, total_formater=None, total_utiliser=None,total_utiliser_formater=None, date_telemetry=None):
    cur.execute(
        """
        INSERT INTO t_disk_device (id_device, id_disk, disponible, disponible_formater, total_reel, total_formater, total_utiliser, total_utiliser_formater, date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id_device, id_disk, date)
        DO UPDATE SET
            disponible             = EXCLUDED.disponible,
            disponible_formater    = EXCLUDED.disponible_formater,
            total_reel             = EXCLUDED.total_reel,
            total_formater         = EXCLUDED.total_formater,
            total_utiliser         = EXCLUDED.total_utiliser,
            total_utiliser_formater = EXCLUDED.total_utiliser_formater
        RETURNING id;
        """,
        (id_device, id_disk, disponible, disponible_formater, total_reel, total_formater, total_utiliser, total_utiliser_formater, date_telemetry)
    )
    row = cur.fetchone()
    return row[0] if row else None


def get_latest_by_device(cur, id_device):
    """
    Retourne le dernier relevé de stockage d'un device, enrichi du disque.
    """
    cur.execute(
        """
        SELECT dd.id, dd.id_device, dd.id_disk, dk.model, dk.type,
               dd.disponible, dd.total_reel, dd.total_utiliser,
               dd.disponible_formater, dd.total_formater,
               dd.total_utiliser_formater, dd.date
        FROM t_disk_device dd
        JOIN t_disk dk ON dk.id = dd.id_disk
        WHERE dd.id_device = %s
        ORDER BY dd.date DESC, dd.id DESC
        LIMIT 1
        """,
        (id_device,)
    )
    row = cur.fetchone()
    if row is None:
        return None

    return {
        "id": row[0],
        "id_device": row[1],
        "id_disk": row[2],
        "disk_model": row[3],
        "disk_type": row[4],
        "disponible": row[5],
        "total_reel": row[6],
        "total_utiliser": row[7],
        "disponible_formater": row[8],
        "total_formater": row[9],
        "total_utiliser_formater": row[10],
        "date": row[11],
    }