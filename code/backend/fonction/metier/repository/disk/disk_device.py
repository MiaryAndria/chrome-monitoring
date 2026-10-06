def get_liste_disk_device(cur):
    cur.execute(
        """
        SELECT *
        FROM t_disk_device
        ORDER BY id ASC;
        """
    )
    return cur.fetchall()


def get_disk_device_by_id(cur, id_disk_device):
    cur.execute(
        """
        SELECT *
        FROM t_disk_device
        WHERE id = %s;
        """,
        (id_disk_device,)
    )
    return cur.fetchone()


def get_disk_device_by_id_device(cur, id_device):
    cur.execute(
        """
        SELECT *
        FROM t_disk_device
        WHERE id_device = %s
        ORDER BY id ASC;
        """,
        (id_device,)
    )
    return cur.fetchall()


def get_disk_device_by_id_disk(cur, id_disk):
    cur.execute(
        """
        SELECT *
        FROM t_disk_device
        WHERE id_disk = %s
        ORDER BY id ASC;
        """,
        (id_disk,)
    )
    return cur.fetchall()


def get_disk_device_by_id_device_and_id_disk(cur, id_device, id_disk):
    cur.execute(
        """
        SELECT *
        FROM t_disk_device
        WHERE id_device = %s AND id_disk = %s
        ORDER BY id ASC;
        """,
        (id_device, id_disk)
    )
    return cur.fetchall()


def insert_disk_device(cur, id_device, id_disk, disponible=None,disponible_formater=None,total_reel=None, total_formater=None, total_utiliser=None,total_utiliser_formater=None, date_telemetry=None):
    cur.execute(
        """
        INSERT INTO t_disk_device (id_device, id_disk, disponible,disponible_formater, total_reel, total_formater, total_utiliser,total_utiliser_formater, date)
        VALUES (%s, %s, %s, %s, %s, %s,%s, %s,%s)
        RETURNING id;
        """,
        (id_device, id_disk, disponible,disponible_formater,total_reel,total_formater, total_utiliser,total_utiliser_formater, date_telemetry)
    )
    row = cur.fetchone()
    return row[0] if row else None


def delete_disk_device_by_id(cur, id_disk_device):
    cur.execute(
        """
        DELETE FROM t_disk_device
        WHERE id = %s;
        """,
        (id_disk_device,)
    )


def delete_disk_device_by_id_device(cur, id_device):
    cur.execute(
        """
        DELETE FROM t_disk_device
        WHERE id_device = %s;
        """,
        (id_device,)
    )


def delete_disk_device_by_id_disk(cur, id_disk):
    cur.execute(
        """
        DELETE FROM t_disk_device
        WHERE id_disk = %s;
        """,
        (id_disk,)
    )


def delete_all_disk_device(cur):
    cur.execute("TRUNCATE TABLE t_disk_device RESTART IDENTITY;")

__all__ = [
    "get_liste_disk_device",
    "get_disk_device_by_id",
    "get_disk_device_by_id_device",
    "get_disk_device_by_id_disk",
    "get_disk_device_by_id_device_and_id_disk",
    "get_or_create_disk_device",
    "insert_disk_device",
    "insert_or_update_disk_device",
    "update_disk_device",
    "delete_disk_device_by_id",
    "delete_disk_device_by_id_device",
    "delete_disk_device_by_id_disk",
    "delete_all_disk_device",
]