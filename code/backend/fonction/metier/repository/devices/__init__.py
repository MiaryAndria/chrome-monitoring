from .devices import (
    get_liste_device,
    get_device_by_id,
    get_device_by_device_id,
    get_device_by_serial_number,
    get_filiale_by_device,
    insert_device,
    update_device,
    insert_device_filiale,
    delete_all,
    recherche_multicritere,
    insert_device_cpu,
    get_last_cpu_for_device,
    update_device_ram_total,
    _get_last_disk_info,
    _get_device_cpu_info,
    get_map_devices,
    get_liste_modele,
    find_devices_paginated,
)

from .type_appareil import (
    get_or_create_type_appareil,
    get_type_appareil_by_id,
    get_type_appareil_by_name,
)

from .device_utilisateur import (
    insert_device_utilisateur,
    get_utilisateurs_by_device,
)

from .device_utilisateur_recent import (
    insert_device_utilisateur_recent,
    get_historique_utilisateurs_device,
    get_dernier_utilisateur_device,
    _get_recent_users,
    get_utilisateur_recent_by_device,
    
)
