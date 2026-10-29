# Déploiement Ubuntu (systemd + nginx)

- `chrome-monitoring-api` → l'API FastAPI (`uvicorn backend.main:app`, écoute sur `127.0.0.1:8000`).
- `chrome-monitoring-synchro` → la synchro Google automatique (`python -m backend.worker`).

Ils démarrent **au boot** de la machine et **redémarrent seuls** en cas de crash.
nginx sert le front buildé et proxifie `/api/` vers l'API (même origine → pas de CORS).

## Prérequis (une seule fois sur le serveur)

1. Récupérer le projet :
   ```bash
   git clone https://github.com/MiaryAndria/chrome-monitoring.git /opt/chrome-monitoring
   ```
2. Déposer `code/.env` et le dossier `credential/` (secrets, **non versionnés**) via SFTP.
3. Créer le venv et installer les dépendances :
   ```bash
   cd /opt/chrome-monitoring/code
   python3 -m venv venv
   venv/bin/pip install -r ../doc/requirements.txt
   ```
4. Construire le front :
   ```bash
   cd /opt/chrome-monitoring/code/frontend
   npm install
   npm run build
   ```

## nginx

```bash
sudo cp /opt/chrome-monitoring/deploy/nginx/chrome-monitoring.conf /etc/nginx/sites-available/chrome-monitoring
sudo ln -s /etc/nginx/sites-available/chrome-monitoring /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```
> Penser à remplacer `server_name ton-domaine.com` par le domaine réel dans le fichier.

## Installation des services systemd

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

- **API interne** : uvicorn écoute sur `127.0.0.1:8000` ; seul nginx y accède. Ne pas
  ouvrir le port 8000 dans le pare-feu.
- **HTTPS** : `sudo certbot --nginx -d ton-domaine.com` puis passer `COOKIE_SECURE=true`
  dans `code/.env` et redémarrer le service API.
- **Secrets** : `code/.env` et `credential/` ne doivent jamais être committés.
