def insert_into_device_ram(cur, id_device, ram_total, ram_utiliser, ram_libre, date):
    """
    Insère un relevé RAM dans t_device_ram.
    - ram_total    : totalRamBytes du rapport JSON (BIGINT, octets)
    - ram_utiliser : ram_total - systemRamFreeBytes (BIGINT, octets)
    - ram_libre    : systemRamFreeBytes du rapport JSON (BIGINT, octets)
    - date         : reportTime du rapport JSON (TIMESTAMPTZ)
    """
    cur.execute(
        """
        INSERT INTO t_device_ram (id_device, ram_total, ram_utiliser, ram_libre, date)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (id_device, date)
        DO UPDATE SET
            ram_total = EXCLUDED.ram_total,
            ram_utiliser = EXCLUDED.ram_utiliser,
            ram_libre = EXCLUDED.ram_libre
        """,
        (id_device, ram_total, ram_utiliser, ram_libre, date)
    )


__all__ = ["insert_into_device_ram"]
