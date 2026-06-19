# Spec: 42 Chat Core (MVP)

## Metadados
- **ID:** 100
- **Status:** draft
- **Aprovado:** true
- **Autor:** phm-aguiar
- **Data:** 2026-06-14
- **Stack:** Go, React, PostgreSQL, Docker
- **Referências:** [[references/42-chat-platform-architecture]], [[references/42-chat-design-system]], [[references/42-chat-engineering-requirements]], [[references/42-chat-architecture-diagram]]

## Propósito
> Chat em tempo real para a 42 São Paulo (~300 alunos simultâneos), substituindo
> Slack/Discord com integração nativa à API da 42. MVP focado: login OAuth2 42,
> WebSocket, sala única "general", mensagens persistidas, estilo brutalista 42.

O campus perdeu o Discord e os alunos têm dificuldade com o Slack. O 42 Chat
resolve isso com uma plataforma leve, integrada à intra da 42, que facilita a
comunicação P2P — essencial para avaliações, pair programming e grupos de estudo.

## Escopo

### Dentro do escopo (MVP)
- **Autenticação:** Login exclusivo via OAuth2 da 42. JWT interno (12h) para sessão
- **Chat em tempo real:** WebSocket (gorilla/websocket) com sala única "general"
- **Persistência:** PostgreSQL para usuários (com `current_host`) e mensagens
- **Cache anti-rate-limit:** 3 camadas — JWT (evita revalidação), cache PostgreSQL no primeiro login, ingestão batch para mapeamento
- **Frontend:** React + Vite + Tailwind + Shadcn/ui. Tema brutalista 42 (cores exatas da wiki)
- **Deploy:** Docker Compose (Go + PostgreSQL). Alvo: AWS EC2 t2.micro
- **API REST:** Rotas para histórico de mensagens, status do usuário, métricas
- **Graceful shutdown:** Interceptação SIGINT/SIGTERM, drenar Hub, flush buffer → PostgreSQL
- **Observabilidade:** `/metrics` com goroutines, memória, DB.Stats(), conexões WS
- **Segurança:** JWT no middleware, CORS, rate limit. Credenciais via env vars. NUNCA hardcode secrets.
- **Dev Mode:** `DEV_MODE=true` habilita `/api/auth/dev/login?login=marvin` para testes sem OAuth2 real.
- **Redirect URI configurável:** `FORTYTWO_REDIRECT_URI` e `VITE_42_REDIRECT_URI` unificam o redirect entre frontend, backend e app 42 Intra.
- **Docker Compose integrado:** PostgreSQL + server com variáveis do `.env`, healthcheck, migration automática.

### Fora do escopo (features futuras)
- **Matchmaking de avaliação** (/eval) — Feature 101 (algoritmo documentado em engineering-requirements)
- **Campus map** (localização em tempo real) — Feature 102 (ingestão batch 30s, diff propagation)
- **TUI cliente terminal** (Bubbletea) — Feature 103
- **Painel admin Bocal** (moderação, kill switch) — Feature 104
- **Salas múltiplas** (públicas, privadas, pair programming) — Feature 105
- **Mensagens diretas (DM)** — Feature 106
- **Salas efêmeras** (/pair) — Feature 107 (janela de tolerância WiFi 5min, GC automático)

## Comportamento Esperado

### Cenário Principal (Happy Path)
1. Aluno acessa https://chat.42sp.org.br
2. Redirecionado para OAuth2 da 42 (authorize endpoint)
3. Autoriza → callback para o backend com authorization code
4. Backend troca code por token (POST /oauth/token)
5. Backend busca dados do aluno (GET /v2/me) e upsert no PostgreSQL (id, login, image_url, current_host, level)
6. Backend gera JWT interno (12h) e retorna pro frontend
7. Frontend armazena JWT (Zustand) e conecta WebSocket com token
8. Aluno vê a sala "general" com histórico recente (últimas 50 mensagens via REST)
9. Envia mensagem → WebSocket → broadcast para todos conectados → persiste PostgreSQL
10. Recebe mensagens de outros alunos em tempo real
11. Logout/desconexão → WebSocket fecha, JWT expira

### Cenário: Reconexão
1. Aluno perde conexão (wi-fi do campus)
2. Frontend detecta WebSocket close e tenta reconectar com backoff exponencial
3. Reconecta → recebe mensagens perdidas (timestamp > última recebida)
4. UI mostra indicador "reconectando..."

### Cenário: Token expirado
1. JWT expira durante sessão
2. Próxima requisição REST retorna 401
3. Frontend redireciona para login OAuth2
4. Se ainda tiver cookie de sessão na 42, login é transparente (sem re-autenticação)

### Cenário: Rate limit da API 42
1. Múltiplos alunos logam simultaneamente
2. Cache 3 camadas: JWT 12h (sem revalidação), perfil em PostgreSQL (1 chamada por aluno), ingestão batch (30s)
3. Se API 42 retornar 429, backend usa cache e agenda retry

## Edge Cases
- **300 conexões simultâneas:** Tuning Linux: fs.file-max=100000, ulimit -n 65535
- **Race condition no Hub:** Modelo híbrido — sync.RWMutex no mapa de clients, send chan como buffer de saída
- **Load balancer timeout:** Ping/Pong a cada 30s (read deadline 60s)
- **Graceful shutdown:** Sinal → parar accept → notificar clientes → flush buffer → fechar DB pool
- **Aluno sem foto:** Placeholder com iniciais em círculo, fundo dot grid, borda cor de acento
- **Mensagem muito longa:** Limite de 5000 caracteres (CHECK constraint no PostgreSQL)
- **Conexão duplicada:** Mesmo aluno em múltiplas abas — cada aba = um client WebSocket independente
- **Logs de auditoria:** Toda mensagem tem user_id + timestamp. Soft delete (deleted_at), nunca hard delete
- **PostgreSQL tuning (1GB RAM):** shared_buffers=256MB, effective_cache_size=512MB, work_mem=16MB, max_connections=100

## Constraints
- **Escala:** Máximo 300 conexões simultâneas (campus presencial)
- **Infra:** AWS EC2 t2.micro (1 vCPU, 1 GB RAM). Go + PostgreSQL no mesmo host
- **Latência:** Mensagens em < 500ms (WebSocket local ao campus)
- **Segurança:** OAuth2 42 obrigatório. JWT 12h. HTTPS (Let's Encrypt). Credenciais via env vars
- **Privacidade:** Retenção de mensagens por 6 meses (LGPD). Cron job de expurgo
- **Estilo visual:** Sistema de design brutalista 42 documentado em [[references/42-chat-design-system]]
- **Cores exatas:** Preto #000000, Branco #FFFFFF, Lime #D4ED31, Ciano #00E5FF, Magenta #FF007A, Azul #304FFE
- **Tipografia:** Montserrat / Poppins / Gotham, títulos Black/Extra-Bold em CAIXA ALTA
- **border-radius: 0** em todos os componentes. Flat design, cantos secos
- **Dot grid background:** `radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px)`
- **Avatar:** grayscale(100%) contrast(120%), borda 2px cor de acento, fundo dot grid

## Critérios de Sucesso
- [ ] Login OAuth2 42 funcional (happy path + token expirado)
- [ ] WebSocket conecta e recebe mensagens em tempo real
- [ ] Mensagens persistidas no PostgreSQL e recuperadas no histórico
- [ ] Frontend renderiza com tema brutalista 42 (cores exatas, dot grid, avatares estilizados)
- [ ] Graceful shutdown: servidor desliga sem corromper mensagens
- [ ] Rate limit da API 42 tratado com cache 3 camadas
- [ ] Docker Compose sobe ambiente completo (go + postgres)
- [ ] 300 conexões simultâneas sem crash (teste de carga)
- [ ] Métricas expostas em /metrics (goroutines, DB stats, conexões WS)
- [ ] Mensagens expurgadas após 6 meses (cron job)
- [ ] Deploy funcional em EC2 t2.micro

## Stack Tecnológica

| Camada | Tecnologia | Justificativa |
|---|---|---|
| Linguagem | Go | Alta concorrência, baixo consumo de RAM |
| WebSocket | gorilla/websocket | Padrão ouro, ping/pong nativo |
| Roteamento | Chi | Minimalista, interface padrão Go |
| Banco | PostgreSQL (Docker) | Relacionamentos, auditoria, integridade transacional |
| Autenticação | OAuth2 42 + JWT (12h) | Integração nativa, sem gestão de senhas |
| Frontend | React + Vite | Build rápido, Module Federation futuro |
| Estilo | Tailwind + Shadcn/ui | Componentes copy-paste, customizáveis (rounded-none) |
| Estado | Zustand | Simples, singleton no Module Federation |
| Container | Docker Compose | Ambiente reproduzível, .env integrado |
| Infra | AWS EC2 t2.micro | Free tier, suficiente pra 300 alunos |
| CI/CD | GitHub Actions + Bitwarden CLI | Deploy com injeção segura de credenciais |

## Variáveis de Ambiente

| Variável | Obrigatória | Default | Descrição |
|---|---|---|---|
| `PORT` | Não | `8080` | Porta do servidor HTTP |
| `DATABASE_URL` | Não | `postgres://chat:***@localhost:5432/chat?sslmode=disable` | Conexão PostgreSQL |
| `JWT_SECRET` | Sim (prod) | `change-me-in-production` | Chave HS256 para JWT |
| `FORTYTWO_CLIENT_ID` | Sim (prod) | — | Client ID do app 42 Intra |
| `FORTYTWO_CLIENT_SECRET` |  Sim (prod) | — | Client Secret do app 42 Intra |
| `FORTYTWO_REDIRECT_URI` | Não | `http://localhost:5173` | Redirect URI (deve bater com app 42) |
| `FORTYTWO_API_URL` | Não | `https://api.intra.42.fr` | Base URL da API 42 |
| `DEV_MODE` | Não | `false` | Habilita `/api/auth/dev/login` |
| `DEV_USER` | Não | `marvin` | Login padrão do dev login |
| `POSTGRES_USER` | Não | `chat` | Usuário PostgreSQL (Docker) |
| `POSTGRES_PASSWORD` | Não | `banana42` | Senha PostgreSQL (Docker) |
| `POSTGRES_DB` | Não | `chat` | Nome do banco (Docker) |

### Frontend (Vite — prefixo `VITE_`)

| Variável | Default | Descrição |
|---|---|---|
| `VITE_DEV_MODE` | `false` | Mostra botão "Dev Login" |
| `VITE_API_URL` | (vazio) | URL base da API (vazio = proxy Vite) |
| `VITE_42_CLIENT_ID` | `dev-client-id` | Client ID para link OAuth2 |
| `VITE_42_REDIRECT_URI` | `http://localhost:5173` | Redirect URI (deve bater com `FORTYTWO_REDIRECT_URI`) |

## Modelagem de Dados (MVP)

### users
| Coluna | Tipo | Descrição |
|---|---|---|
| id | INT PK | ID da API 42 |
| login | VARCHAR(50) UNIQUE | Login da intra (ex: marvin) |
| image_url | TEXT | URL da foto de perfil |
| current_host | VARCHAR(20) | Localização no campus (ex: e1z2m4) |
| level | NUMERIC(4,2) | Nível na intra |
| created_at | TIMESTAMP | — |

### messages
| Coluna | Tipo | Descrição |
|---|---|---|
| id | UUID PK | gen_random_uuid() |
| user_id | INT FK → users | Autor |
| content | TEXT | Máx 5000 chars (CHECK constraint) |
| created_at | TIMESTAMP | Indexado |
| deleted_at | TIMESTAMP | Soft delete (auditoria) |

## Abordagem Escolhida
> **Backend Go monolítico + Frontend React.** Go serve REST API e WebSocket Hub
> no mesmo processo. Chi para rotas, gorilla/websocket para upgrade. PostgreSQL
> persiste usuários e mensagens com soft delete. Cache 3 camadas anti-rate-limit.
> Modelo híbrido de concorrência: sync.RWMutex no mapa + send chan como buffer.
> Frontend React + Vite + Tailwind + Shadcn/ui com tema brutalista 42 documentado
> em [[references/42-chat-design-system]]. Deploy via Docker Compose + GitHub Actions.

### Alternativas Consideradas
| Abordagem | Trade-off | Por que não |
|-----------|-----------|-------------|
| Channels puros no Hub | Go idiomático | Round-trip via goroutine por mensagem adiciona latência |
| Mutex exclusivo no Hub | Simples | Bloqueia leituras simultâneas, estrangulamento em broadcast |
| SQLite ao invés de PostgreSQL | Zero infra de banco | Sem concorrência real, sem soft delete nativo |
| Next.js ao invés de Vite | Mais features | Overengineering. Vite é mais leve e rápido |
