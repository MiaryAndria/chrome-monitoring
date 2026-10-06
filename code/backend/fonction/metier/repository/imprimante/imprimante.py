def get_liste_imprimante(cur):
    cur.execute(
        """
        SELECT * FROM t_imprimante
        """
    )
    result = cur.fetchall()
    return result

def get_imprimante_by_id(cur,id):
    cur.execute(
        """
        SELECT * FROM t_imprimante WHERE id = %s
        """,(id,)
    )
    result = cur.fetchone()
    return result

def get_imprimante_by_vid(cur,vid):
    cur.execute(
        """
        SELECT * FROM t_imprimante WHERE vid = %s
        """,(vid,)
    )
    result = cur.fetchone()
    return result

def get_imprimante_by_pid(cur,pid):
    cur.execute(
        """
        SELECT * FROM t_imprimante WHERE pid = %s
        """,(pid,)
    )
    result = cur.fetchone()
    return result

def get_imprimante_by_vendor(cur,vendor):
    cur.execute(
        """
        SELECT * FROM t_imprimante WHERE vendor = %s
        """,(vendor,)
    )
    result = cur.fetchone()
    return result

def get_imprimante_by_nom(cur,nom):
    cur.execute(
        """
        SELECT * FROM t_imprimante WHERE nom = %s
        """,(nom,)
    )
    result = cur.fetchone()
    return result

def search_imprimante(cur,recherche):
    cur.execute(
        """
        SELECT * FROM t_imprimante
        WHERE CAST(vid AS TEXT) ILIKE %s
           OR CAST(pid AS TEXT) ILIKE %s
           OR vendor ILIKE %s
           OR nom ILIKE %s
        """,(recherche,recherche,recherche,recherche,)
    )
    result = cur.fetchall()
    return result

def get_nombre_imprimante(cur):
    cur.execute(
        """
        SELECT COUNT(*) FROM t_imprimante
        """
    )
    result = cur.fetchone()
    return result

def get_imprimante_by_vid_and_pid(cur,vid,pid):
    cur.execute(
        """
        SELECT * FROM t_imprimante WHERE vid = %s AND pid = %s
        """,(vid,pid,)
    )
    result = cur.fetchall()
    return result

def get_imprimante_by_vendor_and_nom(cur,vendor,nom):
    cur.execute(
        """
        SELECT * FROM t_imprimante WHERE vendor = %s AND nom = %s
        """,(vendor,nom,)
    )
    result = cur.fetchone()
    return result

def insert_imprimante(cur, vid, pid, vendor, nom):
    cur.execute(
        """
        INSERT INTO t_imprimante (vid, pid, vendor, nom)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
        """,
        (vid, pid, vendor, nom)
    )

# def getImprimantesDevice(cur,id_device):
#     cur.execute("""
#         SELECT i.id, i.vid, i.pid, i.vendor, i.nom, MAX(idv.date)
#         FROM imprimante_device idv
#         JOIN imprimante i ON i.id = idv.id_imprimante
#         WHERE idv.id_device = %s
#         GROUP BY i.id, i.vid, i.pid, i.vendor, i.nom
#         ORDER BY i.nom
#     """, (id_device,))
#     return [
#         {"id": r[0], "vid": r[1], "pid": r[2],
#          "vendor": r[3], "nom": r[4], "derniere_detection": r[5]}
#         for r in cur.fetchall()
#     ]
    
def get_or_create_imprimante(cur,vid,pid,vendor,nom):
    imprimante = get_imprimante_by_vid_and_pid(cur,vid,pid)
    if not imprimante :
        insert_imprimante(cur,vid,pid,vendor,nom)
        imprimante = get_imprimante_by_vid_and_pid(cur,vid,pid)
        
    return imprimante 
