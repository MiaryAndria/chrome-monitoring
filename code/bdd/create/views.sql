-- ============================================================
-- VIEWS — Monitoring ChromeOS & Imprimantes
-- Source unique des VIEWS du projet.
--
-- ⚠️ À exécuter MANUELLEMENT par l'utilisateur sur la base
--    PostgreSQL. L'agent IA ne crée jamais les VIEWS.
-- ============================================================

-- ------------------------------------------------------------
-- v_appareils_filtres
-- But : exposer la liste des appareils avec statut, filiale,
--       utilisateur, CPU et disque déjà résolus, pour des
--       filtres et une pagination 100 % backend.
-- Colonnes : id, device_id, serial_number, modele,
--            id_type_appareil, type_appareil, chromeos_version,
--            chrome_version, mac_adress, ip_adress, date,
--            ram_total, id_utilisateur, utilisateur_email,
--            status, id_filiale, filiale, utilisateurs_recents,
--            cpu_model, cpu_freq_max, cpu_architecture,
--            disk_total, disk_free, disk_used, disk_model,
--            disk_type
-- Utilisée par : AJUSTEMENT 3 (filtres backend + pagination)
--                AJUSTEMENT 12 (filtres date)
--                C1 (performance pagination : agrégats globaux)
-- Consommateur : repository/devices/devices.py (find_devices_paginated)
--                → GET /device/liste, GET /filiale/{id}/devices
-- Rôle : une ligne par device avec son dernier statut, sa filiale, son
--        utilisateur principal, ses utilisateurs récents, son dernier
--        CPU et son dernier disque.
-- Pourquoi une VIEW : évite le N+1 et les LATERAL par device ; chaque
--        "dernier ..." est calculé une seule fois pour tout le parc.
-- Explication détaillée : doc/md/bdd.md
-- À exécuter dans code/bdd/views.sql puis sur la base.
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_appareils_filtres AS
WITH dernier_statut AS (
    SELECT DISTINCT ON (ds.id_device)
        ds.id_device,
        s.nom
    FROM t_device_statut ds
    JOIN t_statut s ON s.id = ds.id_statut
    ORDER BY ds.id_device, ds.date DESC, ds.id DESC
),
dernier_utilisateur AS (
    SELECT DISTINCT ON (du.id_device)
        du.id_device,
        du.id_utilisateur,
        u.email
    FROM t_device_utilisateur du
    JOIN t_utilisateur u ON u.id = du.id_utilisateur
    ORDER BY du.id_device, du.id ASC
),
utilisateurs_recents AS (
    SELECT
        dur.id_device,
        array_agg(u.email ORDER BY dur.date_observation DESC) AS emails
    FROM t_device_utilisateur_recent dur
    JOIN t_utilisateur u ON u.id = dur.id_utilisateur
    GROUP BY dur.id_device
),
derniere_filiale AS (
    SELECT DISTINCT ON (df.id_device)
        df.id_device,
        f.id AS id_filiale,
        f.org_unit_path
    FROM t_device_filiale df
    JOIN t_filiale f ON f.id = df.id_filiale
    ORDER BY df.id_device, df.id ASC
),
dernier_cpu AS (
    SELECT DISTINCT ON (dc.id_device)
        dc.id_device,
        c.cpu_model,
        c.freq_max_proc,
        c.cpu_architecture
    FROM t_device_cpu dc
    JOIN t_cpu c ON c.id = dc.id_cpu
    ORDER BY dc.id_device, dc.date DESC, dc.id DESC
),
dernier_disk AS (
    SELECT DISTINCT ON (dd.id_device)
        dd.id_device,
        dd.total_reel,
        dd.disponible,
        dd.total_utiliser,
        dk.model,
        dk.type
    FROM t_disk_device dd
    JOIN t_disk dk ON dk.id = dd.id_disk
    ORDER BY dd.id_device, dd.date DESC, dd.id DESC
)
SELECT
    d.id,
    d.device_id,
    d.serial_number,
    d.modele,
    d.id_type_appareil,
    ta.nom AS type_appareil,
    d.chromeos_version,
    d.chrome_version,
    d.mac_adress,
    d.ip_adress,
    d.date_creation AS date,
    d.ram_total,
    du.id_utilisateur,
    du.email AS utilisateur_email,
    st.nom AS status,
    fi.id_filiale,
    fi.org_unit_path AS filiale,
    ru.emails AS utilisateurs_recents,
    cp.cpu_model,
    cp.freq_max_proc AS cpu_freq_max,
    cp.cpu_architecture,
    di.total_reel AS disk_total,
    di.disponible AS disk_free,
    di.total_utiliser AS disk_used,
    di.model AS disk_model,
    di.type AS disk_type
FROM t_device d
LEFT JOIN t_type_appareil ta ON ta.id = d.id_type_appareil
LEFT JOIN dernier_utilisateur du ON du.id_device = d.id
LEFT JOIN dernier_statut st ON st.id_device = d.id
LEFT JOIN derniere_filiale fi ON fi.id_device = d.id
LEFT JOIN utilisateurs_recents ru ON ru.id_device = d.id
LEFT JOIN dernier_cpu cp ON cp.id_device = d.id
LEFT JOIN dernier_disk di ON di.id_device = d.id;

-- ------------------------------------------------------------
-- v_evenements_avec_appareil
-- But : exposer les événements avec leur type, l'appareil et
--       la filiale associés, pour des filtres backend
--       (type, filiale, recherche, plage date/heure).
-- Colonnes : id, date_evenement, details, type_evenement,
--            id_device, device_id, serial_number, modele,
--            id_filiale, filiale
-- Utilisée par : AJUSTEMENT 3 (filtres backend + pagination)
--                AJUSTEMENT 12 (filtres date + heure)
--                C1 (performance pagination : agrégat global)
-- Consommateur : repository/evenement/evenement_device.py
--                (find_evenements_paginated) → GET /evenement/liste
-- Rôle : une ligne par événement avec son type, son appareil et sa
--        filiale, pour filtrer/paginer côté backend.
-- Pourquoi une VIEW : résout la filiale une seule fois (DISTINCT ON)
--        au lieu de la recalculer pour chaque événement.
-- Explication détaillée : doc/md/bdd.md
-- À exécuter dans code/bdd/views.sql puis sur la base.
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_evenements_avec_appareil AS
WITH derniere_filiale AS (
    SELECT DISTINCT ON (df.id_device)
        df.id_device,
        f.id AS id_filiale,
        f.org_unit_path
    FROM t_device_filiale df
    JOIN t_filiale f ON f.id = df.id_filiale
    ORDER BY df.id_device, df.id ASC
)
SELECT
    ed.id,
    ed.date_evenement,
    ed.details,
    te.type AS type_evenement,
    d.id AS id_device,
    d.device_id,
    d.serial_number,
    d.modele,
    fi.id_filiale,
    fi.org_unit_path AS filiale
FROM t_evenement_device ed
LEFT JOIN t_type_evenement te ON te.id = ed.id_type_evenement
LEFT JOIN t_device d ON d.id = ed.id_device
LEFT JOIN derniere_filiale fi ON fi.id_device = d.id;

-- ------------------------------------------------------------
-- v_tableau_de_bord_resume
-- But : indicateurs agrégés du tableau de bord en une seule ligne
--       (un seul appel API, cache côté service).
-- Colonnes : nb_total_appareils, nb_actifs, nb_indisponibles,
--            nb_anomalie, nb_reparation, nb_crashs,
--            nb_incidents, nb_imprimantes,
--            repartition_statuts, repartition_types,
--            repartition_evenements
-- Mapping métier :
--   actifs        = dernier statut ACTIVE
--   indisponibles = dernier statut DISABLED ou DEPROVISIONED
--   anomalie      = dernier statut DELINQUENT
--   reparation    = devices ayant au moins une alerte non RESOLUE
--   crashs        = nombre de lignes t_evenement_device
--   incidents     = nombre d'incident_key distincts
-- Utilisée par : AJUSTEMENT 8 (dashboard rapide)
-- Consommateur : repository/dashboard/dashboard.py (get_summary)
--                → GET /dashboard/summary (cache dashboard:summary)
-- Rôle : une seule ligne contenant tous les indicateurs du dashboard
--        (totaux, statuts, crashs, incidents, imprimantes, répartitions).
-- Pourquoi une VIEW : le dashboard est chargé en UN seul appel API
--        au lieu de plusieurs requêtes/endpoints.
-- Explication détaillée : doc/md/bdd.md
-- À exécuter dans code/bdd/views.sql puis sur la base.
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_tableau_de_bord_resume AS
WITH derniers_statuts AS (
    SELECT DISTINCT ON (ds.id_device)
        ds.id_device,
        s.nom
    FROM t_device_statut ds
    JOIN t_statut s ON s.id = ds.id_statut
    ORDER BY ds.id_device, ds.date DESC, ds.id DESC
),
repartition_statuts AS (
    SELECT COALESCE(jsonb_object_agg(nom, nb), '{}'::jsonb) AS valeur
    FROM (
        SELECT nom, COUNT(*) AS nb
        FROM derniers_statuts
        WHERE nom IN ('ACTIVE', 'DELINQUENT', 'DISABLED', 'DEPROVISIONED')
        GROUP BY nom
    ) t
),
repartition_types AS (
    SELECT COALESCE(jsonb_object_agg(nom, nb), '{}'::jsonb) AS valeur
    FROM (
        SELECT ta.nom, COUNT(*) AS nb
        FROM t_device d
        JOIN t_type_appareil ta ON ta.id = d.id_type_appareil
        GROUP BY ta.nom
    ) t
),
repartition_evenements AS (
    SELECT COALESCE(jsonb_object_agg(type, nb), '{}'::jsonb) AS valeur
    FROM (
        SELECT te.type, COUNT(*) AS nb
        FROM t_evenement_device ed
        JOIN t_type_evenement te ON te.id = ed.id_type_evenement
        GROUP BY te.type
    ) t
)
SELECT
    (SELECT COUNT(*) FROM t_device) AS nb_total_appareils,
    (SELECT COUNT(*) FROM derniers_statuts WHERE nom = 'ACTIVE') AS nb_actifs,
    (SELECT COUNT(*) FROM derniers_statuts
      WHERE nom IN ('DISABLED', 'DEPROVISIONED')) AS nb_indisponibles,
    (SELECT COUNT(*) FROM derniers_statuts WHERE nom = 'DELINQUENT') AS nb_anomalie,
    (SELECT COUNT(DISTINCT da.id_device)
       FROM t_device_alerte da
      WHERE NOT EXISTS (
          SELECT 1
          FROM t_device_alerte_statut das
          JOIN t_statut s ON s.id = das.id_statut
          WHERE das.id_device_alerte = da.id AND s.nom = 'RESOLUE'
      )) AS nb_reparation,
    (SELECT COUNT(*) FROM t_evenement_device) AS nb_crashs,
    (SELECT COUNT(DISTINCT ed.details->>'incident_key')
       FROM t_evenement_device ed) AS nb_incidents,
    (SELECT COUNT(*) FROM t_imprimante) AS nb_imprimantes,
    (SELECT valeur FROM repartition_statuts) AS repartition_statuts,
    (SELECT valeur FROM repartition_types) AS repartition_types,
    (SELECT valeur FROM repartition_evenements) AS repartition_evenements;

-- ------------------------------------------------------------
-- v_imprimantes_filtrees
-- But : exposer les imprimantes avec leur dernière date de
--       détection, pour les filtres date + heure backend.
-- Colonnes : id, vid, pid, vendor, nom, derniere_detection
-- Utilisée par : AJUSTEMENT 12 (filtres date + heure)
-- Consommateur : repository/imprimante/imprimante.py
--                (find_imprimantes_paginated) → GET /imprimante/liste
-- Rôle : une ligne par imprimante avec sa dernière date de détection.
-- Pourquoi une VIEW : la date est portée par t_imprimante_device (1-N) ;
--        la VIEW agrège cette relation une seule fois pour permettre
--        la recherche, le filtre date+heure et la pagination.
-- Explication détaillée : doc/md/bdd.md
-- À exécuter dans code/bdd/views.sql puis sur la base.
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_imprimantes_filtrees AS
SELECT i.id, i.vid, i.pid, v.vendor, i.nom,
       MAX(idv.date) AS derniere_detection
FROM t_imprimante i
LEFT JOIN t_vendor v ON v.id = i.id_vendor
LEFT JOIN t_imprimante_device idv ON idv.id_imprimante = i.id
GROUP BY i.id, i.vid, i.pid, v.vendor, i.nom;
