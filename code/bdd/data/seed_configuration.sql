-- ============================================================
-- SEED CONFIGURATION (ids explicites)
-- Objectif : recreer t_categorie_type_configuration, t_type_configuration,
--            t_configuration et les statuts CREER associes.
-- Idempotent : oui (ON CONFLICT DO NOTHING)
-- Ids bases sur la base actuelle.
-- ============================================================

BEGIN;

-- 1) Categories
INSERT INTO t_categorie_type_configuration (id, categorie) VALUES
    (1, 'SYNCHRONISATION'),
    (2, 'SYSTEME'),
    (3, 'GOOGLE_API'),
    (4, 'CRASH'),
    (5, 'IMPRESSION')
ON CONFLICT DO NOTHING;

-- 2) Types de configuration (id -> type)
INSERT INTO t_type_configuration (id, type, id_categorie) VALUES
    (1,  'SYNC_SOURCE',                      1),
    (2,  'SYNC_MARGE_HEURES_HISTORIQUE',     1),
    (3,  'SYNC_MARGE_HEURES_JOUR',           1),
    (4,  'SYNC_PREMIERE_FENETRE_JOURS',      1),
    (5,  'SYNC_INTERVALLE_SECONDES',         1),
    (6,  'TZ_OFFSET',                        2),
    (7,  'GOOGLE_PAGE_SIZE_PRINT_LOGS',      3),
    (8,  'GOOGLE_PAGE_SIZE_TELEMETRY_DEVICES', 3),
    (9,  'GOOGLE_PAGE_SIZE_TELEMETRY',       3),
    (10, 'GOOGLE_PAGE_SIZE_DIRECTORY',       3),
    (11, 'GOOGLE_PAGE_SIZE_DEVICES',         3),
    (12, 'GOOGLE_RETRY_BASE_DELAY_S',        3),
    (13, 'GOOGLE_RETRY_MAX',                 3),
    (14, 'GOOGLE_CUSTOMER_ID',               3),
    (15, 'CRASH_CONTEXT_TYPES',              4),
    (16, 'CRASH_MEDIUM_GAP_MIN',             4),
    (17, 'CRASH_SHORT_GAP_MIN',              4),
    (18, 'CRASH_REPORT_MAX_AGE_MIN',         4),
    (19, 'CRASH_CONTEXT_COUNT',              4),
    (20, 'CRASH_CONTEXT_MINUTES',            4),
    (21, 'CRASH_CONTEXT_LOOKBACK_H',         4),
    (22, 'CRASH_CLUSTER_WINDOW_S',           4),
    (23, 'CRASH_BOOT_REPORT_MIN',            4),
    (24, 'PRINT_NON_PRINTER_KEYWORDS',       5),
    (25, 'PRINT_STRONG_KEYWORDS',            5),
    (26, 'PRINT_SCANNER_KEYWORDS',           5),
    (27, 'PRINT_AUDIT_DAYS',                 5),
    (28, 'PRINT_MAX_DELTA_HOURS',            5),
    (29, 'PRINT_OLD_PRINT_DAYS',             5),
    (30, 'PRINT_MAX_DEVICES_PER_USER',       5),
    (31, 'PRINT_CLASS_CODE',                 5),
    (32, 'ALERTE_EVENEMENTS_FENETRE_JOURS',  2),
    (33, 'CONFIGURATION_SUPPRESSION',        2)
ON CONFLICT DO NOTHING;

-- 3) Configurations (id -> id_type_configuration, valeur)
INSERT INTO t_configuration (id, id_type_configuration, valeur) VALUES
    (1,  5,  '120'),
    (2,  4,  '90'),
    (3,  3,  '1'),
    (4,  2,  '72'),
    (5,  1,  'google'),
    (6,  6,  '3'),
    (7,  14, 'my_customer'),
    (8,  13, '4'),
    (9,  12, '1.0'),
    (10, 11, '250'),
    (11, 10, '100'),
    (12, 9,  '1000'),
    (13, 8,  '100'),
    (14, 7,  '1000'),
    (15, 23, '15'),
    (16, 22, '300'),
    (17, 21, '2'),
    (18, 20, '60'),
    (19, 19, '5'),
    (20, 18, '180'),
    (21, 17, '3'),
    (22, 16, '60'),
    (23, 15, 'USB_ADDED,USB_REMOVED,NETWORK_STATE_CHANGE,VPN_CONNECTION_STATE_CHANGE,AUDIO_SEVERE_UNDERRUN'),
    (24, 31, '7'),
    (25, 30, '5'),
    (26, 29, '60'),
    (27, 28, '48'),
    (28, 27, '90'),
    (29, 26, 'canoscan,lidescan,lide ,lide,scanjet,scansnap'),
    (30, 25, 'printer,deskjet,laserjet,officejet,envy,pagewide,pixma,ecotank,workforce,imageclass,mfc-,dcp-,hl-,p-touch,lq-,l3110,l3150,l3250,l3210,l4260,l5290,lexmark,xerox,kyocera,ricoh,zebra,dymo,bixolon,printer-80,usb printer port'),
    (31, 24, 'mouse,keyboard,root hub, hub,camera,webcam,headset,audio,microphone,mic ,storage,disk,flash,mtp,android,phone,galaxy,iphone,touchpad,gamepad,joystick,barcode,reader,ethernet,wireless,bluetooth,receiver,motorola,moto g'),
    (34, 32, '7'),
    (35, 33, '30')
ON CONFLICT DO NOTHING;

-- 4) Statut CREER (id 12) pour chaque configuration sans statut
INSERT INTO t_configuration_statut (id_configuration, id_statut, date)
SELECT c.id, 12, NOW()
FROM t_configuration c
WHERE NOT EXISTS (
    SELECT 1
    FROM t_configuration_statut cs
    WHERE cs.id_configuration = c.id
);

-- 5) Resynchroniser les sequences
DO $$
DECLARE seq text;
BEGIN
    seq := pg_get_serial_sequence('t_categorie_type_configuration', 'id');
    IF seq IS NOT NULL THEN
        PERFORM setval(seq, GREATEST((SELECT COALESCE(MAX(id), 1) FROM t_categorie_type_configuration), 1));
    END IF;

    seq := pg_get_serial_sequence('t_type_configuration', 'id');
    IF seq IS NOT NULL THEN
        PERFORM setval(seq, GREATEST((SELECT COALESCE(MAX(id), 1) FROM t_type_configuration), 1));
    END IF;

    seq := pg_get_serial_sequence('t_configuration', 'id');
    IF seq IS NOT NULL THEN
        PERFORM setval(seq, GREATEST((SELECT COALESCE(MAX(id), 1) FROM t_configuration), 1));
    END IF;
END $$;

COMMIT;
