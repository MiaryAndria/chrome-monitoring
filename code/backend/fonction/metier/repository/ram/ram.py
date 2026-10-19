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
    """
    Retourne la plus grande valeur de ram_total relevée pour un device.
    Les bornes de date sont optionnelles (TIMESTAMPTZ).
    """
    query = """
        SELECT MAX(ram_total)
        FROM t_device_ram
        WHERE id_device = %s
    """
    params = [id_device]

    if datetime_from is not None:
        query += " AND date >= %s"
        params.append(datetime_from)
    if datetime_to is not None:
        query += " AND date <= %s"
        params.append(datetime_to)

    cur.execute(query, tuple(params))
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


__all__ = [
    "insert_into_device_ram",
    "get_max_total_ram",
    "get_latest_by_device",
    "get_ram_device_date",
]
