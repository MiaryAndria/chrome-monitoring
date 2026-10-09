# from backend.google_api.devices import get_credentials, get_devices
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# from backend.google_api.devices import get_devices,get_credentials,get_telemetry_devices,get_telemetry_events
from backend.fonction.metier.controller.user_controller import router as user_router
from backend.fonction.metier.controller.device_controller import router as device_router
from backend.fonction.metier.controller.filiale_controller import router as filiale_router
from backend.fonction.metier.controller.dashboard_controller import router as dashboard_router
from backend.fonction.metier.controller.statut_controller import router as statut_router
from backend.fonction.metier.controller.rapport_controller import router as rapport_router
from backend.fonction.metier.controller.imprimante_controller import router as imprimante_router
from backend.fonction.metier.controller.evenement_controller import router as evenement_router
from backend.fonction.metier.service.import_service import synchroniser_tout
from backend.fonction.metier.service.reset_service import reset_data
import logging
import threading
from contextlib import asynccontextmanager
from backend.google_api.auto_synch import (demarrer_auto_synchronisation,arreter_auto_synchronisation)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s : %(message)s",
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    demarrer_auto_synchronisation()
    yield
    arreter_auto_synchronisation()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard_router,prefix="/dashboard",tags=["dashboard"])
app.include_router(user_router,prefix="/user",tags=["user"])
app.include_router(device_router,prefix="/device",tags=["device"])
app.include_router(filiale_router,prefix="/filiale",tags=["filiale"])
app.include_router(statut_router,prefix="/statut",tags=["statut"])
app.include_router(rapport_router,prefix="/rapport",tags=["rapport"])
app.include_router(imprimante_router,prefix="/imprimante",tags=["imprimante"])
app.include_router(evenement_router,prefix="/evenement",tags=["evenement"])

@app.get("/")
def accueil():
    return {
        "message": "Bienvenue sur mon API"
    }

@app.post("/synch")
def synchDevices():
    try:
        synchroniser_tout()
        return {"message": "Synchronisation terminée avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset")
def resetAll():
    try:
        reset_data()
        return {"message": "Suppression terminée avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# @app.get("/liste/device")
# def getListe():
#     credential = get_credentials()
#     device = get_devices(credential)
#     return device

# @app.get("/telemetry/device")
# def getTelemetryDevice():
#     credential = get_credentials()
#     telemetryDevice = get_telemetry_devices(credential)
#     return telemetryDevice
    
# @app.get("/telemetry/events")
# def getTelemetryEvents():
#     credential = get_credentials()
#     telemtryEvents = get_telemetry_events(credential)
#     return telemtryEvents

