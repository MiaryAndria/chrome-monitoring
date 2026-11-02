-- ============================================================
-- MOTEUR D'ALERTES — configuration + seuils
-- Fichier    : init_config_alerte.sql
-- Objectif   : 1) creer la cle de configuration de la fenetre (jours)
--                 du seuil d'evenements (lue par le moteur d'alertes)
--              2) creer (optionnel) les seuils manquants
-- Consommateur: service/alerte_service.py (_executer_moteur)
-- Idempotent : oui (ON CONFLICT / NOT EXISTS)
-- A executer : une fois, manuellement  ->  psql -f ce_fichier
-- ============================================================

BEGIN;

-- 1) Cle de configuration : fenetre (jours) du seuil d'evenements
INSERT INTO t_type_configuration (type, id_categorie)
SELECT 'ALERTE_EVENEMENTS_FENETRE_JOURS', c.id
FROM t_categorie_type_configuration c
WHERE c.categorie = 'SYSTEME'
ON CONFLICT (type) DO NOTHING;

INSERT INTO t_configuration (id_type_configuration, valeur)
SELECT t.id, '7'
FROM t_type_configuration t
WHERE t.type = 'ALERTE_EVENEMENTS_FENETRE_JOURS'
ON CONFLICT (id_type_configuration) DO NOTHING;

INSERT INTO t_configuration_statut (id_configuration, id_statut, date)
SELECT c.id, s.id, NOW()
FROM t_configuration c
JOIN t_type_configuration t ON t.id = c.id_type_configuration
CROSS JOIN t_statut s
WHERE t.type = 'ALERTE_EVENEMENTS_FENETRE_JOURS' AND s.nom = 'CREER'
  AND NOT EXISTS (SELECT 1 FROM t_configuration_statut cs WHERE cs.id_configuration = c.id);

-- 2) OPTIONNEL : creer les seuils manquants (valeurs a ajuster)
INSERT INTO t_seuil (id_type_seuil, valeur)
SELECT t.id, v.valeur
FROM (VALUES
    ('seuil_stockage', 80),
    ('seuil_sante_batterie', 60),
    ('seuil_evenements', 10)
) AS v(type, valeur)
JOIN t_type_seuil t ON t.type = v.type
ON CONFLICT (id_type_seuil) DO NOTHING;

INSERT INTO t_seuil_statut (id_seuil, id_statut, date)
SELECT s.id, st.id, NOW()
FROM t_seuil s
CROSS JOIN t_statut st
WHERE st.nom = 'CREER'
  AND NOT EXISTS (SELECT 1 FROM t_seuil_statut ss WHERE ss.id_seuil = s.id);

-- Verification
SELECT t.type, c.valeur
FROM t_configuration c
JOIN t_type_configuration t ON t.id = c.id_type_configuration
WHERE t.type = 'ALERTE_EVENEMENTS_FENETRE_JOURS';

SELECT t.type, s.valeur
FROM t_seuil s
JOIN t_type_seuil t ON t.id = s.id_type_seuil
ORDER BY t.type;

COMMIT;
