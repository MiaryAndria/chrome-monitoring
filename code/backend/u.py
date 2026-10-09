from backend.fonction.metier.repository.devices import _get_recent_users,get_device_by_serial_number
from backend.fonction.metier.repository.statut import get_status_actuel_device
from backend.utils.save_to_file import save
from backend.utils.save_to_json import save_to_json
from backend.fonction.conn.connexion import get_connection, close_connection

SN = [
    "5CD5286VM3", "5CD5286VN1", "5CD5286VN2", "5CD5286VN9",
    "5CD5286VNB", "5CD5286VNC", "5CD5286VNN", "5CD5286VNQ",
    "5CD5286VNW", "5CD5286VP3", "5CD5286VP4", "5CD5286VP8",
    "5CD5286VPM", "5CD5286VQB", "5CD5286VQD", "5CD5286VQN",
    "5CD5286VQT", "5CD5286VR6", "5CD5286VRL", "5CD5286VS1",
    "5CD5286VS4", "5CD5286VS8", "5CD5286VSH", "5CD5286VSP",
    "5CD5286VSV", "5CD5286VSY", "5CD5286VSZ", "5CD5286VTG",
    "5CD5286VTN", "5CD5286VTP", "5CD5286VTT", "5CD5286VV8",
    "5CD5286VV9", "5CD5286VVD", "5CD5286VVF", "5CD5286VVN",
    "5CD5286VVP", "5CD5286VVQ", "5CD5286VW2", "5CD5286VWB",
    "5CD5286VW0", "5CD5286VWV", "5CD5286VX5", "5CD5286VX9",
    "5CD5286VXB", "5CD5286VXC", "5CD5286VXD", "5CD5286VXH",
    "5CD5286VXL", "5CD5286VXM", "5CD5286VXQ", "5CD5286VY3",
    "5CD5286VY8", "5CD5286VYB", "5CD5286VYQ", "5CD5286VZ3",
    "5CD5286VZ7", "5CD5286VZJ", "5CD5286W01", "5CD5286W0B",
    "5CD5286W0D", "5CD5286W0G", "5CD5286W1C", "5CD5286W1R",
    "5CD5286W22", "5CD5286W27", "5CD5286W2D", "5CD5286W2L",
    "5CD5286W2M", "5CD5286W2Q", "5CD5286W2Z", "5CD5286W39",
    "5CD5286W3B", "5CD5286W3S", "5CD5286W45", "5CD5286W4K",
    "5CD5286W1M", "5CD5286VMB"
]

def getStatutEtUtilisateurRecent(cur):
    resultats = []

    for s in SN:
        device = get_device_by_serial_number(cur, s)

        if not device:
            print(f"Device introuvable pour le serial : {s}")
            continue

        serialNumber = device[2]
        deviceId = device[0]

        statut = get_status_actuel_device(cur, deviceId)
        utilisateurs = _get_recent_users(cur, deviceId)

        resultats.append({
            "serialNumber": serialNumber,
            "statut": statut,
            "utilisateurs_recents": utilisateurs
        })

    return resultats

def save_report(cur):
    resultats = getStatutEtUtilisateurRecent(cur)
    save_to_json(resultats, "statut_utilisateurs_recents")
    save(resultats,"statut_utilisateurs_recents","Statut et utilisateurs récents")


def getResult(cur):
    resultats = getStatutEtUtilisateurRecent(cur)

    print("===== STATUT ET UTILISATEURS RÉCENTS =====")

    for resultat in resultats:
        print(f"Serial Number  : {resultat['serialNumber']}")
        print(f"Statut         : {resultat['statut']}")
        print(f"Utilisateurs récents : {resultat['utilisateurs_recents']}")

    save_report(cur)

    return resultats

if __name__ == "__main__":
    connexion = get_connection()
    cur = connexion.cursor()

    try:
        getResult(cur)
    finally:
        cur.close()
        close_connection(connexion)
