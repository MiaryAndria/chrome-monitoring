import json
from datetime import datetime, timezone,timedelta

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime
from backend.utils.chrono import _aware, chrono, memo

def _appel_chrono(etapes, label, callback, *args):
    with chrono(label, etapes):
        return callback(*args)

from backend.fonction.conn.connexion import get_connection, close_connection
from backend.google_api.devices import get_credential, get_devices, get_telemetry_devices
from backend.google_api.print import extract_printers_from_telemetry
from backend.google_api.event import fetch_crash_sources, build_crash_incidents
from backend.fonction.metier.repository.devices import (
    insert_device,
    update_device,
    insert_device_cpu,
    get_last_cpu_for_device,
    update_device_ram_total,
    get_device_by_device_id,
    insert_device_filiale,
    insert_device_utilisateur_recent,
    insert_device_utilisateur,
    get_or_create_type_appareil,
    get_map_devices
)
from backend.fonction.metier.repository.filiale import get_or_create_filiale
from backend.fonction.metier.repository.cpu import get_or_create_cpu
from backend.fonction.metier.repository.disk import get_or_create_disk
from backend.fonction.metier.repository.disk.disk_device import insert_disk_device
from backend.fonction.metier.repository.statut import get_or_create_statut, insert_device_statut
from backend.fonction.metier.repository.rapport import (
    create_type_rapport,
    create_rapport_device,
    get_liste_type_rapport,
    insert_rapport_lot,
    init_default_types_rapport,
)
from backend.fonction.metier.repository.evenement import get_or_create_type_evenement, create_evenement_device
from backend.fonction.metier.repository.utilisateur_google import (
    get_or_create_filiale_utilisateur,
    get_or_create_utilisateur,
)
from backend.fonction.metier.repository.imprimante import insert_imprimante_device, get_or_create_imprimante, insert_imprimante_user
from backend.fonction.metier.repository.reseau import get_or_create_reseau, insert_into_reseau_filiale
from backend.utils.format_valeur import _to_int, format_bytes
from backend.utils.format_date import parse_date_safe
from backend.fonction.metier.repository.devices.device_utilisateur_recent import get_utilisateur_recent_by_device


# @contextmanager
# def chrono(label):
#     start = time.perf_counter()
#     yield
#     elapsed = time.perf_counter() - start
#     print(f"[{label}] {elapsed:.2f}s")


# def _appel_chrono(label, callback, *args, **kwargs):
#     with chrono(label):
#         return callback(*args, **kwargs)


def insertion_device(cur, dvc_list):
    print("\n--- Ingestion des appareils ---")
    for d in dvc_list:
        device_id = d.get("deviceId")
        if not device_id:
            continue
        email_user = d.get("annotatedUser") or "non_assigne@domaine.com"
        utilisateur_id = get_or_create_utilisateur(cur, email_user)
        if utilisateur_id is None:
            continue

        model_nom = d.get("model", "Chromebook Inconnu")
        type_appareil_id = get_or_create_type_appareil(cur, model_nom)
        if type_appareil_id is None:
            continue

        networks = d.get("lastKnownNetwork", [])
        ip_adresse = networks[0].get("ipAddress") if networks and isinstance(networks, list) and len(networks) > 0 else None
        mac_adresse = d.get("macAddress") or d.get("ethernetMacAddress")
        date_creation = parse_date_safe(d.get("lastEnrollmentTime"))

        org_unit_path = d.get("orgUnitPath") or 'organisation de base'
        id_filiale = get_or_create_filiale(cur, org_unit_path)
        status_google = d.get("status") or "UNKNOWN"

        try:
            default_cpu_id = get_or_create_cpu(cur, "UNKNOWN", None, "UNKNOWN")

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
                if db_device_id:
                    last_cpu = get_last_cpu_for_device(cur, db_device_id)
                    if not last_cpu:
                        insert_device_cpu(cur, default_cpu_id, db_device_id)
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
                    last_cpu = get_last_cpu_for_device(cur, db_device_id)
                    if not last_cpu:
                        insert_device_cpu(cur, default_cpu_id, db_device_id)

            if db_device_id:
                insert_device_utilisateur(cur, db_device_id, utilisateur_id)
                if id_filiale:
                    insert_device_filiale(cur, db_device_id, id_filiale)
                    get_or_create_filiale_utilisateur(cur, id_filiale, utilisateur_id)
                    if ip_adresse:
                        id_reseau = get_or_create_reseau(cur, ip_adresse)
                        if id_reseau is not None:
                            insert_into_reseau_filiale(cur, id_reseau, id_filiale)

                id_statut = get_or_create_statut(cur, status_google)

                if id_statut is not None:
                    insert_device_statut(cur, db_device_id, id_statut)

                for user in d.get("recentUsers", []):
                    ru_email = user.get("email") or "email@gmail.com"
                    ru_user_id = get_or_create_utilisateur(cur, ru_email)
                    if ru_user_id is not None:
                        insert_device_utilisateur_recent(cur, db_device_id, ru_user_id)
                        if id_filiale:
                            get_or_create_filiale_utilisateur(cur, id_filiale, ru_user_id)

            print(f" Device synchronisé : {device_id} [{status_google}]")
        except Exception as err:
            print(f" Erreur device {device_id}: {err}")


# def insert_telemetry(cur, telemetry_devices_list):
#     print("\n--- Ingestion de la télémétrie ---")
#     init_default_types_rapport(cur)
#     types_rapport = get_liste_type_rapport(cur)
#     if not types_rapport:
#         print(" Aucun type de rapport disponible en base.")
#         return

#     for tel in telemetry_devices_list:
#         tel_device_id = tel.get("deviceId")
#         if not tel_device_id:
#             continue

#         device_by_id = get_device_by_device_id(cur, tel_device_id)
#         if not device_by_id or len(device_by_id) == 0:
#             continue
#         db_device_id = device_by_id[0]

#         cpu_model = None
#         freq_max_proc = None
#         cpu_architecture = None
#         cpu_reports = tel.get("cpuInfo") or []
#         if cpu_reports and isinstance(cpu_reports, list):
#             cpu = cpu_reports[0] if isinstance(cpu_reports[0], dict) else {}
#             cpu_model = cpu.get("model") or cpu.get("name") or cpu.get("cpuModel")
#             freq_max_proc = _to_int(
#                 cpu.get("maxClockSpeedKhz")
#                 or cpu.get("maxClockSpeed")
#                 or cpu.get("frequencyKhz")
#                 or cpu.get("maxClockSpeedHz")
#             )
#             cpu_architecture = cpu.get("architecture") or cpu.get("architectureName")

#         ram_total = None
#         memory_info = tel.get("memoryInfo") or {}
#         if isinstance(memory_info, dict):
#             ram_total = _to_int(
#                 memory_info.get("totalRamBytes")
#                 or memory_info.get("totalMemoryBytes")
#                 or memory_info.get("ramTotalBytes")
#             )
#             if ram_total is not None:
#                 update_device_ram_total(cur, db_device_id, ram_total)

#         disk_model = None
#         disk_type = None
#         disk_size = None
#         disk_used = None
#         disk_available = None
#         disk_report_time = None
#         storage_info = tel.get("storageInfo") or {}
#         storage_reports = tel.get("storageStatusReport") or []

#         if isinstance(storage_info, dict):
#             disk_size = _to_int(
#                 storage_info.get("totalDiskBytes")
#                 or storage_info.get("totalStorageBytes")
#                 or storage_info.get("totalBytes")
#             )
#             disk_available = _to_int(
#                 storage_info.get("availableDiskBytes")
#                 or storage_info.get("freeDiskBytes")
#                 or storage_info.get("freeBytes")
#             )

#         if storage_reports and isinstance(storage_reports, list):
#             storage_data = storage_reports[0]
#             if isinstance(storage_data, dict):
#                 disk_report_time = parse_date_safe(storage_data.get("reportTime"))
#                 disks = storage_data.get("disk") or storage_data.get("disks") or []
#                 disk = disks[0] if isinstance(disks, list) and disks else {}
#                 if not disk_model:
#                     disk_model = disk.get("model") or disk.get("name")
#                 if not disk_type:
#                     disk_type = disk.get("type") or disk.get("diskType")
#                 if disk_size is None:
#                     disk_size = _to_int(disk.get("sizeBytes") or disk.get("totalBytes") or disk.get("size"))
#                 if disk_used is None:
#                     disk_used = _to_int(disk.get("usedBytes") or disk.get("usedSpaceBytes") or disk.get("storageUsedBytes"))
#                 if disk_available is None:
#                     disk_available = _to_int(
#                         disk.get("availableBytes")
#                         or disk.get("freeBytes")
#                         or disk.get("availableSpaceBytes")
#                     )

#         if cpu_model or cpu_architecture or freq_max_proc is not None:
#             cpu_id = get_or_create_cpu(cur, cpu_model or "UNKNOWN", freq_max_proc, cpu_architecture or "UNKNOWN")
#             if cpu_id:
#                 last_cpu = get_last_cpu_for_device(cur, db_device_id)
#                 if last_cpu != cpu_id:
#                     insert_device_cpu(cur, cpu_id, db_device_id)

#         if disk_model or disk_type or disk_size is not None:
#             disk_id = get_or_create_disk(cur, disk_model or "UNKNOWN", disk_type or "UNKNOWN")
#             if disk_id:
#                 total_reel = disk_size if disk_size is not None else 0
#                 total_formater = format_bytes(total_reel)

#                 if disk_available is not None:
#                     disponible = max(disk_available, 0)
#                 elif disk_used is not None and total_reel is not None:
#                     disponible = max(total_reel - disk_used, 0)
#                 else:
#                     disponible = total_reel if total_reel is not None else None

#                 if disk_used is not None:
#                     utiliser = max(disk_used, 0)
#                 elif disponible is not None and total_reel is not None:
#                     utiliser = max(total_reel - disponible, 0)
#                 else:
#                     utiliser = None

#                 total_utiliser_formater = format_bytes(utiliser) if utiliser is not None else None
#                 disponible_formater = format_bytes(disponible) if disponible is not None else None

#                 insert_disk_device(
#                     cur,
#                     db_device_id,
#                     disk_id,
#                     disponible,
#                     disponible_formater,
#                     total_reel,
#                     total_formater,
#                     utiliser,
#                     total_utiliser_formater,
#                     disk_report_time or datetime.now(),
#                 )

#         for item in types_rapport:
#             id_type_rapport, nom_type, cle_api = item[0], item[1], item[2]
#             if not cle_api:
#                 continue
#             liste_releve = tel.get(cle_api, [])
#             if liste_releve and isinstance(liste_releve, list):
#                 for releve in liste_releve:
#                     date_releve = parse_date_safe(releve.get("reportTime")) or datetime.now()
#                     if nom_type == 'MEMORY_STATUS' and ram_total is not None:
#                         releve = {**releve, 'totalRamBytes': ram_total}
#                     create_rapport_device(cur, db_device_id, id_type_rapport, date_releve, json.dumps(releve))

def insert_telemetry(cur, telemetry_devices_list, debut=None):
    print("\n--- Ingestion de la télémétrie ---")
    init_default_types_rapport(cur)
    types_rapport = get_liste_type_rapport(cur)
    if not types_rapport:
        print(" Aucun type de rapport disponible en base.")
        return

    debut = _aware(debut)

    # Caches valables pour cette synchro seulement
    get_cpu = memo(get_or_create_cpu)
    get_disk = memo(get_or_create_disk)

    # Tous les appareils en une requête
    # ADAPTE : nom de la table et des colonnes (device_id = identifiant Google, id = clé interne)
    map_devices = get_map_devices(cur)

    lignes = []   # relevés à insérer en lot

    for tel in telemetry_devices_list:
        tel_device_id = tel.get("deviceId")
        if not tel_device_id:
            continue

        db_device_id = map_devices.get(tel_device_id)
        if db_device_id is None:
            continue

        cpu_model = None
        freq_max_proc = None
        cpu_architecture = None
        cpu_reports = tel.get("cpuInfo") or []
        if cpu_reports and isinstance(cpu_reports, list):
            cpu = cpu_reports[0] if isinstance(cpu_reports[0], dict) else {}
            cpu_model = cpu.get("model") or cpu.get("name") or cpu.get("cpuModel")
            freq_max_proc = _to_int(
                cpu.get("maxClockSpeedKhz")
                or cpu.get("maxClockSpeed")
                or cpu.get("frequencyKhz")
                or cpu.get("maxClockSpeedHz")
            )
            cpu_architecture = cpu.get("architecture") or cpu.get("architectureName")

        ram_total = None
        memory_info = tel.get("memoryInfo") or {}
        if isinstance(memory_info, dict):
            ram_total = _to_int(
                memory_info.get("totalRamBytes")
                or memory_info.get("totalMemoryBytes")
                or memory_info.get("ramTotalBytes")
            )
            if ram_total is not None:
                update_device_ram_total(cur, db_device_id, ram_total)

        disk_model = None
        disk_type = None
        disk_size = None
        disk_used = None
        disk_available = None
        disk_report_time = None
        storage_info = tel.get("storageInfo") or {}
        storage_reports = tel.get("storageStatusReport") or []

        if isinstance(storage_info, dict):
            disk_size = _to_int(
                storage_info.get("totalDiskBytes")
                or storage_info.get("totalStorageBytes")
                or storage_info.get("totalBytes")
            )
            disk_available = _to_int(
                storage_info.get("availableDiskBytes")
                or storage_info.get("freeDiskBytes")
                or storage_info.get("freeBytes")
            )

        if storage_reports and isinstance(storage_reports, list):
            storage_data = storage_reports[0]
            if isinstance(storage_data, dict):
                disk_report_time = parse_date_safe(storage_data.get("reportTime"))
                disks = storage_data.get("disk") or storage_data.get("disks") or []
                disk = disks[0] if isinstance(disks, list) and disks else {}
                if not disk_model:
                    disk_model = disk.get("model") or disk.get("name")
                if not disk_type:
                    disk_type = disk.get("type") or disk.get("diskType")
                if disk_size is None:
                    disk_size = _to_int(disk.get("sizeBytes") or disk.get("totalBytes") or disk.get("size"))
                if disk_used is None:
                    disk_used = _to_int(disk.get("usedBytes") or disk.get("usedSpaceBytes") or disk.get("storageUsedBytes"))
                if disk_available is None:
                    disk_available = _to_int(
                        disk.get("availableBytes")
                        or disk.get("freeBytes")
                        or disk.get("availableSpaceBytes")
                    )

        if cpu_model or cpu_architecture or freq_max_proc is not None:
            cpu_id = get_cpu(cur, cpu_model or "UNKNOWN", freq_max_proc, cpu_architecture or "UNKNOWN")
            if cpu_id:
                last_cpu = get_last_cpu_for_device(cur, db_device_id)
                if last_cpu != cpu_id:
                    insert_device_cpu(cur, cpu_id, db_device_id)

        if disk_model or disk_type or disk_size is not None:
            disk_id = get_disk(cur, disk_model or "UNKNOWN", disk_type or "UNKNOWN")
            if disk_id:
                total_reel = disk_size if disk_size is not None else 0
                total_formater = format_bytes(total_reel)

                if disk_available is not None:
                    disponible = max(disk_available, 0)
                elif disk_used is not None and total_reel is not None:
                    disponible = max(total_reel - disk_used, 0)
                else:
                    disponible = total_reel if total_reel is not None else None

                if disk_used is not None:
                    utiliser = max(disk_used, 0)
                elif disponible is not None and total_reel is not None:
                    utiliser = max(total_reel - disponible, 0)
                else:
                    utiliser = None

                total_utiliser_formater = format_bytes(utiliser) if utiliser is not None else None
                disponible_formater = format_bytes(disponible) if disponible is not None else None

                insert_disk_device(
                    cur,
                    db_device_id,
                    disk_id,
                    disponible,
                    disponible_formater,
                    total_reel,
                    total_formater,
                    utiliser,
                    total_utiliser_formater,
                    disk_report_time or datetime.now(),
                )

        for item in types_rapport:
            id_type_rapport, nom_type, cle_api = item[0], item[1], item[2]
            if not cle_api:
                continue
            liste_releve = tel.get(cle_api, [])
            if liste_releve and isinstance(liste_releve, list):
                for releve in liste_releve:
                    date_releve = parse_date_safe(releve.get("reportTime")) or datetime.now()

                    # Relevé plus ancien que la fenêtre : déjà inséré par une synchro précédente
                    if debut is not None and _aware(date_releve) < debut:
                        continue

                    if nom_type == 'MEMORY_STATUS' and ram_total is not None:
                        releve = {**releve, 'totalRamBytes': ram_total}
                    lignes.append((db_device_id, id_type_rapport, date_releve, json.dumps(releve)))

    if lignes:
        insert_rapport_lot(cur,lignes)
    
def insert_imprimante(cur, telemetry_devices_list):
    printers = extract_printers_from_telemetry(telemetry_devices_list)
    for p in printers:
        vid = p["vid"]
        pid = p["pid"]
        vendor = p["vendor"]
        nom = p["model"]
        device_id = p["deviceId"]
        date = p["lastSeen"]

        device = get_device_by_device_id(cur, device_id)
        if not device:
            continue
        id_device = device[0]
        imprimante = get_or_create_imprimante(cur, vid, pid, vendor, nom)
        if not imprimante:
            continue

        id_imprimante = imprimante[0][0]
        nouveau = insert_imprimante_device(cur, id_imprimante, id_device, date)
        if nouveau:
            utilisateur = get_utilisateur_recent_by_device(cur, id_device)
            if utilisateur:
                insert_imprimante_user(cur, id_imprimante, utilisateur[0], date)


def insert_event(cur, crashes_data):
    evenements = crashes_data.get("evenements", []) if isinstance(crashes_data, dict) else crashes_data

    for crash in evenements:
        device_id_uuid = crash.get("deviceId")
        if not device_id_uuid:
            continue

        device = get_device_by_device_id(cur, device_id_uuid)
        if not device:
            continue
        id_device = device[0]

        crash_type = crash.get("crashType", "UNKNOWN")
        id_type_evenement = get_or_create_type_evenement(cur, crash_type)
        date_evenement = crash.get("time") or crash.get("last_event_time")

        details_dict = {
            "incident_key": crash.get("incident_key"),
            "cause_class": crash.get("cause_class"),
            "cause_hint": crash.get("cause_hint"),
            "last_user": crash.get("lastUserBestGuess") or crash.get("lastUser"),
            "minutes_since_boot": crash.get("minutes_since_boot"),
            "activities_before_crash": crash.get("activities_before_crash"),
            "raw_events": crash.get("raw_events"),
            "crash_seq": crash.get("crash_seq"),
        }
        details_json = json.dumps(details_dict, ensure_ascii=False)

        create_evenement_device(cur, id_device, id_type_evenement, date_evenement, details_json)


# def synchroniser_tout(debut=None, fin=None):
#     print(" Démarrage de la synchronisation...")
#     credential = get_credential()

#     connexion = get_connection()
#     if connexion is None:
#         print(" Connexion BDD impossible")
#         return 0

#     try:
#         with chrono("Google TOTAL (parallèle)"):
#             with ThreadPoolExecutor(max_workers=3) as pool:
#                 f_dev = pool.submit(_appel_chrono, "Google devices", get_devices, credential)
#                 f_tel = pool.submit(_appel_chrono, "Google télémétrie", get_telemetry_devices, credential)
#                 f_crash = pool.submit(_appel_chrono, "Google crashs + contexte",
#                                       fetch_crash_sources, credential, debut)
#                 dvc_list = f_dev.result()
#                 telemetry_devices_list = f_tel.result()
#                 events, ctx = f_crash.result()

#         with chrono("Enrichissement crashs"):
#             crashes_data = build_crash_incidents(events, ctx, dvc_list, telemetry_devices_list, debut)

#         cur = connexion.cursor()
#         nb_lignes = 0

#         print('Insertion device')
#         insertion_device(cur, dvc_list)
#         nb_lignes += len(dvc_list) if isinstance(dvc_list, list) else 0

#         print('Insertion telemetry')
#         insert_telemetry(cur, telemetry_devices_list)
#         nb_lignes += len(telemetry_devices_list) if isinstance(telemetry_devices_list, list) else 0

#         print('Insertion imprimante')
#         insert_imprimante(cur, telemetry_devices_list)

#         print('Insertion evenement')
#         insert_event(cur, crashes_data)
#         if isinstance(crashes_data, dict):
#             nb_lignes += len(crashes_data.get('evenements', []))
#         elif isinstance(crashes_data, list):
#             nb_lignes += len(crashes_data)

#         connexion.commit()
#         print("\n Synchronisation complète terminée et validée en BDD !")
#         return nb_lignes
#     except Exception as e:
#         connexion.rollback()
#         print(f"\n Erreur pendant la synchronisation : {e}")
#         return 0
#     finally:
#         close_connection(connexion)

def synchroniser_tout(debut=None, fin=None, suivi=None):
    suivi = suivi if suivi is not None else {}
    etapes = suivi.setdefault("etapes_s", {})
    compteurs = suivi.setdefault("compteurs", {})

    print(" Démarrage de la synchronisation...")
    with chrono("google_credential", etapes):
        credential = get_credential()

    connexion = get_connection()
    if connexion is None:
        raise RuntimeError("Connexion BDD impossible")

    try:
        with chrono("google_total_parallele", etapes):
            with ThreadPoolExecutor(max_workers=3) as pool:
                f_dev = pool.submit(_appel_chrono, etapes, "google_devices", get_devices, credential)
                f_tel = pool.submit(_appel_chrono, etapes, "google_telemetrie", get_telemetry_devices, credential)
                f_crash = pool.submit(_appel_chrono, etapes, "google_crashs",
                                      fetch_crash_sources, credential, debut)
                dvc_list = f_dev.result()
                telemetry_devices_list = f_tel.result()
                events, ctx = f_crash.result()

        with chrono("enrichissement_crashs", etapes):
            crashes_data = build_crash_incidents(events, ctx, dvc_list, telemetry_devices_list, debut)

        cur = connexion.cursor()

        nb_dev = len(dvc_list) if isinstance(dvc_list, list) else 0
        nb_tel = len(telemetry_devices_list) if isinstance(telemetry_devices_list, list) else 0
        evenements = crashes_data.get("evenements", []) if isinstance(crashes_data, dict) else (crashes_data or [])
        compteurs.update({"devices": nb_dev, "telemetrie": nb_tel, "evenements": len(evenements)})

        with chrono("db_devices", etapes):
            insertion_device(cur, dvc_list)
        with chrono("db_telemetrie", etapes):
            insert_telemetry(cur, telemetry_devices_list, debut-timedelta(hours=24))
        with chrono("db_imprimantes", etapes):
            insert_imprimante(cur, telemetry_devices_list)
        with chrono("db_evenements", etapes):
            insert_event(cur, crashes_data)
        with chrono("db_commit", etapes):
            connexion.commit()

        print("\n Synchronisation complète terminée et validée en BDD !")
        return nb_dev + nb_tel + len(evenements)
    except Exception:
        connexion.rollback()
        raise
    finally:
        close_connection(connexion)
