import re
from statistics import mean

# Poids de puissance relatif par palier CPU (heuristique, PAS un benchmark).
TIERS_CPU = {"i3": 1.0, "i5": 1.15, "i7": 1.30, "i9": 1.50}


def resume_serie(valeurs):
    """
    Résume une série de valeurs numériques via la stdlib `statistics` :
    {moyenne, min, max, n}. Retourne None si la série est vide.
    Les valeurs None sont ignorées.
    """
    nombres = [float(v) for v in valeurs if v is not None]
    if not nombres:
        return None
    return {
        "moyenne": round(mean(nombres), 2),
        "min": round(min(nombres), 2),
        "max": round(max(nombres), 2),
        "n": len(nombres),
    }


def _tier_cpu(cpu_model):
    """Palier CPU déduit du modèle (i3/i5/i7/i9) -> poids relatif de puissance."""
    if not cpu_model:
        return None
    modele = str(cpu_model).lower()
    for tier, poids in TIERS_CPU.items():
        if re.search(rf"\b{tier}\b", modele):
            return poids
    return None


def score_puissance_cpu(specs):
    """
    Score de puissance CPU (heuristique, PAS un benchmark) :
    fréquence max (GHz) x poids du palier i3/i5/i7/i9.
    Retourne None si la fréquence max est inconnue.
    """
    specs = specs or {}
    try:
        freq_ghz = float(specs.get("freq_max_proc")) / 1_000_000
    except (TypeError, ValueError):
        return None
    if freq_ghz <= 0:
        return None
    poids = _tier_cpu(specs.get("cpu_model")) or 1.0
    return round(freq_ghz * poids, 4)


def score_puissance_ram(specs):
    """Score de puissance RAM = capacité totale (octets). None si inconnue."""
    specs = specs or {}
    try:
        return int(specs.get("ram_total"))
    except (TypeError, ValueError):
        return None


def vainqueur(a, b):
    """
    Compare deux valeurs numériques -> "a" | "b" | "egal" | "indetermine".
    "indetermine" si l'une des deux manque.
    """
    if a is None or b is None:
        return "indetermine"
    if a > b:
        return "a"
    if b > a:
        return "b"
    return "egal"
