def extraire_reseau(data: dict) -> tuple[str | None, str | None]:
    reseau = data.get("lastKnownNetwork") or []
    ip = reseau[0].get("ipAddress") if reseau else None
    mac = data.get("ethernetMacAddress") or data.get("macAddress")

    return ip, mac