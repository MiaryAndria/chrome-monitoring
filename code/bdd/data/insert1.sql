INSERT INTO t_user (nom,email,mdp) VALUES('administrateur','gtadmin@gmail.com','Gtadmin','Gtadmin');
INSERT INTO t_statut(nom)VALUES('COMMENCER');
INSERT INTO t_statut(nom)VALUES('EN_COURS');
INSERT INTO t_statut(nom)VALUES('TERMINER');
INSERT INTO t_statut (nom) VALUES ('ECHEC');
INSERT INTO t_statut (nom) VALUES ('CREER'),('MODIFIER'),('SUPPRIMER'), ('RESOLUE');
INSERT INTO t_statut(nom)VALUES('RESTAURER')
INSERT INTO t_type_comparaison(type)VALUES('Simple'),('Double');

INSERT INTO t_vendor (vendor)
SELECT DISTINCT i.vendor
FROM t_imprimante i
WHERE i.vendor IS NOT NULL AND i.vendor <> ''
  AND NOT EXISTS (SELECT 1 FROM t_vendor v WHERE v.vendor = i.vendor);