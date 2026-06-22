---
title: OAuth2 42 Debugging Pitfalls
category: references
tags: [oauth2, 42, debug, security, env]
sources:
  - "conversation:2026-06-18"
summary: "3 pitfalls comuns ao integrar OAuth2 da 42 Intra: redirect_uri divergente, shell env vars sobrescrevendo .env no Docker, e React StrictMode double-invocando token exchange."
provenance:
  extracted: 0.90
  inferred: 0.05
  ambiguous: 0.05
base_confidence: 0.70
lifecycle: draft
lifecycle_changed: "2026-06-18"
created: 2026-06-18
rag_score: 0.48
updated: 2026-06-18
---
# OAuth2 42 Debugging Pitfalls

3 problemas não-óbvios que quebram o fluxo OAuth2 da 42 Intra.

## 1. redirect_uri divergente entre 3 lugares {#redirect-uri}

O `redirect_uri` precisa ser **idêntico** (byte a byte) em:

| Local | Onde configurar |
|---|---|
| App na intra.42.fr | https://profile.intra.42.fr/oauth/applications |
| Frontend (authorize URL) | `VITE_42_REDIRECT_URI` no `frontend/.env` |
| Backend (token exchange) | `FORTYTWO_REDIRECT_URI` no `.env` |

**Sintoma:** `invalid_grant: "does not match the redirection URI used in the authorization request"`

**Causa comum:** barra final (`/` vs sem barra), `localhost` vs `127.0.0.1`, `http` vs `https`.

**Solução:** unificar os 3 com uma variável de ambiente. O backend lê `FORTYTWO_REDIRECT_URI`, o frontend lê `VITE_42_REDIRECT_URI`.

## 2. Shell env vars sobrescrevem `.env` no Docker Compose {#shell-env}

Docker Compose lê variáveis do **shell** com prioridade máxima, acima do arquivo `.env`. Se o shell tiver `FORTYTWO_CLIENT_ID=123` (placeholder de outro contexto), o container usará `123` mesmo com o `.env` correto.

**Sintoma:** `invalid_client: "Client authentication failed due to unknown client"` mesmo com `.env` preenchido.

**Diagnóstico:**
```bash
env | grep FORTYTWO          # vê o que o shell tem
docker compose config | grep FORTYTWO  # vê o que o compose interpreta
```

**Solução:**
```bash
env -u FORTYTWO_CLIENT_ID -u FORTYTWO_CLIENT_SECRET docker compose up -d
```

## 3. React StrictMode double-invoca token exchange {#strictmode}

React 18 StrictMode (dev only) executa `useEffect` **duas vezes**. No Callback OAuth2, isso faz o `fetch(/api/auth/42/callback?code=xxx)` rodar duas vezes. O primeiro exchange funciona (200) e loga o usuário. O segundo falha (500 — código já consumido) e o `catch` derruba o login.

**Sintoma:** chat aparece brevemente e depois volta pra tela de login.

**Diagnóstico:** Network tab mostra dois requests ao callback — primeiro 200, segundo 500.

**Solução:** `useRef` como guard:
```tsx
const called = useRef(false)
useEffect(() => {
  if (called.current) return  // StrictMode guard
  called.current = true
  // ... fetch exchange
}, [])
```

## Relacionado

- [[references/42-api-specification|42 API Specification]]
- [[references/react-vite-environment-config|React + Vite Environment Config]]
- [[journal/2026-06-18-sessao-feat100-oauth|Sessão 18/jun — Feature 100 + OAuth2]]
