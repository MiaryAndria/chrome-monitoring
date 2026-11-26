import json

from backend.fonction.metier.repository.statut import ID_STATUT_TERMINER


def insert_synchronisation_historique(cur, source, lancement, fenetre_debut, fenetre_fin):
    cur.execute("""
        INSERT INTO t_synchronisation_historique
            (source, date_debut, fenetre_debut, fenetre_fin)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (source, lancement, fenetre_debut, fenetre_fin))
    return cur.fetchone()[0]


def get_date_derniere_synchronisation(cur):
    cur.execute(
        f"""
        SELECT MAX(h.date_debut)
        FROM t_synchronisation_historique h
        WHERE EXISTS (
            SELECT 1 FROM t_statut_synchronisation ss
            WHERE ss.id_synchronisation = h.id AND ss.id_statut = {ID_STATUT_TERMINER}
        )
        """
    )
    row = cur.fetchone()
    return row[0] if row else None


def get_derniere_fenetre_fin_by_source(cur, source):
    cur.execute(f"""
        SELECT MAX(h.fenetre_fin)
        FROM t_synchronisation_historique h
        WHERE h.source = %s
          AND EXISTS (
              SELECT 1 FROM t_statut_synchronisation ss
              WHERE ss.id_synchronisation = h.id AND ss.id_statut = {ID_STATUT_TERMINER}
          )
    """, (source,))
    return cur.fetchone()[0]

def update_synchronisation_resultat(cur, id_sync, fin, nb_lignes, message):
    cur.execute("""
        UPDATE t_synchronisation_historique
        SET date_fin = %s, nb_lignes = %s, message = %s
        WHERE id = %s
    """, (fin, nb_lignes, message, id_sync))

def update_synchronisation_journal(cur, id_sync, journal):
    cur.execute("""
        UPDATE t_synchronisation_historique
        SET journal = %s
        WHERE id = %s
    """, (json.dumps(journal, ensure_ascii=False), id_sync))
    

def get_liste_synchronisation(cur, limit, offset, statut=None, date_debut=None, date_fin=None,fenetre_debut=None,fenetre_fin=None):
    cur.execute(
        """
        SELECT id, source, date_debut, date_fin, fenetre_debut, fenetre_fin,
               nb_lignes, message, statut, date_statut
        FROM v_synchronisation
        WHERE (%s IS NULL OR statut = %s)
          AND (%s IS NULL OR date_debut >= %s)
          AND (%s IS NULL OR date_debut < (%s + INTERVAL '1 day'))
          AND (%s IS NULL OR fenetre_debut >= %s)
          AND (%s IS NULL OR fenetre_fin < (%s + INTERVAL '1 day'))
        ORDER BY date_debut DESC, id DESC
        LIMIT %s OFFSET %s
        """,
        (statut, statut, date_debut, date_debut, date_fin, date_fin, fenetre_debut, fenetre_debut, fenetre_fin, fenetre_fin, limit, offset),
    )
    return cur.fetchall()


def count_synchronisation(cur, statut=None, date_debut=None, date_fin=None,fenetre_debut=None,fenetre_fin=None):
    cur.execute(
        """
        SELECT COUNT(*) FROM v_synchronisation
        WHERE (%s IS NULL OR statut = %s)
          AND (%s IS NULL OR date_debut >= %s)
          AND (%s IS NULL OR date_debut < (%s + INTERVAL '1 day'))
          AND (%s IS NULL OR fenetre_debut >= %s)
          AND (%s IS NULL OR fenetre_fin < (%s + INTERVAL '1 day'))
        """,
        (statut, statut, date_debut, date_debut, date_fin, date_fin, fenetre_debut, fenetre_debut, fenetre_fin, fenetre_fin),
    )
    row = cur.fetchone()
    return row[0] if row else 0


def get_synchronisation_by_id(cur, id_sync):
    cur.execute(
        "SELECT * FROM v_synchronisation WHERE id = %s",
        (id_sync,),
    )
    return cur.fetchone()


def delete_synchronisation_statut(cur, date_limite):
    cur.execute(
        """
        DELETE FROM t_statut_synchronisation
        WHERE id_synchronisation IN (
            SELECT id FROM t_synchronisation_historique WHERE date_debut < %s
        )
        """,
        (date_limite,),
    )


def delete_synchronisation_historique(cur, date_limite):
    cur.execute(
        "DELETE FROM t_synchronisation_historique WHERE date_debut < %s",
        (date_limite,),
    )


def get_synchronisation_en_cours(cur):
    cur.execute(
        """
        SELECT *
        FROM v_synchronisation
        WHERE statut IN ('EN_COURS', 'COMMENCER')
        ORDER BY id DESC
        LIMIT 1
        """
    )
    return cur.fetchone()


def get_statuts_synchronisation(cur):
    cur.execute(
        """
        SELECT DISTINCT statut
        FROM v_synchronisation
        WHERE statut IS NOT NULL
        ORDER BY statut
        """
    )
    return cur.fetchall()
