from backend.fonction.conn.connexion import get_connection

connexion = get_connection()
cur=connexion.cursor()

def get_liste_device_historique(cur):
    cur.execute(
        """
        SELECT * FROM t_device_historique
        """
    )
    result = cur.fetchall()
    return result

def get_device_historique_by_id(cur,id):
    cur.execute(
        """
        SELECT * FROM t_device_historique WHERE id = %s
        """,(id,)
    )
    result = cur.fetchone()
    return result

def get_historique_by_device(cur,id_device):
    cur.execute(
        """
        SELECT * FROM t_device_historique WHERE id_device = %s
        ORDER BY date_mise_a_jour DESC
        """,(id_device,)
    )
    result = cur.fetchall()
    return result

def get_historique_by_utilisateur(cur,id_utilisateur):
    cur.execute(
        """
        SELECT * FROM t_device_historique WHERE id_utilisateur = %s
        ORDER BY date_mise_a_jour DESC
        """,(id_utilisateur,)
    )
    result = cur.fetchall()
    return result

def get_historique_by_statut(cur,id_statut):
    cur.execute(
        """
        SELECT * FROM t_device_historique WHERE id_statut = %s
        ORDER BY date_mise_a_jour DESC
        """,(id_statut,)
    )
    result = cur.fetchall()
    return result

def get_historique_device_by_period(cur,id_device,date_debut,date_fin):
    cur.execute(
        """
        SELECT * FROM t_device_historique
        WHERE id_device = %s AND date_mise_a_jour BETWEEN %s AND %s
        ORDER BY date_mise_a_jour DESC
        """,(id_device,date_debut,date_fin,)
    )
    result = cur.fetchall()
    return result

def get_dernier_historique_device(cur,id_device):
    cur.execute(
        """
        SELECT * FROM t_device_historique
        WHERE id_device = %s
        ORDER BY date_mise_a_jour DESC
        LIMIT 1
        """,(id_device,)
    )
    result = cur.fetchone()
    return result

def get_historique_by_device_and_statut(cur,id_device,id_statut):
    cur.execute(
        """
        SELECT * FROM t_device_historique
        WHERE id_device = %s AND id_statut = %s
        ORDER BY date_mise_a_jour DESC
        """,(id_device,id_statut,)
    )
    result = cur.fetchall()
    return result

def get_historique_by_device_and_utilisateur(cur,id_device,id_utilisateur):
    cur.execute(
        """
        SELECT * FROM t_device_historique
        WHERE id_device = %s AND id_utilisateur = %s
        ORDER BY date_mise_a_jour DESC
        """,(id_device,id_utilisateur,)
    )
    result = cur.fetchall()
    return result

def get_historique_by_utilisateur_and_statut(cur,id_utilisateur,id_statut):
    cur.execute(
        """
        SELECT * FROM t_device_historique
        WHERE id_utilisateur = %s AND id_statut = %s
        ORDER BY date_mise_a_jour DESC
        """,(id_utilisateur,id_statut,)
    )
    result = cur.fetchall()
    return result

def get_historique_by_device_statut_and_period(cur,id_device,id_statut,date_debut,date_fin):
    cur.execute(
        """
        SELECT * FROM t_device_historique
        WHERE id_device = %s AND id_statut = %s AND date_mise_a_jour BETWEEN %s AND %s
        ORDER BY date_mise_a_jour DESC
        """,(id_device,id_statut,date_debut,date_fin,)
    )
    result = cur.fetchall()
    return result
