CREATE DATABASE gt,
\c gt,

CREATE TABLE t_user (
    id SERIAL PRIMARY KEY ,
    nom VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    mdp VARCHAR(255) NOT NULL
);

CREATE TABLE t_filiale (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(255) UNIQUE NOT NULL,
    org_unit_path VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE t_reseau (
    id SERIAL PRIMARY KEY,
    valeur VARCHAR(255) NOT NULL
);

CREATE TABLE t_statut(
    id SERIAL PRIMARY KEY ,
    nom VARCHAR(255) NOT NULL
);

CREATE TABLE t_reseau_filiale (
    id SERIAL PRIMARY KEY,
    id_reseau INT NOT NULL REFERENCES t_reseau(id),
    id_filiale INT NOT NULL REFERENCES t_filiale(id),
    UNIQUE (id_reseau, id_filiale)
);

CREATE TABLE t_type_appareil (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE t_utilisateur (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE t_filiale_utilisateur (
    id SERIAL PRIMARY KEY,
    id_filiale INT NOT NULL REFERENCES t_filiale(id),
    id_utilisateur INT NOT NULL REFERENCES t_utilisateur(id),
    UNIQUE (id_filiale, id_utilisateur)
);

CREATE TABLE t_cpu (
    id SERIAL PRIMARY KEY,
    cpu_model VARCHAR(250) UNIQUE,
    freq_max_proc BIGINT,
    cpu_architecture VARCHAR(50)
);

CREATE TABLE t_device (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(255) UNIQUE NOT NULL,
    serial_number VARCHAR(255),
    modele VARCHAR(255),
    id_type_appareil INT NOT NULL REFERENCES t_type_appareil(id),
    chromeos_version VARCHAR(100),
    chrome_version VARCHAR(100),
    mac_adress VARCHAR(255),
    ram_total BIGINT,       
    ip_adress VARCHAR(255),
    date_creation TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE t_disk (
    id SERIAL PRIMARY KEY,
    model VARCHAR(250),
    type VARCHAR(250),
    UNIQUE (model, type)
);

CREATE TABLE t_disk_device (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),
    id_disk INT NOT NULL REFERENCES t_disk(id),
    disponible BIGINT,
    total_reel BIGINT,
    disponible_formater VARCHAR(50),
    total_formater VARCHAR(50),
    taille_utiliser BIGINT,
    total_utiliser_formater VARCHAR(50),
    date TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE t_device_statut (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),
    id_statut INT NOT NULL REFERENCES t_statut(id),
    date TIMESTAMPTZ DEFAULT NOW()
);

-- CREATE TABLE t_device_historique (
--     id SERIAL PRIMARY KEY,
--     id_device INT NOT NULL REFERENCES t_device(id),
--     id_utilisateur INT REFERENCES t_utilisateur(id),
--     id_statut INT REFERENCES t_statut(id),
--     org_unit_path VARCHAR(255),
--     last_sync TIMESTAMPTZ,
-- );

CREATE TABLE t_device_utilisateur (
    id SERIAL PRIMARY KEY , 
    id_device INT NOT NULL REFERENCES t_device(id),
    id_utilisateur INT NOT NULL REFERENCES t_utilisateur(id),
    UNIQUE (id_device, id_utilisateur)
);

CREATE TABLE t_device_filiale (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),
    id_filiale INT NOT NULL REFERENCES t_filiale(id),
    UNIQUE (id_device, id_filiale)
);

CREATE TABLE t_device_utilisateur_recent (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),
    id_utilisateur INT NOT NULL REFERENCES t_utilisateur(id),
    date_observation TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE t_type_rapport (
    id SERIAL PRIMARY KEY,
    type VARCHAR(100) UNIQUE NOT NULL,
    cle_api VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE t_rapport_device (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),
    id_type_rapport INT NOT NULL REFERENCES t_type_rapport(id),
    report_time TIMESTAMPTZ NOT NULL,
    donnees JSONB NOT NULL 
    UNIQUE(id_device,id_type_rapport,report_time)
);

-- CREATE TABLE t_version_report (
--     id SERIAL PRIMARY KEY,
--     id_device INT NOT NULL REFERENCES t_device(id),
--     chromeos_version VARCHAR(100),
--     chrome_version VARCHAR(100),
--     date_observation TIMESTAMPTZ DEFAULT NOW()
-- );

CREATE TABLE t_type_evenement (
    id SERIAL PRIMARY KEY,
    type VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE t_evenement_device (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),
    id_type_evenement INT NOT NULL REFERENCES t_type_evenement(id),
    date_evenement TIMESTAMPTZ NOT NULL,
    details JSONB
);

CREATE TABLE t_imprimante (
    id SERIAL PRIMARY KEY,
    vid INT,
    pid INT,
    vendor VARCHAR(255),
    nom VARCHAR(255)
);

CREATE TABLE t_imprimante_device (
    id SERIAL PRIMARY KEY,
    id_imprimante INT NOT NULL REFERENCES t_imprimante(id),
    id_device INT NOT NULL REFERENCES t_device(id),
    date TIMESTAMPTZ DEFAULT NOW()
    UNIQUE (id_imprimante, id_device,date)
);

CREATE TABLE t_imprimante_user(
    id SERIAL PRIMARY KEY , 
    id_imprimante INT NOT NULL REFERENCES t_imprimante(id),
    id_utilisateur INT NOT NULL REFERENCES t_utilisateur(id),
    date TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(id_imprimante,id_utilisateur,date)
);

CREATE TABLE t_alerte (
    id SERIAL PRIMARY KEY,
    type VARCHAR(100) UNIQUE NOT NULL,
    message TEXT
);

CREATE TABLE t_device_alerte (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),
    id_alerte INT NOT NULL REFERENCES t_alerte(id),
    date TIMESTAMPTZ DEFAULT NOW(),
    date_resolution TIMESTAMPTZ
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
    date_reference_a TIMESTAMPTZ,
    date_reference_b TIMESTAMPTZ,
    date_comparaison TIMESTAMPTZ DEFAULT NOW(),
    resultat JSONB,
    commentaires TEXT
);

CREATE TABLE t_device_cpu (
    id SERIAL PRIMARY KEY ,
    id_device INT NOT NULL REFERENCES t_device(id),
    id_cpu INT NOT NULL REFERENCES t_cpu(id),
    date TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE t_user ADD COLUMN vrai_mdp VARCHAR(255)NOT NULL;
ALTER TABLE t_utilisateur DROP COLUMN google_customer_id ;
ALTER TABLE t_device ADD COLUMN mac_adress VARCHAR(255)NOT NULL;
ALTER TABLE t_device ADD COLUMN ip_adress VARCHAR(255) NOT NULL; 
ALTER TABLE t_device ALTER COLUMN ip_adress DROP NOT NULL;
ALTER TABLE t_device ALTER COLUMN mac_adress DROP NOT NULL;
ALTER TABLE t_filiale_utilisateur ADD COLUMN id_utilisateur_recent INT UNIQUE NOT NULL;
ALTER TABLE t_filiale_utilisateur DROP COLUMN id_utilisateur_recent;
ALTER TABLE t_type_rapport ADD COLUMN IF NOT EXISTS cle_api VARCHAR(255);
ALTER TABLE t_device ADD COLUMN ram_total BIGINT, ADD COLUMN disk_total BIGINT
ALTER TABLE t_device DROP COLUMN cpu_model ;
ALTER TABLE t_device DROP COLUMN cpu_max_clock;
ALTER TABLE t_device DROP COLUMN cpu_architecture;
ALTER TABLE t_device ADD COLUMN id_cpu INT REFERENCES t_cpu(id);
ALTER TABLE t_device ALTER COLUMN id_cpu DROP NOT NULL;
ALTER TABLE t_disk_device DROP COLUMN taille_utiliser;
ALTER TABLE t_disk_device ADD COLUMN total_utiliser BIGINT;
ALTER TABLE t_device ALTER COLUMN id_cpu DROP NOT NULL;
ALTER TABLE t_disk_device ALTER COLUMN total_formater TYPE VARCHAR(50);
ALTER TABLE t_disk_device ADD COLUMN disponible_formater VARCHAR(50);
ALTER TABLE t_disk_device ADD COLUMN total_utiliser_formater VARCHAR(50);
ALTER TABLE t_device DROP COLUMN id_cpu ;
alter table t_imprimante_device drop column date_premiere_detection;
alter table t_imprimante_device add column date TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE t_device_historique drop column date_mise_a_jour;
ALTER TABLE t_rapport_device ADD CONSTRAINT uq_rapport_device_type_time UNIQUE (id_device, id_type_rapport, report_time);
ALTER TABLE t_imprimante_device
ALTER TABLE t_imprimante_device ADD CONSTRAINT uq_imprimante_device_date UNIQUE (id_imprimante, id_device, date);
ALTER TABLE t_imprimante_user ADD CONSTRAINT uq_imprimante_user UNIQUE (id_imprimante, id_utilisateur, date);
ALTER TABLE t_imprimante_device DROP CONSTRAINT t_imprimante_device_id_imprimante_id_device_key;
ALTER TABLE t_imprimante_user DROP CONSTRAINT t_imprimante_user_id_imprimante_id_utilisateur_key;