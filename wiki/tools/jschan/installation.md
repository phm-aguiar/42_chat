---
title: "jschan — Guia de Instalação"
category: tools
tags: [jschan, installation, mongodb, redis, nginx, nodejs, pm2]
created: "2026-06-20"
rag_score: 0.5
author: phm-aguiar
aliases: ["instalar jschan", "jschan setup"]
---

# jschan — Guia de Instalação

> Passo a passo para instalar uma instância jschan do zero em Debian/Ubuntu.
> Baseado no [INSTALLATION.md](https://gitgud.io/fatchan/jschan/-/blob/master/INSTALLATION.md) oficial.

## Pré-requisitos

- Linux (Debian/Ubuntu recomendado)
- Node.js LTS (via [nvm](https://github.com/nvm-sh/nvm))
- MongoDB ≥ 4.4 (AVX required para 5.0+)
- Redis
- Nginx (compilado com geoip, subfilter)
- Certbot/Let's Encrypt
- GraphicsMagick + ImageMagick
- FFmpeg

## Passo a passo

### 1. Setup básico do servidor

```bash
# Usuário separado e sem privilégios para rodar a aplicação
# SSH: root login desabilitado, apenas key login
# Firewall: ufw — negar tudo exceto 80/443 e porta SSH
# Timezone: UTC
sudo timedatectl set-timezone UTC
```

### 2. Clonar repositório

```bash
git clone https://gitgud.io/fatchan/jschan.git /opt/jschan
cd /opt/jschan
```

### 3. Instalar dependências do sistema

```bash
sudo apt update -y
sudo apt install curl wget libgeoip-dev gnupg ffmpeg imagemagick graphicsmagick fontconfig fonts-dejavu certbot -y
```

### 4. Instalar MongoDB 7.0

```bash
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb http://repo.mongodb.org/apt/debian $(lsb_release -sc)/mongodb-org/7.0 main" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt update && sudo apt install -y mongodb-org
sudo systemctl enable --now mongod
```

Habilitar autenticação:

```bash
mongosh admin --eval "db.getSiblingDB('jschan').createUser({user: 'jschan', pwd: 'SUA-SENHA-SEGURA', roles: [{role:'readWrite', db:'jschan'}]})"
# Editar /etc/mongod.conf para security.authorization: enabled
sudo systemctl restart mongod
```

### 5. Instalar Redis

```bash
sudo apt install redis-server -y
echo "requirepass SUA-SENHA-REDIS" | sudo tee -a /etc/redis/redis.conf
sudo systemctl enable --now redis-server
```

### 6. Instalar Node.js via nvm

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm install --lts
```

### 7. Configurar Nginx

```bash
# Instalar nginx compilado com módulos extras
wget https://raw.githubusercontent.com/fatchan/nginx-autoinstall/master/nginx-autoinstall.sh
chmod +x nginx-autoinstall.sh
HEADLESS=y OPTION=1 NGINX_VER=STABLE SUBFILTER=y RTMP=y ./nginx-autoinstall.sh
rm nginx-autoinstall.sh

# Configurar sites
sudo mkdir -p /etc/nginx/snippets
sudo bash configs/nginx/nginx.sh
```

### 8. Configurar backend jschan

```bash
# Secrets
cp configs/secrets.js.example configs/secrets.js
editor configs/secrets.js  # Preencher credenciais MongoDB, Redis, secrets

# Dependências Node
npm install

# Setup inicial
npm run-script setup

# Reset (cria banco, admin account — guarde a senha!)
npx gulp reset

# PM2
npx pm2 completion install
npx pm2 startup
npm run-script start
npx gulp
npx pm2 save
```

### 9. (Opcional) Tor .onion / Lokinet .loki

```bash
sudo apt install tor -y
# Configurar HiddenService em /etc/tor/torrc
sudo systemctl restart tor
cat /var/lib/tor/jschan/hostname  # Seu endereço .onion
```

### 10. Pronto!

Acesse `https://seu-dominio.com` e comece a criar boards.

## Docker (desenvolvimento apenas)

O docker-compose.yml no repositório é **experimental, apenas para dev**:

```bash
docker-compose up -d mongodb redis
docker-compose up jschan-reset   # Primeira execução
docker-compose up -d jschan
docker-compose up -d nginx
```

## Troubleshooting

| Problema | Solução |
|---|---|
| MongoDB não inicia | Verificar permissões: `sudo chown -R mongodb:mongodb /var/lib/mongodb /var/log/mongodb` |
| Redis auth falha | Conferir `requirepass` no `/etc/redis/redis.conf` |
| PM2 não inicia | Rodar `npx pm2 startup` e seguir instruções |
| 502 Bad Gateway | jschan backend não está rodando: `pm2 list`, verificar logs |
| Esqueci senha admin | `npx gulp password` — reseta e imprime nova senha |

## Relacionado

- [[overview|Visão Geral do jschan]]
- [[operations|Guia de Operações]]
