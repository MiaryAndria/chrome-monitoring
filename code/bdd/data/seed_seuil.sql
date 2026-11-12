-- ============================================================
-- SEED SEUIL
-- Fichier : seed_seuil.sql
-- Objectif :
--   1. Creer les categories de seuil manquantes
--   2. Creer les types de seuil manquants (metadonnees d'alerte)
--   3. Creer un seuil uniquement si le type n'a encore aucune valeur
--   4. Associer le statut CREER aux seuils sans statut
-- Idempotent : oui (ON CONFLICT / NOT EXISTS)
-- A executer : psql -f seed_seuil.sql
-- ============================================================

\set ON_ERROR_STOP on

BEGIN;

-- 1) Categories de seuil
INSERT INTO t_categorie_type_seuil (categorie) VALUES
    ('RESSOURCE'),
    ('STOCKAGE'),
    ('BATTERIE'),
    ('IMPRESSION'),
    ('EVENEMENT')
ON CONFLICT (categorie) DO NOTHING;

-- 2) Types de seuil (uniquement s'ils n'existent pas deja)
INSERT INTO t_type_seuil (type, id_categorie, sens, type_alerte, metrique, message, limite)
SELECT v.type, c.id, v.sens, v.type_alerte, v.metrique, v.message, v.limite
FROM (VALUES
    ('seuil_capteur_cpu',      'RESSOURCE',  '>', 'ALERTE_TEMPERATURE',    'temperature',    'Température capteur CPU supérieure au seuil',  150),
    ('seuil_utilisation_ram',  'RESSOURCE',  '>', 'ALERTE_RAM',            'ram',            'Utilisation RAM supérieure au seuil',          100),
    ('seuil_utilisation_cpu',  'RESSOURCE',  '>', 'ALERTE_CPU',            'cpu',            'Utilisation CPU supérieure au seuil',          100),
    ('seuil_stockage',         'STOCKAGE',   '>', 'ALERTE_STOCKAGE',       'stockage',       'Utilisation du stockage supérieure au seuil',  100),
    ('seuil_sante_batterie',   'BATTERIE',   '<', 'ALERTE_SANTE_BATTERIE', 'sante_batterie', 'Santé de la batterie inférieure au seuil',     100),
    ('seuil_batterie',         'BATTERIE',   '<', 'ALERTE_BATTERIE',       'batterie',       'Niveau de batterie inférieur au seuil',        100),
    ('seuil_tache_print',      'IMPRESSION', '>', 'ALERTE_TACHE_PRINT',    'tache_print',    'Nombre de tâches d''impression supérieur au seuil', NULL::int),
    ('seuil_evenements',       'EVENEMENT',  '>', 'ALERTE_EVENEMENTS',     'evenements',     'Nombre d''événements supérieur au seuil',      NULL::int)
) AS v(type, categorie, sens, type_alerte, metrique, message, limite)
JOIN t_categorie_type_seuil c ON c.categorie = v.categorie
ON CONFLICT (type) DO NOTHING;

-- 2b) Remplir la limite des types deja existants
UPDATE t_type_seuil t
SET limite = v.limite
FROM (VALUES
    ('seuil_capteur_cpu',      150),
    ('seuil_utilisation_ram',  100),
    ('seuil_utilisation_cpu',  100),
    ('seuil_stockage',         100),
    ('seuil_sante_batterie',   100),
    ('seuil_batterie',         100),
    ('seuil_tache_print',      NULL::int),
    ('seuil_evenements',       NULL::int)
) AS v(type, limite)
WHERE t.type = v.type
  AND t.limite IS NULL;

-- 3) Valeur de seuil : une seule par type, insert seulement si absente
INSERT INTO t_seuil (id_type_seuil, valeur)
SELECT t.id, v.valeur
FROM (VALUES
    ('seuil_capteur_cpu',      75),
    ('seuil_utilisation_ram',  80),
    ('seuil_utilisation_cpu',  75),
    ('seuil_stockage',         80),
    ('seuil_sante_batterie',   60),
    ('seuil_batterie',         20),
    ('seuil_tache_print',       5),
    ('seuil_evenements',       10)
) AS v(type, valeur)
JOIN t_type_seuil t ON t.type = v.type
WHERE NOT EXISTS (
    SELECT 1
    FROM t_seuil s
    WHERE s.id_type_seuil = t.id
);

-- 4) Statut CREER pour chaque seuil qui n'a aucun statut
INSERT INTO t_seuil_statut (id_seuil, id_statut, date)
SELECT s.id, st.id, NOW()
FROM t_seuil s
JOIN t_statut st ON st.nom = 'CREER'
WHERE NOT EXISTS (
    SELECT 1
    FROM t_seuil_statut ss
    WHERE ss.id_seuil = s.id
);

-- 5) Resynchroniser les sequences
DO $$
DECLARE seq text;
BEGIN
    seq := pg_get_serial_sequence('t_categorie_type_seuil', 'id');
    IF seq IS NOT NULL THEN
        PERFORM setval(seq, GREATEST((SELECT COALESCE(MAX(id), 1) FROM t_categorie_type_seuil), 1));
    END IF;

    seq := pg_get_serial_sequence('t_type_seuil', 'id');
    IF seq IS NOT NULL THEN
        PERFORM setval(seq, GREATEST((SELECT COALESCE(MAX(id), 1) FROM t_type_seuil), 1));
    END IF;

    seq := pg_get_serial_sequence('t_seuil', 'id');
    IF seq IS NOT NULL THEN
        PERFORM setval(seq, GREATEST((SELECT COALESCE(MAX(id), 1) FROM t_seuil), 1));
    END IF;

    seq := pg_get_serial_sequence('t_seuil_statut', 'id');
    IF seq IS NOT NULL THEN
        PERFORM setval(seq, GREATEST((SELECT COALESCE(MAX(id), 1) FROM t_seuil_statut), 1));
    END IF;
END $$;

COMMIT;

-- Verification
SELECT t.type, s.valeur
FROM t_seuil s
JOIN t_type_seuil t ON t.id = s.id_type_seuil
ORDER BY t.type;
