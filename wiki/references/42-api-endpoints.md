---
title: 42 Intra API v2 — Endpoints Reference
category: references
tags: [42, api, endpoints, reference]
sources: [_raw/42_api_docs.md]
summary: Catálogo de endpoints da API Intra 42 v2: 96 recursos, 739 endpoints. Organizado por relevância para o 42 Chat com indicadores de acesso (público/restrito).
provenance:
  extracted: 0.90
  inferred: 0.08
  ambiguous: 0.02
base_confidence: 0.59
lifecycle: draft
lifecycle_changed: 2026-06-16
tier: supporting
created: 2026-06-16T00:00:00Z
updated: 2026-06-16T00:00:00Z
---

# 42 Intra API v2 — Endpoints Reference

> **96 recursos, 739 endpoints.** Base URL: `https://api.intra.42.fr/v2`
> 🔒 = restricted (auth) | 🌐 = public

## Core (42 Chat)

Recursos essenciais para o chat P2P no campus 42.

### Users

Usuário 42 (estudante, staff, qualquer entidade com conta).

| Método | Path | Acesso |
|--------|------|--------|
| GET | `/v2/users` | 🌐 |
| GET | `/v2/users/:id` | 🌐 |
| GET | `/v2/me` | 🌐 |
| GET | `/v2/users/:id/locations_stats` | 🌐 |
| GET | `/v2/campus/:campus_id/users` | 🌐 |
| GET | `/v2/cursus/:cursus_id/users` | 🌐 |
| GET | `/v2/users/:user_id/projects_users/registration` | 🌐 |

### Campus

Locais físicos da 42.

| Método | Path | Acesso |
|--------|------|--------|
| GET | `/v2/campus` | 🌐 |
| GET | `/v2/campus/:id` | 🌐 |
| GET | `/v2/campus/:campus_id/stats` | 🌐 |

### Locations

Localização de um usuário num campus (host/logtime).

| Método | Path | Acesso |
|--------|------|--------|
| GET | `/v2/locations` | 🌐 |
| GET | `/v2/users/:user_id/locations` | 🌐 |
| GET | `/v2/locations/:id` | 🌐 |

### Projects

Projetos pedagógicos de um cursus.

| Método | Path | Acesso |
|--------|------|--------|
| GET | `/v2/projects` | 🌐 |
| GET | `/v2/projects/:id` | 🌐 |
| GET | `/v2/cursus/:cursus_id/projects` | 🌐 |
| GET | `/v2/me/projects` | 🌐 |

### Projects Users

Usuários que fizeram ou estão fazendo um projeto.

| Método | Path | Acesso |
|--------|------|--------|
| GET | `/v2/projects_users` | 🌐 |
| GET | `/v2/users/:user_id/projects_users` | 🌐 |
| GET | `/v2/projects/:project_id/projects_users` | 🌐 |

### Cursus

Ciclo educacional 42.

| Método | Path | Acesso |
|--------|------|--------|
| GET | `/v2/cursus` | 🌐 |
| GET | `/v2/cursus/:id` | 🌐 |

### Cursus Users

Usuários inscritos em um cursus.

| Método | Path | Acesso |
|--------|------|--------|
| GET | `/v2/cursus_users` | 🌐 |
| GET | `/v2/users/:user_id/cursus_users` | 🌐 |
| GET | `/v2/cursus/:cursus_id/cursus_users` | 🌐 |

### Scale Teams

Defesas de projeto (avaliador + avaliado).

| Método | Path | Acesso |
|--------|------|--------|
| GET | `/v2/scale_teams` | 🌐 |
| GET | `/v2/users/:user_id/scale_teams` | 🌐 |
| GET | `/v2/users/:user_id/scale_teams/as_corrector` | 🌐 |
| GET | `/v2/users/:user_id/scale_teams/as_corrected` | 🌐 |
| GET | `/v2/me/scale_teams` | 🌐 |

### Teams

Times de usuários para projetos em grupo.

| Método | Path | Acesso |
|--------|------|--------|
| GET | `/v2/teams` | 🌐 |
| GET | `/v2/users/:user_id/teams` | 🌐 |
| GET | `/v2/me/teams` | 🌐 |

### Slots

Slots disponíveis para agendar defesas.

| Método | Path | Acesso |
|--------|------|--------|
| GET | `/v2/slots` | 🌐 |
| GET | `/v2/me/slots` | 🌐 |
| GET | `/v2/users/:user_id/slots` | 🌐 |

## Perfil & Progresso

### Achievements

Conquistas (meta-goals) ganhas por usuários.

| Método | Path | Acesso |
|--------|------|--------|
| GET | `/v2/achievements` | 🔒 |
| GET | `/v2/achievements/:id` | 🌐 |
| GET | `/v2/achievements/:achievement_id/achievements_users` | 🌐 |

### Titles

Títulos obtidos (exibidos no perfil e forum).

| Método | Path | Acesso |
|--------|------|--------|
| GET | `/v2/titles` | 🌐 |
| GET | `/v2/users/:user_id/titles` | 🌐 |

### Skills

Habilidades.

| Método | Path | Acesso |
|--------|------|--------|
| GET | `/v2/skills` | 🌐 |

### Experiences

Experiência ganha por usuário em uma skill.

| Método | Path | Acesso |
|--------|------|--------|
| GET | `/v2/users/:user_id/experiences` | 🔒 |

### Expertises

Expertises pedagógicas.

| Método | Path | Acesso |
|--------|------|--------|
| GET | `/v2/expertises` | 🌐 |
| GET | `/v2/users/:user_id/expertises_users` | 🌐 |

### Tags

Tags não-hierárquicas (metadados de entidades).

| Método | Path | Acesso |
|--------|------|--------|
| GET | `/v2/tags` | 🌐 |
| GET | `/v2/users/:user_id/tags` | 🌐 |

### Languages

Idiomas.

| Método | Path | Acesso |
|--------|------|--------|
| GET | `/v2/languages` | 🌐 |
| GET | `/v2/users/:user_id/languages_users` | 🌐 |

### Groups

Grupos (label no perfil e forum).

| Método | Path | Acesso |
|--------|------|--------|
| GET | `/v2/groups` | 🌐 |
| GET | `/v2/users/:user_id/groups` | 🌐 |

### Coalitions

Usuários competindo dentro de um bloco.

| Método | Path | Acesso |
|--------|------|--------|
| GET | `/v2/coalitions` | 🌐 |
| GET | `/v2/users/:user_id/coalitions` | 🌐 |

## Eventos & Logística

### Events

Eventos em campus/cursus.

| Método | Path | Acesso |
|--------|------|--------|
| GET | `/v2/events` | 🌐 |
| GET | `/v2/campus/:campus_id/events` | 🌐 |
| GET | `/v2/users/:user_id/events` | 🌐 |

### Exams

Exames.

| Método | Path | Acesso |
|--------|------|--------|
| GET | `/v2/exams` | 🔒 |
| GET | `/v2/exams/:id` | 🌐 |

### Broadcasts

Broadcasts de um campus.

| Método | Path | Acesso |
|--------|------|--------|
| GET | `/v2/campus/:campus_id/broadcasts` | 🌐 |

## Admin (restricted)

Recursos de administração — acesso restrito a apps com escopos adequados.

### Accreditations, Amendments, Anti grav units, Apps, Attachments
### Balances, Blocs, Bloc deadlines, Certificates, Closes
### Clusters, Commands, Community services, Companies
### Dashes, Endpoints, Evaluations, Flags, Flashes
### Gitlab users, Internships, Journals, Levels, Mailings
### Notes, Notions, Offers, Patronages, Pools
### Products, Project data, Project sessions, Quests
### Roles, Rules, Scales, Scores, Squads
### Subnotions, Teams uploads, Transactions, Translations
### User candidatures, Waitlists, Webhook registeries

> Estes recursos têm endpoints GET/POST/PATCH/DELETE padrão. Consulte a [API doc oficial](https://api.intra.42.fr/apidoc) para detalhes.

## Padrões de URL

**Recursos aninhados:**
- `/v2/users/:user_id/<resource>` — recursos por usuário
- `/v2/campus/:campus_id/<resource>` — por campus
- `/v2/cursus/:cursus_id/<resource>` — por cursus
- `/v2/projects/:project_id/<resource>` — por projeto

**Graph endpoints:**
- `/v2/<resource>/graph(/on/:field(/by/:interval))` — dados agregados temporais

**Me endpoints:**
- `/v2/me` — perfil autenticado
- `/v2/me/<resource>` — recursos do usuário autenticado

## Ver Também

- [[references/42-api-specification|42 API Specification]] — Guia de uso: auth, paginação, rate limits
- [[references/42-chat-sec5-api-42-rate-limits|42 Chat — Sec 5: API 42 & Rate Limits]] — Estratégia de rate limiting
- [[references/42-chat-platform-architecture|42 Chat Platform Architecture]] — Stack do chat
- [[references/42-chat-engineering-requirements|42 Chat Engineering Requirements]] — Requisitos de engenharia
