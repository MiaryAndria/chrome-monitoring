INSERT INTO t_user (nom,email,mdp) VALUES('administrateur','gtadmin@gmail.com','Gtadmin','Gtadmin');
INSERT INTO t_statut (id, nom) VALUES
 (1,'ACTIVE'), (2,'DELINQUENT'), (3,'DISABLED'), (4,'DEPROVISIONED'),
 (5,'COMMENCER'), (6,'EN_COURS'), (7,'TERMINER'), (8,'ECHEC'),
 (12,'CREER'), (13,'MODIFIER'), (14,'SUPPRIMER'), (15,'RESOLUE'), (16,'RESTAURER')
ON CONFLICT (id) DO NOTHING;
INSERT INTO t_type_comparaison(type)VALUES('Simple'),('Double');

INSERT INTO t_vendor (vendor)
SELECT DISTINCT i.vendor
FROM t_imprimante i
WHERE i.vendor IS NOT NULL AND i.vendor <> ''
  AND NOT EXISTS (SELECT 1 FROM t_vendor v WHERE v.vendor = i.vendor);

INSERT INTO t_role(role)VALUES('admin'),('lecture');
INSERT INTO t_user(id_role)VALUES(1);
