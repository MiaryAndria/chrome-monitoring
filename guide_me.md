# Guide et Plan d'Action (TODO List) - Chrome Monitoring

Ce document est un guide pas-à-pas pour terminer la réalisation de la plateforme de monitoring ChromeOS, basé sur le cahier des charges, votre schéma de base de données, et l'estimation fournie.

**État actuel :**
- ✅ Installation et configuration de base terminées.
- ✅ Liste des filiales (Backend & Frontend) terminée.
- ✅ Liste des devices par filiale (Backend & Frontend) terminée.
- ✅ Connexion API Google de base (récupération devices/télémétrie) implémentée.

---

## 1. Finaliser le Dashboard (Indicateurs & Statistiques Globales)
*Estimation restante : ~1h*

L'objectif est d'afficher les indicateurs synthétiques sur la page d'accueil (`dashboard.jsx`).

### Backend (Python/FastAPI)
- [x] Créer une route `GET /dashboard/stats` dans un nouveau contrôleur (ex: `statistiques_controller.py`).
- [x] Créer le service associé pour exécuter des requêtes SQL (via psycopg2) afin de compter :
  - Le nombre total d'appareils (`t_device`).
  - Le nombre par type (Chromebook vs Chromebox) via `t_type_appareil`.
  - Le nombre d'imprimantes (`t_imprimante`).
  - Le nombre d'appareils avec un statut spécifique (Actifs, Indisponibles, En réparation, Anomalies) via `t_device_statut` et `t_statut`.

### Frontend (React/Vite)
- [x] Mettre à jour `frontend/src/page/dashboard.jsx`.
- [x] Créer un composant pour afficher ces indicateurs sous forme de "Cards" (Cartes de statistiques).
- [x] Appeler la nouvelle route API `GET /dashboard/stats` via `axios`.

---

## 2. Page Liste Globale des Matériels (ChromeBook / ChromeBox)
*Estimation : ~1,5h*

Une page pour voir tous les matériels, sans passer par les filiales, avec filtres avancés.

### Backend
- [ ] Ajouter une fonction dans `device_service.py` pour récupérer tous les appareils avec des filtres optionnels (type, statut, date).
- [ ] S'assurer que la route `GET /device/liste` (déjà existante) gère bien ces filtres optionnels (via les query parameters de FastAPI).

### Frontend
- [ ] Finaliser/Améliorer `frontend/src/page/device/liste.jsx`.
- [ ] Ajouter une barre de recherche (par `serial_number`, `mac_adress`, ou email de l'utilisateur).
- [ ] Ajouter des listes déroulantes pour filtrer par type (Chromebook/Chromebox) et par statut.
- [ ] Assurer la pagination si la liste est longue.

---

## 3. Page Détail d'un Appareil (ChromeBook / ChromeBox)
*Estimation : ~6h*

C'est une page critique qui consolide toutes les informations d'un seul appareil.

### Backend
- [ ] Compléter `getDeviceDetail(id)` dans `device_service.py` pour récupérer (via des jointures SQL) :
  - Les informations générales (`t_device`, `t_utilisateur`).
  - L'état actuel et l'historique des statuts (`t_device_statut`, `t_device_historique`).
  - Les données de télémétrie récentes (extraites de `t_rapport_device` si stockées là).
  - L'historique des événements/crashs (`t_evenement_device`).
- [ ] Créer une route `GET /device/{id}/telemetrie` (si séparé) pour obtenir les données JSON (CPU, RAM, Réseau) formattées pour les graphiques.

* detail taille total stockage et stockage utilisé 
* combien de ram utilisé sur combien 
* valeur maximum degré car resultat faussé 

### Frontend
- [ ] Compléter `frontend/src/page/device/detail_device.jsx`.
- [ ] **Onglet/Section 1 : Infos Générales** (Modèle, OS, MAC, Utilisateur assigné).
- [ ] **Onglet/Section 2 : État Actuel (Ressources)** (Affichage CPU, RAM, Stockage via des jauges ou barres de progression).
- [ ] **Onglet/Section 3 : Historique & Crashs** (Tableau listant les entrées de `t_evenement_device`).
- [ ] **Bouton d'Export** : Implémenter l'export PDF (ex: via `jspdf` ou `react-to-print`) et Excel (via `xlsx`).

---

## 4. Page Statistiques et Graphiques
*Estimation : ~4h*

### Backend
- [ ] Ajouter des routes dans `statistiques_controller.py` pour fournir des données de séries temporelles (Time Series).
- [ ] Route `GET /stats/ressources` (évolution CPU/RAM moyenne sur une période).
- [ ] Route `GET /stats/incidents` (nombre de crashs/événements par jour/semaine).

### Frontend
- [ ] Créer une nouvelle page `frontend/src/page/statistiques.jsx`.
- [ ] Installer une bibliothèque de graphiques (ex: `recharts` ou `chart.js`).
- [ ] Intégrer des sélecteurs de date (Période : 7 derniers jours, 1 mois, etc.).
- [ ] Afficher les graphiques d'évolution (Lignes, Barres).
- [ ] Bouton d'export pour ces graphiques/données.

---

## 5. Page Comparaison
*Estimation : ~4,5h*

### Backend
- [ ] Créer un contrôleur `comparaison_controller.py`.
- [ ] Route `GET /compare/devices?id1={id1}&id2={id2}` pour comparer deux appareils distincts.
- [ ] Route `GET /compare/device-history?id={id}&date1={date1}&date2={date2}` pour comparer le même appareil à deux dates différentes (utilise `t_device_historique` et `t_rapport_device`).
- [ ] Route `POST /compare/save` pour sauvegarder le résultat de la comparaison dans `t_comparaison`.

### Frontend
- [ ] Créer la page `frontend/src/page/comparaison.jsx`.
- [ ] Interface avec deux colonnes (ou tableau) pour afficher côte à côte les ressources, versions d'OS, et nombre de crashs.
- [ ] Sélecteurs permettant de choisir "Quoi comparer" (Appareil vs Appareil OU Avant vs Après).

---

## 6. Gestion des Alertes
*Estimation : ~4h*

### Backend
- [ ] Créer un contrôleur `alerte_controller.py`.
- [ ] Routes `GET /alertes` (liste des alertes non résolues/toutes les alertes).
- [ ] Route `PUT /alertes/{id}/resolve` (pour marquer une alerte avec une `date_resolution` dans `t_device_alerte`).
- [ ] **Logique Métier (Service) :** Créer un script (qui peut être appelé lors de la synchro `POST /synch`) qui analyse les données reçues. S'il détecte un CPU > 90% ou un statut "offline" prolongé, il insère une nouvelle ligne dans `t_device_alerte`.

### Frontend
- [ ] Créer la page `frontend/src/page/alertes.jsx`.
- [ ] Tableau listant les alertes (Date, Appareil, Type d'alerte, Statut).
- [ ] Bouton d'action "Marquer comme résolue" sur chaque ligne.

---

## 7. Gestion des Imprimantes
*Estimation : ~3h (1h Liste + 2h Détails)*

### Backend
- [ ] Créer un contrôleur `imprimante_controller.py`.
- [ ] Route `GET /imprimantes` (lecture de `t_imprimante`).
- [ ] Route `GET /imprimantes/{id}` (détails et appareils liés via `t_imprimante_device`).

### Frontend
- [ ] Créer la page `frontend/src/page/imprimante/liste.jsx`.
  - Tableau des imprimantes avec recherche (par nom, vendor).
- [ ] Créer la page `frontend/src/page/imprimante/detail_imprimante.jsx`.
  - Informations de base.
  - Historique des détections.
  - Fonction d'export PDF de cette fiche.

---

## 8. Configuration
*Estimation : ~2h*

### Backend
- [ ] Créer un contrôleur `configuration_controller.py`.
- [ ] Routes `GET /configuration` et `PUT /configuration` pour lire/modifier `t_configuration` (ex: `seuil_cpu`, `frequence_synchro_heures`).

### Frontend
- [ ] Créer la page `frontend/src/page/configuration.jsx`.
- [ ] Formulaire permettant de modifier les seuils d'alerte.

---

## 9. Finalisation de la Sécurité et Routage Frontend
*Estimation : ~2,5h*

### Backend
- [ ] Vérifier que `user_controller.py` et `auth.py` utilisent bien les JWT (déjà dans les requirements).
- [ ] Ajouter un décorateur / middleware de vérification de token sur **toutes les routes API** (sauf `/login`).

### Frontend
- [ ] Mettre en place la gestion de l'état d'authentification (ex: via Context API ou Redux).
- [ ] Protéger les routes dans `App.jsx` (Rediriger vers `/login` si pas de token valide dans le `localStorage`).
- [ ] S'assurer que le token est envoyé dans le header `Authorization: Bearer <token>` de toutes les requêtes Axios.

---

## 💡 Comment utiliser ce guide ?

1. Commencez par le **Point 1 (Dashboard)** et le **Point 2 (Liste Globale)** car ils réutilisent beaucoup de choses que vous avez déjà faites pour la liste par filiale.
2. Attaquez ensuite le **Point 3 (Détail de l'appareil)**. C'est le cœur de l'application. Vous devrez vous assurer que la synchro Google API insère bien les données JSON dans `t_rapport_device` et `t_evenement_device` pour pouvoir les afficher.
3. Cochez les cases au fur et à mesure. N'hésitez pas à demander de l'aide sur une fonctionnalité spécifique (ex: *"Aide moi à créer le backend pour la page de détail d'un appareil"*).

CPU : Modèle, nombre de cœurs, fréquence, température, utilisation (%)
Mémoire RAM : Capacité totale, mémoire utilisée, mémoire disponible
Stockage : Capacité totale du disque, espace utilisé, espace libre
Batterie (si Chromebook) : Niveau de charge (%), état de santé, nombre de cycles de charge
Réseau : État de la connexion (Wi-Fi / Ethernet), force du signal, vitesse de transmission
Périphériques connectés : Imprimantes détectées, périphériques USB / externes
