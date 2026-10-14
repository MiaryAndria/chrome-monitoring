def insert_cpu_device(cur, id_device, id_cpu, cpu_utiliser, cpu_total, cpu_libre, date):
    """
    Insère un relevé CPU dans t_device_cpu.
    - cpu_utiliser : pourcentage utilisé tel qu'obtenu dans le JSON (NUMERIC(5,2), ex. 18.50)
    - cpu_total    : total de référence du CPU (BIGINT, ex. 100)
    - cpu_libre    : total - utilisation arrondi (BIGINT, ex. 82)
    - date         : reportTime du rapport JSON (TIMESTAMPTZ)
    """
    cur.execute(
        """
        INSERT INTO t_device_cpu (id_device, id_cpu, cpu_utiliser, cpu_libre, cpu_total, date)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (id_device, date)
        DO UPDATE SET
            id_cpu = EXCLUDED.id_cpu,
            cpu_utiliser = EXCLUDED.cpu_utiliser,
            cpu_libre = EXCLUDED.cpu_libre,
            cpu_total = EXCLUDED.cpu_total
        """,
        (id_device, id_cpu, cpu_utiliser, cpu_libre, cpu_total, date)
    )


def update_date_cpu_device(cur, id, date):
    cur.execute(
        """
        UPDATE t_device_cpu SET date = %s WHERE id = %s
        """,
        (date, id)
    )


__all__ = ["insert_cpu_device", "update_date_cpu_device"]
