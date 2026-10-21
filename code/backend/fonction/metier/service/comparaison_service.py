import json
from backend.fonction.conn.connexion import get_connection, close_connection
from backend.fonction.metier.repository.devices import get_device_by_id
from backend.fonction.metier.repository.cpu.device_cpu import get_cpu_device_one_date
from backend.fonction.metier.repository.ram.ram import get_ram_device_one_date
from backend.fonction.metier.repository.comparaison.comparaison import (
    get_liste_comparaison,
    insert_comparaison_simple,
    insert_comparaison_double,
    insert_comparaison_statut,
)


def getListeComparaison():
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        rows = get_liste_comparaison(cur)
        return [
            {
                "id": r[0],
                "id_device_a": r[1],
                "id_device_b": r[2],
                "date_reference_a": r[3],
                "date_reference_b": r[4],
                "date_comparaison": r[5],
                "resultat": r[6],
            }
            for r in rows
        ]
    finally:
        close_connection(connexion)


def insertComparaisonSimple(id1, id2, date1, date2, resultat):
    connexion = get_connection()
    if connexion is None:
        return None
    try:
        cur = connexion.cursor()
        row = insert_comparaison_simple(cur, id1, id2, date1, date2, resultat, 1)
        connexion.commit()
        return row[0]
    except Exception:
        connexion.rollback()
        raise
    finally:
        close_connection(connexion)


def getDeviceDetail(cur, id_device, date):
    device = get_device_by_id(cur, id_device)
    if device is None:
        return None
    return {
        "id_device": device[0],
        "cpu": get_cpu_device_one_date(cur, device[0], date),
        "ram": get_ram_device_one_date(cur, device[0], date),
    }


def comparaisonDouble(id1, id2, date1, date2):
    connexion = get_connection()
    if connexion is None:
        return None
    try:
        cur = connexion.cursor()

        row = insert_comparaison_double(cur, id1, id2, date1, date2, None, 2)
        id_comparaison = row[0]
        insert_comparaison_statut(cur, id_comparaison, 5)
        connexion.commit()

        insert_comparaison_statut(cur, id_comparaison, 6)
        connexion.commit()

        detail1 = getDeviceDetail(cur, id1, date1)
        detail2 = getDeviceDetail(cur, id2, date2)
        if detail1 is None or detail2 is None:
            raise ValueError("Appareil introuvable")

        resultat = json.dumps(compare(detail1, detail2), default=str)  # compare() à écrire/importer

        cur.execute(
            "UPDATE t_comparaison SET resultat = %s WHERE id_comparaison = %s",
            (resultat, id_comparaison),
        )
        
        insert_comparaison_statut(cur, id_comparaison, 7)
        connexion.commit()
        return id_comparaison
    except Exception:
        connexion.rollback()
        raise
    finally:
        close_connection(connexion)