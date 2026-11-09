import json
from datetime import datetime, timezone

from backend.fonction.conn.connexion import get_connection, close_connection
from backend.fonction.metier.repository.devices import (
    get_device_by_id,
    _get_device_cpu_info,
    get_liste_version_by_device,
    get_version_intervalle,
)
from backend.fonction.metier.repository.cpu import get_cpu_device_date
from backend.fonction.metier.repository.ram import get_ram_device_date
from backend.fonction.metier.repository.comparaison.comparaison import (
    get_liste_comparaison,
    find_comparaisons_paginated,
    get_comparaison_by_id,
    insert_comparaison,
    update_comparaison_resultat,
    insert_comparaison_statut,
)
from backend.utils.pagination import build_page
from backend.core.cache import cache_get, cache_set, cache_invalidate_prefix
from backend.utils.datetime_tools import local_to_utc
from backend.utils.config_db import get_int_configuration
from backend.utils.comparaison_stats import (
    normaliser_ram_pct,
    resume_serie,
    score_puissance_cpu,
    score_puissance_ram,
    vainqueur,
)
from backend.fonction.metier.repository.statut.constants import (
    ID_STATUT_COMMENCER,
    ID_STATUT_EN_COURS,
    ID_STATUT_TERMINER,
    ID_STATUT_ECHEC,
)

# t_type_comparaison : 1 = Simple, 2 = Double
TYPE_SIMPLE = 1
TYPE_DOUBLE = 2

# t_statut : cycle de vie d'une comparaison
STATUT_COMMENCER = ID_STATUT_COMMENCER
STATUT_EN_COURS = ID_STATUT_EN_COURS
STATUT_TERMINER = ID_STATUT_TERMINER
STATUT_ECHEC = ID_STATUT_ECHEC

def getListeComparaison():
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        rows = get_liste_comparaison(cur)
        resultat = []
        for r in rows:
            id_a = r[1]
            id_b = r[2]
            device_a = get_device_by_id(cur, id_a)
            device_b = get_device_by_id(cur, id_b)
            resultat.append({
                "id": r[0],
                "id_device_a": id_a,
                "version_a":r[8],
                "version_b":r[9],
                "id_device_b": id_b,
                "device_a": device_a[2] if device_a else None,
                "device_b": device_b[2] if device_b else None,
                "id_type_comparaison": r[3],
                "date_reference_a": str(r[4]) if r[4] else None,
                "date_reference_b": str(r[5]) if r[5] else None,
                "date_comparaison": str(r[6]) if r[6] else None,
                "resultat": r[7],
            })
        return resultat
    finally:
        close_connection(connexion)



def _comparaison_row_to_dict(r):
    return {
        "id": r[0],
        "id_device_a": r[1],
        "id_device_b": r[2],
        "device_a": r[10],
        "device_b": r[11],
        "id_type_comparaison": r[3],
        "date_reference_a": str(r[4]) if r[4] else None,
        "date_reference_b": str(r[5]) if r[5] else None,
        "date_comparaison": str(r[6]) if r[6] else None,
        "resultat": r[7],
        "version_a": r[8],
        "version_b": r[9],
    }


def _fetch_comparaisons_page(page=1, page_size=10, datetime_from=None, datetime_to=None):
    connexion = get_connection()
    if connexion is None:
        return build_page([], 0, page, page_size)
    try:
        cur = connexion.cursor()
        rows = find_comparaisons_paginated(cur, page, page_size, datetime_from, datetime_to)
        total = rows[0][12] if rows else 0
        items = [_comparaison_row_to_dict(r) for r in rows]
        cur.close()
        return build_page(items, total, page, page_size)
    finally:
        close_connection(connexion)


def getComparaisonsPage(page=1, page_size=10, datetime_from=None, datetime_to=None):
    offset = get_int_configuration("TZ_OFFSET", 3)
    datetime_from = local_to_utc(datetime_from, offset)
    datetime_to = local_to_utc(datetime_to, offset)

    cle = f"comparaisons:{page}:{page_size}:{datetime_from}:{datetime_to}"
    valeur = cache_get(cle)
    if valeur is not None:
        return valeur

    return cache_set(
        cle,
        _fetch_comparaisons_page(page, page_size, datetime_from, datetime_to)
    )


def get_comparaison_detail(id):
    connexion = get_connection()
    if connexion is None:
        return None
    try:
        cur = connexion.cursor()
        row = get_comparaison_by_id(cur, id)
        if row is None:
            return None
        return _comparaison_row_to_dict(row)
    finally:
        close_connection(connexion)


def _extraire_specs(device, cpu_info):
    """Specs matérielles d'un appareil (voir get_device_by_id + _get_device_cpu_info)."""
    return {
        "cpu_model": cpu_info[0] if cpu_info else None,
        "freq_max_proc": cpu_info[1] if cpu_info else None,
        "cpu_architecture": cpu_info[2] if cpu_info else None,
        "ram_total": device[10] if len(device) > 10 else None,
    }

def get_liste_version_device(id_device):
    connexion = get_connection()
    if connexion is None :
        return []
    try:
        cur = connexion.cursor()
        liste = get_liste_version_by_device(cur,id_device)
        result = []
        for l in liste:
            result.append({
                "id": l[0],
                "chromeos_version": l[1],
                "date": l[2],
            })
        return result 
    finally:
        close_connection(connexion)
             
def get_data_device(cur, id_device, chromeos_version):
    """Données comparables d'un appareil sur l'intervalle d'une version."""
    intervalle = get_version_intervalle(cur, id_device, chromeos_version)
    if intervalle is None:
        return None

    date_debut, date_fin = intervalle
    if date_fin is None:
        date_fin = datetime.now(timezone.utc)

    device = get_device_by_id(cur, id_device)
    if device is None:
        return None

    specs = _extraire_specs(device, _get_device_cpu_info(cur, id_device))

    releves_cpu = get_cpu_device_date(cur, id_device, date_debut, date_fin)
    releves_ram = get_ram_device_date(cur, id_device, date_debut, date_fin)

    cpu_resume = resume_serie([r["valeur"] for r in releves_cpu])
    ram_resume = resume_serie([r["valeur"] for r in releves_ram])
    
    return {
        "id_device": device[0],
        "device_id": device[1],
        "serial_number": device[2],
        "modele": device[3],
        "version": chromeos_version,
        "date_reference": date_debut,
        "specs": specs,
        "version":chromeos_version,
        "cpu": cpu_resume or {"moyenne": None, "min": None, "max": None, "n": 0},
        "ram": {
            "moyenne_util": ram_resume["moyenne"] if ram_resume else None,
            "moyenne_pct": normaliser_ram_pct(ram_resume["moyenne"], specs["ram_total"]) if ram_resume else None,
            "total": specs["ram_total"],
            "n": ram_resume["n"] if ram_resume else 0,
        },
    }


def _ecart(a, b):
    if a is None or b is None:
        return None
    return round(abs(a - b), 2)


def _bloc_usage_cpu(detail_a, detail_b):
    a = detail_a["cpu"]
    b = detail_b["cpu"]
    return {
        "a": {"moyenne": a.get("moyenne"), "min": a.get("min"), "max": a.get("max"), "n": a.get("n")},
        "b": {"moyenne": b.get("moyenne"), "min": b.get("min"), "max": b.get("max"), "n": b.get("n")},
        "plus_utilise": vainqueur(a.get("moyenne"), b.get("moyenne")),
        "ecart_pts": _ecart(a.get("moyenne"), b.get("moyenne")),
    }


def _bloc_usage_ram(detail_a, detail_b):
    a = detail_a["ram"]
    b = detail_b["ram"]
    return {
        "a": {"moyenne_pct": a.get("moyenne_pct"), "moyenne_util": a.get("moyenne_util"),
              "total": a.get("total"), "n": a.get("n")},
        "b": {"moyenne_pct": b.get("moyenne_pct"), "moyenne_util": b.get("moyenne_util"),
              "total": b.get("total"), "n": b.get("n")},
        "plus_utilise": vainqueur(a.get("moyenne_pct"), b.get("moyenne_pct")),
        "ecart_pct": _ecart(a.get("moyenne_pct"), b.get("moyenne_pct")),
    }


def _bloc_puissance_cpu(detail_a, detail_b):
    specs_a = detail_a["specs"]
    specs_b = detail_b["specs"]
    score_a = score_puissance_cpu(specs_a)
    score_b = score_puissance_cpu(specs_b)
    return {
        "a": {"cpu_model": specs_a.get("cpu_model"), "freq_max_proc": specs_a.get("freq_max_proc"),
              "cpu_architecture": specs_a.get("cpu_architecture"), "score": score_a},
        "b": {"cpu_model": specs_b.get("cpu_model"), "freq_max_proc": specs_b.get("freq_max_proc"),
              "cpu_architecture": specs_b.get("cpu_architecture"), "score": score_b},
        "plus_puissant": vainqueur(score_a, score_b),
        "ecart": _ecart(score_a, score_b),
    }


def _bloc_puissance_ram(detail_a, detail_b):
    specs_a = detail_a["specs"]
    specs_b = detail_b["specs"]
    score_a = score_puissance_ram(specs_a)
    score_b = score_puissance_ram(specs_b)
    return {
        "a": {"ram_total": specs_a.get("ram_total"), "score": score_a},
        "b": {"ram_total": specs_b.get("ram_total"), "score": score_b},
        "plus_puissant": vainqueur(score_a, score_b),
        "ecart_octets": _ecart(score_a, score_b),
    }


def _etiquette(detail):
    nom = detail.get("serial_number") or detail.get("device_id") or f"device {detail.get('id_device')}"
    version = detail.get("version")
    return f"{nom} · {version}" if version else nom


def _phrase(titre, nom_a, nom_b, gagnant, ecart, unite):
    if gagnant == "indetermine":
        return f"{titre} : indéterminé (données manquantes)."
    if gagnant == "egal":
        return f"{titre} : égalité."
    nom = nom_a if gagnant == "a" else nom_b
    if ecart is None:
        return f"{titre} : {nom} en tête."
    return f"{titre} : {nom} en tête (écart {ecart}{unite})."

def _resume_verdict(detail_a, detail_b, cpu, ram):
    nom_a = _etiquette(detail_a)
    nom_b = _etiquette(detail_b)
    return " ".join([
        _phrase("CPU usage", nom_a, nom_b, cpu["usage"]["plus_utilise"], cpu["usage"].get("ecart_pts"), " pts"),
        _phrase("CPU puissance", nom_a, nom_b, cpu["puissance"]["plus_puissant"], cpu["puissance"].get("ecart"), ""),
        _phrase("RAM usage", nom_a, nom_b, ram["usage"]["plus_utilise"], ram["usage"].get("ecart_pct"), "%"),
        _phrase("RAM capacité", nom_a, nom_b, ram["puissance"]["plus_puissant"], None, ""),
    ])


def compare(detail_a, detail_b):
    """
    Compare deux appareils sur CPU et RAM, en deux blocs séparés par ressource :
    - usage      : qui consomme le plus (moyennes sur la plage)
    - puissance  : qui a le meilleur matériel (specs, heuristique)
    Ne lève jamais : données manquantes -> null + "indetermine".
    """
    cpu = {
        "usage": _bloc_usage_cpu(detail_a, detail_b),
        "puissance": _bloc_puissance_cpu(detail_a, detail_b),
    }
    ram = {
        "usage": _bloc_usage_ram(detail_a, detail_b),
        "puissance": _bloc_puissance_ram(detail_a, detail_b),
    }
    return {
        "cpu": cpu,
        "ram": ram,
        "verdict": {"resume": _resume_verdict(detail_a, detail_b, cpu, ram)},
    }


def _marquer_echec(connexion, id_comparaison):
    if id_comparaison is None:
        return
    try:
        cur = connexion.cursor()
        insert_comparaison_statut(cur, id_comparaison, STATUT_ECHEC)
        connexion.commit()
    except Exception:
        connexion.rollback()


def _executer_comparaison(id_device_a, id_device_b, version_a, version_b, id_type_comparaison):
    connexion = get_connection()
    if connexion is None:
        return None
    id_comparaison = None
    try:
        cur = connexion.cursor()

        detail_a = get_data_device(cur, id_device_a, version_a)
        detail_b = get_data_device(cur, id_device_b, version_b)
        if detail_a is None or detail_b is None:
            raise ValueError("Appareil ou version introuvable")

        id_comparaison = insert_comparaison(
            cur, id_device_a, id_device_b,
            detail_a["date_reference"], detail_b["date_reference"],
            id_type_comparaison,
            version_a, version_b,
        )
        insert_comparaison_statut(cur, id_comparaison, STATUT_COMMENCER)
        connexion.commit()

        insert_comparaison_statut(cur, id_comparaison, STATUT_EN_COURS)
        connexion.commit()

        resultat = compare(detail_a, detail_b)
        update_comparaison_resultat(cur, id_comparaison, json.dumps(resultat, default=str))

        insert_comparaison_statut(cur, id_comparaison, STATUT_TERMINER)
        connexion.commit()
        cache_invalidate_prefix("comparaisons:")
        return {"id_comparaison": id_comparaison, "resultat": resultat}
    except Exception:
        connexion.rollback()
        _marquer_echec(connexion, id_comparaison)
        raise
    finally:
        close_connection(connexion)


def comparaisonSimple(id_device, version_a, version_b):
    if version_a == version_b:
        raise ValueError("Il faut deux versions différentes")
    return _executer_comparaison(id_device, id_device, version_a, version_b, TYPE_SIMPLE)


def comparaisonDouble(id_device_a, version_a, id_device_b, version_b):
    if id_device_a == id_device_b:
        raise ValueError("Il faut deux appareils différents")
    return _executer_comparaison(id_device_a, id_device_b, version_a, version_b, TYPE_DOUBLE)


# if __name__ == "__main__":
#     # Test manuel :
#     #   python -m backend.fonction.metier.service.comparaison_service <id_a> <version_a> <id_b> <version_b>
#     import sys

#     args = sys.argv[1:]
#     if len(args) < 4:
#         print("Usage: python -m backend.fonction.metier.service.comparaison_service <id_a> <version_a> <id_b> <version_b>")
#         sys.exit(1)

#     id_a, version_a, id_b, version_b = int(args[0]), args[1], int(args[2]), args[3]
#     resultat = comparaisonDouble(id_a, version_a, id_b, version_b)
#     print(json.dumps(resultat["resultat"] if resultat else None, ensure_ascii=False, indent=2))
