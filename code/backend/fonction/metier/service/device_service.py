import json
from datetime import datetime
from backend.fonction.conn.connexion import get_connection, close_connection
from backend.google_api.devices import (get_credentials,get_devices,get_telemetry_devices,get_telemetry_events)
from backend.fonction.metier.repository.filiale.filiale import get_or_create_filiale
from backend.fonction.metier.repository.devices import (
    insert_device, update_device, get_device_by_id, get_device_by_device_id,
    insert_device_filiale, delete_all, get_liste_device, recherche_multicritere,
    get_filiale_by_device,insert_device_utilisateur_recent, get_historique_utilisateurs_device, insert_device_utilisateur, get_utilisateurs_by_device,get_or_create_type_appareil, get_type_appareil_by_id
)

from backend.fonction.metier.repository.statut.statut import get_or_create_statut, get_status_actuel_device,insert_device_statut
from backend.fonction.metier.repository.rapport import (
    create_type_rapport,
    create_rapport_device,
    get_liste_type_rapport,
    init_default_types_rapport,
    get_or_create_type_rapport
)
from backend.fonction.metier.repository.evenement import (create_type_evenement, create_evenement_device)
from backend.fonction.metier.repository.utilisateur_google import (get_or_create_filiale_utilisateur, get_or_create_utilisateur, get_utilisateur_by_id)
from backend.fonction.metier.repository.reseau import (get_or_create_reseau, insert_into_reseau_filiale)
from backend.utils.format_date import parse_date_safe




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
                    d.get("osVersion"),
                    d.get("osVersion"),
                    date_creation,
                    ip_adresse,
                    mac_adresse,
                )
                    
            if db_device_id:
                insert_device_utilisateur(cur, db_device_id, utilisateur_id)
                if id_filiale:
                    insert_device_filiale(cur, db_device_id, id_filiale)
                    get_or_create_filiale_utilisateur(cur, id_filiale, utilisateur_id)
                    if ip_adresse:
                        reseau_res = get_or_create_reseau(cur, ip_adresse)
                        if reseau_res:
                            id_reseau = reseau_res[0]
                            insert_into_reseau_filiale(cur, id_reseau, id_filiale)


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
    init_default_types_rapport(cur)
    types_rapport = get_liste_type_rapport(cur)
    if not types_rapport:
        print(" Aucun type de rapport disponible en base.")
        return

    for tel in telemetry_devices_list:
        tel_device_id = tel.get("deviceId")
        if not tel_device_id:
            continue
        
        device_by_id = get_device_by_device_id(cur, tel_device_id)
        if not device_by_id or len(device_by_id) == 0:
            continue
        db_device_id = device_by_id[0]

        for item in types_rapport:
            id_type_rapport, nom_type, cle_api = item[0], item[1], item[2]
            if not cle_api:
                continue
            liste_releve = tel.get(cle_api, [])
            if liste_releve and isinstance(liste_releve, list):
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
        return []
    cur = connexion.cursor()
    try:
        devices = get_liste_device(cur)
        result = []
        for d in devices:
            status = get_status_actuel_device(cur, d[0])
            utilisateurs = get_utilisateurs_by_device(cur, d[0])
            id_utilisateur = utilisateurs[0][0] if utilisateurs else None
            utilisateur_email = utilisateurs[0][1] if utilisateurs else "N/A"
            
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
                "chromeos_version": d[5],
                "chrome_version":   d[6],
                "mac_adress":       d[7],
                "ip_adress":        d[8],
                "date":             str(d[9]) if d[9] else None,
                "id_utilisateur":   id_utilisateur,
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
        utilisateurs = get_utilisateurs_by_device(cur, d[0])
        id_utilisateur = utilisateurs[0][0] if utilisateurs else None
        utilisateur_email = utilisateurs[0][1] if utilisateurs else "N/A"

        utilisateurs_recents = []
        historique = get_historique_utilisateurs_device(cur, d[0])
        if historique:
            for ur in historique:
                if ur[2]:
                    ur_u = get_utilisateur_by_id(cur, ur[2])
                    if ur_u and ur_u[1] not in utilisateurs_recents:
                        utilisateurs_recents.append(ur_u[1])

        filiale_res = get_filiale_by_device(cur, d[0])
        filiale_nom = filiale_res[1] if filiale_res and filiale_res[1] else None

        type_appareil_res = get_type_appareil_by_id(cur, d[4]) if d[4] else None
        type_appareil_nom = type_appareil_res[1] if type_appareil_res else None

        return {
            "id":               d[0],
            "id_device":        d[1],
            "serial_number":    d[2],
            "modele":           d[3],
            "id_type_appareil": d[4],
            "type_appareil":    type_appareil_nom,
            "chromeos_version": d[5],
            "chrome_version":   d[6],
            "mac_adress":       d[7],
            "ip_adress":        d[8],
            "date":             str(d[9]) if d[9] else None,
            "id_utilisateur":   id_utilisateur,
            "status":           status,
            "utilisateur_email": utilisateur_email,
            "utilisateurs_recents": utilisateurs_recents,
            "filiale":          filiale_nom,
        }
    finally:
        close_connection(connexion)
        
def getDeviceFiltered(recherche):
    connexion = get_connection()
    if connexion is None:
        print("Connexion BDD IMPOSSIBLE")
        return []
    try:
        cur = connexion.cursor()
        devices = recherche_multicritere(cur, recherche)
        if not devices:
            return []
        
        result = []
        for d in devices:
            status = get_status_actuel_device(cur, d[0])
            utilisateurs = get_utilisateurs_by_device(cur, d[0])
            id_utilisateur = utilisateurs[0][0] if utilisateurs else None
            utilisateur_email = utilisateurs[0][1] if utilisateurs else "N/A"
            
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
                "chromeos_version": d[5],
                "chrome_version":   d[6],
                "mac_adress":       d[7],
                "ip_adress":        d[8],
                "date":             str(d[9]) if d[9] else None,
                "id_utilisateur":   id_utilisateur,
                "status":           status,
                "utilisateur_email": utilisateur_email,
                "utilisateurs_recents": utilisateurs_recents,
            })
        return result
    finally:
        close_connection(connexion)
        
# if __name__ == "__main__":
#     connexion = get_connection()
#     cur = connexion.cursor()
#     # device = recherche_multicritere(cur,'digital.salamander@taloumis.mg')
#     # device = getDeviceDetail(2)
#     print(device)