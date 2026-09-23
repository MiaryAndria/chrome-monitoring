import json
from datetime import datetime
from backend.fonction.conn.connexion import get_connection, close_connection
from backend.google_api.devices import (
    get_credentials,
    get_devices,
    get_telemetry_devices,
    get_telemetry_events
)
from backend.fonction.metier.repository.filiale.filiale import get_or_create_filiale
from backend.fonction.metier.repository.devices.devices import (
    insert_device, update_device, get_device_by_id, get_device_by_device_id,
    insert_device_filiale, delete_all, get_liste_device
)
from backend.fonction.metier.repository.devices.type_appareil import get_or_create_type_appareil
from backend.fonction.metier.repository.devices.device_utilisateur_recent import (
    insert_device_utilisateur_recent, get_historique_utilisateurs_device
)
from backend.fonction.metier.repository.statut.statut import get_or_create_statut, get_status_actuel_device,insert_device_statut
from backend.fonction.metier.repository.rapport.type_rapport import create_type_rapport
from backend.fonction.metier.repository.rapport.rapport_device import create_rapport_device
from backend.fonction.metier.repository.evenement.type_evenement import create_type_evenement
from backend.fonction.metier.repository.evenement.evenement_device import create_evenement_device
from backend.fonction.metier.repository.utilisateur_google.utilisateur_filiale import get_or_create_filiale_utilisateur
from backend.utils.format_date import parse_date_safe
from backend.fonction.metier.repository.utilisateur_google.utilisateur import get_or_create_utilisateur, get_utilisateur_by_id

CATEGORIES_RAPPORT = {
    "cpuStatusReport": "CPU_STATUS",
    "memoryStatusReport": "MEMORY_STATUS",
    "networkStatusReport": "NETWORK_STATUS",
    "osUpdateStatus": "OS_UPDATE_STATUS",
    "batteryStatusReport": "BATTERY_STATUS",
    "storageStatusReport": "STORAGE_STATUS",
    "graphicsStatusReport": "GRAPHICS_STATUS",
    "audioStatusReport": "AUDIO_STATUS",
    "bootPerformanceReport": "BOOT_PERFORMANCE",
    "heartbeatStatusReport": "HEARTBEAT_STATUS",
    "peripheralsReport": "PERIPHERALS_REPORT",
    "networkDiagnosticsReport": "NETWORK_DIAGNOSTICS",
    "networkBandwidthReport": "NETWORK_BANDWIDTH",
}

def insertion_device(cur, dvc_list):
    print("\n--- Ingestion des appareils ---")
    for d in dvc_list:
        device_id = d.get("deviceId")
        if not device_id:
            continue
        email_user = d.get("annotatedUser") or "non_assigne@domaine.com"
        user_res = get_or_create_utilisateur(cur, email_user)
        if not user_res or len(user_res) == 0:
            continue
        utilisateur_id = user_res[0]

        model_nom = d.get("model", "Chromebook Inconnu")
        type_res = get_or_create_type_appareil(cur, model_nom)
        if not type_res or len(type_res) == 0:
            continue
        type_appareil_id = type_res[0]

        networks = d.get("lastKnownNetwork", [])
        ip_adresse = networks[0].get("ipAddress") if networks and isinstance(networks, list) and len(networks) > 0 else None
        mac_adresse = d.get("macAddress") or d.get("ethernetMacAddress")
        date_creation = parse_date_safe(d.get("lastEnrollmentTime"))


        org_unit_path = d.get("orgUnitPath") or 'organisation de base'
        filiale = get_or_create_filiale(cur, org_unit_path)
        id_filiale = filiale[0] if filiale else None
    
        status_google = d.get("status") or "UNKNOWN"

        try:
            existing = get_device_by_device_id(cur, device_id)
            if existing:
                db_device_id = update_device(
                    cur,
                    device_id,
                    d.get("serialNumber"),
                    model_nom,
                    d.get("osVersion"),
                    d.get("osVersion"),
                    ip_adresse,
                    mac_adresse,
                )
            else:
                db_device_id = insert_device(
                    cur,
                    device_id,
                    d.get("serialNumber"),
                    model_nom,
                    type_appareil_id,
                    utilisateur_id,
                    d.get("osVersion"),
                    d.get("osVersion"),
                    date_creation,
                    ip_adresse,
                    mac_adresse,
                )
            
                        
            if db_device_id:
                if id_filiale:
                    insert_device_filiale(cur, db_device_id, id_filiale)
                    get_or_create_filiale_utilisateur(cur, id_filiale, utilisateur_id)

                statut_res = get_or_create_statut(cur, status_google)
                  
                if statut_res:
                    insert_device_statut(cur, db_device_id, statut_res[0])
                    
                for user in d.get("recentUsers", []):
                    ru_email = user.get("email") or "email@gmail.com"
                    ru_user = get_or_create_utilisateur(cur, ru_email)
                    ru_user_id = ru_user[0]
                    if ru_user:
                        insert_device_utilisateur_recent(cur, db_device_id, ru_user_id)
                        if id_filiale:
                            get_or_create_filiale_utilisateur(cur, id_filiale, ru_user_id)

            print(f" Device synchronisé : {device_id} [{status_google}]")
        except Exception as err:
            print(f" Erreur device {device_id}: {err}")

def insert_telemetry(cur, telemetry_devices_list):
    print("\n--- Ingestion de la télémétrie ---")
    for tel in telemetry_devices_list:
        tel_device_id = tel.get("deviceId")
        if not tel_device_id:
            continue
        
        device_by_id = get_device_by_device_id(cur, tel_device_id)
        if not device_by_id or len(device_by_id) == 0:
            continue
        db_device_id = device_by_id[0]

        for cle_api, nom_type in CATEGORIES_RAPPORT.items():
            liste_releve = tel.get(cle_api, [])
            if liste_releve and isinstance(liste_releve, list):
                type_res = create_type_rapport(cur, nom_type)
                if not type_res or len(type_res) == 0:
                    continue
                id_type_rapport = type_res[0]

                for releve in liste_releve:
                    date_releve = parse_date_safe(releve.get("reportTime")) or datetime.now()
                    create_rapport_device(
                        cur,
                        db_device_id,
                        id_type_rapport,
                        date_releve,
                        json.dumps(releve)
                    )
                print(f" {len(liste_releve)} relevés '{nom_type}' insérés pour device : {tel_device_id}")

def insert_event(cur, telemetry_events_list):
    print("\n--- Ingestion des événements ---")
    for evt in telemetry_events_list:
        evt_device_id = evt.get("device", {}).get("deviceId")
        if not evt_device_id:
            continue

        device_by_id = get_device_by_device_id(cur, evt_device_id)
        if not device_by_id or len(device_by_id) == 0:
            continue
        db_device_id = device_by_id[0]

        event_type_str = evt.get("eventType") or "OS_CRASH"
        evt_type_res = create_type_evenement(cur, event_type_str)
        if not evt_type_res or len(evt_type_res) == 0:
            continue
        id_type_evt = evt_type_res[0]

        evt_date = parse_date_safe(evt.get("reportTime")) or datetime.now()
        create_evenement_device(
            cur,
            db_device_id,
            id_type_evt,
            evt_date,
            json.dumps(evt)
        )
        print(f" Événement inséré pour device : {evt_device_id}")

def synchroniser_tout():
    print(" Démarrage de la synchronisation...")
    credential = get_credentials()
    dvc_list = get_devices(credential)
    telemetry_devices_list = get_telemetry_devices(credential)
    telemetry_events_list = get_telemetry_events(credential)

    print(f"-> Devices récupérés : {len(dvc_list)}")
    print(f"-> Télémétrie récupérée : {len(telemetry_devices_list)}")
    print(f"-> Événements récupérés : {len(telemetry_events_list)}")

    connexion = get_connection()
    if connexion is None:
        print(" Connexion BDD impossible")
        return None
    cur = connexion.cursor()
    try:
        insertion_device(cur, dvc_list)
        insert_telemetry(cur, telemetry_devices_list)
        insert_event(cur, telemetry_events_list)
        connexion.commit()
        print("\n Synchronisation complète terminée et validée en BDD !")
    except Exception as e:
        connexion.rollback()
        print(f"\n Erreur pendant la synchronisation : {e}")
    finally:
        close_connection(connexion)
    
# if __name__ == "__main__":
#     synchroniser_tout()

def reset_data():
    connexion = get_connection()
    cur = connexion.cursor()
    try:
        delete_all(cur)
        connexion.commit()
    finally:
        close_connection(connexion)
        
def getListeDevice():
    connexion = get_connection()
    if connexion is None:
        print("Connexion BDD impossible")
        return None 
    cur = connexion.cursor()
    try:
        devices = get_liste_device(cur)
        result = []
        for d in devices:
            
            status = get_status_actuel_device(cur, d[0])
            
            utilisateur_email = "N/A"
            if d[5]:
                
                u = get_utilisateur_by_id(cur, d[5])
                if u:
                    utilisateur_email = u[1]
            
            utilisateurs_recents = []
            historique = get_historique_utilisateurs_device(cur, d[0])
            if historique:
                for ur in historique:
                    if ur[2]:
                        ur_u = get_utilisateur_by_id(cur, ur[2])
                        if ur_u and ur_u[1] not in utilisateurs_recents:
                            utilisateurs_recents.append(ur_u[1])

            result.append({
                "id":               d[0],
                "id_device":        d[1],
                "serial_number":    d[2],
                "modele":           d[3],
                "id_type_appareil": d[4],
                "id_utilisateur":   d[5],
                "chromeos_version": d[6],
                "chrome_version":   d[7],
                "date":             str(d[8]) if d[8] else None,
                "ip_adress":        d[9],
                "mac_adress":       d[10],
                "status":           status,
                "utilisateur_email": utilisateur_email,
                "utilisateurs_recents": utilisateurs_recents,
            })
        cur.close()
        return result

    finally:
        close_connection(connexion)

def getDeviceDetail(id):
    connexion = get_connection()
    if connexion is None:
        print("Connexion BDD IMPOSSIBLE")
        return None
    try:
        cur = connexion.cursor()
        d = get_device_by_id(cur, id)
        if not d:
            return None

        status = get_status_actuel_device(cur, d[0])

        utilisateur_email = "N/A"
        if d[5]:
            u = get_utilisateur_by_id(cur, d[5])
            if u:
                utilisateur_email = u[1]

        utilisateurs_recents = []
        historique = get_historique_utilisateurs_device(cur, d[0])
        if historique:
            for ur in historique:
                if ur[2]:
                    ur_u = get_utilisateur_by_id(cur, ur[2])
                    if ur_u and ur_u[1] not in utilisateurs_recents:
                        utilisateurs_recents.append(ur_u[1])

        return {
            "id": d[0],
            "id_device": d[1],
            "serial_number": d[2],
            "modele": d[3],
            "id_type_appareil": d[4],
            "id_utilisateur": d[5],
            "chromeos_version": d[6],
            "chrome_version": d[7],
            "date": str(d[8]) if d[8] else None,
            "ip_adress": d[9],
            "mac_adress": d[10],
            "status": status,
            "utilisateur_email": utilisateur_email,
            "utilisateurs_recents": utilisateurs_recents,
        }
    finally:
        close_connection(connexion)