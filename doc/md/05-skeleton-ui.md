# AJUSTEMENT 5 — Skeleton UI

## 1. Contexte

Guide agent, §3 AJUSTEMENT 5. Objectif : remplacer les spinners de
chargement par des **squelettes** (placeholders) afin d'éviter les
sauts de mise en page et de n'afficher un squelette que sur les zones
non encore chargées.

## 2. Fichiers existants vérifiés

- [x] Aucun composant `Skeleton` existant
- [x] `components/` contient : `EmptyState`, `ExportModal`,
      `GenericTable`, `MouseSpotlight`, `Navbar`, `PageLayout`, `Sidebar`
- [x] Spinners recensés :
      `dashboard.jsx`, `device/liste.jsx`, `device/detail_device.jsx`,
      `filiale/liste.jsx`, `filiale/liste_device.jsx`,
      `event/liste.jsx`, `imprimante/liste.jsx`,
      `imprimante/detailImprimante.jsx`, `configuration/liste.jsx`,
      `configuration/archived.jsx`

## 3. Décision : fichiers/fonctions identifiés

- Base réutilisable : `components/Skeleton.jsx`.
- Squelettes dédiés demandés par le guide : `DeviceListSkeleton`,
  `EventListSkeleton`, `PrinterListSkeleton`, `DashboardSkeleton`,
  `CpuRamChartSkeleton`.
- Squelettes génériques ajoutés pour les pages non listées par le
  guide : `TableSkeleton` (configurations, détail imprimante) et
  `CardGridSkeleton` (liste des filiales).

## 4. Fichiers créés / modifiés

| Fichier | Nature |
|---|---|
| `components/Skeleton.jsx` | créé (base `animate-pulse`) |
| `components/skeletons/DeviceListSkeleton.jsx` | créé (grid + table) |
| `components/skeletons/EventListSkeleton.jsx` | créé |
| `components/skeletons/PrinterListSkeleton.jsx` | créé |
| `components/skeletons/DashboardSkeleton.jsx` | créé |
| `components/skeletons/CpuRamChartSkeleton.jsx` | créé |
| `components/skeletons/TableSkeleton.jsx` | créé |
| `components/skeletons/CardGridSkeleton.jsx` | créé |
| `page/dashboard.jsx` | spinner → `DashboardSkeleton` |
| `page/device/liste.jsx` | spinner → `DeviceListSkeleton` |
| `page/device/detail_device.jsx` | page + onglets → `Skeleton` / `CpuRamChartSkeleton` |
| `page/filiale/liste.jsx` | spinner → `CardGridSkeleton` |
| `page/filiale/liste_device.jsx` | spinner → `DeviceListSkeleton` |
| `page/event/liste.jsx` | spinner → `EventListSkeleton` |
| `page/imprimante/liste.jsx` | spinner → `PrinterListSkeleton` |
| `page/imprimante/detailImprimante.jsx` | spinner → `Skeleton` + `TableSkeleton` |
| `page/configuration/liste.jsx` | spinner → `TableSkeleton` |
| `page/configuration/archived.jsx` | spinner → `TableSkeleton` |

## 5. ⚠️ Views à créer — À exécuter manuellement par l'utilisateur

**Aucune nouvelle VIEW.** Rappel : `v_appareils_filtres` et
`v_evenements_avec_appareil` (AJUSTEMENT 3) restent à créer.

## 6. Spécifications

- `Skeleton` : bloc `div` avec `animate-pulse`, `bg-white/5`,
  `rounded-xl`, `aria-hidden="true"`, surchargeable via `className` et
  `style`.
- Les squelettes épousent la structure réelle (cartes devices/events/
  imprimantes, lignes de tableau, cartes du dashboard, panneau + barres
  du graphique CPU/RAM).
- Un squelette n'est affiché que si la zone n'a **aucune donnée** :
  conditions `loading && items.length === 0` (pas de remplacement des
  données déjà affichées).
- Cas du détail device : le squelette d'onglet n'apparaît que si les
  données de l'onglet sont absentes (`tabLoading && ongletNonCharge`).
- Le spinner plein écran de la Sidebar (synchronisation/réinitialisation)
  est conservé : c'est un indicateur de progression d'une action
  longue, pas une zone de contenu en chargement.

## 7. Critères d'acceptation

- [x] Composant `Skeleton` réutilisable
- [x] Les 5 squelettes dédiés existent
- [x] Tous les spinners de chargement de contenu sont remplacés
- [x] Squelette visible uniquement sur les zones non chargées
- [x] Build frontend OK

## 8. Tests réalisés

| Test | Résultat |
|---|---|
| Recherche `loading-infinity` dans `src/` | 0 occurrence |
| Recherche `animate-spin` dans `src/` | uniquement Sidebar (action sync/reset) |
| `npm run build` | OK (2564 modules, 1,64 s) |

Aucune vérification BDD nécessaire pour cet ajustement (UI uniquement).

## 9. Risques / régressions

- Purement visuel ; aucune signature d'API modifiée.
- Les squelettes utilisent les classes existantes (`device-card`,
  `telemetry-panel`, `stat-card`) pour rester alignés sur la grille.
- `CpuRamChartSkeleton` accepte une hauteur relative via `style` sur
  `Skeleton`.

## 10. Respect §2.4

Les composants auxiliaires (`DeviceCardSkeleton`, etc.) sont déclarés au
niveau module, jamais imbriqués dans un autre composant. Aucune closure
ni lambda complexe côté backend (ajustement frontend uniquement).
