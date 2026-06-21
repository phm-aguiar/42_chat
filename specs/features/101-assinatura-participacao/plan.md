# Plano Arquitetural — Feature 101: Assinatura de Participação

## 1. Metadados do Plano

- **Stack Tecnológico:** Go 1.24+ (Chi router, gorilla/websocket, lib/pq), React 19 + TypeScript (Vite, Tailwind CSS, Zustand), PostgreSQL 16
- **Feature Fonte:** `specs/features/101-assinatura-participacao/spec.md`
- **Escopo:** Componente `UserSignature` inline abaixo de mensagens exibindo stats de engajamento (total de mensagens, salas ativas, tier de participação), alimentado por API on-demand + WebSocket push em tempo real, sem tabela materializada.

## 2. Design de Contratos e Fronteiras

### Contrato de API (novo endpoint)

```
GET /api/users/{id}/stats
```

**Response (200):**
```json
{
  "user_id": "int",
  "login": "string",
  "avatar_url": "string",
  "total_messages": "int",
  "active_rooms": "int",
  "tier": "novato | iniciante | participante | veterano",
  "member_since": "ISO8601"
}
```

### Contrato WebSocket (evento novo no hub existente)

```
Evento: user_stats_changed
Payload: { "user_id": int, "total_messages": int, "active_rooms": int, "tier": string }
```

- Broadcast para todos os clientes conectados quando uma mensagem é enviada
- Debounce de 2s no servidor: múltiplas mensagens do mesmo usuário em <2s geram um único broadcast

### Contrato de Componente (React)

```tsx
// Props do UserSignature
interface UserSignatureProps {
  userId: number;
  // O componente busca stats via API e escuta WebSocket internamente
}
```

### Convenções

- Endpoint novo em `internal/handler/stats.go`
- Query SQL no repository layer: `internal/db/stats.go`
- Componente em `frontend/src/components/UserSignature.tsx`
- Hook de WebSocket existente (`useWebSocket`) estendido com listener para `user_stats_changed`

## 3. Decisões Arquiteturais e Justificativas (ADR)

### ADR-1: API on-demand + WebSocket push (sem tabela materializada)

- **Decisão:** Stats computados via query SQL agregada (`COUNT + COUNT DISTINCT`) na tabela `messages` no momento da requisição. Sem tabela `user_stats` derivada.
- **Justificativa:** Sem constraint de performance, a query agregada é trivial para o volume esperado. Evita estado derivado e mantém single source of truth no banco.
- **Alternativa rejeitada:** Tabela `user_stats` materializada com triggers. Introduz complexidade de sincronização e risco de inconsistência sem ganho real de latência.

### ADR-2: Stats globais, não por canal

- **Decisão:** `total_messages` e `active_rooms` são contagens globais (todas as salas), não filtradas pelo canal atual.
- **Justificativa:** Stats são marcador de reputação comunitária, não métrica de sala. Um usuário com 50 mensagens no canal A deve exibir seus stats completos no canal B. Evita fragmentação e simplifica queries.
- **Alternativa rejeitada:** Stats por canal. Fragmentaria a identidade do usuário e exigiria parâmetro `room_id` no endpoint, complexidade desnecessária.

### ADR-3: WebSocket push com debounce de 2s no servidor

- **Decisão:** Quando uma mensagem é enviada, o hub agenda um broadcast de `user_stats_changed` com debounce de 2s por `user_id`. Múltiplas mensagens do mesmo autor em <2s colapsam em um único evento.
- **Justificativa:** Evita rajadas de updates no frontend em cenários de chat rápido. 2s é imperceptível para o usuário mas reduz tráfego significativamente.
- **Alternativa rejeitada:** Broadcast imediato a cada mensagem. Sobrecarregaria o WebSocket e forçaria re-renders desnecessários no frontend.

### ADR-4: Componente autossuficiente (fetch + listen internos)

- **Decisão:** `UserSignature` recebe apenas `userId` como prop. Busca stats via `GET /api/users/{userId}/stats` no mount e escuta evento `user_stats_changed` do WebSocket para atualização em tempo real.
- **Justificativa:** Componente desacoplado — pode ser dropado em qualquer lugar (chat, futuro fórum) sem que o parent precise gerenciar fetching ou WebSocket. Single responsibility: o componente é dono dos seus dados.
- **Alternativa rejeitada:** Stats injetados via props pelo parent. Acoplaria o componente ao container e exigiria orchestration de fetching em cada uso, violando reusabilidade.

## 4. Auditoria de Constituição

- [x] **Validação SDD obrigatória:** `spec.md` + `plan.md` (este arquivo) + `tasks.md` (a ser gerado) — estrutura completa após este passo.
- [x] **Aprovação humana:** `spec.md` com `Status: approved`. `plan.md` aguarda aprovação do usuário antes do save.
- [x] **Smoke test:** `build-check` (go build + npm run build) será uma task explícita no `tasks.md`. Teste de integração: chamar `GET /api/users/{id}/stats` e verificar resposta.
- [x] **Vault Obsidian fiel:** Feature 101 terá página wiki criada via `wiki-ingest` após implementação. Feature 100 pendente de captura (gap conhecido).
- [x] **Agentes versionados:** Não se aplica diretamente — esta feature não cria agentes, apenas estende código existente.
- [x] **Skills versionadas:** Não se aplica — sem novas skills.
- [x] **Pipeline imutável:** Fluxo `spec → plan → tasks → orchestrator` sendo seguido. Próximo passo: `sdd-generate-tasks`.
- [x] **Isolamento de agentes:** Subagentes serão spawnados com contexto limpo via `agent-run`. Sem corrosão de contexto.
- [x] **Framework primeiro, app depois:** Feature 101 é parte do framework SDD (exercita o pipeline completo em feature de aplicação real).
- [x] **Knowledge management first-class:** Vault será atualizado após implementação. Journal do brainstorm já capturado em `wiki/journal/2026-06-17-brainstorm-feature-101.md`.
- [x] **Ferramentas inventadas:** Zero. Todas as tecnologias listadas existem na stack homologada (Go/Chi/gorilla/Postgres/React/Vite/Tailwind).
- [x] **Credenciais hardcoded:** Nenhuma credencial nova. Stats são públicos, sem autenticação adicional além do JWT existente.
