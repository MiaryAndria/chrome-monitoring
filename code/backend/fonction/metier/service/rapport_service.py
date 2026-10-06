from backend.fonction.conn.connexion import get_connection, close_connection
from backend.fonction.metier.repository.rapport import (
    get_id_by_type_name,
    get_rapport_by_device_and_type,
    get_rapport_by_device_type_and_period,
)

def serialize_rapport_rows(rows):
    if not rows:
        return []
    for r in rows:
        if r.get("report_time") is not None:
            r["report_time"] = str(r["report_time"])
    return rows

def _get_rapport_by_type(cur, device_id, type_name):
    type_id = get_id_by_type_name(cur, type_name)
    if not type_id:
        return []
    rows = get_rapport_by_device_and_type(cur, device_id, type_id)
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
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        return getDeviceCpuRaport(cur, id)
    finally:
        close_connection(connexion)

def getRamRaportById(id: int):
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        return getRamRaport(cur, id)
    finally:
        close_connection(connexion)

def getStockageRaportById(id: int):
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        return getStockageRaport(cur, id)
    finally:
        close_connection(connexion)

def getBatterieRaportById(id: int):
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        return getBatterieRaport(cur, id)
    finally:
        close_connection(connexion)

def getReseauRaportById(id: int):
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        return getReseauRaport(cur, id)
    finally:
        close_connection(connexion)

def getConnectedPerRaportById(id: int):
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        return getConnectedPerRaport(cur, id)
    finally:
        close_connection(connexion)

def getDeviceRaportGeneral(id: int):
    connexion = get_connection()
    if connexion is None:
        print("Connexion BDD impossible")
        return None
    cur = connexion.cursor()
    try:
        cpu = getDeviceCpuRaport(cur, id)
        ram = getRamRaport(cur, id)
        stockage = getStockageRaport(cur, id)
        batterie = getBatterieRaport(cur, id)
        reseau = getReseauRaport(cur, id)
        peripheriques = getConnectedPerRaport(cur, id)

        result = {
            "cpu": cpu,
            "ram": ram,
            "stockage": stockage,
            "batterie": batterie,
            "reseau": reseau,
            "peripheriques": peripheriques
        }
        return result
    finally:
        close_connection(connexion)
        
def filterRapportDeviceByDate(id_device, id_type_rapport, date_debut, date_fin):
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        rows = get_rapport_by_device_type_and_period(
            cur, id_device, id_type_rapport, date_debut, date_fin
        )
        return rows
    finally:
        close_connection(connexion)
        
def idByName(id_rapport):
    connexion = get_connection()
    if connexion is None : 
        return []
    try:
        cur = connexion.cursor ()
        return get_id_by_type_name(cur,id_rapport)
    finally:
        close_connection(connexion)
# if __name__ == "__main__":
#     id_device = 1
#     result = getDeviceRaportGeneral(id_device)
#     print(result)
def getReportsForExport(onglet, id_device, date_debut=None, date_fin=None):
    connexion = get_connection()
    if connexion is None:
        return {} if onglet == "general" else []
    try:
        cur = connexion.cursor()
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
                return get_rapport_by_device_type_and_period(cur, id_device, type_id, date_debut, date_fin)
            return get_rapport_by_device_and_type(cur, id_device, type_id)

        if onglet == "general":
            return {key: fetch(name) for key, name in types.items()}
        return fetch(types[onglet])
    finally:
        close_connection(connexion)