def find_devices_without_network(cur):
    """
    Retourne (id_device, id_reseau, ip_adress) pour les devices qui
    n'ont aucune ligne dans t_device_reseau.

    t_device ne possède pas de colonne id_reseau dans le schéma actuel :
    la valeur retournée est donc NULL et la résolution se fait par
    t_device.ip_adress (attention : un seul "d").
    """
    cur.execute(
        """
        SELECT d.id, NULL::int AS id_reseau, d.ip_adress
        FROM t_device d
        WHERE NOT EXISTS (
            SELECT 1
            FROM t_device_reseau dr
            WHERE dr.id_device = d.id
        )
        ORDER BY d.id ASC
        """
    )
    return cur.fetchall()


def get_reseau_id_by_ip(cur, ip):
    cur.execute(
        """
        SELECT id
        FROM t_reseau
        WHERE valeur = %s
        ORDER BY id ASC
        LIMIT 1
        """,
        (ip,)
    )
    row = cur.fetchone()
    return row[0] if row else None


def get_by_device_and_reseau(cur, device_id, reseau_id):
    cur.execute(
        """
        SELECT id, id_device, id_reseau, date
        FROM t_device_reseau
        WHERE id_device = %s AND id_reseau = %s
        LIMIT 1
        """,
        (device_id, reseau_id)
    )
    return cur.fetchone()


def insert_device_reseau(cur, device_id, reseau_id):
    cur.execute(
        """
        INSERT INTO t_device_reseau (id_device, id_reseau)
        VALUES (%s, %s)
        RETURNING id;
        """,
        (device_id, reseau_id)
    )
    row = cur.fetchone()
    return row[0] if row else None


def create_savepoint_ligne_reseau(cur):
    cur.execute("SAVEPOINT sync_reseau_ligne;")


def rollback_savepoint_ligne_reseau(cur):
    cur.execute("ROLLBACK TO SAVEPOINT sync_reseau_ligne;")


__all__ = [
    "find_devices_without_network",
    "get_reseau_id_by_ip",
    "get_by_device_and_reseau",
    "insert_device_reseau",
    "create_savepoint_ligne_reseau",
    "rollback_savepoint_ligne_reseau",
]
