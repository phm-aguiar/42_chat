# tasks.md: Feature 101 — Assinatura de Participação

> DAG de tarefas atômicas para execução pelo agent-orchestrator (feature 005).
> Formato: Papel, Dependências, Paralelizável, Arquivos.

## Fase 1: Fundação

- [x] **T001:** Criar query SQL de stats agregados — `COUNT` total de mensagens, `COUNT DISTINCT` salas ativas, computar tier (novato/iniciante/participante/veterano) baseado nos thresholds do spec
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `internal/db/stats.go`

- [x] **T002:** Criar cenários Gherkin para assinatura de participação — happy path (stats visíveis inline), usuário novato (placeholder sem mensagens), atualização via WebSocket após nova mensagem, transição de tier, stats globais (cross-channel)
  - **Papel:** QA
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `specs/features/101-assinatura-participacao/acceptance/user-signature.feature`

## Fase 2: Implementação

- [x] **T003:** Criar handler `GET /api/users/{id}/stats` — extrai user_id dos path params, chama query do repositório, retorna JSON com user_id, login, avatar_url, total_messages, active_rooms, tier, member_since
  - **Papel:** Dev
  - **Dependências:** T001
  - **Paralelizável:** true
  - **Arquivos:** `internal/handler/stats.go`

- [x] **T004:** Estender WebSocket hub existente com evento `user_stats_changed` — broadcast para todos os clientes quando uma mensagem é enviada, com debounce de 2s por user_id (múltiplas mensagens do mesmo autor em <2s colapsam em um único broadcast)
  - **Papel:** Dev
  - **Dependências:** T001
  - **Paralelizável:** true
  - **Arquivos:** `internal/ws/hub.go`

- [x] **T005:** Registrar rota `GET /api/users/{id}/stats` no Chi router — mapear para o handler criado em T003
  - **Papel:** Dev
  - **Dependências:** T003
  - **Paralelizável:** false
  - **Arquivos:** `internal/router/router.go`

- [x] **T006:** Criar componente React `UserSignature` — recebe `userId` como prop, faz fetch `GET /api/users/{userId}/stats` no mount, escuta evento `user_stats_changed` do WebSocket para atualização em tempo real, renderiza cartão com avatar, login, tier, total de mensagens, salas ativas. Placeholder visual reduzido para tier "novato" (0 mensagens)
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `frontend/src/components/UserSignature.tsx`

- [x] **T007:** Integrar `UserSignature` abaixo de cada mensagem no componente `MessageList` — passar `message.author_id` como `userId` prop, garantir que não quebra o layout do chat
  - **Papel:** Dev
  - **Dependências:** T006
  - **Paralelizável:** false
  - **Arquivos:** `frontend/src/components/MessageList.tsx`

- [x] **T008:** Criar testes unitários Go para stats query e handler — testar query com 0 mensagens (tier novato), 50 mensagens (tier iniciante), 200 mensagens (tier participante), 500 mensagens (tier veterano), múltiplas salas (COUNT DISTINCT), handler retorna 200 com payload correto, handler retorna 404 para user_id inexistente
  - **Papel:** QA
  - **Dependências:** T003
  - **Paralelizável:** true
  - **Arquivos:** `internal/db/stats_test.go`, `internal/handler/stats_test.go`

## Fase 3: Validação

- [x] **T009:** Implementar step definitions para os cenários Gherkin (T002) — steps em TypeScript para Playwright: dado usuário logado, quando abre o chat, então vê assinatura abaixo das mensagens, etc.
  - **Papel:** QA
  - **Dependências:** T002, T003
  - **Paralelizável:** false
  - **Arquivos:** `specs/features/101-assinatura-participacao/acceptance/steps.ts`

- [x] **T010:** Smoke test — `go build ./...` + `go vet ./...` + `npm run build` (frontend) + curl smoke `GET /api/users/1/stats` com JWT válido, verificar status 200 e campos obrigatórios
  - **Papel:** QA
  - **Dependências:** T003, T005, T007
  - **Paralelizável:** false
  - **Arquivos:** (execução somente, sem novos arquivos)

## Fase 4: Documentação

- [x] **T011:** Atualizar `llms.txt` com entry da feature 101 + criar página wiki `feature-101-assinatura-participacao.md` no vault com metadados, resumo das ADRs, e links para spec/plan/tasks
  - **Papel:** Dev
  - **Dependências:** T010
  - **Paralelizável:** false
  - **Arquivos:** `llms.txt`, `wiki/projects/42_chat/features/feature-101-assinatura-participacao.md`
