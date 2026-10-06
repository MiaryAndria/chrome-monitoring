def to_number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def format_bytes(value, decimals=2, base=1000):
    n = to_number(value)
    if n is None:
        return None
    if n == 0:
        return "0 o"

    units = ["o", "Ko", "Mo", "Go", "To", "Po"]
    i = 0
    while n >= base and i < len(units) - 1:
        n /= base
        i += 1

    rounded = round(n, decimals)
    if rounded == int(rounded):
        rounded = int(rounded)
    return f"{rounded} {units[i]}"


def format_frequency(khz):
    n = to_number(khz)
    if n is None or n <= 0:
        return None
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f} GHz"
    if n >= 1_000:
        return f"{n / 1_000:.0f} MHz"
    return f"{int(n)} kHz"


def usage_percent(used, total, decimals=1):
    u, t = to_number(used), to_number(total)
    if u is None or t is None or t <= 0:
        return None
    return round(u / t * 100, decimals)


def format_used_over_total(used, total, decimals=1):
    u, t = format_bytes(used, decimals), format_bytes(total, decimals)
    if u is None or t is None:
        return None
    return f"{u} / {t}"


def format_temperature(value):
    n = to_number(value)
    return None if n is None else f"{int(n)}°C"


def format_percent(value, decimals=1):
    n = to_number(value)
    if n is None:
        return None
    rounded = round(n, decimals)
    if rounded == int(rounded):
        rounded = int(rounded)
    return f"{rounded}%"


def _to_int(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        cleaned = value.replace(" ", "").replace(",", "")
        try:
            return int(float(cleaned))
        except ValueError:
            return None
    return None
