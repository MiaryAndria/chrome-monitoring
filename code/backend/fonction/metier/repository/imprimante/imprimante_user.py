def insert_imprimante_user(cur,id_imprimante,id_user,date):
    cur.execute(
    """
    INSERT INTO t_imprimante_user (id_imprimante,id_utilisateur,date)
    VALUES (%s, %s, %s)ON CONFLICT (id_imprimante, id_utilisateur, date) DO NOTHING
        RETURNING id
    """,(id_imprimante,id_user,date)
    )
