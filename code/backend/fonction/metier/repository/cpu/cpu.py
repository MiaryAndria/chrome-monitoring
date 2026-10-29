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


def get_or_create_cpu(cur, cpu_model, freq_max_proc, cpu_architecture):
    cpu_model = cpu_model.strip() if isinstance(cpu_model, str) else cpu_model
    cpu_architecture = cpu_architecture.strip() if isinstance(cpu_architecture, str) else cpu_architecture
    cpu_by_model_architecture = get_cpu_by_model_and_architecture(cur, cpu_model, cpu_architecture)

    if cpu_by_model_architecture:
        first_row = cpu_by_model_architecture[0]
        return first_row[0] if isinstance(first_row, (list, tuple)) else first_row

    return insert_cpu(cur, cpu_model, freq_max_proc, cpu_architecture)

