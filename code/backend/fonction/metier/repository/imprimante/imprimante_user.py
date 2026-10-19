def insert_imprimante_user(cur,id_imprimante,id_user,date):
    cur.execute(
    """
    INSERT INTO t_imprimante_user (id_imprimante,id_utilisateur,date)
    VALUES (%s, %s, %s)ON CONFLICT (id_imprimante, id_utilisateur, date) DO NOTHING
        RETURNING id
    """,(id_imprimante,id_user,date)
    )
    
def get_utilisateurs_by_imprimante(cur, id_imprimante):
    """
    Retourne la liste des utilisateurs ayant utilisé une imprimante.
    Chaque utilisateur est retourné avec sa dernière date d'utilisation.
    """
    cur.execute("""
        SELECT DISTINCT ON (u.id)
            u.id                AS id_utilisateur,
            u.email,
            iu.date             AS derniere_utilisation
        FROM t_imprimante_user iu
        JOIN t_utilisateur u ON u.id = iu.id_utilisateur
        WHERE iu.id_imprimante = %s
        ORDER BY u.id, iu.date DESC
    """, (id_imprimante,))

    rows = cur.fetchall()
    return [
        {
            "id_utilisateur": r[0],
            "email": r[1],
            "derniere_utilisation": r[2],
        }
        for r in rows
    ]