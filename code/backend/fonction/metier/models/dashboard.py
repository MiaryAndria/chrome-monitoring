from typing import Dict

from pydantic import BaseModel


class DashboardSummaryResponse(BaseModel):
    nb_total_appareils: int
    nb_actifs: int
    nb_indisponibles: int
    nb_anomalie: int
    nb_reparation: int
    nb_crashs: int
    nb_incidents: int
    nb_imprimantes: int
    repartition_statuts: Dict[str, int]
    repartition_types: Dict[str, int]
    repartition_evenements: Dict[str, int]
    total_alerte: int
    alerte_active: int
    alerte_resolue: int
