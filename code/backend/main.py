# from backend.google_api.devices import get_credentials, get_devices
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
# from backend.google_api.devices import get_devices,get_credentials,get_telemetry_devices,get_telemetry_events
from backend.core.security import get_current_user
from backend.fonction.metier.controller.user_controller import router as user_router
from backend.fonction.metier.controller.device_controller import router as device_router
from backend.fonction.metier.controller.filiale_controller import router as filiale_router
from backend.fonction.metier.controller.dashboard_controller import router as dashboard_router
from backend.fonction.metier.controller.statut_controller import router as statut_router
from backend.fonction.metier.controller.rapport_controller import router as rapport_router
from backend.fonction.metier.controller.imprimante_controller import router as imprimante_router
from backend.fonction.metier.controller.evenement_controller import router as evenement_router
from backend.fonction.metier.controller.configuration_controller import router as configuration_router
from backend.fonction.metier.controller.ram_controller import router as ram_router
from backend.fonction.metier.controller.cpu_controller import router as cpu_router
from backend.fonction.metier.controller.disk_controller import router as disk_router
# from backend.fonction.metier.service.import_service import synchroniser_tout
from backend.fonction.metier.service.reset_service import reset_data

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # même host que le front (localhost, pas 127.0.0.1)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dépendance appliquée à toutes les routes privées
protected = [Depends(get_current_user)]

# Public : login / logout (/me se protège lui-même dans le controller)
app.include_router(user_router, prefix="/user", tags=["user"])

# Protégé : nécessite un cookie access_token valide
app.include_router(dashboard_router,     prefix="/dashboard",     tags=["dashboard"],     dependencies=protected)
app.include_router(device_router,        prefix="/device",        tags=["device"],        dependencies=protected)
app.include_router(filiale_router,       prefix="/filiale",       tags=["filiale"],       dependencies=protected)
app.include_router(statut_router,        prefix="/statut",        tags=["statut"],        dependencies=protected)
app.include_router(rapport_router,       prefix="/rapport",       tags=["rapport"],       dependencies=protected)
app.include_router(imprimante_router,    prefix="/imprimante",    tags=["imprimante"],    dependencies=protected)
app.include_router(evenement_router,     prefix="/evenement",     tags=["evenement"],     dependencies=protected)
app.include_router(configuration_router, prefix="/configuration", tags=["configuration"], dependencies=protected)
app.include_router(ram_router,           prefix="/ram",           tags=["ram"],           dependencies=protected)
app.include_router(cpu_router,           prefix="/cpu",           tags=["cpu"],           dependencies=protected)
app.include_router(disk_router,          prefix="/disk",          tags=["disk"],          dependencies=protected)

@app.get("/")
def accueil():
    return {
        "message": "Bienvenue sur mon API"
    }

# @app.post("/synch", dependencies=protected)
# def synchDevices():
#     try:
#         synchroniser_tout()
#         return {"message": "Synchronisation terminée avec succès"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset", dependencies=protected)
def resetAll():
    try:
        reset_data()
        return {"message": "Suppression terminée avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @app.get("/liste/device", dependencies=protected)
# def getListe():
#     credential = get_credentials()
#     device = get_devices(credential)
#     return device

# @app.get("/telemetry/device", dependencies=protected)
# def getTelemetryDevice():
#     credential = get_credentials()
#     telemetryDevice = get_telemetry_devices(credential)
#     return telemetryDevice

# @app.get("/telemetry/events", dependencies=protected)
# def getTelemetryEvents():
#     credential = get_credentials()
#     telemtryEvents = get_telemetry_events(credential)
#     return telemtryEvents