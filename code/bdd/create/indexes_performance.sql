-- ============================================================
-- INDEX DE PERFORMANCE — listes
-- Fichier : indexes_performance.sql
-- Objectif : accelerer les tris et sous-requetes des pages liste
--            (alertes, utilisateurs, stockage, filiales, config/seuil).
-- Idempotent : oui (IF NOT EXISTS)
-- A executer : manuellement -> psql -f ce_fichier
-- ============================================================

BEGIN;

-- ------------------------------------------------------------
-- t_device_alerte : ORDER BY da.date DESC, da.id DESC + filtres date
-- Utilise par : GET /alerte/device/page et /alerte/device/resolue/page
-- Sans lui : tri complet de toutes les alertes a chaque page.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_t_device_alerte_date
    ON t_device_alerte (date DESC, id DESC);

-- ------------------------------------------------------------
-- t_user_statut : dernier statut d'un utilisateur (WHERE + SELECT)
-- Utilise par : GET /user/liste/page et /user/liste/archiver/page
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_t_user_statut_user_date
    ON t_user_statut (id_user, date DESC, id DESC);

-- ------------------------------------------------------------
-- t_disk_device : dernier disque d'un device (CTE dernier_disk)
-- Utilise par : v_appareils_filtres -> GET /device/liste + /filiale/{id}/devices
-- Sans lui : seq scan + tri complet de t_disk_device a chaque page.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_t_disk_device_device_date
    ON t_disk_device (id_device, date DESC, id DESC);

-- ------------------------------------------------------------
-- t_device_utilisateur : premier/dernier utilisateur d'un device
-- Utilise par : v_appareils_filtres (CTE dernier_utilisateur)
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_t_device_utilisateur_device
    ON t_device_utilisateur (id_device, id);

-- ------------------------------------------------------------
-- t_configuration_statut : dernier statut d'une configuration
-- Utilise par : GET /configuration/liste/page (LEFT JOIN LATERAL)
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_t_configuration_statut_config_date
    ON t_configuration_statut (id_configuration, date DESC, id DESC);

-- ------------------------------------------------------------
-- t_seuil_statut : dernier statut d'un seuil
-- Utilise par : GET /seuil/liste/page (LEFT JOIN LATERAL)
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_t_seuil_statut_seuil_date
    ON t_seuil_statut (id_seuil, date DESC, id DESC);

COMMIT;
