---
title: "Sessão 18/jun — Feature 100 execução, OAuth2 42, credenciais"
category: journal
tags: [sessao, journal, feature-100, oauth2, debug, constitution]
sources:
  - "conversation:2026-06-18"
summary: "Execução da feature 100 (42 Chat MVP) com agent-orchestrator fase a fase, debug do fluxo OAuth2 42 (redirect_uri, StrictMode, shell env), regra anti-hardcoded-credentials no constitution, .env.example limpo."
provenance:
  extracted: 0.90
  inferred: 0.05
  ambiguous: 0.05
base_confidence: 0.60
lifecycle: draft
lifecycle_changed: "2026-06-18"
created: 2026-06-18
updated: 2026-06-18
---
# Sessão 18/jun — Feature 100, OAuth2, Credenciais

*Sessão capturada: 2026-06-18*

## Tópicos

- Execução do agent-orchestrator na feature 100 (42 Chat MVP) — 23 tasks em 4 fases
- Descoberta: projeto já tinha código backend + frontend implementado
- Debug do fluxo OAuth2 42 Intra (3 problemas resolvidos)
- Adição de DEV_MODE com `/api/auth/dev/login` para testes sem OAuth
- Regra constitucional: nunca hardcode credenciais
- `.env.example` limpo com VAR="" para secrets

## Key Takeaways

1. **Orchestrator fase a fase funcionou** — spawn manual de tasks em batches de 3, validação de evidência (arquivos existem, build passa, testes passam), 23/23 tasks concluídas
2. **OAuth2 42 — 3 problemas em cascata:** (a) `redirect_uri` divergente entre frontend/backend/app 42, (b) shell env vars (`FORTYTWO_CLIENT_ID=123`) sobrescrevendo `.env` no Docker Compose, (c) React StrictMode double-invocando o effect do Callback — primeiro exchange (200) funcionava, segundo (500) derrubava o login
3. **`#` em DATABASE_URL** quebra o parser de `.env` do Docker — resolveu com `%23`
4. **DEV_MODE** (`/api/auth/dev/login?login=marvin`) permite testar chat sem OAuth2 real
5. **Constitution atualizado** — anti-padrão #7: credenciais hardcoded proibidas

## Decisões

- `FORTYTWO_REDIRECT_URI` como env var configurável, default `http://localhost:5173`
- Callback.tsx usa `useRef` como guard contra double-invoke do StrictMode
- Login.tsx detecta `?code=` na home e redireciona pra `/callback`
- docker-compose.yml usa `env -u FORTYTWO_CLIENT_ID -u FORTYTWO_CLIENT_SECRET` pra evitar poluição do shell Hermes

## Referências

- [[references/42-api-specification|42 API Specification]]
- [[references/42-chat-platform-architecture|42 Chat Architecture]]
- [[references/react-vite-development|React + Vite Development]]
- [[concepts/sdd|SDD]]
