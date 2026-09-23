-- =========================================================
-- 1. UTILISATEURS DE L'APPLICATION
-- =========================================================

CREATE TABLE t_user (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    mdp VARCHAR(255) NOT NULL
);


-- =========================================================
-- 2. FILIALE
-- =========================================================

CREATE TABLE t_filiale (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(255) UNIQUE NOT NULL,
    org_unit_path VARCHAR(255) UNIQUE NOT NULL
);


-- =========================================================
-- 3. RESEAU
-- =========================================================

CREATE TABLE t_reseau (
    id SERIAL PRIMARY KEY,
    valeur VARCHAR(255) NOT NULL
);

CREATE TABLE t_reseau_filiale (
    id SERIAL PRIMARY KEY,
    id_reseau INT NOT NULL REFERENCES t_reseau(id),
    id_filiale INT NOT NULL REFERENCES t_filiale(id),
    UNIQUE (id_reseau, id_filiale)
);


-- =========================================================
-- 4. TYPES D'APPAREILS
-- =========================================================

CREATE TABLE t_type_appareil (
    id SERIAL PRIMARY KEY,
    type_device VARCHAR(100) UNIQUE NOT NULL
);


-- =========================================================
-- 5. UTILISATEURS GOOGLE / EMPLOYES
-- =========================================================

CREATE TABLE t_utilisateur (
    id SERIAL PRIMARY KEY,
    google_user_id VARCHAR(255) UNIQUE,
    email VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE t_filiale_utilisateur (
    id SERIAL PRIMARY KEY,
    id_filiale INT NOT NULL REFERENCES t_filiale(id),
    id_utilisateur INT NOT NULL REFERENCES t_utilisateur(id),
    UNIQUE (id_filiale, id_utilisateur)
);


-- =========================================================
-- 6. STATUTS
-- =========================================================

CREATE TABLE t_statut (
    id SERIAL PRIMARY KEY,
    statut VARCHAR(100) UNIQUE NOT NULL
);


-- =========================================================
-- 7. DEVICES
-- =========================================================

CREATE TABLE t_device (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(255) UNIQUE NOT NULL,
    serial_number VARCHAR(255),
    modele VARCHAR(255),

    id_type_appareil INT REFERENCES t_type_appareil(id),
    id_utilisateur INT REFERENCES t_utilisateur(id),

    chromeos_version VARCHAR(100),
    chrome_version VARCHAR(100),

    date_creation TIMESTAMPTZ DEFAULT NOW()
);


-- =========================================================
-- 8. HISTORIQUE DES MISES A JOUR DU DEVICE
-- =========================================================

CREATE TABLE t_device_historique (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),

    id_utilisateur INT REFERENCES t_utilisateur(id),
    id_statut INT REFERENCES t_statut(id),

    org_unit_path VARCHAR(255),
    last_sync TIMESTAMPTZ,

    date_mise_a_jour TIMESTAMPTZ DEFAULT NOW()
);


-- =========================================================
-- 9. DEVICE <-> FILIALE
-- =========================================================

CREATE TABLE t_device_filiale (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),
    id_filiale INT NOT NULL REFERENCES t_filiale(id),

    date_affectation TIMESTAMPTZ DEFAULT NOW(),
    date_fin_affectation TIMESTAMPTZ,

    UNIQUE (id_device, id_filiale, date_affectation)
);


-- =========================================================
-- 10. UTILISATEURS RECENTS D'UN DEVICE
-- =========================================================

CREATE TABLE t_device_utilisateur_recent (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),
    id_utilisateur INT NOT NULL REFERENCES t_utilisateur(id),

    date_observation TIMESTAMPTZ DEFAULT NOW()
);


-- =========================================================
-- 11. HISTORIQUE DES VERSIONS
-- =========================================================

CREATE TABLE t_version_report (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),

    chromeos_version VARCHAR(100),
    chrome_version VARCHAR(100),

    date_observation TIMESTAMPTZ DEFAULT NOW()
);


-- =========================================================
-- 12. TELEMETRY - CPU
-- =========================================================

CREATE TABLE t_cpu_report (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),

    report_time TIMESTAMPTZ NOT NULL,

    cpu_utilisation_pct NUMERIC,
    temperature_max_celsius NUMERIC
);


-- =========================================================
-- 13. TELEMETRY - MEMOIRE
-- =========================================================

CREATE TABLE t_memory_report (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),

    report_time TIMESTAMPTZ NOT NULL,

    ram_libre_bytes BIGINT,
    page_faults BIGINT
);


-- =========================================================
-- 14. TELEMETRY - STOCKAGE
-- =========================================================

CREATE TABLE t_storage_report (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),

    report_time TIMESTAMPTZ NOT NULL,

    disque_libre_bytes BIGINT,
    disque_total_bytes BIGINT,

    available_disk_bytes BIGINT,
    total_disk_bytes BIGINT
);


-- =========================================================
-- 15. TELEMETRY - ETAT DU STOCKAGE / DISQUE
-- =========================================================

CREATE TABLE t_storage_status_report (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),

    report_time TIMESTAMPTZ NOT NULL,

    serial_number VARCHAR(255),
    manufacturer VARCHAR(255),
    modele VARCHAR(255),

    size_bytes BIGINT,
    type VARCHAR(50),

    bytes_read_this_session BIGINT,
    bytes_written_this_session BIGINT,

    read_time_seconds BIGINT,
    write_time_seconds BIGINT,
    io_time_seconds BIGINT,
    discard_time_seconds BIGINT
);


-- =========================================================
-- 16. TELEMETRY - RESEAU
-- =========================================================

CREATE TABLE t_network_report (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),

    report_time TIMESTAMPTZ NOT NULL,

    ip_address VARCHAR(50),
    gateway_ip_address VARCHAR(50),

    connection_type VARCHAR(50),
    connection_state VARCHAR(50),

    vitesse_kbps BIGINT,
    latence_ms NUMERIC
);


-- =========================================================
-- 17. TELEMETRY - DIAGNOSTIC RESEAU
-- =========================================================

CREATE TABLE t_network_diagnostics_report (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),

    report_time TIMESTAMPTZ NOT NULL,

    problem VARCHAR(100),
    latency_seconds NUMERIC
);


-- =========================================================
-- 18. TELEMETRY - BANDE PASSANTE
-- =========================================================

CREATE TABLE t_network_bandwidth_report (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),

    report_time TIMESTAMPTZ NOT NULL,

    download_speed_kbps BIGINT
);


-- =========================================================
-- 19. TELEMETRY - BOOT
-- =========================================================

CREATE TABLE t_boot_report (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),

    report_time TIMESTAMPTZ NOT NULL,

    boot_up_duration_seconds NUMERIC,
    boot_up_time TIMESTAMPTZ,

    shutdown_duration_seconds NUMERIC,
    shutdown_time TIMESTAMPTZ,

    shutdown_reason VARCHAR(100)
);


-- =========================================================
-- 20. TELEMETRY - PERIPHERIQUES
-- =========================================================

CREATE TABLE t_peripherique_report (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),

    report_time TIMESTAMPTZ NOT NULL,

    vendor VARCHAR(255),
    nom VARCHAR(255),

    vid INT,
    pid INT,

    class_id INT,
    subclass_id INT
);


-- =========================================================
-- 21. TELEMETRY - BATTERIE
-- =========================================================

CREATE TABLE t_battery_report (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),

    report_time TIMESTAMPTZ NOT NULL,

    battery_percent NUMERIC,
    battery_status VARCHAR(50)
);


-- =========================================================
-- 22. TELEMETRY - AUDIO
-- =========================================================

CREATE TABLE t_audio_status_report (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),

    report_time TIMESTAMPTZ NOT NULL,

    output_volume INT,
    output_device VARCHAR(255),

    input_gain INT,
    input_device VARCHAR(255)
);


-- =========================================================
-- 23. TELEMETRY - INFORMATIONS GRAPHIQUES
-- =========================================================

CREATE TABLE t_graphics_info (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),

    adapter VARCHAR(500),
    driver_version VARCHAR(100),
    graphics_device_id VARCHAR(100),

    date_observation TIMESTAMPTZ DEFAULT NOW()
);


-- =========================================================
-- 24. TELEMETRY - ETAT GRAPHIQUE
-- =========================================================

CREATE TABLE t_graphics_status_report (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),

    report_time TIMESTAMPTZ NOT NULL,

    display_device_id VARCHAR(100),
    is_internal BOOLEAN,

    resolution_width INT,
    resolution_height INT,

    refresh_rate NUMERIC,

    display_name VARCHAR(255),
    edid_version VARCHAR(50)
);


-- =========================================================
-- 25. TELEMETRY - HEARTBEAT
-- =========================================================

CREATE TABLE t_heartbeat_status_report (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),

    report_time TIMESTAMPTZ NOT NULL,

    state VARCHAR(50)
);


-- =========================================================
-- 26. TYPES D'EVENEMENTS
-- =========================================================

CREATE TABLE t_type_evenement (
    id SERIAL PRIMARY KEY,
    type VARCHAR(100) UNIQUE NOT NULL
);


-- =========================================================
-- 27. EVENEMENTS SUR LES DEVICES
-- =========================================================

CREATE TABLE t_evenement_device (
    id SERIAL PRIMARY KEY,

    id_device INT NOT NULL REFERENCES t_device(id),
    id_type_evenement INT NOT NULL REFERENCES t_type_evenement(id),

    date_evenement TIMESTAMPTZ NOT NULL,

    details JSONB
);


-- =========================================================
-- 28. DETAILS DES MISES A JOUR CHROMEOS
-- =========================================================

CREATE TABLE t_os_update_report (
    id SERIAL PRIMARY KEY,

    id_evenement INT NOT NULL
        REFERENCES t_evenement_device(id),

    last_update_time TIMESTAMPTZ,
    last_update_check_time TIMESTAMPTZ,
    last_reboot_time TIMESTAMPTZ,

    date_observation TIMESTAMPTZ DEFAULT NOW()
);


-- =========================================================
-- 29. IMPRIMANTES
-- =========================================================

CREATE TABLE t_imprimante (
    id SERIAL PRIMARY KEY,

    vid INT,
    pid INT,

    vendor VARCHAR(255),
    nom VARCHAR(255),

    date_premiere_detection TIMESTAMPTZ DEFAULT NOW()
);


-- =========================================================
-- 30. IMPRIMANTE <-> DEVICE
-- =========================================================

CREATE TABLE t_imprimante_device (
    id SERIAL PRIMARY KEY,

    id_imprimante INT NOT NULL REFERENCES t_imprimante(id),
    id_device INT NOT NULL REFERENCES t_device(id),

    premiere_detection TIMESTAMPTZ DEFAULT NOW(),
    derniere_detection TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE (id_imprimante, id_device)
);


-- =========================================================
-- 31. ALERTES
-- =========================================================

CREATE TABLE t_alerte (
    id SERIAL PRIMARY KEY,

    type VARCHAR(100) UNIQUE NOT NULL,
    message TEXT
);


-- =========================================================
-- 32. ALERTE <-> DEVICE
-- =========================================================

CREATE TABLE t_device_alerte (
    id SERIAL PRIMARY KEY,

    id_device INT NOT NULL REFERENCES t_device(id),
    id_alerte INT NOT NULL REFERENCES t_alerte(id),

    date TIMESTAMPTZ DEFAULT NOW(),
    date_resolution TIMESTAMPTZ
);


-- =========================================================
-- 33. CONFIGURATION
-- =========================================================

CREATE TABLE t_configuration (
    id SERIAL PRIMARY KEY,

    type VARCHAR(100) UNIQUE NOT NULL,
    valeur VARCHAR(255) NOT NULL
);


-- =========================================================
-- 34. COMPARAISON
-- =========================================================

CREATE TABLE t_comparaison (
    id SERIAL PRIMARY KEY,

    id_device_a INT NOT NULL REFERENCES t_device(id),
    id_device_b INT NOT NULL REFERENCES t_device(id),

    date_comparaison TIMESTAMPTZ DEFAULT NOW(),

    resultat TEXT,
    commentaires TEXT
);