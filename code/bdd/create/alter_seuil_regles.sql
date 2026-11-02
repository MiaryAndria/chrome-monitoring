-- ============================================================
-- REGLES D'ALERTE EN BASE — t_type_seuil
-- Fichier      : alter_seuil_regles.sql
-- Objectif     : rendre modifiables en base le SENS de comparaison (> / <),
--                le TYPE d'alerte, la METRIQUE et le MESSAGE de chaque seuil,
--                pour qu'il n'y ait PLUS de signe de comparaison en dur dans le code.
-- Consommateur : service/alerte_service.py (_executer_moteur)
--                via repository/seuil/seuil.py::get_regles_seuil
-- Idempotent   : oui (ADD COLUMN IF NOT EXISTS + UPDATE)
-- A executer   : une fois, manuellement -> psql -f ce_fichier
-- ============================================================

BEGIN;

ALTER TABLE t_type_seuil
    ADD COLUMN IF NOT EXISTS sens VARCHAR(1) NOT NULL DEFAULT '>',
    ADD COLUMN IF NOT EXISTS type_alerte VARCHAR(100),
    ADD COLUMN IF NOT EXISTS metrique VARCHAR(50),
    ADD COLUMN IF NOT EXISTS message TEXT;

UPDATE t_type_seuil SET sens='>', type_alerte='ALERTE_CPU',            metrique='cpu',            message='Utilisation CPU supérieure au seuil'             WHERE type='seuil_utilisation_cpu';
UPDATE t_type_seuil SET sens='>', type_alerte='ALERTE_RAM',            metrique='ram',            message='Utilisation RAM supérieure au seuil'             WHERE type='seuil_utilisation_ram';
UPDATE t_type_seuil SET sens='>', type_alerte='ALERTE_TEMPERATURE',    metrique='temperature',    message='Température capteur CPU supérieure au seuil'     WHERE type='seuil_capteur_cpu';
UPDATE t_type_seuil SET sens='>', type_alerte='ALERTE_STOCKAGE',       metrique='stockage',       message='Utilisation du stockage supérieure au seuil'     WHERE type='seuil_stockage';
UPDATE t_type_seuil SET sens='<', type_alerte='ALERTE_SANTE_BATTERIE', metrique='sante_batterie', message='Santé de la batterie inférieure au seuil'       WHERE type='seuil_sante_batterie';
UPDATE t_type_seuil SET sens='<', type_alerte='ALERTE_BATTERIE',       metrique='batterie',       message='Niveau de batterie inférieur au seuil'           WHERE type='seuil_batterie';
UPDATE t_type_seuil SET sens='>', type_alerte='ALERTE_TACHE_PRINT',    metrique='tache_print',    message='Nombre de tâches d''impression supérieur au seuil' WHERE type='seuil_tache_print';
UPDATE t_type_seuil SET sens='>', type_alerte='ALERTE_EVENEMENTS',     metrique='evenements',     message='Nombre d''événements supérieur au seuil'         WHERE type='seuil_evenements';

-- Verification
SELECT type, sens, type_alerte, metrique, message
FROM t_type_seuil
ORDER BY id;

COMMIT;
