


def get_disk_by_model_and_type(cur, disk_model, disk_type):
    cur.execute(
        """
        SELECT *
        FROM t_disk
        WHERE model = %s AND type = %s
        ORDER BY id ASC;
        """,
        (disk_model, disk_type)
    )
    return cur.fetchall()


def get_or_create_disk(cur, disk_model, disk_type):

    disk_model = disk_model.strip() if isinstance(disk_model, str) else disk_model
    disk_type = disk_type.strip() if isinstance(disk_type, str) else disk_type

    disk_by_model_type = get_disk_by_model_and_type(cur, disk_model, disk_type)

    if disk_by_model_type:
        first_row = disk_by_model_type[0]
        return first_row[0] if isinstance(first_row, (list, tuple)) else first_row

    return insert_disk(cur, disk_model, disk_type)


def insert_disk(cur, disk_model, disk_type):
    cur.execute(
        """
        INSERT INTO t_disk (model, type)
        VALUES (%s, %s)
        RETURNING id;
        """,
        (disk_model, disk_type)
    )
    row = cur.fetchone()
    return row[0] if row else None


