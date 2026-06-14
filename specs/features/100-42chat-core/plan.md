# Plano Arquitetural: 42 Chat Core (feature 100)

## 1. Metadados do Plano
- **Stack Tecnológico:** Go (Chi, gorilla/websocket), PostgreSQL (Docker), React/Vite (Tailwind, Shadcn/ui), Docker Compose, AWS EC2 t2.micro
- **Feature Fonte:** `specs/features/100-42chat-core/spec.md`
- **Referências Wiki:** [[references/42-chat-platform-architecture]], [[references/42-chat-design-system]], [[references/42-chat-engineering-requirements]], [[references/42-chat-architecture-diagram]]
- **Escopo:** MVP com sala única "general": login OAuth2 42, WebSocket Hub (modelo híbrido RWMutex + channels), persistência PostgreSQL, frontend brutalista 42, graceful shutdown, observabilidade

## 2. Design de Contratos e Fronteiras

### Estrutura do Projeto
```
cmd/
  server/
    main.go                 # Entry point: configuração, graceful shutdown
internal/
  auth/
    oauth42.go              # OAuth2 42: authorize, callback, token exchange, JWT (12h)
  chat/
    hub.go                  # WebSocket Hub: modelo híbrido RWMutex + channels
    client.go               # WebSocket Client: readPump, writePump, ping/pong
    message.go              # Modelo de mensagem
  api/
    routes.go               # Rotas REST (Chi): /api/auth/*, /api/messages, /api/me, /metrics
    handler_auth.go         # Handlers de autenticação
    handler_messages.go     # Handlers de histórico de mensagens
    middleware.go            # Middleware JWT, CORS, rate limit
  repository/
    users.go                # Queries SQL: users (upsert com current_host, find by id/login)
    messages.go             # Queries SQL: messages (insert, fetch recent, soft delete, expurgo 6 meses)
    db.go                   # Conexão PostgreSQL, pool config (max_connections=100), migrations
  cache/
    user_cache.go           # Cache anti-rate-limit 3 camadas: JWT, PostgreSQL, batch ingest
  observability/
    metrics.go              # /metrics: goroutines, memória, DB.Stats(), conexões WS ativas
web/
  src/
    App.jsx                  # Shell principal: OAuth2 redirect, Zustand store, tema 42
    components/
      ChatRoom.jsx           # Sala de chat: mensagens, input, WebSocket hook
      MessageBubble.jsx      # Bolha de mensagem (preto + borda neon)
      LoginButton.jsx        # Botão "Entrar com a 42" (lime #D4ED31)
    store/
      authStore.js           # Zustand: JWT, user info
      chatStore.js           # Zustand: mensagens, status WS
    hooks/
      useWebSocket.js        # Hook: conexão JWT, reconexão com backoff, ping/pong
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
| GET | /metrics | Métricas (goroutines, DB stats, WS connections) | Não (interno) |

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

### Contrato WebSocket Hub (Modelo Híbrido)
- **`sync.RWMutex`** protege o mapa de clients (`map[*Client]bool`)
  - Leituras de broadcast paralelas (RLock)
  - Bloqueio exclusivo apenas em insert/remove (Lock)
- **`send chan []byte`** como buffer elástico de saída por client
  - Evita bloqueio do Hub durante broadcast lento
- **Ping/Pong:** servidor envia ping a cada 30s (ticker), client responde pong
- **Read deadline:** 60s sem mensagem = desconexão
- **Write deadline:** 10s

### Modelagem PostgreSQL
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    login VARCHAR(50) NOT NULL UNIQUE,
    image_url TEXT,
    current_host VARCHAR(20),        -- ex: e1z2m4
    level NUMERIC(4,2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL REFERENCES users(id),
    content TEXT NOT NULL CHECK (char_length(content) <= 5000),
    created_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP              -- soft delete
);

CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_deleted_at ON messages(deleted_at);
```

### PostgreSQL Tuning (1GB RAM total)
| Parâmetro | Valor | Justificativa |
|---|---|---|
| `shared_buffers` | 256MB (~25% RAM) | Cache de dados em memória |
| `effective_cache_size` | 512MB | Estimativa para query planner |
| `work_mem` | 16MB | Memória por operação sort/hash |
| `max_connections` | 100 | Alinhado ao pool Go |

### Tuning Linux (EC2 t2.micro)
| Parâmetro | Valor |
|---|---|
| `fs.file-max` | 100000 |
| `ulimit -n` | 65535 |

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
  suporta concorrência real, soft delete, CHECK constraints, e migrations.
- **Alternativa Rejeitada:** SQLite — sem concorrência real, sem suporte a múltiplos
  leitores/escritores simultâneos

### ADR-3: JWT interno (12h) após OAuth2 42
- **Decisão:** Backend gera JWT próprio com 12h de expiração após validar token da 42.
  Claims: user_id, login. Validado no middleware.
- **Justificativa:** Evita chamar API 42 em cada requisição. 12h cobre um dia inteiro
  no campus, reduzindo tráfego contra rate limit da 42
- **Alternativa Rejeitada:** Sessão em cookie — não funciona bem com WebSocket upgrade

### ADR-4: Cache anti-rate-limit em 3 camadas
- **Decisão:** (1) JWT 12h elimina revalidação contínua, (2) perfil do aluno cacheado
  no PostgreSQL no primeiro login, (3) mapeamento de laboratório via ingestão batch 30s
- **Justificativa:** API 42 impõe ~2 req/s e 1200 req/h. As 3 camadas reduzem tráfego
  de N chamadas por visualização para 1 chamada por aluno por período
- **Alternativa Rejeitada:** Redis como cache externo — dependência extra desnecessária
  pra 300 alunos

### ADR-5: WebSocket Hub — Modelo Híbrido (RWMutex + send chan)
- **Decisão:** `sync.RWMutex` no mapa de clients para leituras paralelas de broadcast
  com bloqueio apenas em insert/remove. Cada client tem `send chan []byte` como buffer
  elástico de saída
- **Justificativa:** Channels puros adicionam latência de round-trip via goroutine por
  mensagem. Mutex exclusivo estrangula leituras simultâneas. O híbrido combina o melhor
  dos dois: leituras rápidas com RLock, buffer assíncrono por client
- **Alternativas Rejeitadas:** (a) Channels puros — round-trip overhead, (b) Mutex
  exclusivo — bloqueia leituras, (c) RWMutex puro — sem buffer de saída, risco de
  bloqueio no broadcast lento

### ADR-6: Frontend React com tema brutalista 42 documentado na wiki
- **Decisão:** React + Vite + Tailwind + Shadcn/ui com Zustand. Cores exatas do design
  system: Preto #000000, Lime #D4ED31 (CTA), Ciano #00E5FF (links), Magenta #FF007A
  (notificações), Azul #304FFE (sobreposições). border-radius: 0 global. Dot grid
  background. Tipografia Montserrat/Poppins/Gotham
- **Justificativa:** Sistema de design completo documentado em [[references/42-chat-design-system]].
  Tailwind config com classes `42-*` garante consistência sem CSS manual
- **Alternativa Rejeitada:** CSS customizado — difícil manter consistência com o design
  system documentado

### ADR-7: Graceful shutdown com signal handling
- **Decisão:** Interceptar SIGINT/SIGTERM → parar HTTP server → notificar clientes →
  flush buffer de mensagens → PostgreSQL → fechar pool de conexões → encerrar
- **Justificativa:** Evita corrupção de dados e desconexões abruptas. Essencial pra deploy
  contínuo sem perda de mensagens
- **Alternativa Rejeitada:** Kill imediato — perda de mensagens em buffer

### ADR-8: Observabilidade com /metrics
- **Decisão:** Endpoint `/metrics` expondo goroutines ativas, memória, DB.Stats()
  (idle connections, in-use, wait count), conexões WebSocket ativas. Goroutine
  secundária coleta DB.Stats() a cada 10s
- **Justificativa:** Essencial para diagnosticar gargalos antes que virem outage.
  DB.Stats() revela pool exhaustion, wait events, conexões idle

## 4. Auditoria de Constituição

- [x] **Validação SDD obrigatória** — Spec aprovado com Aprovado: true
- [x] **Aprovação humana** — Spec aprovado pelo autor
- [x] **Smoke test** — `go build`, `go test`, Docker Compose up
- [x] **Vault Obsidian fiel** — Documentar feature 100 no vault após implementação
- [x] **Agentes versionados** — N/A (não é agente, é aplicação)
- [x] **Skills versionadas** — N/A
- [x] **Pipeline imutável** — SDD: spec → plan → tasks → orchestrator
- [x] **Isolamento de agentes** — N/A
- [x] **Framework primeiro, app depois** — O framework já existe. Esta feature É a aplicação
- [x] **Specs são do framework** — Spec 100 descreve a aplicação
- [x] **Knowledge management first-class** — Vault será atualizado; referências wiki já documentadas
- [x] **Nunca implementar sem spec aprovada** — Spec aprovado
- [x] **Todas as dependências especificadas** — Stack completa documentada em platform-architecture
- [x] **Vault desatualizado** — Será atualizado após implementação
