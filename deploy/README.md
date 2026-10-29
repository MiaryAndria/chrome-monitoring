# Déploiement Ubuntu (systemd)

Deux services systemd, sans modification du code :

- `chrome-monitoring-api` → l'API FastAPI (`uvicorn backend.main:app`, port 8000).
- `chrome-monitoring-synchro` → la synchro Google automatique (`python -m backend.worker`).

Ils démarrent **au boot** de la machine et **redémarrent seuls** en cas de crash.

## Prérequis (une seule fois sur le serveur)

1. Copier le projet sur le serveur, ex. `/opt/chrome-monitoring`.
2. Créer le venv et installer les dépendances :
   ```bash
   cd /opt/chrome-monitoring/code
   python3 -m venv venv
   venv/bin/pip install -r ../doc/requirements.txt
   ```
3. Configurer `code/.env` (copie de `code/.env.example`) et le dossier `credential/`.

## Installation des services

Depuis la racine du projet :
```bash
sudo ./deploy/install.sh
```

Le script détecte le dossier du projet et l'utilisateur, écrit les unités dans
`/etc/systemd/system/`, recharge systemd, puis active et démarre les deux services.

## Commandes utiles

```bash
# État
systemctl status chrome-monitoring-api chrome-monitoring-synchro

# Logs en direct
journalctl -u chrome-monitoring-api -f
journalctl -u chrome-monitoring-synchro -f

# Redémarrer / arrêter / désactiver au boot
sudo systemctl restart chrome-monitoring-api
sudo systemctl stop chrome-monitoring-synchro
sudo systemctl disable chrome-monitoring-api chrome-monitoring-synchro
```

## À vérifier après déploiement

- **Accès réseau** : l'API écoute sur `0.0.0.0:8000`. Pour l'exposer derrière un
  nom de domaine, prévoir un **reverse proxy nginx** (et le HTTPS).
- **CORS** : `backend/main.py` n'autorise que `http://localhost:5173`. Adapter les
  origines autorisées à l'URL réelle du front en production.
- **Frontend** : servir le build (`npm run build` → `dist/`) via nginx plutôt que
  `npm run dev`.
