from backend.google_api.auto_synch import demarrer_auto_synchronisation, arreter_auto_synchronisation
import signal, time
demarrer_auto_synchronisation()
def stop(sig, frame):
    arreter_auto_synchronisation()
    exit(0)
signal.signal(signal.SIGINT, stop)
signal.signal(signal.SIGTERM, stop)
while True:
    time.sleep(60)