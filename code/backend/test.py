import time
from contextlib import contextmanager

from backend.fonction.conn.connexion import get_connection, close_connection
from backend.google_api.devices import get_credential, get_devices, get_telemetry_devices
from backend.google_api.event import get_crash_incidents
from backend.fonction.metier.service.import_service import (
    insertion_device,
    insert_telemetry,
    insert_imprimante,
    insert_event,
)

# Pause (en secondes) entre chaque requête/étape
PAUSE_SECONDS = 60  # mets 45 si tu veux 45s


@contextmanager
def chrono(label):
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    print(f"[{label}] {elapsed:.2f}s")


def pause(seconds=PAUSE_SECONDS, label=""):
    if seconds <= 0:
        return
    msg = f"Pause de {seconds}s"
    if label:
        msg += f" (après : {label})"
    print(f"{msg}...")
    time.sleep(seconds)


def benchmark_sync():
    creds = get_credential()

    with chrono("Google - devices"):
        devices = get_devices(creds)
    pause(label="Google - devices")

    with chrono("Google - telemetry"):
        telemetry = get_telemetry_devices(creds)
    pause(label="Google - telemetry")

    with chrono("Google - crash incidents"):
        crashes = get_crash_incidents(creds)
    pause(label="Google - crash incidents")

    connexion = get_connection()
    if connexion is None:
        raise RuntimeError("Connexion BDD impossible")

    cur = connexion.cursor()
    try:
        with chrono("BDD - insertion devices"):
            insertion_device(cur, devices)
        pause(label="BDD - insertion devices")

        with chrono("BDD - insertion telemetry"):
            insert_telemetry(cur, telemetry)
        pause(label="BDD - insertion telemetry")

        with chrono("BDD - insertion imprimantes"):
            insert_imprimante(cur, telemetry)
        pause(label="BDD - insertion imprimantes")

        with chrono("BDD - insertion evenements"):
            insert_event(cur, crashes)

        connexion.commit()
        print(f"\nDevices: {len(devices)}")
        print(f"Telemetry: {len(telemetry)}")
        print(f"Crash events: {len(crashes) if isinstance(crashes, list) else 'n/a'}")
    except Exception:
        connexion.rollback()
        raise
    finally:
        close_connection(connexion)


if __name__ == "__main__":
    benchmark_sync()