---
title: "Docker & Compose no 42 Chat"
tags: [docker, devops, go]
created: 2026-06-21
rag_score: 0.5
category: references
summary: Estrutura Docker do 42 Chat Core — multistage build, docker-compose, health checks, variáveis de ambiente e padrões dev vs prod.
provenance:
  extracted: 0.98
  inferred: 0.02
  ambiguous: 0.00
---

# Docker & Compose no 42 Chat Core

Referência da infraestrutura Docker do projeto — do `Dockerfile` multistage ao `docker-compose.yml` com PostgreSQL integrado.

---

## Multistage Build

O `Dockerfile` usa **dois estágios** para produzir uma imagem final mínima.

### Estágio 1 — Builder

```dockerfile
FROM golang:1.25-alpine AS builder

RUN apk add --no-cache git ca-certificates

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /server ./cmd/server/
```

**Decisões chave:**

| Decisão                  | Justificativa                                         |
|--------------------------|-------------------------------------------------------|
| `golang:1.25-alpine`     | Imagem Alpine é ~5x menor que Debian; Go 1.25 bate `go.mod` |
| `go mod download` antes  | Otimiza cache de layer — só re-download quando `go.mod`/`go.sum` mudam |
| `CGO_ENABLED=0`          | Gera binário estático, sem dependência de libc        |
| `-ldflags="-s -w"`       | Strip symbols (`-s`) e DWARF debug info (`-w`) — binário ~30% menor |
| `-o /server`             | Output explícito na raiz do container, fácil de copiar |

### Estágio 2 — Runtime

```dockerfile
FROM alpine:3.21

RUN apk add --no-cache ca-certificates tzdata

COPY --from=builder /server /server

EXPOSE 8080

ENTRYPOINT ["/server"]
```

| Decisão                  | Justificativa                                         |
|--------------------------|-------------------------------------------------------|
| `alpine:3.21`            | Imagem base de ~7 MB — sem Go toolchain               |
| `ca-certificates`        | Necessário para TLS (OAuth2 ↔ api.intra.42.fr)        |
| `tzdata`                 | Timezone data para `TIMESTAMPTZ` funcionar corretamente |
| `EXPOSE 8080`            | Documenta a porta (não publica — isso é feito no compose) |
| `ENTRYPOINT ["/server"]` | Forma exec — recebe sinais UNIX corretamente          |

### Tamanho estimado da imagem

- Builder: ~350 MB (Go toolchain + source)
- Final: **~15 MB** (Alpine + binário estático de ~8 MB + certs + tzdata)

---

## docker-compose.yml — Estrutura

O compose define **2 serviços** + 1 volume + 1 rede.

```
services:
  postgres   → PostgreSQL 16 Alpine
  server     → 42 Chat Core (build local)

volumes:
  pgdata     → Persistência do banco

networks:
  42chat     → Bridge network isolada
```

### Serviço: postgres

```yaml
postgres:
  image: postgres:16-alpine
  container_name: 42chat-postgres
  restart: unless-stopped
  ports:
    - "${POSTGRES_PORT:-5432}:5432"
  environment:
    POSTGRES_USER: ${POSTGRES_USER:-chat}
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-banana42}
    POSTGRES_DB: ${POSTGRES_DB:-chat}
  volumes:
    - pgdata:/var/lib/postgresql/data
    - ./internal/db/migrations:/docker-entrypoint-initdb.d:ro,z
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-chat} -d ${POSTGRES_DB:-chat}"]
    interval: 5s
    timeout: 3s
    retries: 5
  networks:
    - 42chat
```

| Configuração             | Detalhe                                              |
|--------------------------|------------------------------------------------------|
| `postgres:16-alpine`     | Versão fixa (16) + Alpine (menor footprint)          |
| `unless-stopped`         | Reinicia automaticamente, exceto se parado manualmente |
| `${VAR:-default}`        | Fallback com valor padrão se a env var não existir   |
| `pgdata` volume          | Persiste dados entre recriações do container         |
| `migrations:ro,z`        | Read-only + SELinux label (`z` = shared, `Z` = private) |
| `docker-entrypoint-initdb.d` | Executa `.sql` na primeira inicialização         |

### Serviço: server

```yaml
server:
  build:
    context: .
    dockerfile: Dockerfile
  container_name: 42chat-server
  restart: unless-stopped
  ports:
    - "${PORT:-8080}:${PORT:-8080}"
  depends_on:
    postgres:
      condition: service_healthy
  environment:
    PORT: ${PORT:-8080}
    DATABASE_URL: postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}?sslmode=disable
    JWT_SECRET: ${JWT_SECRET:-change-me-in-production-please}
    DEV_MODE: ${DEV_MODE:-false}
    DEV_USER: ${DEV_USER:-marvin}
    FORTYTWO_CLIENT_ID: ${FORTYTWO_CLIENT_ID:-}
    FORTYTWO_CLIENT_SECRET: ${FORTYTWO_CLIENT_SECRET:-}
    FORTYTWO_REDIRECT_URI: ${FORTYTWO_REDIRECT_URI:-http://localhost:5173}
    FORTYTWO_API_URL: ${FORTYTWO_API_URL:-https://api.intra.42.fr}
  networks:
    - 42chat
```

| Configuração                      | Detalhe                                          |
|-----------------------------------|--------------------------------------------------|
| `depends_on.condition: service_healthy` | Só sobe quando o PostgreSQL passar no healthcheck |
| `DATABASE_URL`                    | Usa hostname `postgres` (nome do serviço no compose) |
| `sslmode=disable`                 | Conexão interna na bridge network — sem TLS       |
| `${VAR:-default}`                 | Todas as env vars têm fallback seguro             |

---

## Dev vs Prod

### Modo desenvolvimento

```bash
# .env
DEV_MODE=true
DEV_USER=seu_login_42
POSTGRES_PASSWORD=banana42
JWT_SECRET=dev-secret
```

- `DEV_MODE=true` ativa endpoints de debug e bypass de OAuth2.
- `DEV_USER` define qual login da 42 é usado no modo dev.
- PostgreSQL com senha fraca (`banana42`) — aceitável só localmente.

### Modo produção

```bash
# .env
DEV_MODE=false
JWT_SECRET=<random-64-chars>
POSTGRES_PASSWORD=<strong-password>
FORTYTWO_CLIENT_ID=<real-client-id>
FORTYTWO_CLIENT_SECRET=<real-client-secret>
```

- `DEV_MODE=false` desabilita endpoints de dev.
- Senhas e secrets devem ser gerados aleatoriamente.
- OAuth2 configurado com credenciais reais da API 42.

---

## Health Checks

### PostgreSQL

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-chat} -d ${POSTGRES_DB:-chat}"]
  interval: 5s
  timeout: 3s
  retries: 5
```

- `pg_isready` é a ferramenta oficial de health check do PostgreSQL.
- **5 retries × 5s interval = 25s máximo** de espera inicial.
- O server usa `depends_on: condition: service_healthy` — **não sobe antes do banco estar pronto**.

### Server

O server **não tem healthcheck explícito no compose**, mas o `NewPostgres()` faz `db.Ping()` no startup — se o banco não responder, o container crasha e o `restart: unless-stopped` tenta de novo.

---

## env -u KEY Pattern

O projeto usa **fallback com valor padrão** em todas as variáveis de ambiente no `docker-compose.yml`:

```yaml
environment:
  PORT: ${PORT:-8080}
  DATABASE_URL: postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}?sslmode=disable
```

**Sintaxe**: `${VAR:-default}`

- Se `VAR` está definida no `.env` ou no ambiente do shell → usa o valor.
- Se `VAR` **não** está definida → usa `default`.

### Exemplos

| Variável                      | Fallback                     |
|-------------------------------|------------------------------|
| `${PORT:-8080}`               | 8080                         |
| `${POSTGRES_USER:-chat}`      | chat                         |
| `${POSTGRES_PASSWORD:-banana42}` | banana42                   |
| `${DEV_MODE:-false}`          | false                        |
| `${FORTYTWO_CLIENT_ID:-}`     | string vazia (OAuth2 desabilitado) |

### Como o .env é carregado

O Docker Compose **automaticamente** carrega variáveis de um arquivo `.env` no mesmo diretório do `docker-compose.yml`. Basta criar:

```bash
cp .env.example .env   # se .env.example existir
# ou criar .env manualmente
```

### Variáveis com string vazia

`${FORTYTWO_CLIENT_ID:-}` — o fallback é string vazia. Isso permite que o servidor suba **sem** OAuth2 configurado (útil para dev local). Se não fosse definida, o compose falharia com erro de variável ausente.

### Boas práticas observadas

1. **Nunca hardcode secrets no compose file** — sempre `${VAR}`.
2. **Fallback seguro para dev** — valores padrão como `banana42` e `change-me` são aceitáveis localmente.
3. **String vazia como fallback intencional** — para features opcionais (OAuth2).
4. **Sem `env_file` directive** — usa o `.env` automático do compose, mais simples.

---

## Rede e Volumes

### Network

```yaml
networks:
  42chat:
    driver: bridge
```

- **Bridge network** isolada — containers se comunicam por hostname (`postgres`, `server`).
- Sem exposição externa do PostgreSQL (a porta `5432` mapeada é opcional, só para debug local).

### Volume

```yaml
volumes:
  pgdata:
    driver: local
```

- **`driver: local`** — volume gerenciado pelo Docker, persiste em `/var/lib/docker/volumes/`.
- Sobrevive a `docker compose down` (sem `-v`).
- Para resetar completamente: `docker compose down -v`.

### Mount bind de migrations

```yaml
- ./internal/db/migrations:/docker-entrypoint-initdb.d:ro,z
```

- **`:ro`** — read-only (container não modifica migrations).
- **`:z`** — SELinux label compartilhado (necessário em Fedora/RHEL/CentOS com SELinux enforcing).

---

## Comandos do dia a dia

```bash
# Subir tudo (primeira vez ou após mudanças)
docker compose up --build -d

# Ver logs
docker compose logs -f server

# Ver status dos serviços
docker compose ps

# Parar sem perder dados
docker compose down

# Parar e resetar banco (recria migrations)
docker compose down -v
docker compose up --build -d

# Acessar psql
docker compose exec postgres psql -U chat -d chat

# Rebuild só do server (após mudar código Go)
docker compose up --build -d server
```
