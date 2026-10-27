-- ============================================================
-- INITIALISATION DES STATUTS DU CATALOGUE D'ALERTE
-- Objectif   : chaque type d'alerte (t_alerte) doit avoir au moins
--              une ligne de cycle de vie dans t_alerte_statut.
-- Contexte   : les types ALERTE_CPU / ALERTE_RAM / ALERTE_TEMPERATURE
--              ont ete crees par le moteur SANS ligne de statut (ancien
--              code), or la liste filtre sur le dernier statut.
-- Consommateur: repository/alerte/alerte.py (get_liste_alerte)
-- Statut pose : CREER (id resolve par nom, jamais code en dur)
-- Idempotent : oui (NOT EXISTS) -> sans effet si deja renseigne
-- A executer : une fois, manuellement  ->  psql -f ce_fichier
-- ============================================================

BEGIN;

INSERT INTO t_alerte_statut (id_alerte, id_statut, date)
SELECT a.id, s.id, NOW()
FROM t_alerte a
CROSS JOIN t_statut s
WHERE s.nom = 'CREER'
  AND NOT EXISTS (
      SELECT 1 FROM t_alerte_statut st WHERE st.id_alerte = a.id
  );

-- Verification
SELECT a.id, a.type, s.nom AS statut, st.date
FROM t_alerte a
JOIN t_alerte_statut st ON st.id_alerte = a.id
JOIN t_statut s ON s.id = st.id_statut
ORDER BY a.id;

COMMIT;
