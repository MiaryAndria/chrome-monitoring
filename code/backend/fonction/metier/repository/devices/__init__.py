from .devices import (
    get_liste_device,
    get_device_by_id,
    get_device_by_device_id,
    get_device_by_serial_number,
    get_device_by_utilisateur,
    get_device_by_filiale,
    get_device_by_type,
    get_device_by_statut,
    get_filiale_by_device,
    get_nombre_device,
    insert_device,
    update_device,
    insert_device_filiale,
    delete_all,
    recherche_multicritere,
)

from .type_appareil import (
    get_or_create_type_appareil,
    get_type_appareil_by_id,
    get_type_appareil_by_name,
    get_liste_type_appareil,
)

from .device_utilisateur import (
    insert_device_utilisateur,
    get_utilisateurs_by_device,
)

from .device_utilisateur_recent import (
    insert_device_utilisateur_recent,
    get_historique_utilisateurs_device,
)
