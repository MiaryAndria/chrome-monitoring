import json
from backend.fonction.conn.connexion import get_connection, close_connection
from backend.fonction.metier.repository.configuration import (
    get_liste_configuration,
    get_liste_archiver,
    get_by_id_liste_archiver,
    get_configuration_by_id,
    insert_configuration,
    insert_configuration_statut,
    update_configuration,
    delete_configuration,
    restore_configuration,
)


def getListeConfiguration():
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        rows = get_liste_configuration(cur)
        result = []
        for r in rows:
            result.append({
                "id": r[0],
                "type": r[1] if r[1] is not None else None,
                "valeur": r[2],
                "date": r[3],
            })
        return result
    finally:
        close_connection(connexion)


def getDetailConfiguration(id_configuration):
    connexion = get_connection()
    if connexion is None:
        return None
    try:
        cur = connexion.cursor()
        row = get_configuration_by_id(cur, id_configuration)
        if row is None:
            return None 
        return{
            "id": row[0],
            "type": row[1] if row[1] is not None else None,
            "valeur": row[2],
            "date": row[3],   
        }
    finally:
        close_connection(connexion)

def UpdateConfiguration(id_configuration, type_, valeur, date=None, status_id=13):
    connexion = get_connection()
    if connexion is None:
        return False
    try:
        cur = connexion.cursor()
        updated_id = update_configuration(cur, id_configuration, type_, valeur, date)
        if updated_id is not None:
            insert_configuration_statut(cur, updated_id, status_id)
        connexion.commit()
        return True
    except Exception:
        connexion.rollback()
        raise
    finally:
        close_connection(connexion)


def InsertConfiguration(type_, valeur, date=None, status_id=12):
    connexion = get_connection()
    if connexion is None:
        return None
    try:
        cur = connexion.cursor()
        id_configuration = insert_configuration(cur, type_, valeur, date)
        if id_configuration is not None:
            insert_configuration_statut(cur, id_configuration, status_id)
        connexion.commit()
        return id_configuration
    except Exception:
        connexion.rollback()
        raise
    finally:
        close_connection(connexion)


def deleteConfiguration(id_configuration, status_id=14,date=None):
    connexion = get_connection()
    if connexion is None:
        return False
    try:
        cur = connexion.cursor()
        delete_configuration(cur, id_configuration, status_id,date)
        connexion.commit()
        return True
    except Exception:
        connexion.rollback()
        raise
    finally:
        close_connection(connexion)


def getListeArchiveConfiguration():
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        rows = get_liste_archiver(cur)
        result = []
        for r in rows:
            result.append({
                "id": r[0],
                "type": r[1] if r[1] is not None else None,
                "valeur": r[2],
                "date": r[3],
            })
        return result
    finally:
        close_connection(connexion)


def reStaurer(id_configuration, status_id=16):
    connexion = get_connection()
    if connexion is None:
        return False
    try:
        cur = connexion.cursor()
        parametre = get_by_id_liste_archiver(cur, id_configuration)
        if parametre is None:
            return False

        restore_configuration(cur, id_configuration, status_id)
        connexion.commit()
        return id_configuration
    except Exception:
        connexion.rollback()
        raise
    finally:
        close_connection(connexion)



        