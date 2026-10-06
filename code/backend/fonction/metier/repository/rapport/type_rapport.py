def get_liste_type_rapport(cur):
    cur.execute(
        """
        SELECT id, type, cle_api FROM t_type_rapport
        """
    )
    result = cur.fetchall()
    return result

def get_type_rapport_by_id(cur, id):
    cur.execute(
        """
        SELECT id, type, cle_api FROM t_type_rapport WHERE id = %s
        """, (id,)
    )
    result = cur.fetchone()
    return result

def get_type_rapport_by_type(cur, type):
    cur.execute(
        """
        SELECT id, type, cle_api FROM t_type_rapport WHERE type = %s
        """, (type,)
    )
    result = cur.fetchone()
    return result

def create_type_rapport(cur, type, cle_api):
    cur.execute(
        """
        INSERT INTO t_type_rapport (type, cle_api) 
        VALUES (%s, %s)
        ON CONFLICT (type) DO UPDATE SET cle_api = EXCLUDED.cle_api
        RETURNING id, type, cle_api;
    """, (type, cle_api)
    )
    result = cur.fetchone()
    return result


def get_or_create_type_rapport(cur, type, cle_api):
    existing = get_type_rapport_by_type(cur, type)
    if existing:
        return existing[0]
    created = create_type_rapport(cur, type, cle_api)
    return created[0] if created else None

def init_default_types_rapport(cur):
    default_categories = {
        "cpuStatusReport": "CPU_STATUS",
        "memoryStatusReport": "MEMORY_STATUS",
        "networkStatusReport": "NETWORK_STATUS",
        "osUpdateStatus": "OS_UPDATE_STATUS",
        "batteryStatusReport": "BATTERY_STATUS",
        "storageStatusReport": "STORAGE_STATUS",
        "graphicsStatusReport": "GRAPHICS_STATUS",
        "audioStatusReport": "AUDIO_STATUS",
        "bootPerformanceReport": "BOOT_PERFORMANCE",
        "heartbeatStatusReport": "HEARTBEAT_STATUS",
        "peripheralsReport": "PERIPHERALS_REPORT",
        "networkDiagnosticsReport": "NETWORK_DIAGNOSTICS",
        "networkBandwidthReport": "NETWORK_BANDWIDTH",
    }
    for cle_api, type_nom in default_categories.items():
        get_or_create_type_rapport(cur, type_nom, cle_api)
 
def get_id_by_type_name(cur, type_name):
    cur.execute("SELECT id FROM t_type_rapport WHERE type = %s", (type_name,))
    res = cur.fetchone()
    return res[0] if res else None

