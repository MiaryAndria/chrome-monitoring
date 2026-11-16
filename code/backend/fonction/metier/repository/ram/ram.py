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


def get_max_total_ram(cur, id_device, datetime_from=None, datetime_to=None):
    cur.execute(
        """
        SELECT MAX(ram_total)
        FROM t_device_ram
        WHERE id_device = %s
          AND (%s IS NULL OR date >= %s)
          AND (%s IS NULL OR date <= %s)
        """,
        (id_device, datetime_from, datetime_from, datetime_to, datetime_to)
    )
    row = cur.fetchone()
    return row[0] if row else None


def get_latest_by_device(cur, id_device):
    cur.execute(
        """
        SELECT id, id_device, ram_total, ram_utiliser, ram_libre, date
        FROM t_device_ram
        WHERE id_device = %s
        ORDER BY date DESC, id DESC
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
        "ram_total": row[2],
        "ram_utiliser": row[3],
        "ram_libre": row[4],
        "date": row[5],
    }


def get_ram_device_date(cur, id_device, date_debut, date_fin):
    """
    Relevés RAM bruts (date, octets utilisés) d'un device sur une période date+heure.
    """
    cur.execute(
        """
        SELECT date, ram_utiliser
        FROM t_device_ram
        WHERE id_device = %s
          AND date >= %s
          AND date <= %s
        ORDER BY date ASC, id ASC
        """,
        (id_device, date_debut, date_fin)
    )
    rows = cur.fetchall()
    return [
        {"date": row[0], "valeur": int(row[1]) if row[1] is not None else 0}
        for row in rows
    ]


