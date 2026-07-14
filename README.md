# app-sia-bot

Automacao para atualizar planilhas Google com dados do SIA (Firebird).

## Estrutura

- `atualiza_sentenciados_p2.py`: atualiza planilha de sentenciados.
- `atualiza_visitantes_p2.py`: atualiza planilha de visitantes.
- `credencial/`: JSON da conta de servico Google (nao versionado).

## Configuracao local

1. Crie `.env` a partir de `.env.example`.
2. Coloque o arquivo da conta de servico em `credencial/google-service-account.json`.
3. Instale dependencias:

```bash
pip install -r requirements.txt
```

4. Rode os scripts:

```bash
python atualiza_sentenciados_p2.py
python atualiza_visitantes_p2.py
```

## Publicar no GitHub

1. Crie repositorio vazio no GitHub.
2. No projeto local, execute:

```bash
git init
git add .
git commit -m "chore: organiza projeto para deploy"
git branch -M main
git remote add origin <URL_DO_REPO>
git push -u origin main
```

## Deploy no Proxmox (Container/VM com Docker)

1. Suba uma VM/LXC Debian 12 ou Ubuntu 22.04.
2. Instale Docker e Docker Compose plugin.
3. Clone o repositorio.
4. Crie `.env` e envie `credencial/google-service-account.json`.
5. Suba:

```bash
docker compose up -d --build
```

6. Verifique logs:

```bash
docker logs -f app-sia-bot
```

## Executar a cada 1 hora no Proxmox

Há duas opções para agendamento no host.

### Opção 1: cron

```bash
crontab -e
```

Adicione:

```bash
0 * * * * /bin/bash /caminho/para/app-sia-bot/run_jobs.sh >> /var/log/app-sia-bot.log 2>&1
```

Antes de usar, dê permissão de execução:

```bash
chmod +x /caminho/para/app-sia-bot/run_jobs.sh
```

### Opção 2: systemd timer (mais robusto)

Copie os arquivos para `/etc/systemd/system/`:

```bash
sudo cp app-sia-bot.service app-sia-bot.timer /etc/systemd/system/
```

Ative e inicie:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now app-sia-bot.timer
sudo systemctl status app-sia-bot.timer
```

Se precisar alterar o caminho do projeto, edite o arquivo `app-sia-bot.service` e troque `/opt/app-sia-bot` pelo caminho real.

## Observacao importante

Nunca commite arquivos de credenciais (`.env` e JSON da pasta `credencial`).
