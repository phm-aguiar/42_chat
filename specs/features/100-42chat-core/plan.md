# Plano Arquitetural: 42 Chat Core (feature 100)

## 1. Metadados do Plano
- **Stack Tecnológico:** Go (Chi, gorilla/websocket), PostgreSQL, React/Vite (Tailwind, Shadcn/ui), Docker Compose, AWS EC2 t2.micro
- **Feature Fonte:** `specs/features/100-42chat-core/spec.md`
- **Escopo:** MVP com sala única "general": login OAuth2 42, WebSocket Hub, persistência PostgreSQL, frontend brutalista, graceful shutdown

## 2. Design de Contratos e Fronteiras

### Estrutura do Projeto
```
cmd/
  server/
    main.go                 # Entry point: configura e inicia o servidor
internal/
  auth/
    oauth42.go              # OAuth2 42: authorize, callback, token exchange, JWT
  chat/
    hub.go                  # WebSocket Hub: gerencia clients, broadcast, register/unregister
    client.go               # WebSocket Client: leitura/escrita, ping/pong, readPump/writePump
    message.go              # Modelo de mensagem
  api/
    routes.go               # Rotas REST: /api/auth/*, /api/messages, /api/me, /metrics
    handler_auth.go         # Handlers de autenticação
    handler_messages.go     # Handlers de histórico de mensagens
    middleware.go            # Middleware JWT, CORS, rate limit
  repository/
    users.go                # Queries SQL: users (upsert, find by id/login)
    messages.go             # Queries SQL: messages (insert, fetch recent, soft delete, expurgo)
    db.go                   # Conexão PostgreSQL, pool, migrations
  cache/
    user_cache.go           # Cache em memória: perfil do aluno (15 min TTL)
  observability/
    metrics.go              # Métricas Prometheus: goroutines, conexões WS, latência DB
web/
  src/
    App.jsx                  # Shell principal: OAuth2 redirect, Zustand store, tema
    components/
      ChatRoom.jsx           # Sala de chat: mensagens, input, WebSocket
      MessageBubble.jsx      # Bolha de mensagem (estilo brutalista)
      LoginButton.jsx        # Botão "Entrar com a 42"
    store/
      authStore.js           # Zustand: JWT, user info
      chatStore.js           # Zustand: mensagens, status WS
    hooks/
      useWebSocket.js        # Hook: conexão, reconexão, ping/pong
docker-compose.yml           # Go + PostgreSQL
Dockerfile                   # Build multi-stage Go
```

### Contrato REST API
| Método | Rota | Descrição | Auth |
|---|---|---|---|
| GET | /api/auth/login | Redireciona para OAuth2 42 | Não |
| GET | /api/auth/callback | Callback OAuth2, retorna JWT | Não |
| GET | /api/me | Dados do usuário logado | JWT |
| GET | /api/messages?before=&limit=50 | Histórico de mensagens | JWT |
| GET | /metrics | Métricas Prometheus | Não (interno) |

### Contrato WebSocket
- **Endpoint:** `ws://host/ws?token=<JWT>`
- **Upgrade:** Servidor valida JWT antes do upgrade
- **Mensagem (cliente → servidor):**
  ```json
  {"type": "message", "content": "texto da mensagem"}
  ```
- **Mensagem (servidor → cliente):**
  ```json
  {"type": "message", "id": "uuid", "user": {"login": "marvin", "image_url": "..."}, "content": "texto", "created_at": "iso8601"}
  ```
- **Sistema (servidor → cliente):**
  ```json
  {"type": "system", "content": "marvin entrou na sala"}
  ```

### Contrato WebSocket Hub
- `Hub` gerencia `map[*Client]bool` protegido por `sync.RWMutex`
- `register` channel: novo client conectado
- `unregister` channel: client desconectado
- `broadcast` channel: mensagem para todos os clients
- Ping/Pong: servidor envia ping a cada 30s, client responde pong
- Read timeout: 60s sem mensagem = desconexão
- Write timeout: 10s

### Modelagem PostgreSQL (Migrations)
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    login VARCHAR(50) NOT NULL UNIQUE,
    image_url TEXT,
    level NUMERIC(4,2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL REFERENCES users(id),
    content TEXT NOT NULL CHECK (char_length(content) <= 5000),
    created_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_deleted_at ON messages(deleted_at);
```

## 3. Decisões Arquiteturais (ADRs)

### ADR-1: Monolito Go (API REST + WebSocket no mesmo processo)
- **Decisão:** Chi para REST e gorilla/websocket no mesmo binário Go
- **Justificativa:** 300 conexões não justificam microserviços. Um processo Go gerencia
  tudo com goroutines. Menos latência (sem rede entre serviços), deploy mais simples
- **Alternativa Rejeitada:** Separar REST e WebSocket em serviços diferentes —
  overengineering pra 300 usuários

### ADR-2: PostgreSQL desde o MVP (não SQLite)
- **Decisão:** PostgreSQL em container Docker desde o primeiro commit
- **Justificativa:** Auditoria do Bocal exige integridade transacional. PostgreSQL
  suporta concorrência real, soft delete, e migrations. Evita migração dolorosa depois
- **Alternativa Rejeitada:** SQLite — sem concorrência real, sem suporte a múltiplos
  leitores/escritores simultâneos

### ADR-3: JWT interno após OAuth2 42
- **Decisão:** Backend gera JWT próprio após validar token da 42
- **Justificativa:** Evita chamar API 42 em cada requisição. JWT carrega user_id
  e login, validado no middleware. Expiração de 24h
- **Alternativa Rejeitada:** Sessão em cookie — não funciona bem com WebSocket upgrade

### ADR-4: Cache em memória para perfil do aluno
- **Decisão:** `sync.Map` em Go com TTL de 15 minutos para dados da API 42
- **Justificativa:** API 42 tem rate limit (~2 req/s). Buscar foto/nível/host a cada
  mensagem quebraria o limite. Cache resolve com zero dependência externa
- **Alternativa Rejeitada:** Redis — dependência extra desnecessária pra 300 alunos

### ADR-5: WebSocket Hub com Channels (não Mutex direto)
- **Decisão:** Goroutine dedicada ao Hub, comunica via channels (register, unregister, broadcast)
- **Justificativa:** Channels são idiomáticos em Go e evitam race conditions sem locks manuais.
  Uma goroutine central processa todas as operações no mapa de clients sequencialmente
- **Alternativa Rejeitada:** sync.RWMutex direto — mais propenso a deadlocks em código concorrente

### ADR-6: Frontend React com Microfrontends futuros
- **Decisão:** React + Vite + Tailwind + Shadcn/ui com Zustand. Estrutura preparada pra
  Module Federation (Shell + Microapps) mas sem implementar no MVP
- **Justificativa:** Shadcn/ui dá componentes copy-paste customizáveis (border-radius: 0).
  Zustand é simples. Module Federation fica pra features futuras
- **Alternativa Rejeitada:** Next.js — overengineering. Vite é mais leve e rápido

### ADR-7: Graceful shutdown com signal handling
- **Decisão:** Interceptar SIGINT/SIGTERM, fechar HTTP server, drenar WebSocket Hub,
  commitar mensagens pendentes no PostgreSQL, fechar pool de conexões
- **Justificativa:** Evita corrupção de dados e desconexões abruptas. Essencial pra deploy
  contínuo sem perda de mensagens
- **Alternativa Rejeitada:** Kill imediato — perda de mensagens em buffer

## 4. Auditoria de Constituição

- [x] **Validação SDD obrigatória** — Spec aprovado com Aprovado: true
- [x] **Aprovação humana** — Spec aprovado pelo autor
- [x] **Smoke test** — `go build`, `go test`, Docker Compose up
- [x] **Vault Obsidian fiel** — Documentar feature 100 no vault após implementação
- [x] **Agentes versionados** — N/A (não é agente, é aplicação)
- [x] **Skills versionadas** — N/A
- [x] **Pipeline imutável** — SDD: spec → plan → tasks → orchestrator
- [x] **Isolamento de agentes** — N/A
- [x] **Framework primeiro, app depois** — Esta feature É a aplicação. O framework já existe (agentes, skills, wiki)
- [x] **Specs são do framework** — Spec 100 descreve a aplicação, não o framework. OK — é o propósito final do framework
- [x] **Knowledge management first-class** — Vault será atualizado
- [x] **Nunca implementar sem spec aprovada** — Spec aprovado
- [x] **Corrosão de contexto** — N/A
- [x] **Agentes que delegam** — N/A
- [x] **Skills fora do padrão** — N/A
- [x] **Ferramentas inventadas** — Todas as dependências estão em tech.md ou especificadas aqui
- [x] **Vault desatualizado** — Será atualizado após implementação
