from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.google_api.devices import get_devices,get_credentials,get_telemetry_devices,get_telemetry_events
from backend.fonction.metier.controller.user_controller import router as user_router
from backend.fonction.metier.controller.device_controller import router as device_router
from backend.fonction.metier.controller.filiale_controller import router as filiale_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router,prefix="/user",tags=["user"])
app.include_router(device_router,prefix="/device",tags=["device"])
app.include_router(filiale_router,prefix="/filiale",tags=["filiale"])
@app.get("/")
def accueil():
    return {
        "message": "Bienvenue sur mon API"
    }
    
@app.get("/liste/device")
def getListe():
    credential = get_credentials()
    device = get_devices(credential)
    return device

@app.get("/telemetry/device")
def getTelemetryDevice():
    credential = get_credentials()
    telemetryDevice = get_telemetry_devices(credential)
    return telemetryDevice
    
@app.get("/telemetry/events")
def getTelemetryEvents():
    credential = get_credentials()
    telemtryEvents = get_telemetry_events(credential)
    return telemtryEvents

