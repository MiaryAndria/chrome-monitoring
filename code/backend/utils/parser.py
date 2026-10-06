from datetime import datetime, timedelta, timezone
def parse_ts(s):
    """RFC3339 (Z, jusqu'à 9 décimales) -> datetime aware."""
    s = s.replace("Z", "+00:00")
    if "." in s:
        head, rest = s.split(".", 1)
        frac, tz = rest[:-6], rest[-6:]
        s = f"{head}.{frac[:6].ljust(6, '0')}{tz}"
    return datetime.fromisoformat(s)


def safe_ts(s):
    try:
        return parse_ts(s) if s else None
    except Exception:
        return None


def parse_dur(s):
    """'12.5s' -> 12.5"""
    if s is None:
        return None
    try:
        return float(str(s).rstrip("s"))
    except ValueError:
        return None


def as_list(x):
    if x is None:
        return []
    return x if isinstance(x, list) else [x]


def flatten(obj, prefix="", out=None):
    """dict/list imbriqués -> {'a.b.0.c': valeur}"""
    out = {} if out is None else out
    if isinstance(obj, dict):
        for k, v in obj.items():
            flatten(v, f"{prefix}.{k}" if prefix else k, out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            flatten(v, f"{prefix}.{i}" if prefix else str(i), out)
    else:
        out[prefix] = obj
    return out


def paginate(method, key, **kwargs):
    token = None
    while True:
        resp = method(pageToken=token, **kwargs).execute()
        yield from resp.get(key, [])
        token = resp.get("nextPageToken")
        if not token:
            break


