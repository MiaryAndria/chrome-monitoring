


def get_filiale_by_utilisateur_and_filiale(cur,id_utilisateur,id_filiale):
    cur.execute(
    """
    SELECT * FROM t_filiale_utilisateur WHERE id_utilisateur =%s AND id_filiale=%s
    """,(id_utilisateur,id_filiale,)
    )
    result = cur.fetchone()
    return result 

def insert_filiale_utilisateur(cur,id_filiale,id_utilisateur):
    cur.execute(
        """
        INSERT INTO t_filiale_utilisateur(id_filiale,id_utilisateur)VALUES(%s,%s)
        """,(id_filiale,id_utilisateur)
    )

def get_or_create_filiale_utilisateur(cur,id_filiale,id_utilisateur):
    filiale_utilisateur = get_filiale_by_utilisateur_and_filiale(cur,id_utilisateur,id_filiale)
    if filiale_utilisateur:
        return filiale_utilisateur[0]
    else:
        insert_filiale_utilisateur(cur,id_filiale,id_utilisateur)
        return get_filiale_by_utilisateur_and_filiale(cur, id_utilisateur, id_filiale)[0] if get_filiale_by_utilisateur_and_filiale(cur, id_utilisateur, id_filiale) else None