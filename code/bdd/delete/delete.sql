-- -- =====================================================================
-- -- 03_reset.sql : vide les donnees de la base gt et remet les id a 1
-- -- ATTENTION : irreversible. t_user (comptes de connexion) est conserve.
-- -- =====================================================================

-- -- ---------------------------------------------------------------------
-- -- A. RESET COMPLET (donnees + tables de reference), puis reinsertion
-- --    des donnees de base indispensables.
-- --    Toutes les tables sont listees dans une seule commande : TRUNCATE
-- --    accepte alors les cles etrangeres sans CASCADE, et echoue
-- --    clairement si une table oubliee en reference une autre.
-- -- ---------------------------------------------------------------------

-- TRUNCATE TABLE
--     -- historiques et liaisons
--     t_device_alerte_statut,
--     t_device_alerte,
--     t_device_cpu,
--     t_device_filiale,
--     t_device_reseau,
--     t_device_statut,
--     t_device_utilisateur,
--     t_device_utilisateur_recent,
--     t_disk_device,
--     t_rapport_device,
--     t_evenement_device,
--     t_imprimante_device,
--     t_imprimante_user,
--     t_statut_comparaison,
--     t_comparaison,
--     t_filiale_utilisateur,
--     t_reseau_filiale,
--     t_statut_synchronisation,
--     t_synchronisation_historique,
--     t_seuil_statut,
--     t_configuration_statut,
--     -- entites
--     t_device,
--     t_imprimante,
--     t_utilisateur,
--     t_filiale,
--     t_reseau,
--     t_cpu,
--     t_disk,
--     t_configuration,
--     t_seuil,
--     -- reference
--     t_alerte,
--     t_type_evenement,
--     t_type_rapport,
--     t_type_appareil,
--     t_statut
-- RESTART IDENTITY;

-- -- Donnees de base (utilisees par la fonction verifier_stockage)
-- INSERT INTO t_statut (nom) VALUES ('ACTIVE'), ('RESOLUE');
-- INSERT INTO t_alerte (type, message) VALUES ('STOCKAGE', 'Stockage au-dessus du seuil');
-- INSERT INTO t_seuil (cle, valeur) VALUES ('STOCKAGE', 80);   -- en pourcentage


TRUNCATE TABLE
    t_device_alerte_statut,
    t_device_alerte,
    t_device_cpu,
    t_device_filiale,
    t_device_reseau,
    t_device_statut,
    t_device_utilisateur,
    t_device_utilisateur_recent,
    t_disk_device,
    t_rapport_device,
    t_evenement_device,
    t_imprimante_device,
    t_imprimante_user,
    t_statut_comparaison,
    t_comparaison,
    t_filiale_utilisateur,
    t_reseau_filiale,
    t_statut_synchronisation,
    t_synchronisation_historique,
    t_device,
    t_imprimante,
    t_utilisateur,
    t_filiale,
    t_reseau,
    t_cpu,
    t_disk
RESTART IDENTITY;

TRUNCATE TABLE t_configuration_statut,t_configuration RESTART IDENTITY;
-- Supression doublons 
-- WITH doublons AS (
--     SELECT id,
--            ROW_NUMBER() OVER (
--                PARTITION BY id_device, date
--                ORDER BY id
--            ) AS rn
--     FROM t_device_cpu
-- )
-- DELETE FROM t_device_cpu
-- WHERE id IN (
--     SELECT id
--     FROM doublons
--     WHERE rn > 1
-- );

-- WITH doublons AS (
--     SELECT id,
--            ROW_NUMBER() OVER (
--                PARTITION BY id_device, date
--                ORDER BY id
--            ) AS rn
--     FROM t_device_cpu
-- )
-- DELETE FROM t_device_cpu
-- WHERE id IN (
--     SELECT id
--     FROM doublons
--     WHERE rn > 1
-- );