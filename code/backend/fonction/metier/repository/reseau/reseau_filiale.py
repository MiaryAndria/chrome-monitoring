def get_filiale_by_reseaux_and_filiale(cur,id_reseau,id_filiale):
    cur.execute(
        """
        SELECT * FROM t_reseau_filiale WHERE id_reseau =%s AND id_filiale=%s
        """,(id_reseau,id_filiale,)
    )
    result = cur.fetchone()
    return result 

def insert_into_reseau_filiale(cur,id_reseau,id_filiale):
    existing = get_filiale_by_reseaux_and_filiale(cur, id_reseau, id_filiale)
    if existing:
        return existing
    cur.execute(
    """
    INSERT INTO t_reseau_filiale(id_reseau,id_filiale) VALUES(%s , %s)
    ON CONFLICT (id_reseau, id_filiale) DO NOTHING
    RETURNING id, id_reseau, id_filiale;
    """,(id_reseau,id_filiale,)
    )
    result = cur.fetchone()
    return result