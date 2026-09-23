from backend.fonction.conn.connexion import get_connection



def get_liste_utilisateur(cur):

    cur.execute("""
        SELECT * FROM t_utilisateur
    """)

    result = cur.fetchall()
    return result


def get_utilisateur_by_id(cur, id):

    cur.execute("""
        SELECT * FROM t_utilisateur
        WHERE id = %s
    """, (id,))

    result = cur.fetchone()
    return result


def get_utilisateur_by_email(cur, email):

    cur.execute("""
        SELECT * FROM t_utilisateur
        WHERE email = %s
    """, (email,))

    result = cur.fetchone()
    return result


def create_utilisateur(cur, email):

    cur.execute("""
        INSERT INTO t_utilisateur (email)
        VALUES (%s)
    """, (email,))


def get_or_create_utilisateur(cur, email):

    utilisateur = get_utilisateur_by_email(cur, email)

    if utilisateur:
        return utilisateur

    create_utilisateur(cur, email)

    return get_utilisateur_by_email(cur, email)