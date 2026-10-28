def get_alerte_by_type(cur, type_):
    cur.execute(
        "SELECT id, type FROM t_alerte WHERE type = %s",
        (type_,),
    )
    return cur.fetchone()


def insert_alerte(cur, type_):
    """Création idempotente d'un type d'alerte (get_or_create via UNIQUE(type)).
    Retourne l'id existant si le type est déjà présent."""
    cur.execute(
        """
        INSERT INTO t_alerte (type)
        VALUES (%s)
        ON CONFLICT (type) DO UPDATE SET type = EXCLUDED.type
        RETURNING id
        """,
        (type_,),
    )
    row = cur.fetchone()
    return row[0] if row else None


def get_temperature_max_device(cur, id_device):
    """Température capteur maximale du dernier rapport CPU_STATUS d'un device (°C)."""
    cur.execute(
        """
        SELECT MAX((capteur->>'temperatureCelsius')::int)
        FROM t_rapport_device r,
             jsonb_array_elements(r.donnees->'cpuTemperatureInfo') AS capteur
        WHERE r.id_device = %s
          AND r.id_type_rapport = 1
          AND r.report_time = (
              SELECT MAX(report_time)
              FROM t_rapport_device
              WHERE id_device = %s AND id_type_rapport = 1
          )
        """,
        (id_device, id_device),
    )
    row = cur.fetchone()
    return row[0] if row else None

def get_type_alerte(cur):
    cur.execute(
    """
    SELECT * FROM t_alerte
    """
    )
    return cur.fetchall()
