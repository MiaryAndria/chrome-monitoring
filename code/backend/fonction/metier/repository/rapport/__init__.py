from .rapport_device import (
    get_liste_rapport_device,
    get_rapport_by_device,
    get_rapport_by_type,
    get_rapport_by_device_and_type,
    create_rapport_device,
    get_rapport_by_device_type_and_period,
)

from .type_rapport import (
    create_type_rapport,
    get_liste_type_rapport,
    get_type_rapport_by_id,
    get_type_rapport_by_type,
    get_or_create_type_rapport,
    init_default_types_rapport,
    get_id_by_type_name,
)
