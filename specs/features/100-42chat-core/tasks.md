# tasks.md: 42 Chat Core (MVP)

> Feature 100. DAG para execução pelo `agent-orchestrator`.
> Total: 23 tasks em 4 fases.

## Fase 1: Fundação

- [x] **T001:** Criar estrutura Go: `cmd/server/`, `internal/{auth,ws,api,db,config,model}/`, `go.mod` com deps (chi, gorilla/websocket, golang-jwt v5, lib/pq)
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `go.mod`, `go.sum`

- [x] **T002:** Criar schema PostgreSQL: migration SQL com `users` + `messages` (UUID PK, FK, CHECK ≤5000, soft delete, índices)
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `internal/db/migrations/001_init.sql`

- [x] **T003:** Criar modelos Go: structs `User` e `Message` com tags `json` + `db`, tipos seguros
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `internal/model/user.go`, `internal/model/message.go`

- [x] **T004:** Criar package `config`: env vars (PORT, DATABASE_URL, JWT_SECRET, 42_CLIENT_ID, 42_CLIENT_SECRET, 42_API_URL) com defaults + validação
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `internal/config/config.go`

## Fase 2: Implementação

- [x] **T005:** Criar DB package: connection pool (`*sql.DB`), queries parametrizadas (upsert user, insert message, select recent messages, select user by id)
  - **Papel:** Dev
  - **Dependências:** T002, T003
  - **Paralelizável:** true
  - **Arquivos:** `internal/db/postgres.go`, `internal/db/queries.go`

- [x] **T006:** Criar auth package: OAuth2 42 callback (troca code → token → `/v2/me` → upsert user), geração JWT (12h, HS256), middleware Chi (extrai claims, injeta context)
  - **Papel:** Dev
  - **Dependências:** T003, T004
  - **Paralelizável:** true
  - **Arquivos:** `internal/auth/oauth.go`, `internal/auth/jwt.go`, `internal/auth/middleware.go`

- [x] **T007:** Criar WebSocket Hub: `sync.RWMutex` no mapa de clients, `send chan` como buffer de saída, métodos `Connect`, `Disconnect`, `Broadcast`
  - **Papel:** Dev
  - **Dependências:** T003
  - **Paralelizável:** true
  - **Arquivos:** `internal/ws/hub.go`

- [x] **T008:** Criar WS handler: upgrade HTTP → WebSocket, valida JWT no connect, read/write pumps (ping/pong 30s, read deadline 60s), serialização JSON dos tipos `message` e `system`
  - **Papel:** Dev
  - **Dependências:** T006, T007
  - **Paralelizável:** false
  - **Arquivos:** `internal/ws/handler.go`

- [x] **T009:** Criar REST handlers: `GET /api/messages?before=&limit=50` (autenticado), `GET /api/users/:id`, `GET /metrics` (Prometheus: goroutines, memória, DB.Stats(), conexões WS)
  - **Papel:** Dev
  - **Dependências:** T005, T006
  - **Paralelizável:** true
  - **Arquivos:** `internal/api/messages.go`, `internal/api/users.go`, `internal/api/metrics.go`

- [x] **T010:** Criar server bootstrap: `cmd/server/main.go` com Chi routes (auth callback, REST, WS upgrade, /metrics), graceful shutdown (SIGINT/SIGTERM → parar accept → notificar clients → flush buffer → fechar DB pool), Dockerfile multi-stage
  - **Papel:** Dev
  - **Dependências:** T008, T009
  - **Paralelizável:** false
  - **Arquivos:** `cmd/server/main.go`, `Dockerfile`

- [x] **T011:** Criar frontend: `npm create vite@latest` React+TS, Tailwind v4, Shadcn/ui, tema brutalista 42 (cores exatas: #000, #FFF, #D4ED31, #00E5FF, #FF007A, #304FFE, border-radius:0, dot grid background, Montserrat/Poppins)
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `frontend/package.json`, `frontend/vite.config.ts`, `frontend/tailwind.config.ts`, `frontend/src/index.css`, `frontend/src/main.tsx`

- [x] **T012:** Criar OAuth2 login flow: botão "Login com 42" → redirect → callback page troca code por JWT → Zustand auth store (token, user, isAuthenticated, login, logout)
  - **Papel:** Dev
  - **Dependências:** T011
  - **Paralelizável:** true
  - **Arquivos:** `frontend/src/stores/auth.ts`, `frontend/src/pages/Login.tsx`, `frontend/src/pages/Callback.tsx`

- [x] **T013:** Criar WebSocket client + ChatRoom: hook `useWebSocket` (connect com token, reconnect com backoff exponencial, ping/pong), componente `ChatRoom` com dot grid background, header com logo 42 + status bar
  - **Papel:** Dev
  - **Dependências:** T011
  - **Paralelizável:** true
  - **Arquivos:** `frontend/src/lib/ws.ts`, `frontend/src/components/ChatRoom.tsx`

- [x] **T014:** Criar MessageList + MessageInput: scroll infinito (carrega histórico ao subir), avatar com iniciais + borda cor de acento + fundo dot grid, input com limite 5000 chars + contador, envio via WebSocket
  - **Papel:** Dev
  - **Dependências:** T011, T013
  - **Paralelizável:** false
  - **Arquivos:** `frontend/src/components/MessageList.tsx`, `frontend/src/components/MessageInput.tsx`, `frontend/src/components/Avatar.tsx`

- [x] **T015:** Criar cenários Gherkin: `chat.feature` cobrindo happy path (login → enviar mensagem → ver broadcast), reconexão (desconecta → reconecta → recupera mensagens), token expirado (401 → redirect login), rate limit (cache 3 camadas)
  - **Papel:** QA
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `specs/features/100-42chat-core/acceptance/chat.feature`

- [x] **T016:** Criar testes unitários Go: model (User, Message marshaling), config (env parsing, defaults), db queries (mock `*sql.DB`), JWT (geração, expiração, middleware)
  - **Papel:** QA
  - **Dependências:** T003, T004, T005, T006
  - **Paralelizável:** true
  - **Arquivos:** `internal/model/*_test.go`, `internal/config/config_test.go`, `internal/db/queries_test.go`, `internal/auth/jwt_test.go`, `internal/auth/middleware_test.go`

## Fase 3: Validação

- [x] **T017:** Criar testes de integração WebSocket: hub broadcast (N clients recebem), reconnect (backoff, recupera mensagens perdidas), ping/pong timeout, graceful shutdown (clientes notificados)
  - **Papel:** QA
  - **Dependências:** T008, T010, T015
  - **Paralelizável:** true
  - **Arquivos:** `internal/ws/hub_test.go`, `internal/ws/handler_test.go`

- [x] **T018:** Criar testes de integração REST: auth flow completo (code → JWT → /v2/me → upsert), rate limit (429 → cache), token expired (401 → redirect), histórico de mensagens (pagination)
  - **Papel:** QA
  - **Dependências:** T009, T010, T015
  - **Paralelizável:** true
  - **Arquivos:** `internal/api/messages_test.go`, `internal/api/auth_test.go`

- [x] **T019:** Rodar lint: golangci-lint no backend (govet, staticcheck, errcheck, gofmt) + ESLint/Prettier no frontend, corrigir automaticamente
  - **Papel:** QA
  - **Dependências:** T010, T014
  - **Paralelizável:** true
  - **Arquivos:** `.golangci.yml`, `frontend/.eslintrc.cjs`

- [x] **T020:** Criar testes E2E Playwright: login OAuth2 → conectar WebSocket → enviar mensagem → verificar broadcast em segundo client → testar reconexão
  - **Papel:** QA
  - **Dependências:** T010, T014
  - **Paralelizável:** true
  - **Arquivos:** `test/e2e/chat.spec.ts`, `test/e2e/auth.spec.ts`

- [x] **T021:** Smoke test fim a fim: `docker-compose up`, health check, 2 clientes WS (gorilla/websocket), 1 envia mensagem, outro recebe, graceful shutdown (`docker-compose down`), verifica 0 mensagens perdidas
  - **Papel:** QA
  - **Dependências:** T010, T014, T017, T018
  - **Paralelizável:** false
  - **Arquivos:** `test/smoke_test.go`

## Fase 4: Documentação

- [x] **T022:** Criar README.md: setup (pré-requisitos, variáveis de ambiente, docker-compose up), arquitetura (diagrama Mermaid), endpoints (REST + WS), deploy (EC2 t2.micro, Let's Encrypt, systemd)
  - **Papel:** Dev
  - **Dependências:** T010, T014, T021
  - **Paralelizável:** false
  - **Arquivos:** `README.md`

- [x] **T023:** Atualizar `llms.txt` e `AGENTS.md`: adicionar entry point da feature 100 com links para spec.md, plan.md, tasks.md, wiki references
  - **Papel:** Dev
  - **Dependências:** T022
  - **Paralelizável:** false
  - **Arquivos:** `llms.txt`
