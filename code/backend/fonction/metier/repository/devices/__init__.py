from .devices import (
    get_liste_device,
    get_device_by_id,
    get_device_by_device_id,
    get_device_by_serial_number,
    get_device_detail,
    insert_device,
    update_device,
    device_filiale_exists,
    insert_device_filiale,
    get_last_version,
    insert_device_version,
    delete_all,
    update_device_ram_total,
    _get_device_cpu_info,
    get_map_devices,
    get_liste_modele,
    get_all_device_stats,
    find_devices_paginated,
    get_version_intervalle,
    get_liste_version_by_device,
    get_device_type
)

from .type_appareil import (
    get_or_create_type_appareil,
    get_type_appareil_by_name,
)

from .device_utilisateur import (
    insert_device_utilisateur,
)

from .device_utilisateur_recent import (
    insert_device_utilisateur_recent,
    get_dernier_utilisateur_device,
    _get_recent_users,
    get_utilisateur_recent_by_device,
)
