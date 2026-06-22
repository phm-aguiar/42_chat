---
title: "Brainstorm Feature 101 — Assinatura de Participação"
category: journal
tags: [sdd, 42chat, brainstorm, feature]
sources:
  - conversation:2026-06-17
created: "2026-06-17T03:30:00Z"
rag_score: 0.5273
updated: "2026-06-17T03:30:00Z"
summary: >-
  Sessão de brainstorm SDD que definiu e aprovou a feature 101 (Assinatura de Participação)
  — componente UserSignature inline com stats de engajamento e tiers de comunidade.
provenance:
  extracted: 0.9
  inferred: 0.1
  ambiguous: 0.0
base_confidence: 0.42
lifecycle: draft
lifecycle_changed: 2026-06-17
tier: supporting
---

# Brainstorm Feature 101 — Assinatura de Participação

*Sessão capturada: 2026-06-17*

## Topics Covered

- **DevOps local:** Vite dev server (5173), docker-compose (Go/Chi API + Postgres), SELinux fix em volume mounts
- **DevMode ativado:** `DEV_MODE: "true"` no docker-compose, endpoint `/api/auth/dev/login?login=<name>` liberado
- **Brainstorm SDD:** Entrevista completa via [[skills/sdd-brainstorm|sdd-brainstorm]] para feature 101

## Key Takeaways

1. **Feature 101 definida e aprovada** — Assinatura de Participação (User Signature) estilo chan/fórum
   - Componente `UserSignature` inline abaixo de cada mensagem (reutilizável para futuro fórum)
   - Stats: total de mensagens, salas ativas, tier de participação
   - API `GET /api/users/{id}/stats` + WebSocket push em tempo real
   - Tiers: novato (0) → iniciante (1-50) → participante (51-200) → veterano (201+)
   - Placeholder "novato" para usuário sem atividade
   - Spec em `specs/features/101-assinatura-participacao/spec.md`

2. **Abordagem A escolhida** — API on-demand + WebSocket push, sem tabela materializada
   - Stats computados via query SQL agregada na tabela `messages`
   - Rejeitadas: tabela materializada (complexidade extra), stats inline (acoplamento)
   - WebSocket com debounce de 2s para evitar rajadas em alta frequência

3. **SELinux em Fedora** — Volumes Docker precisam de `:z` no mount para relabel automático
   - Sintoma: `ls: can't open '/docker-entrypoint-initdb.d/': Permission denied`
   - Fix: `./internal/db/migrations:/docker-entrypoint-initdb.d:ro,z`
   - Aplicável a qualquer volume bind-mount em Fedora/RHEL

4. **Dev login via API** — Endpoint `/api/auth/dev/login?login=<name>` cria/atualiza mock user (ID 42) e retorna JWT
   - Só disponível com `DEV_MODE=true`
   - JWT pode ser usado no header `Authorization: Bearer <token>` para endpoints autenticados

## Decisions Made

- **Tiers de participação:** 4 níveis com thresholds simples (0 / 1-50 / 51-200 / 201+). Sem complexidade de gamificação — YAGNI.
- **Atualização em tempo real:** WebSocket (hub existente da feature 100) em vez de polling. Debounce de 2s para evitar spam.
- **Stats globais, não por canal:** Um usuário com 50 mensagens no canal A mostra stats completos no canal B. Evita fragmentação.
- **Implementação imediata no chat:** Componente desenhado para ser reutilizável no fórum futuro, mas primeira integração é no chat atual.

## Open Questions

- Feature 100 (42chat-core) ainda não tem página no wiki. Precisa ser capturada.
- Feature 101 aguarda `sdd-generate-plan` → `plan.md` → `sdd-generate-tasks` → `tasks.md` → implementação.
- Pipeline continua amanhã.

## Related

- [[skills/sdd-brainstorm]] — Skill usada na entrevista
- [[concepts/sdd]] — Metodologia SDD
- [[projects/42_chat/42_chat]] — Visão geral do projeto
- [[projects/42_chat/skills/sdd-brainstorm]] — Skill instanciada no projeto
