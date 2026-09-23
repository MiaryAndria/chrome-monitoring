-- ============================================================
-- 1. IDENTITÉ / RÉFÉRENTIEL
-- ============================================================

CREATE TABLE t_customer (
    id SERIAL PRIMARY KEY,
    google_customer_id VARCHAR(50) UNIQUE NOT NULL,
    nom VARCHAR(255),
    email VARCHAR(255)
);

CREATE TABLE t_filiale (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(255) UNIQUE NOT NULL,
    org_unit_id VARCHAR(255),
    id_customer INT REFERENCES t_customer(id)
);

CREATE TABLE t_reseau_filiale (
    id SERIAL PRIMARY KEY,
    id_filiale INT REFERENCES t_filiale(id),
    nom VARCHAR(255),
    valeur VARCHAR(255)
);

CREATE TABLE t_user (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    mdp VARCHAR(255)
);

-- ============================================================
-- 2. APPAREILS CHROMEOS
-- ============================================================

CREATE TABLE t_device (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(255) UNIQUE NOT NULL,
    serial_number VARCHAR(255),
    id_type_appareil INT REFERENCES t_type_appareil (id)
    modele VARCHAR(255),
    id_customer INT REFERENCES t_customer(id),
    id_filiale INT REFERENCES t_filiale(id),
    annotated_user VARCHAR(255),
    statut_admin VARCHAR(50),
    statut_manuel VARCHAR(50),
    date_creation TIMESTAMP DEFAULT NOW(),
    date_maj TIMESTAMP DEFAULT NOW()
);

create TABLE t_device_statut (
    id 
    id_device
    id_statut

);

create table t_device_type_appareil(
    id 
    id_type_appareil
    id_device
);

create table t_device_customer(
    id
    id_device
    id_customer
);

create table t_device_filiale(
    id 
    id_device
    id_filiale
);

create t_user_filiale (
    id 
    id_filiale
    id_user
);

create table reseau (
    id 
    reseau 
);

create table t_reseau_filiale(
    id
    id_reseau
    id_filiale
);


create table t_type_appareil(
    id SERIAL PRIMARY KEY,
    type_device VARCHAR(255),

);

-- ============================================================
-- 3. TÉLÉMÉTRIE — historique, jamais écrasé
-- ============================================================

CREATE TABLE t_cpu_report (
    id SERIAL PRIMARY KEY,
    id_device INT REFERENCES t_device(id),
    report_time TIMESTAMP NOT NULL,
    cpu_utilisation_pct NUMERIC,
    temperature_max_celsius NUMERIC
);

CREATE TABLE t_memory_report (
    id SERIAL PRIMARY KEY,
    id_device INT REFERENCES t_device(id),
    report_time TIMESTAMP NOT NULL,
    ram_libre_bytes BIGINT,
    page_faults BIGINT
);

CREATE TABLE t_storage_report (
    id SERIAL PRIMARY KEY,
    id_device INT REFERENCES t_device(id),
    report_time TIMESTAMP NOT NULL,
    disque_libre_bytes BIGINT,
    disque_total_bytes BIGINT
);

CREATE TABLE t_network_report (
    id SERIAL PRIMARY KEY,
    id_device INT REFERENCES t_device(id),
    report_time TIMESTAMP NOT NULL,
    ip_address VARCHAR(50),
    connection_type VARCHAR(50),
    connection_state VARCHAR(50),
    vitesse_kbps BIGINT,
    latence_ms NUMERIC
);

CREATE TABLE t_boot_report (
    id SERIAL PRIMARY KEY,
    id_device INT REFERENCES t_device(id),
    report_time TIMESTAMP NOT NULL,
    boot_up_time TIMESTAMP,
    shutdown_time TIMESTAMP,
    shutdown_reason VARCHAR(100)
);

CREATE TABLE t_peripherique_report (
    id SERIAL PRIMARY KEY,
    id_device INT REFERENCES t_device(id),
    report_time TIMESTAMP NOT NULL,
    vendor VARCHAR(255),
    nom VARCHAR(255),
    vid INT,
    pid INT,
    class_id INT
);

-- ============================================================
-- 4. ÉVÉNEMENTS
-- ============================================================

CREATE TABLE t_type_evenement (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE t_evenement_device (
    id SERIAL PRIMARY KEY,
    id_device INT REFERENCES t_device(id),
    id_type_evenement INT REFERENCES t_type_evenement(id),
    date_evenement TIMESTAMP NOT NULL,
    details JSONB
);

-- ============================================================
-- 5. ALERTES
-- ============================================================

CREATE TABLE t_alerte (
    id SERIAL PRIMARY KEY,
    id_device INT REFERENCES t_device(id),
    type VARCHAR(50) NOT NULL,
    gravite VARCHAR(20),
    message TEXT,
);

CREATE TABLE t_alerte_status(
    id 
    id_alerte
    id_status
    date
);

-- ============================================================
-- 6. IMPRIMANTES — déduites des peripheralsReport (USB)
-- ============================================================

CREATE TABLE t_imprimante (
    id SERIAL PRIMARY KEY,
    vid INT NOT NULL,
    pid INT NOT NULL,
    vendor VARCHAR(255),
    nom VARCHAR(255),
    id_filiale INT REFERENCES t_filiale(id),
    statut_manuel VARCHAR(50),
    date_premiere_detection TIMESTAMP DEFAULT NOW(),
    UNIQUE (vid, pid)
);

CREATE TABLE t_imprimante_device (
    id SERIAL PRIMARY KEY,
    id_imprimante INT REFERENCES t_imprimante(id),
    id_device INT REFERENCES t_device(id),
    premiere_detection TIMESTAMP DEFAULT NOW(),
    derniere_detection TIMESTAMP DEFAULT NOW(),
    UNIQUE (id_imprimante, id_device)
);

CREATE TABLE t_imprimante_usage (
    id SERIAL PRIMARY KEY,
    id_imprimante INT REFERENCES t_imprimante(id),
    id_device INT REFERENCES t_device(id),
    report_time TIMESTAMP NOT NULL
);

-- ============================================================
-- 7. COMPARAISON
-- ============================================================

CREATE TABLE t_comparaison (
    id SERIAL PRIMARY KEY,
    id_device_a INT REFERENCES t_device(id),
    id_device_b INT REFERENCES t_device(id),
    date_comparaison TIMESTAMP DEFAULT NOW(),
    commentaire TEXT
);

-- ============================================================
-- 8. CONFIGURATION
-- ============================================================

CREATE TABLE t_configuration (
    id SERIAL PRIMARY KEY,
    type VARCHAR(100) UNIQUE NOT NULL,
    valeur VARCHAR(255) NOT NULL
);


CREATE TABLE t_statut (
    id SERIAL PRIMARY KEY ,
    type_statut VARCHAR (255)
);


-- ============================================================
-- UTILISATEURS RÉELS DES APPAREILS (Google Workspace users)
-- ============================================================
-- Modifie t_device pour pointer vers cette table au lieu d'un champ texte libre
ALTER TABLE t_device DROP COLUMN annotated_user;
ALTER TABLE t_device ADD COLUMN id_utilisateur_assigne INT REFERENCES t_utilisateur(id);

-- Historique des utilisateurs récents connectés (recentUsers) — jamais écrasé
CREATE TABLE t_device_utilisateur_recent (
    id SERIAL PRIMARY KEY,
    id_device INT REFERENCES t_device(id),
    id_utilisateur INT REFERENCES t_utilisateur(id),
    date_connexion TIMESTAMP DEFAULT NOW()
);