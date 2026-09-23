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
    id_utilisateur INT NOT NULL REFERENCES t_utilisateur(id)
    UNIQUE (id_filiale, id_utilisateur)
);

CREATE TABLE t_statut (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE t_device (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(255) UNIQUE NOT NULL,
    serial_number VARCHAR(255),
    modele VARCHAR(255),
    id_type_appareil INT REFERENCES t_type_appareil(id),
    id_utilisateur INT REFERENCES t_utilisateur(id),
    chromeos_version VARCHAR(100),
    chrome_version VARCHAR(100),
    mac_adress VARCHAR(255),
    ip_adress VARCHAR(255),
    date_creation TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE t_device_statut (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),
    id_statut INT NOT NULL REFERENCES t_statut(id),
    date TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE t_device_historique (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),
    id_utilisateur INT REFERENCES t_utilisateur(id),
    id_statut INT REFERENCES t_statut(id),
    org_unit_path VARCHAR(255),
    last_sync TIMESTAMPTZ,
    date_mise_a_jour TIMESTAMPTZ DEFAULT NOW()
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
    type VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE t_rapport_device (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),
    id_type_rapport INT NOT NULL REFERENCES t_type_rapport(id),
    report_time TIMESTAMPTZ NOT NULL,
    donnees JSONB NOT NULL
);

CREATE TABLE t_version_report (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),
    chromeos_version VARCHAR(100),
    chrome_version VARCHAR(100),
    date_observation TIMESTAMPTZ DEFAULT NOW()
);

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
    nom VARCHAR(255),
    date_premiere_detection TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE t_imprimante_device (
    id SERIAL PRIMARY KEY,
    id_imprimante INT NOT NULL REFERENCES t_imprimante(id),
    id_device INT NOT NULL REFERENCES t_device(id),
    premiere_detection TIMESTAMPTZ DEFAULT NOW(),
    derniere_detection TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (id_imprimante, id_device)
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

ALTER TABLE t_user ADD COLUMN vrai_mdp VARCHAR(255)NOT NULL;
ALTER TABLE t_utilisateur DROP COLUMN google_customer_id ;
ALTER TABLE t_device ADD COLUMN mac_adress VARCHAR(255)NOT NULL;
ALTER TABLE t_device ADD COLUMN ip_adress VARCHAR(255) NOT NULL; 
ALTER TABLE t_device ALTER COLUMN ip_adress DROP NOT NULL;
ALTER TABLE t_device ALTER COLUMN mac_adress DROP NOT NULL;
ALTER TABLE t_filiale_utilisateur ADD COLUMN id_utilisateur_recent INT UNIQUE NOT NULL;
ALTER TABLE t_filiale_utilisateur DROP COLUMN id_utilisateur_recent;