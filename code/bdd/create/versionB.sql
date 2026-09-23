CREATE TABLE t_user (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    mdp VARCHAR(255) NOT NULL,

);

CREATE TABLE t_customer (
    id SERIAL PRIMARY KEY,
    google_customer_id VARCHAR(100) UNIQUE NOT NULL,
    nom VARCHAR(255),
    email VARCHAR(255)
);

CREATE TABLE t_filiale (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(255) UNIQUE NOT NULL,
    org_unit_path VARCHAR(255),
    id_customer INT REFERENCES t_customer(id)
);

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

CREATE TABLE t_type_appareil (
    id SERIAL PRIMARY KEY,
    type_device VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE t_utilisateur (
    id SERIAL PRIMARY KEY,
    google_user_id VARCHAR(255) UNIQUE,
    email VARCHAR(255) UNIQUE NOT NULL,
    nom VARCHAR(255),
    prenom VARCHAR(255)
);

CREATE TABLE t_filiale_user (
    id SERIAL PRIMARY KEY,
    id_filiale INT NOT NULL REFERENCES t_filiale(id),
    id_user INT NOT NULL REFERENCES t_user(id),
    UNIQUE (id_filiale, id_user)
);

CREATE TABLE t_filiale_utilisateur (
    id SERIAL PRIMARY KEY,
    id_filiale INT NOT NULL REFERENCES t_filiale(id),
    id_utilisateur INT NOT NULL REFERENCES t_utilisateur(id),
    UNIQUE (id_filiale, id_utilisateur)
);

CREATE TABLE t_device (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(255) UNIQUE NOT NULL,
    serial_number VARCHAR(255),
    modele VARCHAR(255),
    id_type_appareil INT REFERENCES t_type_appareil(id),
    annotated_user VARCHAR(255),
    date_creation TIMESTAMP DEFAULT NOW(),
    date_maj TIMESTAMP DEFAULT NOW()
);

CREATE TABLE t_filiale_device (
    id SERIAL PRIMARY KEY,
    id_filiale INT NOT NULL REFERENCES t_filiale(id),
    id_device INT NOT NULL REFERENCES t_device(id),
    date_affectation TIMESTAMP DEFAULT NOW(),
    date_fin_affectation TIMESTAMP,
    UNIQUE (id_filiale, id_device, date_affectation)
);

CREATE TABLE t_device_utilisateur (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),
    id_utilisateur INT NOT NULL REFERENCES t_utilisateur(id),
    date_debut TIMESTAMP,
    date_fin TIMESTAMP
);

CREATE TABLE t_device_utilisateur_recent (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),
    id_utilisateur INT NOT NULL REFERENCES t_utilisateur(id),
    date_observation TIMESTAMP DEFAULT NOW()
);

CREATE TABLE t_statut (
    id SERIAL PRIMARY KEY,
    statut VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE t_device_statut (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),
    id_statut INT NOT NULL REFERENCES t_statut(id),
    date TIMESTAMP DEFAULT NOW()
);

CREATE TABLE t_cpu_report (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),
    report_time TIMESTAMP NOT NULL,
    cpu_utilisation_pct NUMERIC,
    temperature_max_celsius NUMERIC
);

CREATE TABLE t_memory_report (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),
    report_time TIMESTAMP NOT NULL,
    ram_libre_bytes BIGINT,
    page_faults BIGINT
);

CREATE TABLE t_storage_report (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),
    report_time TIMESTAMP NOT NULL,
    disque_libre_bytes BIGINT,
    disque_total_bytes BIGINT
);

CREATE TABLE t_network_report (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),
    report_time TIMESTAMP NOT NULL,
    ip_address VARCHAR(50),
    connection_type VARCHAR(50),
    connection_state VARCHAR(50),
    vitesse_kbps BIGINT,
    latence_ms NUMERIC
);

CREATE TABLE t_boot_report (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),
    report_time TIMESTAMP NOT NULL,
    boot_up_time TIMESTAMP,
    shutdown_time TIMESTAMP,
    shutdown_reason VARCHAR(100)
);

CREATE TABLE t_peripherique_report (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),
    report_time TIMESTAMP NOT NULL,
    vendor VARCHAR(255),
    nom VARCHAR(255),
    vid INT,
    pid INT,
    class_id INT,
    subclass_id INT
);

CREATE TABLE t_type_evenement (
    id SERIAL PRIMARY KEY,
    code VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE t_evenement_device (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),
    id_type_evenement INT REFERENCES t_type_evenement(id),
    date_evenement TIMESTAMP NOT NULL,
    details JSONB
);

CREATE TABLE t_imprimante (
    id SERIAL PRIMARY KEY,
    vid INT,
    pid INT,
    vendor VARCHAR(255),
    nom VARCHAR(255),
    date_premiere_detection TIMESTAMP DEFAULT NOW()
);

CREATE TABLE t_imprimante_device (
    id SERIAL PRIMARY KEY,
    id_imprimante INT NOT NULL REFERENCES t_imprimante(id),
    id_device INT NOT NULL REFERENCES t_device(id),
    premiere_detection TIMESTAMP DEFAULT NOW(),
    derniere_detection TIMESTAMP DEFAULT NOW(),
    UNIQUE (id_imprimante, id_device)
);

CREATE TABLE t_alerte (
    id SERIAL PRIMARY KEY,
    id_device INT REFERENCES t_device(id),
    type VARCHAR(100) NOT NULL,
    gravite VARCHAR(50),
    message TEXT,
    date_creation TIMESTAMP DEFAULT NOW()
);

CREATE TABLE t_alerte_statut (
    id SERIAL PRIMARY KEY,
    id_alerte INT NOT NULL REFERENCES t_alerte(id),
    id_statut INT NOT NULL REFERENCES t_statut(id),
    date TIMESTAMP DEFAULT NOW()
);

CREATE TABLE t_configuration (
    id SERIAL PRIMARY KEY,
    type VARCHAR(100) UNIQUE NOT NULL,
    valeur VARCHAR(255) NOT NULL
);

CREATE TABLE t_comparaison (
    id SERIAL PRIMARY KEY,
    id_device_a INT NOT NULL REFERENCES t_device(id),
    id_device_b INT NOT NULL REFERENCES t_device(id),
    date_comparaison TIMESTAMP DEFAULT NOW(),
    commentaires TEXT
);