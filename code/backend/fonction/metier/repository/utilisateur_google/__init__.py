from .utilisateur import (
    get_utilisateur_by_id,
    get_utilisateur_by_email,
    create_utilisateur,
    get_or_create_utilisateur,
    find_utilisateurs_recent_paginated,
    get_devices_by_utilisateur_recent,
)

from .utilisateur_filiale import (
    insert_filiale_utilisateur,
    get_or_create_filiale_utilisateur,
)
