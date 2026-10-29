from backend.fonction.conn.connexion import get_connection

connexion = get_connection()
cur=connexion.cursor()

def get_devices_by_filiale(cur,id_filiale):
    cur.execute(
        """
        SELECT * FROM t_device_filiale WHERE id_filiale = %s
        ORDER BY date_affectation DESC
        """,(id_filiale,)
    )
    result = cur.fetchall()
    return result

