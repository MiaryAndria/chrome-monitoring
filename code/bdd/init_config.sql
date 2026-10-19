-- ============================================================
-- INITIALISATION DES CONFIGURATIONS
-- Modules : auto_synch, devices, event, print
-- Fichier : init_configs.sql
-- ============================================================

BEGIN;

INSERT INTO t_configuration (type, valeur)
VALUES
    -- ============ AUTO SYNCHRONISATION ============
    ('SYNC_INTERVALLE_SECONDES',       '120'),
    ('SYNC_PREMIERE_FENETRE_JOURS',    '90'),
    ('SYNC_MARGE_HEURES_JOUR',         '1'),
    ('SYNC_MARGE_HEURES_HISTORIQUE',   '72'),
    ('SYNC_SOURCE',                    'google'),

    -- ============ FUSEAU HORAIRE ============
    ('TZ_OFFSET',                      '3'),

    -- ============ GOOGLE API ============
    ('GOOGLE_CUSTOMER_ID',             'my_customer'),
    ('GOOGLE_RETRY_MAX',               '4'),
    ('GOOGLE_RETRY_BASE_DELAY_S',      '1.0'),
    ('GOOGLE_PAGE_SIZE_DEVICES',           '250'),
    ('GOOGLE_PAGE_SIZE_DIRECTORY',         '100'),
    ('GOOGLE_PAGE_SIZE_TELEMETRY',         '1000'),
    ('GOOGLE_PAGE_SIZE_TELEMETRY_DEVICES', '100'),
    ('GOOGLE_PAGE_SIZE_PRINT_LOGS',        '1000'),

    -- ============ DETECTION DES CRASHS ============
    ('CRASH_BOOT_REPORT_MIN',          '15'),
    ('CRASH_CLUSTER_WINDOW_S',         '300'),
    ('CRASH_CONTEXT_LOOKBACK_H',       '2'),
    ('CRASH_CONTEXT_MINUTES',          '60'),
    ('CRASH_CONTEXT_COUNT',            '5'),
    ('CRASH_REPORT_MAX_AGE_MIN',       '180'),
    ('CRASH_SHORT_GAP_MIN',            '3'),
    ('CRASH_MEDIUM_GAP_MIN',           '60'),
    ('CRASH_CONTEXT_TYPES',            'USB_ADDED,USB_REMOVED,NETWORK_STATE_CHANGE,VPN_CONNECTION_STATE_CHANGE,AUDIO_SEVERE_UNDERRUN'),

    -- ============ DETECTION DES IMPRIMANTES ============
    ('PRINT_CLASS_CODE',               '7'),
    ('PRINT_MAX_DEVICES_PER_USER',     '5'),
    ('PRINT_OLD_PRINT_DAYS',           '60'),
    ('PRINT_MAX_DELTA_HOURS',          '48'),
    ('PRINT_AUDIT_DAYS',               '90'),

    -- Listes de mots-cles
    ('PRINT_SCANNER_KEYWORDS',         'canoscan,lidescan,lide ,lide,scanjet,scansnap'),
    ('PRINT_STRONG_KEYWORDS',          'printer,deskjet,laserjet,officejet,envy,pagewide,pixma,ecotank,workforce,imageclass,mfc-,dcp-,hl-,p-touch,lq-,l3110,l3150,l3250,l3210,l4260,l5290,lexmark,xerox,kyocera,ricoh,zebra,dymo,bixolon,printer-80,usb printer port'),
    ('PRINT_NON_PRINTER_KEYWORDS',     'mouse,keyboard,root hub, hub,camera,webcam,headset,audio,microphone,mic ,storage,disk,flash,mtp,android,phone,galaxy,iphone,touchpad,gamepad,joystick,barcode,reader,ethernet,wireless,bluetooth,receiver,motorola,moto g')

ON CONFLICT (type) DO NOTHING;

-- Associer un statut "creation" a chaque configuration
INSERT INTO t_configuration_statut (id_configuration, id_statut, date)
SELECT c.id, 12, NOW()
FROM t_configuration c
WHERE NOT EXISTS (
    SELECT 1 FROM t_configuration_statut cs WHERE cs.id_configuration = c.id
);

-- Verification
SELECT 
    c.id, c.type, c.valeur,
    LENGTH(c.valeur) AS longueur,
    s.nom AS statut
FROM t_configuration c
LEFT JOIN t_configuration_statut cs ON cs.id_configuration = c.id
LEFT JOIN t_statut s ON s.id = cs.id_statut
ORDER BY c.type;

SELECT COUNT(*) AS total_configs FROM t_configuration;
SELECT COUNT(*) AS total_statuts FROM t_configuration_statut;

COMMIT;