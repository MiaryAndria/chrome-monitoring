# Validation du schéma BDD (version propre)

## 1. Cardinalités 1-N / N-N — verdict

**La structure est globalement correcte.** Les relations many-to-many ont bien une
table de jointure avec `UNIQUE`, et les one-to-many utilisent une FK directe.

### N-N (tables de jointure) — correct
| Jointure | Colonnes | UNIQUE |
|---|---|---|
| `t_reseau_filiale` | id_reseau, id_filiale | ✅ |
| `t_filiale_utilisateur` | id_filiale, id_utilisateur | ✅ |
| `t_device_utilisateur` | id_device, id_utilisateur | ✅ |
| `t_device_filiale` | id_device, id_filiale | ✅ |
| `t_device_reseau` | id_device, id_reseau | ✅ (après correction syntaxe) |

### 1-N (FK directe) — correct
- `t_type_appareil` → `t_device`
- `t_device` → (`t_device_statut`, `t_device_cpu`, `t_device_ram`, `t_disk_device`,
  `t_rapport_device`, `t_evenement_device`, `t_imprimante_device`,
  `t_imprimante_user`, `t_device_alerte`, `t_comparaison` ×2)
- `t_utilisateur` → (`t_device_utilisateur`, `t_filiale_utilisateur`,
  `t_device_utilisateur_recent`, `t_imprimante_user`)
- `t_cpu` → `t_device_cpu` ; `t_disk` → `t_disk_device`
- `t_statut` → (`t_device_statut`, `t_configuration_statut`, `t_seuil_statut`,
  `t_statut_synchronisation`, `t_statut_comparaison`, `t_device_alerte_statut`)
- `t_type_rapport` → `t_rapport_device` ; `t_type_evenement` → `t_evenement_device`
- `t_imprimante` → (`t_imprimante_device`, `t_imprimante_user`)
- `t_alerte` → `t_device_alerte` ; `t_device_alerte` → `t_device_alerte_statut`
- `t_seuil` → `t_seuil_statut` ; `t_configuration` → `t_configuration_statut`
- `t_synchronisation_historique` → `t_statut_synchronisation`
- `t_type_comparaison` → `t_comparaison`

---

## 2. Erreurs bloquantes

### 2.1 Syntaxe — virgule manquante (le script ne passe pas)

**`t_device_reseau`** :
```sql
date TIMESTAMPTZ NOT NULL DEFAULT NOW()   -- ❌ virgule manquante
UNIQUE (id_device, id_reseau)
```
Correction :
```sql
CREATE TABLE t_device_reseau(
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),
    id_reseau INT NOT NULL REFERENCES t_reseau(id),
    date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (id_device, id_reseau)
);
```

**`t_seuil_statut`** : même problème.
```sql
CREATE TABLE t_seuil_statut (
    id SERIAL PRIMARY KEY,
    id_seuil INT NOT NULL REFERENCES t_seuil(id),
    id_statut INT NOT NULL REFERENCES t_statut(id),
    date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (id_seuil, id_statut, date)
);
```

### 2.2 `t_rapport_device` — nom de contrainte attendu par le code

Le code fait :
```sql
ON CONFLICT ON CONSTRAINT uq_rapport_device_type_time DO NOTHING
```
(`repository/rapport/rapport_device.py`, `insert_rapport_lot`)

Or la contrainte UNIQUE du DDL n'est **pas nommée** → PostgreSQL lui donne un nom
auto (`t_rapport_device_id_device_id_type_rapport_report_time_key`) → **l'insert
échoue**. Correction :
```sql
CREATE TABLE t_rapport_device (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES t_device(id),
    id_type_rapport INT NOT NULL REFERENCES t_type_rapport(id),
    report_time TIMESTAMPTZ NOT NULL,
    donnees JSONB NOT NULL,
    CONSTRAINT uq_rapport_device_type_time
        UNIQUE (id_device, id_type_rapport, report_time)
);
```

### 2.3 `t_cpu` — UNIQUE incompatible avec le code

Le code fait `ON CONFLICT (cpu_model, cpu_architecture)`
(`repository/cpu/cpu.py`, `insert_or_update_cpu`) et `get_or_create_cpu` cherche
par `(cpu_model, cpu_architecture)`. Or le DDL met `cpu_model UNIQUE` **seul** →
pas de contrainte `(cpu_model, cpu_architecture)` → erreur, et impossible d'avoir
2 architectures pour un même modèle. Correction :
```sql
CREATE TABLE t_cpu (
    id SERIAL PRIMARY KEY,
    cpu_model VARCHAR(250) NOT NULL,
    freq_max_proc BIGINT,
    cpu_architecture VARCHAR(50),
    UNIQUE (cpu_model, cpu_architecture)
);
```

### 2.4 `t_device.date_creation NOT NULL` + valeur possiblement NULL

`insertion_device` fait `date_creation = parse_date_safe(d.get("lastEnrollmentTime"))`
qui peut renvoyer `None`. `insert_device` passe alors explicitement `NULL` →
`NOT NULL` refusé (le device n'est pas inséré). Deux options :
- rendre la colonne nullable : `date_creation TIMESTAMPTZ DEFAULT NOW()`, ou
- garder `NOT NULL` et fallback côté code : `date_creation or datetime.now(timezone.utc)`.

### 2.5 `t_device_filiale` sans colonnes de date

Des fonctions du repository référencent `date_affectation` / `date_fin_affectation`
qui **n'existent pas** dans ce DDL :
- `repository/devices/device_filiale.py` (`get_filiales_by_device`,
  `get_affectation_actuelle_device`, `get_historique_affectation_device`, …),
- `repository/devices/devices.py` (lignes ~368/381/395).

Si ces fonctions sont appelées → erreur SQL. À vérifier / nettoyer (code mort ?),
ou ajouter les colonnes :
```sql
date_affectation     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
date_fin_affectation TIMESTAMPTZ
```

---

## 3. Incohérences avec le code (`ON CONFLICT`)

Contraintes nécessaires et **bien présentes** dans le DDL :

| Code | ON CONFLICT | DDL |
|---|---|---|
| device_utilisateur | (id_device, id_utilisateur) | ✅ |
| ram | (id_device, date) | ✅ |
| device_cpu | (id_device, date) | ✅ |
| disk_device | (id_device, id_disk, date) | ✅ |
| evenement | (id_device, id_type_evenement, date_evenement) | ✅ |
| imprimante_device | (id_imprimante, id_device, date) | ✅ |
| imprimante_user | (id_imprimante, id_utilisateur, date) | ✅ |
| reseau_filiale | (id_reseau, id_filiale) | ✅ |
| filiale | (org_unit_path) | ✅ |
| disk (insert_or_update) | (model, type) | ✅ |
| type_evenement | (type) | ✅ |
| type_rapport | (type) | ✅ |
| **rapport_device (lot)** | **CONSTRAINT nommée** | ❌ à nommer |
| **cpu (insert_or_update)** | **(cpu_model, cpu_architecture)** | ❌ à corriger |

---

## 4. Points de modélisation à trancher

1. **`t_imprimante` garde `vendor` et n'a pas `id_vendor`** alors que `t_vendor`
   existe. Décider :
   - soit normaliser (`id_vendor INT NOT NULL REFERENCES t_vendor(id)`, retirer
     `vendor`, adapter la vue + le code) — cf. doc 14 ;
   - soit garder `vendor` denormalisé et **supprimer `t_vendor`** (inutilisé).
   `UNIQUE (vid, pid, vendor, nom)` : avec `vendor` nullable, les NULL ne sont pas
   dédupliqués ; et le code cherche par `(vid, pid)` seul → préférer
   `UNIQUE (vid, pid)` (ou `(vid, pid, nom)`).

2. **`t_configuration UNIQUE(type)`** : empêche plusieurs lignes pour un même type.
   Or le flux archive/restore conserve la ligne (statut 14/16). Si un jour on crée
   une nouvelle conf du même type, l'insert échouera. Décision métier.

3. **`t_seuil`** : `cle ... UNIQUE` en colonne **et** `UNIQUE(cle)` en table →
   doublon inutile.

4. **`t_device_cpu.id_cpu NOT NULL`** : si le CPU n'est pas résolu
   (`default_cpu_id = None`), l'insert échoue (capté par try/except et ignoré).
   Envisager nullable, ou un CPU de secours `UNKNOWN`.

5. **`t_device_statut` / `t_device_utilisateur_recent`** : pas d'UNIQUE → historiques
   qui grossissent (voulu ?). À confirmer.

6. **`t_imprimante` insert sans `ON CONFLICT`** : avec un UNIQUE, un doublon lève
   une erreur ; `get_or_create_imprimante` protège via `(vid, pid)` — à garder
   cohérent avec le choix du point 1.

---

## 5. Checklist de validation

- [ ] Ajouter les 2 virgules (`t_device_reseau`, `t_seuil_statut`).
- [ ] Nommer la contrainte `uq_rapport_device_type_time` sur `t_rapport_device`.
- [ ] Remplacer `cpu_model UNIQUE` par `UNIQUE (cpu_model, cpu_architecture)`.
- [ ] Décider `t_device.date_creation` (nullable ou fallback code).
- [ ] Trancher `t_device_filiale` (colonnes de date ou nettoyage du code mort).
- [ ] Trancher `vendor` (normaliser via `t_vendor` ou retirer `t_vendor`).
- [ ] Trancher `t_configuration UNIQUE(type)`.
- [ ] Supprimer le doublon `UNIQUE(cle)` de `t_seuil`.
- [ ] Vérifier `t_device_cpu.id_cpu NOT NULL`.
