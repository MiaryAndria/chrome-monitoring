# Plan de Travail Détaillé - Plateforme de Monitoring ChromeOS (Phase de Développement)
## 1. Finalisation de la Synchronisation des Données (Backend)

Il reste à récupérer et insérer les données liées aux appareils (télémétrie, historiques, réseau, imprimantes). Cette logique doit se faire dans le service de synchronisation.

### 1.1 Organisation et Utilisateurs (OU & Google Workspace Users)
**Fichiers à modifier / créer :**
- `backend/fonction/metier/repository/filiale/filiale.py` (ou équivalent) : 
  - Ajouter/Vérifier la fonction `insert_filiale(cur, nom, org_unit_path)`.
- `backend/fonction/metier/repository/utilisateur_google/utilisateur.py` : 
  - Ajouter/Vérifier `insert_utilisateur(cur, email)`.
- `backend/fonction/metier/repository/filiale/filiale_utilisateur.py` (Nouveau) : 
  - Créer `insert_filiale_utilisateur(cur, id_filiale, id_utilisateur)` pour alimenter `t_filiale_utilisateur`.
- `backend/fonction/metier/service/filiale_service.py` : 
  - Ajouter la logique métier appelant l'API Google Directory pour récupérer les OUs et les utilisateurs.
  - Appeler ensuite les fonctions des repositories ci-dessus pour insérer en base.

### 1.2 Liaisons et Historiques des Devices
**Fichiers à modifier / créer :**
- `backend/fonction/metier/repository/devices/device_filiale.py` : 
  - Implémenter l'insertion de l'association `id_device` <-> `id_filiale` (et mise à jour si l'OU change).
- `backend/fonction/metier/repository/devices/device_statut.py` : 
  - Implémenter l'historisation des changements d'états (ex: ACTIVE -> DEPROVISIONED).
- `backend/fonction/metier/repository/devices/historique_device.py` : 
  - Enregistrer chaque mise à jour de l'appareil (date de sync, statut, org_unit_path).
- `backend/fonction/metier/service/device_service.py` : 
  - Dans la fonction globale `synchroniser_tout()`, ajouter la logique pour appeler ces insertions de liaison *après* avoir inséré ou mis à jour un `t_device`.

### 1.3 Télémétrie, Ressources et Rapports (Chrome Management Telemetry API)
**Fichiers à modifier / créer :**
- `backend/fonction/metier/models/rapport.py` (Nouveau) : 
  - Créer les classes/modèles Pydantic pour valider les données de télémétrie.
- `backend/fonction/metier/repository/rapport/type_rapport.py` (Nouveau) : 
  - Gestion de la table `t_type_rapport`.
- `backend/fonction/metier/repository/rapport/rapport_device.py` (Nouveau) : 
  - Fonctions pour insérer les données JSON d'utilisation (CPU, RAM) dans `t_rapport_device` et tracer l'évolution des versions dans `t_version_report`.
- `backend/fonction/metier/service/telemetry_service.py` (Nouveau) : 
  - Logique d'appel à l'API Google Telemetry.
  - Extraction et traitement du JSON reçu.
  - Appel des repositories `rapport_device.py` pour stockage.

### 1.4 Événements, Crashs et Alertes
**Fichiers à modifier / créer :**
- `backend/fonction/metier/repository/evenement/evenement.py` (Nouveau) : 
  - Fonctions d'insertion dans `t_type_evenement` et `t_evenement_device`.
- `backend/fonction/metier/repository/alerte/alerte.py` (Nouveau) : 
  - Détection de seuils dépassés et insertion dans `t_alerte` et `t_device_alerte`.
- `backend/fonction/metier/service/evenement_service.py` (Nouveau) : 
  - Logique de récupération des "Telemetry Events" (crashs, incidents) via Google API et passage aux repositories.

### 1.5 Gestion des Imprimantes
**Fichiers à modifier / créer :**
- `backend/fonction/metier/models/imprimante.py` (Nouveau) : 
  - Modèles Pydantic pour les imprimantes.
- `backend/fonction/metier/repository/imprimante/imprimante.py` (Nouveau) : 
  - Fonctions d'insertion / MAJ dans `t_imprimante`.
- `backend/fonction/metier/repository/imprimante/imprimante_device.py` (Nouveau) : 
  - Fonctions d'insertion des liens imprimante-device dans `t_imprimante_device`.
- `backend/fonction/metier/service/imprimante_service.py` (Nouveau) : 
  - Traitement des données d'imprimantes issues de la télémétrie et enregistrement en base.

---

## 2. Développement des Routes API Rest (Controllers Backend)

Une fois les données stockées de manière fiable, il faut les exposer au Frontend.

### 2.1 Devices (Fiche détaillée)
- `backend/fonction/metier/controller/device_controller.py` : 
  - **Créer la route `GET /api/devices/{id}`** : 
    - Appelle un `device_service.get_device_detail(id)` qui regroupe les données de `device_repository`, `device_statut_repository`, etc. (informations générales, réseau, utilisateurs récents).
  - **Créer la route `GET /api/devices/{id}/events`** : 
    - Renvoie la liste des incidents/crashs spécifiques à cet appareil.

### 2.2 Statistiques et Comparaison
- `backend/fonction/metier/controller/stats_controller.py` (Nouveau) : 
  - **Créer `GET /api/stats/dashboard`** : Renvoie les KPIs (nb total d'appareils, nb d'appareils actifs, nb total d'imprimantes, alertes en cours).
  - **Créer `GET /api/stats/resources`** : Exécute des requêtes SQL groupées pour remonter l'évolution CPU/RAM sur une période.
- `backend/fonction/metier/controller/comparaison_controller.py` (Nouveau) :
  - **Créer `GET /api/compare?id_a=X&id_b=Y`** : Calcule et renvoie un JSON contenant les différences de configuration ou d'état entre deux devices ou deux dates.

### 2.3 Imprimantes et Alertes
- `backend/fonction/metier/controller/imprimante_controller.py` (Nouveau) :
  - **Créer `GET /api/printers`** : Liste de toutes les imprimantes.
  - **Créer `GET /api/printers/{id}`** : Détails d'utilisation et matériels associés.
- `backend/fonction/metier/controller/alerte_controller.py` (Nouveau) :
  - **Créer `GET /api/alerts`** : Liste des alertes actives nécessitant une intervention.

---

## 3. Développement de l'Interface Utilisateur (Frontend React)

Les appels aux APIs créées précédemment se feront dans le dossier `frontend/src/fonction/` (ex: `deviceFonction.js`).

### 3.1 Dashboard (`src/page/dashboard.jsx`)
- **Service** : Implémenter l'appel Axios vers `/api/stats/dashboard`.
- **UI Components** : 
  - Remplir les cartes d'indicateurs existantes (Total appareils, actifs, inactifs, etc.) avec les vraies données de la BDD.
  - Intégrer des graphiques (ex: via `recharts` ou `chart.js`) pour visualiser la répartition des types d'appareils ou les alertes.

### 3.2 Liste des Appareils (`src/page/device/liste.jsx`)
- **Évolutions UI** : 
  - Ajouter la gestion de filtres combinés (par type: Chromebook/Chromebox, par Filiale/OU).
  - Rendre les lignes du tableau cliquables pour rediriger l'utilisateur vers la route `/devices/:id` en utilisant `react-router-dom`.

### 3.3 Page Détail Appareil (`src/page/device/detail.jsx` - À Créer)
- **Services** : Créer `getDeviceDetails(id)` et `getDeviceEvents(id)` dans `frontend/src/fonction/deviceFonction.js`.
- **UI Components** : 
  - Créer des onglets (Tabs) pour organiser l'information :
    - *Onglet 1* : Infos générales, Utilisateurs récents, MAC/IP.
    - *Onglet 2* : Matériel (Graphiques de CPU, RAM, Stockage).
    - *Onglet 3* : Tableau chronologique des activités, changements d'états et crashs.

### 3.4 Pages Imprimantes (`src/page/imprimante/liste.jsx` & `detail.jsx` - À Créer)
- **Services** : Créer `getListeImprimantes()` et `getDetailImprimante(id)`.
- **UI Components** : 
  - Page `liste.jsx` : Tableau avec recherche (Marque, Modèle, Date d'identification).
  - Page `detail.jsx` : Fiche détaillée (Infos réseau, statistiques d'impression).

### 3.5 Page Statistiques (`src/page/rapport/statistiques.jsx` - À Créer)
- **Services** : Implémenter l'appel aux endpoints de statistiques globales.
- **UI Components** : 
  - Sélecteur de date/période.
  - Différents graphiques illustrant la santé globale du parc (utilisation moyenne CPU, mémoire, évolution des crashs dans le temps).

### 3.6 Page Comparaison (`src/page/comparaison/compare.jsx` - À Créer)
- **UI Components** : 
  - Interface en deux colonnes (ou tableau split-view).
  - Listes déroulantes (Select) ou champ de recherche pour sélectionner 2 appareils distincts.
  - Mise en évidence visuelle (Couleur / Icônes) des différences de caractéristiques ou de version ChromeOS.

### 3.7 Gestion des Alertes (`src/page/alerte/alertes.jsx` - À Créer)
- **UI Components** : 
  - Tableau ou grille de cartes listant les alertes non résolues.
  - Affichage : Type d'alerte, Appareil concerné, Message, Date de déclenchement.
  - Bouton ou action pour passer une alerte en statut "Résolue" (qui appellera un endpoint `PUT /api/alerts/{id}`).
