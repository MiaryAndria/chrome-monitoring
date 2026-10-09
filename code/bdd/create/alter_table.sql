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
ALTER TABLE t_configuration ADD COLUMN date TIMESTAMPTZ NOT NULL DEFAULT now();
ALTER TABLE t_configuration DROP CONSTRAINT t_configuration_type_key;
ALTER TABLE t_synchronisation_historique DROP COLUMN message_erreur;
ALTER TABLE t_synchronisation_historique ADD COLUMN message TEXT DEFAULT '';
ALTER TABLE t_synchronisation_historique ALTER COLUMN date_fin DROP NOT NULL;
ALTER TABLE t_synchronisation_historique ALTER COLUMN date_debut SET NOT NULL;
UPDATE t_synchronisation_historique SET date_debut = date_fin;
ALTER TABLE t_synchronisation_historique
    ADD COLUMN fenetre_debut timestamptz,
    ADD COLUMN fenetre_fin   timestamptz;