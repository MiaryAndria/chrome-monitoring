from backend.fonction.conn.transaction import lecture
from backend.fonction.metier.repository.rapport import (
    get_id_by_type_name,
    get_rapport_by_device_and_type,
    get_rapport_by_device_type_and_period,
    get_rapport_by_device_type_and_datetime,
    get_liste_rapport_device
)
from backend.utils.format_date import format_date

def serialize_rapport_rows(rows):
    if not rows:
        return []
    for r in rows:
        if r.get("report_time") is not None:
            r["report_time"] = str(r["report_time"])
    return rows

GENERAL_REPORT_LIMIT = 300


def _get_rapport_by_type(cur, device_id, type_name, limit=None):
    type_id = get_id_by_type_name(cur, type_name)
    if not type_id:
        return []
    rows = get_rapport_by_device_and_type(cur, device_id, type_id, limit=limit)
    return serialize_rapport_rows(rows)

def getDeviceCpuRaport(cur, id):
    return _get_rapport_by_type(cur, id, "CPU_STATUS")

def getRamRaport(cur, id):
    return _get_rapport_by_type(cur, id, "MEMORY_STATUS")

def getStockageRaport(cur, id):
    return _get_rapport_by_type(cur, id, "STORAGE_STATUS")

def getBatterieRaport(cur, id):
    return _get_rapport_by_type(cur, id, "BATTERY_STATUS")

def getReseauRaport(cur, id):
    return _get_rapport_by_type(cur, id, "NETWORK_STATUS")

def getConnectedPerRaport(cur, id):
    return _get_rapport_by_type(cur, id, "PERIPHERALS_REPORT")


def getCpuRaportById(id: int):
    with lecture() as cur:
        if cur is None:
            return []
        return getDeviceCpuRaport(cur, id)

def getRamRaportById(id: int):
    with lecture() as cur:
        if cur is None:
            return []
        return getRamRaport(cur, id)

def getStockageRaportById(id: int):
    with lecture() as cur:
        if cur is None:
            return []
        return getStockageRaport(cur, id)

def getBatterieRaportById(id: int):
    with lecture() as cur:
        if cur is None:
            return []
        return getBatterieRaport(cur, id)

def getReseauRaportById(id: int):
    with lecture() as cur:
        if cur is None:
            return []
        return getReseauRaport(cur, id)

def getConnectedPerRaportById(id: int):
    with lecture() as cur:
        if cur is None:
            return []
        return getConnectedPerRaport(cur, id)

def getDeviceRaportGeneral(id: int):
    with lecture() as cur:
        if cur is None:
            print("Connexion BDD impossible")
            return None
        cpu = _get_rapport_by_type(cur, id, "CPU_STATUS", GENERAL_REPORT_LIMIT)
        ram = _get_rapport_by_type(cur, id, "MEMORY_STATUS", GENERAL_REPORT_LIMIT)
        stockage = _get_rapport_by_type(cur, id, "STORAGE_STATUS", GENERAL_REPORT_LIMIT)
        batterie = _get_rapport_by_type(cur, id, "BATTERY_STATUS", GENERAL_REPORT_LIMIT)
        reseau = _get_rapport_by_type(cur, id, "NETWORK_STATUS", GENERAL_REPORT_LIMIT)
        peripheriques = _get_rapport_by_type(cur, id, "PERIPHERALS_REPORT", GENERAL_REPORT_LIMIT)

        return {
            "cpu": cpu,
            "ram": ram,
            "stockage": stockage,
            "batterie": batterie,
            "reseau": reseau,
            "peripheriques": peripheriques
        }

def filterRapportDeviceByDate(id_device, id_type_rapport, date_debut, date_fin):
    with lecture() as cur:
        if cur is None:
            return []
        return get_rapport_by_device_type_and_period(
            cur, id_device, id_type_rapport, date_debut, date_fin
        )


def filterRapportDeviceByDatetime(id_device, id_type_rapport, datetime_from,
                                  datetime_to):
    with lecture() as cur:
        if cur is None:
            return []
        return get_rapport_by_device_type_and_datetime(
            cur, id_device, id_type_rapport, datetime_from, datetime_to
        )

def idByName(id_rapport):
    with lecture() as cur:
        if cur is None:
            return []
        return get_id_by_type_name(cur, id_rapport)

def getReportsForExport(onglet, id_device, date_debut=None, date_fin=None):
    with lecture() as cur:
        if cur is None:
            return {} if onglet == "general" else []
        types = {
            "cpu": "CPU_STATUS", "ram": "MEMORY_STATUS", "stockage": "STORAGE_STATUS",
            "batterie": "BATTERY_STATUS", "reseau": "NETWORK_STATUS",
            "peripheriques": "PERIPHERALS_REPORT",
        }

        def fetch(type_name):
            type_id = get_id_by_type_name(cur, type_name)
            if not type_id:
                return []
            if date_debut and date_fin:
                return get_rapport_by_device_type_and_datetime(
                    cur, id_device, type_id, date_debut, date_fin
                )
            return get_rapport_by_device_and_type(cur, id_device, type_id)

        if onglet == "general":
            return {key: fetch(name) for key, name in types.items()}
        return fetch(types[onglet])

def getListeReport():
    with lecture() as cur:
        if cur is None:
            return []
        return get_liste_rapport_device(cur)


def build_imprimante_sections(detail: dict):
    return [
        (
            "Informations générales",
            ["Fabricant", "Modèle / Nom", "VID", "PID"],
            [[
                detail.get("vendor") or "-",
                detail.get("nom") or "-",
                detail.get("vid") if detail.get("vid") is not None else "-",
                detail.get("pid") if detail.get("pid") is not None else "-",
            ]],
        ),
        (
            "Devices",
            ["Modèle", "N° de série", "IP", "MAC", "ChromeOS", "Dernière détection"],
            [
                [
                    d.get("modele") or "-",
                    d.get("serial_number") or "-",
                    d.get("ip_adress") or "-",
                    d.get("mac_adress") or "-",
                    d.get("chromeos_version") or "-",
                    format_date(d.get("derniere_detection")),
                ]
                for d in detail.get("device", [])
            ],
        ),
        (
            "Utilisateurs",
            ["Email", "Dernière utilisation"],
            [
                [u.get("email") or "-", format_date(u.get("derniere_utilisation"))]
                for u in detail.get("user", [])
            ],
        ),
    ]
    