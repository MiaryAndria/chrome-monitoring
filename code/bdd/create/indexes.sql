-- ============================================================
-- INDEX — pagination
-- À exécuter MANUELLEMENT par l'utilisateur.
-- L'agent IA ne crée jamais les index.
-- Explication détaillée : doc/md/first_ajustement/bdd.md
--
-- Note : idx_t_device_reseau_device a été retiré de ce fichier car
-- il est redondant avec uq_device_reseau UNIQUE (id_device, id_reseau).
-- Voir code/bdd/drop_indexes.sql.
-- ============================================================

-- ------------------------------------------------------------
-- idx_t_device_statut_device_date
-- Table      : t_device_statut
-- Colonnes   : (id_device, date DESC, id DESC)
-- Rôle       : trouver le DERNIER statut d'un device sans trier les
--              ~87 000 lignes de t_device_statut.
-- Accélère   : CTE "dernier_statut" de v_appareils_filtres et
--              "derniers_statuts" de v_tableau_de_bord_resume.
-- Sans lui   : DISTINCT ON + ORDER BY date DESC déclenche un tri complet
--              (cause majeure de l'ancienne pagination à ~16 s).
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_t_device_statut_device_date
    ON t_device_statut (id_device, date DESC, id DESC);

-- ------------------------------------------------------------
-- idx_t_device_utilisateur_recent_device_date
-- Table      : t_device_utilisateur_recent
-- Colonnes   : (id_device, date_observation DESC)
-- Rôle       : agréger les emails récents par device dans l'ordre
--              chronologique.
-- Accélère   : CTE "utilisateurs_recents"
--              (array_agg ... ORDER BY date_observation DESC) de
--              v_appareils_filtres.
-- Sans lui   : agrégation avec tri complet des ~154 000 lignes.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_t_device_utilisateur_recent_device_date
    ON t_device_utilisateur_recent (id_device, date_observation DESC);

-- ------------------------------------------------------------
-- idx_t_device_date_creation
-- Table      : t_device
-- Colonnes   : (date_creation DESC)
-- Rôle       : accélérer les bornes de date sur la création du device.
-- Accélère   : GET /device/liste?datetime_from=&datetime_to=
--              (colonne "date" de v_appareils_filtres).
-- Sans lui   : parcours complet de t_device pour filtrer la plage.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_t_device_date_creation
    ON t_device (date_creation DESC);

-- ------------------------------------------------------------
-- idx_t_device_filiale_filiale
-- Table      : t_device_filiale
-- Colonnes   : (id_filiale, id_device)
-- Rôle       : lister les devices d'une filiale sans passer par l'index
--              existant (id_device, id_filiale) dont la 1re colonne est
--              id_device.
-- Accélère   : GET /filiale/{id}/devices, filtre id_filiale de
--              GET /device/liste.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_t_device_filiale_filiale
    ON t_device_filiale (id_filiale, id_device);

-- ------------------------------------------------------------
-- idx_t_evenement_device_date
-- Table      : t_evenement_device
-- Colonnes   : (date_evenement DESC, id DESC)
-- Rôle       : trier les événements par date décroissante et filtrer
--              une plage date+heure sans tri complet.
-- Accélère   : ORDER BY date_evenement DESC, id DESC et
--              datetime_from/datetime_to de GET /evenement/liste.
-- Sans lui   : tri de tous les événements à chaque page (5 500+ lignes
--              actuellement, en croissance).
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_t_evenement_device_date
    ON t_evenement_device (date_evenement DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_device_alerte_statut_device
    ON t_device_alerte_statut (id_device_alerte, date DESC, id DESC);