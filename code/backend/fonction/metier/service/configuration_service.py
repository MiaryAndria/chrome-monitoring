import json
from backend.fonction.conn.connexion import get_connection, close_connection
from backend.fonction.metier.repository.configuration import get_liste_configuration,get_configuration_by_id,insert_configuration,update_configuration


def getListeConfiguration():
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        rows = get_liste_configuration(cur)
        cur.close()

        result = []
        for r in rows:
            result.append({
                "id": r[0],
                "type": r[1] if r[1] is not None else None,
                "valeur": r[2],
                "date":r[3],
            })
        return result
    finally:
        close_connection(connexion)
        
def getDetailConfiguration(id):
    connexion = get_connection()
    if connexion is None :
        return []
    try:
        cur = connexion.cursor()
        rows = get_configuration_by_id(cur,id)
        return rows 
    finally:
        close_connection(connexion)
        
def UpdateConfiguration(type,valeur,date,id):
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur=connexion.cursor()
        update_configuration(cur,type,valeur,date,id)
        connexion.commit()
        return True
    except Exception:
        connexion.rollback()
        raise
    finally:
        close_connection(connexion)
        
def InsertConfiguration(type_, valeur, date):
    connexion = get_connection()
    if connexion is None:
        return None
    try:
        cur = connexion.cursor()
        insert_configuration(cur, type_, valeur, date)
        connexion.commit()
        return True
    except Exception:
        connexion.rollback()
        raise
    finally:
        close_connection(connexion)
    