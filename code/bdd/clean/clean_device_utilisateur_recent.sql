-- ============================================================
-- Nettoyage de t_device_utilisateur_recent
-- Objectif :
--   1. Garder une seule ligne par couple (id_device, id_utilisateur)
--   2. Ajouter la contrainte UNIQUE qui empeche les futurs doublons
--
-- A executer sur la BASE SERVEUR, backend arrete de preference.
-- Idempotent : si la contrainte existe deja, elle n'est pas recreee.
--
-- Usage :
--   psql -h <HOST> -p 5432 -U <USER> -d <DB> -v ON_ERROR_STOP=1 \
--        -f clean_device_utilisateur_recent.sql
-- ============================================================

\set ON_ERROR_STOP on

-- Sauvegarde optionnelle (decommenter si besoin d'un filet de securite)
-- CREATE TABLE t_device_utilisateur_recent_backup AS
-- SELECT * FROM t_device_utilisateur_recent;

BEGIN;

-- Evite de bloquer indefiniment si une session tient la table
SET LOCAL lock_timeout = '30s';

CREATE TEMP TABLE tmp_dur ON COMMIT DROP AS
SELECT id_device,
       id_utilisateur,
       COALESCE(MAX(date_observation), NOW()) AS date_observation
FROM t_device_utilisateur_recent
GROUP BY id_device, id_utilisateur;

TRUNCATE TABLE t_device_utilisateur_recent;

INSERT INTO t_device_utilisateur_recent (id_device, id_utilisateur, date_observation)
SELECT id_device, id_utilisateur, date_observation
FROM tmp_dur;

-- Contrainte creee seulement si elle n'existe pas deja
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'uq_device_utilisateur_recent'
          AND conrelid = 't_device_utilisateur_recent'::regclass
    ) THEN
        ALTER TABLE t_device_utilisateur_recent
        ADD CONSTRAINT uq_device_utilisateur_recent
        UNIQUE (id_device, id_utilisateur);
    END IF;
END
$$;

COMMIT;

ANALYZE t_device_utilisateur_recent;

-- Verification
SELECT COUNT(*) AS lignes FROM t_device_utilisateur_recent;
SELECT COUNT(*) AS groupes_dupliques FROM (
    SELECT id_device, id_utilisateur
    FROM t_device_utilisateur_recent
    GROUP BY id_device, id_utilisateur
    HAVING COUNT(*) > 1
) x;
SELECT conname, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conrelid = 't_device_utilisateur_recent'::regclass
  AND contype = 'u';
