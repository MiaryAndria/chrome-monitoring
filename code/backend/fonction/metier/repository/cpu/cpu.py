def get_liste_cpu(cur):
    cur.execute(
        """
        SELECT *
        FROM t_cpu
        ORDER BY id ASC;
        """
    )
    return cur.fetchall()


def get_cpu_by_id(cur, id_cpu):
    cur.execute(
        """
        SELECT *
        FROM t_cpu
        WHERE id = %s;
        """,
        (id_cpu,)
    )
    return cur.fetchone()


def get_cpu_by_model(cur, cpu_model):
    cur.execute(
        """
        SELECT *
        FROM t_cpu
        WHERE cpu_model = %s
        ORDER BY id ASC;
        """,
        (cpu_model,)
    )
    return cur.fetchall()


def get_cpu_by_architecture(cur, cpu_architecture):
    cur.execute(
        """
        SELECT *
        FROM t_cpu
        WHERE cpu_architecture = %s
        ORDER BY id ASC;
        """,
        (cpu_architecture,)
    )
    return cur.fetchall()


def get_cpu_by_model_and_architecture(cur, cpu_model, cpu_architecture):
    cur.execute(
        """
        SELECT *
        FROM t_cpu
        WHERE cpu_model = %s AND cpu_architecture = %s
        ORDER BY id ASC;
        """,
        (cpu_model, cpu_architecture)
    )
    return cur.fetchall()


def get_or_create_cpu(cur, cpu_model, freq_max_proc=None, cpu_architecture=None):
    cpu_model = cpu_model.strip() if isinstance(cpu_model, str) else cpu_model
    cpu_architecture = cpu_architecture.strip() if isinstance(cpu_architecture, str) else cpu_architecture

    cur.execute(
        """
        SELECT id
        FROM t_cpu
        WHERE cpu_model = %s AND cpu_architecture = %s;
        """,
        (cpu_model, cpu_architecture)
    )
    row = cur.fetchone()
    if row:
        cpu_id = row[0]
        if freq_max_proc is not None:
            cur.execute(
                """
                UPDATE t_cpu
                SET freq_max_proc = %s
                WHERE id = %s
                RETURNING id;
                """,
                (freq_max_proc, cpu_id)
            )
        return cpu_id

    cur.execute(
        """
        INSERT INTO t_cpu (cpu_model, freq_max_proc, cpu_architecture)
        VALUES (%s, %s, %s)
        RETURNING id;
        """,
        (cpu_model, freq_max_proc, cpu_architecture)
    )
    row = cur.fetchone()
    return row[0] if row else None


def insert_cpu(cur, cpu_model, freq_max_proc, cpu_architecture):
    cur.execute(
        """
        INSERT INTO t_cpu (cpu_model, freq_max_proc, cpu_architecture)
        VALUES (%s, %s, %s)
        RETURNING id;
        """,
        (cpu_model, freq_max_proc, cpu_architecture)
    )
    row = cur.fetchone()
    return row[0] if row else None


def insert_or_update_cpu(cur, cpu_model, freq_max_proc, cpu_architecture):
    cur.execute(
        """
        INSERT INTO t_cpu (cpu_model, freq_max_proc, cpu_architecture)
        VALUES (%s, %s, %s)
        ON CONFLICT (cpu_model, cpu_architecture)
        DO UPDATE SET
            freq_max_proc = EXCLUDED.freq_max_proc
        RETURNING id;
        """,
        (cpu_model, freq_max_proc, cpu_architecture)
    )
    row = cur.fetchone()
    return row[0] if row else None


def update_cpu(cur, id_cpu, cpu_model=None, freq_max_proc=None, cpu_architecture=None):
    if cpu_model is None and freq_max_proc is None and cpu_architecture is None:
        return None

    query_parts = ["UPDATE t_cpu SET"]
    values = []

    if cpu_model is not None:
        query_parts.append("cpu_model = %s")
        values.append(cpu_model)
    if freq_max_proc is not None:
        query_parts.append("freq_max_proc = %s")
        values.append(freq_max_proc)
    if cpu_architecture is not None:
        query_parts.append("cpu_architecture = %s")
        values.append(cpu_architecture)

    query_parts.append("WHERE id = %s RETURNING id;")
    values.append(id_cpu)

    cur.execute(" ".join(query_parts), tuple(values))
    row = cur.fetchone()
    return row[0] if row else None


def delete_cpu_by_id(cur, id_cpu):
    cur.execute(
        """
        DELETE FROM t_cpu
        WHERE id = %s;
        """,
        (id_cpu,)
    )


def delete_cpu_by_model(cur, cpu_model):
    cur.execute(
        """
        DELETE FROM t_cpu
        WHERE cpu_model = %s;
        """,
        (cpu_model,)
    )


def delete_cpu_by_architecture(cur, cpu_architecture):
    cur.execute(
        """
        DELETE FROM t_cpu
        WHERE cpu_architecture = %s;
        """,
        (cpu_architecture,)
    )


def delete_all_cpu(cur):
    cur.execute("TRUNCATE TABLE t_cpu RESTART IDENTITY;")


__all__ = [
    "get_liste_cpu",
    "get_cpu_by_id",
    "get_cpu_by_model",
    "get_cpu_by_architecture",
    "get_cpu_by_model_and_architecture",
    "get_or_create_cpu",
    "insert_cpu",
    "insert_or_update_cpu",
    "update_cpu",
    "delete_cpu_by_id",
    "delete_cpu_by_model",
    "delete_cpu_by_architecture",
    "delete_all_cpu",
]
