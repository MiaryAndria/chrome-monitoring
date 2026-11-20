-- =====================================================================
-- Migration : rôles des utilisateurs en many-to-many avec historique.
-- Un utilisateur n'a qu'un rôle ACTIF à la fois : c'est la ligne la plus
-- récente de t_user_role pour cet utilisateur. Les lignes précédentes
-- constituent l'historique.
--
-- Remplace la colonne unique t_user.id_role par une table de liaison
-- t_user_role (id_user, id_role, date).
-- =====================================================================

-- 1) Nouvelle table de liaison user → role
CREATE TABLE IF NOT EXISTS t_user_role (
    id          SERIAL PRIMARY KEY,
    id_user     INT NOT NULL REFERENCES t_user(id),
    id_role     INT NOT NULL REFERENCES t_role(id),
    date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (id_user, id_role, date)
);

-- 2) Migration des rôles existants depuis t_user.id_role
INSERT INTO t_user_role (id_user, id_role, date)
SELECT u.id, u.id_role, NOW()
FROM t_user u
WHERE u.id_role IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM t_user_role ur
      WHERE ur.id_user = u.id
  );

-- 3) Suppression de l'ancienne colonne (après vérification de la migration)
ALTER TABLE t_user DROP COLUMN IF EXISTS id_role;