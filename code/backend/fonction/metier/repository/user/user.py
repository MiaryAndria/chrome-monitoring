from backend.fonction.conn.connexion import get_connection, close_connection
from backend.utils.password_hashage import hasher_password
# connexion = get_connection()
# cur = connexion.cursor()
def get_liste_user(cur):
    cur.execute(
        """
        SELECT *
        FROM t_user
        """
    )
    result = cur.fetchall()
    return result 
  
def get_liste_user_by_id(cur,id):
    cur.execute(
        """
        SELECT * FROM t_user where id = %s
        """,(id,)
    )
    result = cur.fetchone()
    return result 

def get_user_by_email(cur,email):
    cur.execute(
        """
        SELECT * FROM t_user where email = %s
        """,(email,)
    )
    result = cur.fetchone()
    return result 

def get_user_by_login(cur,email,mdp):
    cur.execute(
    """
    SELECT * FROM t_user where email = %s AND mdp = %s
    """ ,(email,mdp,)
    )
    result = cur.fetchone()
    return result 

def get_liste_user_by_name(cur,name):
    cur.execute(
        """
        SELECT * FROM t_user where nom =%s
        """ ,(name,),  
        )
    result = cur.fetchone()
    return result 

def get_user_by_nom_and_email(cur,nom,email):
    cur.execute(
        """
        SELECT * FROM t_user WHERE nom = %s AND email = %s
        """,(nom,email,)
    )
    result = cur.fetchone()
    return result

def insert_user(cur,nom,email,mdp):
    mot_de_passe = hasher_password(mdp)
    cur.execute(
    """
    INSERT INTO t_user (nom,email,mdp,vrai_mdp ) VALUES(%s,%s,%s,%s)
    """,(nom,email,mot_de_passe,mdp)
    )
    # connexion.commit()

def delete_all_user(cur):
    cur.execute(
    """
    TRUNCATE TABLE t_user RESTART IDENTITY CASCADE; 
    """,
    )

def delete_user(cur,id):
    cur.execute(
    """
    DELETE FROM TABLE t_user where id = %s
    """,(id,)
    )
# insert_user(cur, 'administrateur', 'gtadmin@gmail.com', 'Gtadmin')