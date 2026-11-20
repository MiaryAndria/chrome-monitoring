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
        ds.id_statut,
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
        array_agg(DISTINCT u.email) AS emails
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
),
derniere_version AS (
    SELECT DISTINCT ON (v.id_device)
        v.id_device,
        v.chromeos_version
    FROM t_device_version v
    ORDER BY v.id_device, v.date DESC, v.id DESC
)
SELECT
    d.id,
    d.device_id,
    d.serial_number,
    d.modele,
    d.id_type_appareil,
    ta.nom AS type_appareil,
    dv.chromeos_version,
    dv.chromeos_version AS chrome_version,
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
    di.type AS disk_type,
    st.id_statut AS id_status
FROM t_device d
LEFT JOIN t_type_appareil ta ON ta.id = d.id_type_appareil
LEFT JOIN dernier_utilisateur du ON du.id_device = d.id
LEFT JOIN dernier_statut st ON st.id_device = d.id
LEFT JOIN derniere_filiale fi ON fi.id_device = d.id
LEFT JOIN utilisateurs_recents ru ON ru.id_device = d.id
LEFT JOIN dernier_cpu cp ON cp.id_device = d.id
LEFT JOIN dernier_disk di ON di.id_device = d.id
LEFT JOIN derniere_version dv ON dv.id_device = d.id;


-- ------------------------------------------------------------
-- v_evenements_avec_appareil
-- But : exposer les événements avec leur type, l'appareil et
--       la filiale associés, pour des filtres backend
--       (type, filiale, recherche, plage date/heure).
--       id_statut = DERNIER statut (via t_evenement_statut).
-- Colonnes : id, date_evenement, details, type_evenement,
--            id_device, device_id, serial_number, modele,
--            id_filiale, filiale, id_statut
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
    fi.org_unit_path AS filiale,
    (
        SELECT s.id_statut
        FROM t_evenement_statut s
        WHERE s.id_evenement = ed.id
        ORDER BY s.date DESC NULLS LAST, s.id DESC
        LIMIT 1
    ) AS id_statut
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
--            repartition_evenements, total_alerte, alerte_active,
--            alerte_resolue, nb_filiales, nb_utilisateurs_recents,
--            nb_utilisateurs
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
    SELECT d.id AS id_device, ds.id_statut, s.nom
    FROM t_device d
    JOIN LATERAL (
        SELECT ds.id_statut
        FROM t_device_statut ds
        WHERE ds.id_device = d.id
        ORDER BY ds.date DESC, ds.id DESC
        LIMIT 1
    ) ds ON TRUE
    JOIN t_statut s ON s.id = ds.id_statut
),
derniers_statuts_alerte AS (
    SELECT da.id AS id_device_alerte,
           (
               SELECT das.id_statut
               FROM t_device_alerte_statut das
               WHERE das.id_device_alerte = da.id
               ORDER BY das.date DESC NULLS LAST, das.id DESC
               LIMIT 1
           ) AS id_statut,
           (
               SELECT s.nom
               FROM t_device_alerte_statut das
               JOIN t_statut s ON s.id = das.id_statut
               WHERE das.id_device_alerte = da.id
               ORDER BY das.date DESC NULLS LAST, das.id DESC
               LIMIT 1
           ) AS nom
    FROM t_device_alerte da
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
    (SELECT COUNT(*) FROM derniers_statuts WHERE id_statut = 1) AS nb_actifs,
    (SELECT COUNT(*) FROM derniers_statuts
      WHERE id_statut IN (3, 4)) AS nb_indisponibles,
    (SELECT COUNT(*) FROM derniers_statuts WHERE id_statut = 2) AS nb_anomalie,
    (SELECT COUNT(DISTINCT da.id_device)
       FROM t_device_alerte da
      WHERE NOT EXISTS (
          SELECT 1
          FROM t_device_alerte_statut das
          WHERE das.id_device_alerte = da.id AND das.id_statut = 15
      )) AS nb_reparation,
    (SELECT COUNT(*) FROM t_evenement_device) AS nb_crashs,
    (SELECT COUNT(DISTINCT ed.details->>'incident_key')
       FROM t_evenement_device ed) AS nb_incidents,
    (SELECT COUNT(*) FROM t_imprimante) AS nb_imprimantes,
    (SELECT valeur FROM repartition_statuts) AS repartition_statuts,
    (SELECT valeur FROM repartition_types) AS repartition_types,
    (SELECT valeur FROM repartition_evenements) AS repartition_evenements,
    (SELECT COUNT(*) FROM derniers_statuts_alerte ) AS total_alerte,
    (SELECT COUNT(*) FROM derniers_statuts_alerte WHERE id_statut = 1) AS alerte_active,
    (SELECT COUNT(*) FROM derniers_statuts_alerte WHERE id_statut = 15) AS alerte_resolue,
    (SELECT COUNT(*) FROM t_filiale) AS nb_filiales,
    (SELECT COUNT(DISTINCT id_utilisateur) FROM t_device_utilisateur_recent) AS nb_utilisateurs_recents,
    (SELECT COUNT(*) FROM t_utilisateur) AS nb_utilisateurs;

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

-- ------------------------------------------------------------
-- VUES MÉTIER centralisées (étape 6 — refactorisation)
-- Chaque vue encapsule les JOIN / LATERAL / sous-requêtes complexes :
-- le code Python ne fait plus que des SELECT simples vers ces vues.
-- Toutes ces vues doivent être exécutées MANUELLEMENT sur la base
-- (cf. en-tête du fichier) AVANT de déployer le code refactoré.
-- ------------------------------------------------------------

-- ------------------------------------------------------------
-- v_seuil
-- But : exposer chaque seuil avec son type, sa catégorie, son sens,
--       sa borne (limite) et son DERNIER statut (archives incluses).
-- Colonnes : id, id_type_seuil, type, categorie, valeur, date,
--            sens, limite, id_statut
-- Consommateur : repository/seuil/seuil.py
--                → GET /seuil/liste, /liste/page, /{id}, /liste/archiver*
-- Rôle : remplace les LATERAL/dernières lectures de t_seuil_statut
--        codés en Python ; la limite provient de t_type_seuil.limite.
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_seuil AS
SELECT s.id,
       s.id_type_seuil,
       t.type,
       c.categorie,
       s.valeur,
       ds.date,
       t.sens,
       t.limite,
       ds.id_statut
FROM t_seuil s
JOIN t_type_seuil t ON t.id = s.id_type_seuil
JOIN t_categorie_type_seuil c ON c.id = t.id_categorie
LEFT JOIN LATERAL (
    SELECT ss.id_statut, ss.date
    FROM t_seuil_statut ss
    WHERE ss.id_seuil = s.id
    ORDER BY ss.date DESC, ss.id DESC
    LIMIT 1
) ds ON true;

-- ------------------------------------------------------------
-- v_configuration
-- But : exposer chaque configuration avec son type, sa catégorie,
--       sa valeur et son DERNIER statut (archives incluses).
-- Colonnes : id, id_type_configuration, type, categorie, valeur,
--            date, id_statut
-- Consommateur : repository/configuration/configuration.py
--                → GET /configuration/liste, /{id}, /liste/archiver*
-- Rôle : remplace LATERAL + *_COLONNES/*_FROM codés en Python.
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_configuration AS
SELECT c.id,
       c.id_type_configuration,
       t.type,
       cat.categorie,
       c.valeur,
       ds.date,
       ds.id_statut
FROM t_configuration c
JOIN t_type_configuration t ON t.id = c.id_type_configuration
JOIN t_categorie_type_configuration cat ON cat.id = t.id_categorie
LEFT JOIN LATERAL (
    SELECT cs.id_statut, cs.date
    FROM t_configuration_statut cs
    WHERE cs.id_configuration = c.id
    ORDER BY cs.date DESC, cs.id DESC
    LIMIT 1
) ds ON true;

-- ------------------------------------------------------------
-- v_comparaison
-- But : exposer les comparaisons avec le numéro de série des
--       deux appareils comparés.
-- Colonnes : id, id_device_a, id_device_b, id_type_comparaison,
--            date_reference_a, date_reference_b, date_comparaison,
--            resultat, version_a, version_b, device_a, device_b
-- Consommateur : repository/comparaison/comparaison.py
--                → GET /comparaison/liste/page, /{id}
-- Rôle : remplace les 2 LEFT JOIN t_device en Python.
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_comparaison AS
SELECT c.id,
       c.id_device_a,
       c.id_device_b,
       c.id_type_comparaison,
       c.date_reference_a,
       c.date_reference_b,
       c.date_comparaison,
       c.resultat,
       c.version_a,
       c.version_b,
       da.serial_number AS device_a,
       db.serial_number AS device_b
FROM t_comparaison c
LEFT JOIN t_device da ON da.id = c.id_device_a
LEFT JOIN t_device db ON db.id = c.id_device_b;

-- ------------------------------------------------------------
-- v_statut_device
-- But : liste des statuts « device » (ACTIVE, DELINQUENT, DISABLED,
--       DEPROVISIONED).
-- Colonnes : id, nom
-- Consommateur : repository/statut/statut.py (get_liste_statut)
--                → GET /statut/liste
-- Rôle : remplace le ANY(%s) sur IDS_STATUTS_DEVICE.
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_statut_device AS
SELECT id, nom
FROM t_statut
WHERE id IN (1, 2, 3, 4)
ORDER BY id ASC;

-- ------------------------------------------------------------
-- v_user
-- But : exposer chaque utilisateur (compte de connexion) avec son
--       rôle ACTIF (le plus récent de t_user_role) et le libellé.
-- Colonnes : id, nom, email, mdp, id_role, role
-- Consommateur : repository/user/user.py (get_user_by_email,
--                get_user_auth_by_id, get_nom_role_by_user_id,
--                list_users, get_user_by_id, get_user_archived,
--                find_users_paginated, find_users_archived_paginated)
--                → GET /user/*, auth (login)
-- Rôle : encapsule le calcul du rôle actif (dernière ligne de
--        t_user_role) une seule fois ; le code Python ne fait que
--        des SELECT simples vers cette vue.
-- Note : nécessite que t_role contienne les rôles et t_user_role
--        les affectations (cf. alter_user_role.sql).
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_user AS
SELECT u.id,
       u.nom,
       u.email,
       u.mdp,
       (SELECT ur.id_role
        FROM t_user_role ur
        WHERE ur.id_user = u.id
        ORDER BY ur.date DESC, ur.id DESC
        LIMIT 1) AS id_role,
       (SELECT r2.role
        FROM t_user_role ur2
        JOIN t_role r2 ON r2.id = ur2.id_role
        WHERE ur2.id_user = u.id
        ORDER BY ur2.date DESC, ur2.id DESC
        LIMIT 1) AS role
FROM t_user u;

-- ------------------------------------------------------------
-- v_device_alerte
-- But : chaque alerte device enrichie — série, type, utilisateur
--       récent, DERNIER statut (ACTIVE/RESOLUE).
-- Colonnes : id, id_device, serial_number, type, message, date,
--            utilisateur_recent, id_statut
-- Consommateur : repository/alerte/device_alerte.py
--                → GET /alerte/device/page, /liste, /nouvelles, /stats
-- Rôle : remplace les LATERAL + COUNT(*) OVER() en Python ;
--        pagination désormais en COUNT séparé.
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_device_alerte AS
SELECT da.id,
       da.id_device,
       d.serial_number,
       tr.type,
       da.message,
       da.date,
       (
           SELECT u.email
           FROM t_device_utilisateur_recent ur
           JOIN t_utilisateur u ON u.id = ur.id_utilisateur
           WHERE ur.id_device = da.id_device
           ORDER BY ur.date_observation DESC
           LIMIT 1
       ) AS utilisateur_recent,
       (
           SELECT s.id_statut
           FROM t_device_alerte_statut s
           WHERE s.id_device_alerte = da.id
           ORDER BY s.date DESC NULLS LAST, s.id DESC
           LIMIT 1
       ) AS id_statut
FROM t_device_alerte da
JOIN t_device d ON d.id = da.id_device
JOIN t_alerte tr ON tr.id = da.id_alerte;

-- ------------------------------------------------------------
-- v_device_detail
-- But : exposer chaque appareil enrichi — type, utilisateur
--       principal, utilisateur récents, DERNIER statut, filiale,
--       dernier CPU / disque / version.
-- Colonnes : id, device_id, serial_number, modele, id_type_appareil,
--            type_appareil, chromeos_version, chrome_version,
--            mac_adress, ip_adress, date, ram_total, id_utilisateur,
--            utilisateur_email, status, id_status, id_filiale, filiale,
--            utilisateurs_recents, cpu_model, cpu_freq_max,
--            cpu_architecture, disk_total, disk_free, disk_used,
--            disk_model, disk_type
-- Consommateur : repository/devices/devices.py
--                → GET /device/liste, /{id}
-- Rôle : remplace LATERAL + get_liste_device/get_device_by_id ;
--        similaire à v_appareils_filtres mais FAIT POUR le refactor.
-- Note : v_appareils_filtres (existante) et v_device_detail coexistent ;
--        le code refactoré utilise v_device_detail.
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_device_detail AS
SELECT
    d.id,
    d.device_id,
    d.serial_number,
    d.modele,
    d.id_type_appareil,
    ta.nom AS type_appareil,
    v.chromeos_version,
    v.chromeos_version AS chrome_version,
    d.mac_adress,
    d.ip_adress,
    d.date_creation AS date,
    d.ram_total,
    du.id_utilisateur,
    du.email AS utilisateur_email,
    st.nom AS status,
    st.id_statut AS id_status,
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
LEFT JOIN LATERAL (
    SELECT du.id_utilisateur, u.email
    FROM t_device_utilisateur du
    JOIN t_utilisateur u ON u.id = du.id_utilisateur
    WHERE du.id_device = d.id
    ORDER BY du.id ASC
    LIMIT 1
) du ON TRUE
LEFT JOIN LATERAL (
    SELECT ds.id_statut, s.nom
    FROM t_device_statut ds
    JOIN t_statut s ON s.id = ds.id_statut
    WHERE ds.id_device = d.id
    ORDER BY ds.date DESC, ds.id DESC
    LIMIT 1
) st ON TRUE
LEFT JOIN LATERAL (
    SELECT df.id_filiale, f.org_unit_path
    FROM t_device_filiale df
    JOIN t_filiale f ON f.id = df.id_filiale
    WHERE df.id_device = d.id
    ORDER BY df.id ASC
    LIMIT 1
) fi ON TRUE
LEFT JOIN LATERAL (
    SELECT array_agg(DISTINCT u2.email) AS emails
    FROM t_device_utilisateur_recent dur
    JOIN t_utilisateur u2 ON u2.id = dur.id_utilisateur
    WHERE dur.id_device = d.id
) ru ON TRUE
LEFT JOIN LATERAL (
    SELECT c.cpu_model, c.freq_max_proc, c.cpu_architecture
    FROM t_device_cpu dc
    JOIN t_cpu c ON c.id = dc.id_cpu
    WHERE dc.id_device = d.id
    ORDER BY dc.date DESC, dc.id DESC
    LIMIT 1
) cp ON TRUE
LEFT JOIN LATERAL (
    SELECT dd.total_reel, dd.disponible, dd.total_utiliser, dk.model, dk.type
    FROM t_disk_device dd
    JOIN t_disk dk ON dk.id = dd.id_disk
    WHERE dd.id_device = d.id
    ORDER BY dd.date DESC, dd.id DESC
    LIMIT 1
) di ON TRUE
LEFT JOIN LATERAL (
    SELECT dv.chromeos_version
    FROM t_device_version dv
    WHERE dv.id_device = d.id
    ORDER BY dv.date DESC, dv.id DESC
    LIMIT 1
) v ON TRUE;



