def get_liste_disk(cur):
    cur.execute(
        """
        SELECT *
        FROM t_disk
        ORDER BY id ASC;
        """
    )
    return cur.fetchall()


def get_disk_by_id(cur, id_disk):
    cur.execute(
        """
        SELECT *
        FROM t_disk
        WHERE id = %s;
        """,
        (id_disk,)
    )
    return cur.fetchone()


def get_disk_by_model(cur, disk_model):
    cur.execute(
        """
        SELECT *
        FROM t_disk
        WHERE model = %s
        ORDER BY id ASC;
        """,
        (disk_model,)
    )
    return cur.fetchall()


def get_disk_by_type(cur, disk_type):
    cur.execute(
        """
        SELECT *
        FROM t_disk
        WHERE type = %s
        ORDER BY id ASC;
        """,
        (disk_type,)
    )
    return cur.fetchall()


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


def insert_or_update_disk(cur, disk_model, disk_type):
    cur.execute(
        """
        INSERT INTO t_disk (model, type)
        VALUES (%s, %s)
        ON CONFLICT (model, type)
        DO UPDATE SET
            model = EXCLUDED.model
        RETURNING id;
        """,
        (disk_model, disk_type)
    )
    row = cur.fetchone()
    return row[0] if row else None


def update_disk(cur, id_disk, disk_model=None, disk_type=None):
    if disk_model is None and disk_type is None:
        return None

    query_parts = ["UPDATE t_disk SET"]
    values = []

    if disk_model is not None:
        query_parts.append("model = %s")
        values.append(disk_model)
    if disk_type is not None:
        query_parts.append("type = %s")
        values.append(disk_type)

    query_parts.append("WHERE id = %s RETURNING id;")
    values.append(id_disk)

    cur.execute(" ".join(query_parts), tuple(values))
    row = cur.fetchone()
    return row[0] if row else None


def delete_disk_by_id(cur, id_disk):
    cur.execute(
        """
        DELETE FROM t_disk
        WHERE id = %s;
        """,
        (id_disk,)
    )


def delete_disk_by_model(cur, disk_model):
    cur.execute(
        """
        DELETE FROM t_disk
        WHERE model = %s;
        """,
        (disk_model,)
    )


def delete_disk_by_type(cur, disk_type):
    cur.execute(
        """
        DELETE FROM t_disk
        WHERE type = %s;
        """,
        (disk_type,)
    )


def delete_all_disk(cur):
    cur.execute("TRUNCATE TABLE t_disk RESTART IDENTITY;")


__all__ = [
    "get_liste_disk",
    "get_disk_by_id",
    "get_disk_by_model",
    "get_disk_by_type",
    "get_disk_by_model_and_type",
    "get_or_create_disk",
    "insert_disk",
    "insert_or_update_disk",
    "update_disk",
    "delete_disk_by_id",
    "delete_disk_by_model",
    "delete_disk_by_type",
    "delete_all_disk",
]