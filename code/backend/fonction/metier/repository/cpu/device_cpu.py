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


def get_latest_by_device(cur, id_device):
    """
    Retourne le dernier relevé CPU d'un device, enrichi du modèle CPU.
    """
    cur.execute(
        """
        SELECT dc.id, dc.id_device, c.cpu_model, c.freq_max_proc,
               c.cpu_architecture, dc.cpu_utiliser, dc.cpu_libre,
               dc.cpu_total, dc.date
        FROM t_device_cpu dc
        JOIN t_cpu c ON c.id = dc.id_cpu
        WHERE dc.id_device = %s
        ORDER BY dc.date DESC, dc.id DESC
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
        "cpu_model": row[2],
        "freq_max_proc": row[3],
        "cpu_architecture": row[4],
        "cpu_utiliser": row[5],
        "cpu_libre": row[6],
        "cpu_total": row[7],
        "date": row[8],
    }


def get_cpu_device_date(cur, id_device, date_debut, date_fin):
    """
    Relevés CPU bruts (date, utilisation) d'un device sur une période date+heure.
    """
    cur.execute(
        """
        SELECT date, cpu_utiliser
        FROM t_device_cpu
        WHERE id_device = %s
          AND date >= %s
          AND date <= %s
        ORDER BY date ASC, id ASC
        """,
        (id_device, date_debut, date_fin)
    )
    rows = cur.fetchall()
    return [
        {"date": row[0], "valeur": float(row[1]) if row[1] is not None else 0.0}
        for row in rows
    ]
    

def get_cpu_device_one_date(cur, id_device, date):
    """
    Relevés CPU bruts (date, utilisation) d'un device
    pour une date donnée.
    """
    cur.execute(
        """
        SELECT date, cpu_utiliser
        FROM t_device_cpu
        WHERE id_device = %s
          AND date = %s
        ORDER BY date ASC, id ASC
        """,
        (id_device, date)
    )

    rows = cur.fetchall()

    return [
        {
            "date": row[0],
            "valeur": float(row[1]) if row[1] is not None else 0.0
        }
        for row in rows
    ]



__all__ = [
    "insert_cpu_device",
    "update_date_cpu_device",
    "get_latest_by_device",
    "get_cpu_device_date",
]
