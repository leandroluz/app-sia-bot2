#!/bin/bash
set -euo pipefail

REPO_DIR="${1:-/opt/app-sia-bot}"

if [ "$(id -u)" -ne 0 ]; then
  echo "Execute este script como root." >&2
  exit 1
fi

mkdir -p "$REPO_DIR"

if [ ! -f "$REPO_DIR/run_jobs.sh" ]; then
  echo "O diretório $REPO_DIR não contém o projeto. Copie o repositório para ele primeiro." >&2
  exit 1
fi

apt-get update
apt-get install -y python3 python3-pip python3-venv git curl

cd "$REPO_DIR"
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

chmod +x "$REPO_DIR/run_jobs.sh"

if [ ! -f "$REPO_DIR/.env" ]; then
  cp "$REPO_DIR/.env.example" "$REPO_DIR/.env"
  echo "Arquivo .env criado em $REPO_DIR/.env. Ajuste os valores antes de rodar." 
fi

if [ ! -f "$REPO_DIR/credencial/google-service-account.json" ]; then
  echo "Aviso: credencial/google-service-account.json não encontrado. Coloque o JSON antes de executar os scripts." >&2
fi

cp "$REPO_DIR/app-sia-bot.service" /etc/systemd/system/app-sia-bot.service
cp "$REPO_DIR/app-sia-bot.timer" /etc/systemd/system/app-sia-bot.timer

systemctl daemon-reload
systemctl enable --now app-sia-bot.timer

systemctl status app-sia-bot.timer --no-pager || true

echo "Deploy concluído. Para testar manualmente:"
echo "  cd $REPO_DIR && ./run_jobs.sh"
