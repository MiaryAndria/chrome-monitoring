-- ============================================================
-- SUPPRESSION DES VIEWS DEVENUES INUTILES
-- À exécuter manuellement par l'utilisateur.
-- Ajouter une ligne quand une VIEW n'est plus utilisée.
-- Ne rien supprimer des autres lignes sans vérifier.
-- ============================================================

-- v_resume_plage_cpu
-- Raison : remplacée par la somme date+heure sur t_device_cpu (C4)
-- Date : 2026-10-19
DROP VIEW IF EXISTS v_resume_plage_cpu;

-- v_resume_plage_ram
-- Raison : remplacée par la somme date+heure sur t_device_ram (C4)
-- Date : 2026-10-19
DROP VIEW IF EXISTS v_resume_plage_ram;
