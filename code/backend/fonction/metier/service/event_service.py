import json
from backend.fonction.conn.connexion import get_connection, close_connection
from backend.fonction.metier.repository.evenement import get_liste_evenement_avec_details,get_liste_type_evenement


def get_event():
    connexion = get_connection()
    if connexion is None:
        return []
    try:
        cur = connexion.cursor()
        rows = get_liste_evenement_avec_details(cur)
        cur.close()

        result = []
        for r in rows:
            details_raw = r[2]
            details = {}
            if details_raw:
                try:
                    details = json.loads(details_raw) if isinstance(details_raw, str) else details_raw
                except Exception:
                    details = {}

            result.append({
                "id":             r[0],
                "date_evenement": str(r[1]) if r[1] else None,
                "type_evenement": r[3],
                "device_id":      r[4],
                "serial_number":  r[5],
                "modele":         r[6],
                "filiale":        r[7],
                "cause_class":    details.get("cause_class"),
                "cause_hint":     details.get("cause_hint"),
                "last_user":      details.get("last_user"),
                "incident_key":   details.get("incident_key"),
                "crash_seq":      details.get("crash_seq"),
                "raw_events":     details.get("raw_events"),
                "minutes_since_boot": details.get("minutes_since_boot"),
            })
        return result
    finally:
        close_connection(connexion)
        
def get_type_evenement():
    connexion = None        
    try:
        connexion = get_connection()
        cur = connexion.cursor()
        rows = get_liste_type_evenement(cur)
        cur.close()
        result = []
        for r in rows:
            result.append({
                "id":   r[0],   
                "type": r[1]   
            })
        return result           
    finally:
        if connexion:          
            close_connection(connexion)
        