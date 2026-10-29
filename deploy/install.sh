#!/usr/bin/env bash
# Installe et active les services systemd de Chrome Monitoring (Ubuntu).
# Usage :  sudo ./deploy/install.sh
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Ce script doit être lancé avec sudo :  sudo ./deploy/install.sh" >&2
  exit 1
fi

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CODE_DIR="${APP_DIR}/code"
VENV_BIN="${CODE_DIR}/venv/bin"
RUN_USER="${SUDO_USER:-root}"
UNIT_DIR="/etc/systemd/system"

if [[ ! -x "${VENV_BIN}/uvicorn" || ! -x "${VENV_BIN}/python" ]]; then
  echo "Environnement virtuel introuvable : ${VENV_BIN}" >&2
  echo "Crée-le d'abord :" >&2
  echo "  cd ${CODE_DIR} && python3 -m venv venv" >&2
  echo "  ${CODE_DIR}/venv/bin/pip install -r ${APP_DIR}/doc/requirements.txt" >&2
  exit 1
fi

if [[ ! -f "${CODE_DIR}/.env" ]]; then
  echo "Attention : ${CODE_DIR}/.env est absent (copie code/.env.example)." >&2
fi

for unit in chrome-monitoring-api chrome-monitoring-synchro; do
  sed -e "s|__APP_DIR__|${APP_DIR}|g" \
      -e "s|__RUN_USER__|${RUN_USER}|g" \
      "${APP_DIR}/deploy/systemd/${unit}.service" \
      > "${UNIT_DIR}/${unit}.service"
  echo "Écrit : ${UNIT_DIR}/${unit}.service"
done

systemctl daemon-reload
systemctl enable --now chrome-monitoring-api.service chrome-monitoring-synchro.service

echo
echo "Services installés, activés au démarrage et démarrés."
echo "  Statut :   systemctl status chrome-monitoring-api chrome-monitoring-synchro"
echo "  Logs API : journalctl -u chrome-monitoring-api -f"
echo "  Logs synchro : journalctl -u chrome-monitoring-synchro -f"
