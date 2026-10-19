import logging

from psycopg2 import IntegrityError

from backend.fonction.metier.repository.reseau import (
    find_devices_without_network,
    get_reseau_id_by_ip,
    get_by_device_and_reseau,
    insert_device_reseau,
    create_savepoint_ligne_reseau,
    rollback_savepoint_ligne_reseau,
)

logger = logging.getLogger(__name__)


def get_missing_networks(cur):
    return find_devices_without_network(cur)


def resolve_id_reseau(cur, device_row):
    """
    Priorité 1 : id_reseau renseigné sur le device.
    Priorité 2 : recherche dans t_reseau via t_device.ip_adress.
    Sinon : None.
    """
    id_reseau = device_row[1]
    if id_reseau is not None:
        return id_reseau

    ip_adress = device_row[2]
    if ip_adress:
        return get_reseau_id_by_ip(cur, ip_adress)

    return None


def upsert_network_for_device(cur, device_row):
    id_device = device_row[0]
    reseau_id = resolve_id_reseau(cur, device_row)

    if reseau_id is None:
        logger.warning("[sync] device %s : aucun reseau resolu, skip", id_device)
        return False

    existing = get_by_device_and_reseau(cur, id_device, reseau_id)
    if existing is not None:
        return False

    insert_device_reseau(cur, id_device, reseau_id)
    return True


def sync_network_row(cur, device_row):
    create_savepoint_ligne_reseau(cur)
    try:
        insere = upsert_network_for_device(cur, device_row)
        return 1 if insere else 0
    except IntegrityError:
        rollback_savepoint_ligne_reseau(cur)
        logger.info("[sync] device %s : reseau deja insere", device_row[0])
        return 0
    except Exception as err:
        rollback_savepoint_ligne_reseau(cur)
        logger.error("[sync] device %s network failed: %s", device_row[0], err)
        return 0


def sync_networks_for_all_devices(cur):
    total = 0
    for device_row in get_missing_networks(cur):
        total += sync_network_row(cur, device_row)
    return total


__all__ = [
    "get_missing_networks",
    "resolve_id_reseau",
    "upsert_network_for_device",
    "sync_network_row",
    "sync_networks_for_all_devices",
]
