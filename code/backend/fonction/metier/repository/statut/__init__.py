from .statut import (
    get_liste_statut,
    get_statut_by_id,
    get_statut_by_name,
    get_or_create_statut,
    insert_device_statut,
    get_status_actuel_device,
)

# Compatibilité avec anciens imports
get_statut_id_by_nom = get_or_create_statut
