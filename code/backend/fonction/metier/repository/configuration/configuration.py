def get_liste_configuration(cur):
    cur.execute(
        """
        SELECT * FROM t_configuration
        """
    )
    result = cur.fetchall()
    return result

def get_configuration_by_id(cur,id):
    cur.execute(
        """
        SELECT * FROM t_configuration WHERE id = %s
        """,(id,)
    )
    result = cur.fetchone()
    return result

def get_configuration_by_type(cur,type):
    cur.execute(
        """
        SELECT * FROM t_configuration WHERE type = %s
        """,(type,)
    )
    result = cur.fetchone()
    return result

def get_valeur_configuration(cur,type):
    cur.execute(
        """
        SELECT valeur FROM t_configuration WHERE type = %s
        """,(type,)
    )
    result = cur.fetchone()
    return result

def insert_configuration(cur, type, valeur, date):
    cur.execute(
        """
        INSERT INTO t_configuration (type, valeur, date)
        VALUES (%s, %s, %s)
        """,
        (type, valeur, date),
    )
    
def update_configuration(cur, type, valeur, date, id):
    cur.execute(
        """
        UPDATE t_configuration
        SET type = %s, valeur = %s, date = %s
        WHERE id = %s
        """,
        (type, valeur, date, id)
    )