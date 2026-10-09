def insert_synchronisation_historique(cur, source, lancement, fenetre_debut, fenetre_fin):
    cur.execute("""
        INSERT INTO t_synchronisation_historique
            (source, date_debut, fenetre_debut, fenetre_fin)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (source, lancement, fenetre_debut, fenetre_fin))
    return cur.fetchone()[0]


# def get_derniere_fenetre_fin_by_source(cur, source):
#     cur.execute("""
#         SELECT MAX(h.date_debut)
#         FROM t_synchronisation_historique h
#         WHERE h.source = %s
#           AND EXISTS (
#               SELECT 1 FROM t_statut_synchronisation ss
#               JOIN t_statut s ON s.id = ss.id_statut
#               WHERE ss.id_synchronisation = h.id AND s.nom = 'TERMINER'
#           )
#     """, (source,))
#     return cur.fetchone()[0]

def get_derniere_fenetre_fin_by_source(cur, source):
    cur.execute("""
        SELECT MAX(h.fenetre_fin)
        FROM t_synchronisation_historique h
        WHERE h.source = %s
          AND EXISTS (
              SELECT 1 FROM t_statut_synchronisation ss
              JOIN t_statut s ON s.id = ss.id_statut
              WHERE ss.id_synchronisation = h.id AND s.nom = 'TERMINER'
          )
    """, (source,))
    return cur.fetchone()[0]

def update_synchronisation_resultat(cur, id_sync, fin, nb_lignes, message):
    cur.execute("""
        UPDATE t_synchronisation_historique
        SET date_fin = %s, nb_lignes = %s, message = %s
        WHERE id = %s
    """, (fin, nb_lignes, message, id_sync))