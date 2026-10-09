from .synchronisation_historique import (
    insert_synchronisation_historique,
    get_derniere_fenetre_fin_by_source,
    update_synchronisation_resultat,
)

from .synchronisation_statut import insert_synchronisation_statut

# Compatibilité avec ancien nom de fonction
insert_synchronisaton_statut = insert_synchronisation_statut
