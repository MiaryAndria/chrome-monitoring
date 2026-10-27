# Normalisation du `vendor` des imprimantes (t_vendor)

## 1. Décision de modélisation

**Recommandation : `id_vendor` directement dans `t_imprimante` (relation 1:N).**

- Un **vendor** (fabricant) possède **plusieurs** imprimantes ; une imprimante a
  **un seul** vendor.
- C'est donc une relation **1:N** : `t_imprimante.id_vendor → t_vendor.id`.
- Une table de jointure `t_vendor_imprimante` ne se justifie que pour une relation
  **N:N** (une imprimante liée à plusieurs vendors) — ce qui n'a pas de sens ici.
  Elle ajouterait une jointure inutile et permettrait des incohérences.

Table cible (déjà existante dans la base) :

```
t_vendor (id, vendor)
```

> Remarque (décision métier, à valider) : ajouter une contrainte
> `UNIQUE (vendor)` sur `t_vendor.vendor` éviterait les doublons de fabricants.

## 2. Pourquoi les deux erreurs

1. `ALTER TABLE t_imprimante DROP COLUMN vendor;`
   → **la VIEW `v_imprimantes_filtrees` dépend de `i.vendor`**. PostgreSQL refuse
   de supprimer une colonne utilisée par une vue. Il faut d'abord **recréer la
   vue** sans référencer `i.vendor` (et non `DROP ... CASCADE`, qui supprimerait
   la vue utilisée par `/imprimante/liste`).

2. `ALTER TABLE t_imprimante ADD COLUMN id_vendor INT NOT NULL ...`
   → la table contient déjà des lignes : une nouvelle colonne `NOT NULL` sans
   valeur par défaut donne `NULL` pour chaque ligne existante → refus.
   Il faut : **ajouter la colonne nullable → remplir → passer en `NOT NULL`**.

## 3. Migration SQL (à exécuter manuellement, dans cet ordre)

```sql
-- 1) Créer la table vendor si elle n'existe pas encore
CREATE TABLE IF NOT EXISTS t_vendor (
    id      SERIAL PRIMARY KEY,
    vendor  VARCHAR NOT NULL
);

-- 2) Alimenter t_vendor avec les vendors distincts de t_imprimante
INSERT INTO t_vendor (vendor)
SELECT DISTINCT i.vendor
FROM t_imprimante i
WHERE i.vendor IS NOT NULL
  AND i.vendor <> ''
  AND NOT EXISTS (SELECT 1 FROM t_vendor v WHERE v.vendor = i.vendor);

-- 3) Ajouter la colonne nullable
ALTER TABLE t_imprimante ADD COLUMN IF NOT EXISTS id_vendor INTEGER;

-- 4) Remplir id_vendor
UPDATE t_imprimante i
SET id_vendor = v.id
FROM t_vendor v
WHERE i.vendor = v.vendor;

-- 5) Sécurité : valeurs restantes NULL (aucune dans l'état actuel)
INSERT INTO t_vendor (vendor)
SELECT 'UNKNOWN'
WHERE NOT EXISTS (SELECT 1 FROM t_vendor WHERE vendor = 'UNKNOWN');

UPDATE t_imprimante
SET id_vendor = (SELECT id FROM t_vendor WHERE vendor = 'UNKNOWN')
WHERE id_vendor IS NULL;

-- 6) Passer en NOT NULL + clé étrangère
ALTER TABLE t_imprimante ALTER COLUMN id_vendor SET NOT NULL;

ALTER TABLE t_imprimante
    ADD CONSTRAINT fk_t_imprimante_vendor
    FOREIGN KEY (id_vendor) REFERENCES t_vendor(id);

-- 7) Recréer la vue SANS dépendre de t_imprimante.vendor
--    (mêmes colonnes/noms/types : id, vid, pid, vendor, nom, derniere_detection)
CREATE OR REPLACE VIEW v_imprimantes_filtrees AS
SELECT
    i.id,
    i.vid,
    i.pid,
    v.vendor,
    i.nom,
    MAX(idv.date) AS derniere_detection
FROM t_imprimante i
LEFT JOIN t_vendor v ON v.id = i.id_vendor
LEFT JOIN t_imprimante_device idv ON idv.id_imprimante = i.id
GROUP BY i.id, i.vid, i.pid, v.vendor, i.nom;

-- 8) Supprimer l'ancienne colonne (la vue ne la référence plus)
ALTER TABLE t_imprimante DROP COLUMN vendor;
```

> Le `CREATE OR REPLACE VIEW` conserve **les mêmes colonnes de sortie**
> (`vendor` reste le nom exposé), donc `find_imprimantes_paginated` continue de
> fonctionner (`WHERE vendor ILIKE ...`).

## 4. Impact côté backend (à adapter après la migration)

La colonne `t_imprimante.vendor` disparaît : tout `SELECT * FROM t_imprimante`
change d'ordre/colonnes. À adapter :

- `repository/imprimante/imprimante.py`
  - `insert_imprimante(...)` : insérer `id_vendor` (résolu via `t_vendor`), plus
    `vendor`.
  - `get_or_create_imprimante(cur, vid, pid, vendor, nom)` : faire un
    `get_or_create_vendor` puis insérer `id_vendor`.
  - `get_liste_imprimante`, `get_imprimante_by_id`, `get_imprimante_by_vid`, etc. :
    joindre `t_vendor` et exposer `vendor` (garder la même forme de tuple/dict).
- `service/imprimante_service.py`
  - `get_imprimante()` lit `r[3]` comme `vendor` → adapter avec la jointure.
  - `get_imprimante_detail()` idem.
- `find_imprimantes_paginated` : **inchangé** (passe par la vue mise à jour).
- `import_service.insert_imprimante` : inchangé (il passe toujours le vendor en
  texte ; la résolution en `id_vendor` se fait dans le repository).

## 5. Vérifications après migration

```sql
-- Plus aucune référence à t_imprimante.vendor
SELECT column_name FROM information_schema.columns
WHERE table_name = 't_imprimante' ORDER BY ordinal_position;

-- La vue expose toujours vendor
SELECT * FROM v_imprimantes_filtrees LIMIT 5;

-- Cohérence
SELECT COUNT(*) FILTER (WHERE id_vendor IS NULL) FROM t_imprimante;
```
