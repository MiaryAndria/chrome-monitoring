-- ============================================================
-- SUPPRESSION DES INDEX DEVENUS INUTILES
-- À exécuter MANUELLEMENT par l'utilisateur.
-- ============================================================

-- idx_t_device_reseau_device
-- Raison : redondant avec uq_device_reseau UNIQUE (id_device, id_reseau),
--          dont la 1re colonne est id_device. Cet index unique couvre
--          déjà WHERE id_device = ... et WHERE id_device = ... AND
--          id_reseau = ... (pré-check get_by_device_and_reseau).
-- Date : 2026-10-19
DROP INDEX IF EXISTS idx_t_device_reseau_device;
