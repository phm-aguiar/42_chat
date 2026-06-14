# tasks.md: 42 Chat Core (feature 100)

## Fase 1: Fundação

- [ ] **T001:** Inicializar módulo Go (`go mod init`) + estrutura de diretórios (cmd/server, internal/{auth,chat,api,repository,cache,observability})
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `go.mod`, `cmd/server/main.go` (esqueleto), diretórios

- [ ] **T002:** Criar modelos Go: Message (id, user_id, content, timestamps) e User (id, login, image_url, level)
  - **Papel:** Dev
  - **Dependências:** T001
  - **Paralelizável:** true
  - **Arquivos:** `internal/chat/message.go`, `internal/repository/models.go`

- [ ] **T003:** Configurar Docker Compose (Go + PostgreSQL) e Dockerfile multi-stage
  - **Papel:** Dev
  - **Dependências:** T001
  - **Paralelizável:** true
  - **Arquivos:** `docker-compose.yml`, `Dockerfile`

## Fase 2: PostgreSQL + Auth

- [ ] **T004:** Criar conexão PostgreSQL com pool (max_connections=100) + migrations SQL (CREATE TABLE users com current_host, messages com CHECK content length, índices) + tuning (shared_buffers, effective_cache_size, work_mem)
  - **Papel:** Dev
  - **Dependências:** T001
  - **Paralelizável:** false
  - **Arquivos:** `internal/repository/db.go`, `internal/repository/migrations/`

- [ ] **T005:** Implementar repositório: queries users (upsert, find by id/login) + messages (insert, fetch recent with limit, soft delete, expurgo > 6 meses)
  - **Papel:** Dev
  - **Dependências:** T004
  - **Paralelizável:** true
  - **Arquivos:** `internal/repository/users.go`, `internal/repository/messages.go`

- [ ] **T006:** Implementar OAuth2 42: authorize URL, callback handler, token exchange, fetch /v2/me (com current_host), JWT generate (12h) + validate. Cache anti-rate-limit 3 camadas
  - **Papel:** Dev
  - **Dependências:** T004
  - **Paralelizável:** true
  - **Arquivos:** `internal/auth/oauth42.go`

## Fase 3: WebSocket Hub + Chat

- [ ] **T007:** Criar WebSocket Hub com modelo híbrido: sync.RWMutex no mapa de clients (RLock em broadcast, Lock em insert/remove) + send chan como buffer elástico de saída por client. Channels: register, unregister, broadcast
  - **Papel:** Dev
  - **Dependências:** T002
  - **Paralelizável:** false
  - **Arquivos:** `internal/chat/hub.go`

- [ ] **T008:** Criar WebSocket Client (readPump, writePump, ping/pong 30s, read timeout 60s, write timeout 10s, send channel)
  - **Papel:** Dev
  - **Dependências:** T007
  - **Paralelizável:** false
  - **Arquivos:** `internal/chat/client.go`

- [ ] **T009:** Integrar JWT validation no WebSocket upgrade (validar token antes de promover conexão)
  - **Papel:** Dev
  - **Dependências:** T006, T008
  - **Paralelizável:** false
  - **Arquivos:** `internal/chat/client.go` (função de upgrade)

## Fase 4: API REST

- [ ] **T010:** Criar rotas REST (Chi) + middleware JWT + CORS + handlers: GET /api/auth/login, GET /api/auth/callback, GET /api/me, GET /api/messages
  - **Papel:** Dev
  - **Dependências:** T006, T005
  - **Paralelizável:** false
  - **Arquivos:** `internal/api/routes.go`, `internal/api/handler_auth.go`, `internal/api/handler_messages.go`, `internal/api/middleware.go`

- [ ] **T011:** Integrar graceful shutdown: signal handling (SIGINT/SIGTERM), parar HTTP server, notificar clientes WS, flush buffer → PostgreSQL, fechar DB pool. Tuning Linux: fs.file-max, ulimit
  - **Papel:** Dev
  - **Dependências:** T007, T010
  - **Paralelizável:** false
  - **Arquivos:** `cmd/server/main.go`

## Fase 5: Frontend

- [ ] **T012:** Criar frontend React: Vite init + Tailwind config com cores 42-* (#D4ED31, #00E5FF, #FF007A, #304FFE) + Shadcn/ui + Zustand stores (authStore, chatStore)
  - **Papel:** Dev
  - **Dependências:** T006
  - **Paralelizável:** true
  - **Arquivos:** `web/src/App.jsx`, `web/src/store/authStore.js`, `web/src/store/chatStore.js`, `web/vite.config.js`, `web/tailwind.config.js`

- [ ] **T013:** Criar ChatRoom + MessageBubble + useWebSocket hook (conexão com token JWT, reconexão com backoff, ping/pong)
  - **Papel:** Dev
  - **Dependências:** T012, T009
  - **Paralelizável:** false
  - **Arquivos:** `web/src/components/ChatRoom.jsx`, `web/src/components/MessageBubble.jsx`, `web/src/hooks/useWebSocket.js`

- [ ] **T014:** Aplicar tema brutalista 42 completo: cores exatas, border-radius:0 global, dot grid background (radial-gradient), avatar grayscale + borda neon, títulos CAIXA ALTA Black/Extra-Bold, botão lime flat, balões mensagem com borda neon
  - **Papel:** Dev
  - **Dependências:** T012
  - **Paralelizável:** true
  - **Arquivos:** `web/tailwind.config.js`, `web/src/index.css`

## Fase 6: Documentação

- [ ] **T015:** Atualizar BACKLOG.md: marcar feature 100 como concluída (ou status atual)
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `specs/BACKLOG.md`

- [ ] **T016:** Criar página wiki: `wiki/projects/42_chat/features/feature-100-42chat-core.md`
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `wiki/projects/42_chat/features/feature-100-42chat-core.md`
