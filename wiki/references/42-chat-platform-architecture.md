---
title: "42 Chat — Platform Architecture"
category: references
tags: [42_chat, architecture, backend, frontend, infrastructure]
sources:
  - wiki/_raw/42-chat-research.md
summary: "Stack tecnológica completa da plataforma de chat P2P para a 42 SP: Go + WebSockets + PostgreSQL no backend, React + Vite + Module Federation no frontend, e infraestrutura Docker + AWS."
provenance:
  extracted: 0.80
  inferred: 0.15
  ambiguous: 0.05
base_confidence: 0.75
lifecycle: draft
lifecycle_changed: "2026-06-14"
tier: core
created: "2026-06-14"
rag_score: 0.48
updated: "2026-06-14"
---

# 42 Chat — Platform Architecture

> Stack completa para ~300 conexões simultâneas no campus 42 São Paulo.

## Visão Geral

Plataforma de chat em tempo real exclusiva para alunos da 42 SP, substituindo Slack/Discord. Foco em peer-to-peer learning, matchmaking de avaliações e localização física nos clusters. Conformidade com requisitos de auditoria do Bocal.

## Stack Tecnológica

### Backend (Motor do Chat)

| Camada | Tecnologia | Justificativa |
|---|---|---|
| **Linguagem** | Go (Golang) | Alta concorrência, baixo consumo de memória, compilação estática |
| **WebSockets** | `gorilla/websocket` | Biblioteca mais testada e robusta do ecossistema Go |
| **Roteamento REST** | `chi` ou `gin` | `chi` usa interface padrão `net/http`; `gin` tem mais adoção |
| **Autenticação** | OAuth2 da 42 → JWT interno | Login exclusivo via Intra, sem gerenciamento de senhas |
| **Banco de Dados** | PostgreSQL (Docker) | Relacionamentos complexos, auditoria, confiabilidade |

### Frontend (Interface Brutalista)

| Camada | Tecnologia | Justificativa |
|---|---|---|
| **Framework** | React + Vite | Build rápido, HMR, suporte nativo a Module Federation |
| **Arquitetura** | Module Federation (Vite) | Microfrontends isolados: Shell/Host + Microapps |
| **Estilização** | Tailwind CSS | Classes utilitárias, zero CSS manual |
| **Componentes** | Shadcn/ui | Copy-paste, controle total sobre o código |
| **Estado Global** | Zustand | Simples, leve, menos verboso que Redux |

### Infraestrutura & Deploy

| Camada | Tecnologia |
|---|---|
| **Conteinerização** | Docker (backend + banco) |
| **Hospedagem Backend** | AWS EC2 (t2.micro/t3.micro, free tier) |
| **Hospedagem Frontend** | Vercel, Netlify ou S3 + CloudFront (estático) |
| **Segredos** | Variáveis de ambiente injetadas via CLI (ex: Bitwarden CLI) |
| **CI/CD** | GitHub Actions com injeção segura de credenciais |

## Arquitetura de Microfrontends

```
┌─────────────────────────────────────────┐
│              Shell / Host                │
│  • Login OAuth2 42                       │
│  • Token JWT                             │
│  • Barra lateral de navegação            │
│  • Zustand (estado global)               │
├──────────────┬──────────────┬────────────┤
│  Microapp 1  │  Microapp 2  │  Futuro   │
│    Chat      │  Radar/Mapa  │  Microapp │
│  • WebSocket │  • API 42    │           │
│  • Mensagens │  • Clusters  │           │
│  • Salas     │  • Status    │           │
└──────────────┴──────────────┴────────────┘
```

## Schema do Banco de Dados

### `users` (sincronizado com a API da Intra)

| Coluna | Tipo | Descrição |
|---|---|---|
| `id` | INT (PK) | ID numérico da 42 |
| `login` | VARCHAR(50) | Ex: `marvin`, `pde-agui` |
| `image_url` | TEXT | Link da foto de perfil da intra |
| `current_host` | VARCHAR(20) | Ex: `e1z2m4` |
| `level` | NUMERIC(4,2) | Nível na intra |
| `created_at` | TIMESTAMP | — |

### `rooms` (salas de conversa)

| Coluna | Tipo | Descrição |
|---|---|---|
| `id` | UUID (PK) | — |
| `name` | VARCHAR(100) | — |
| `type` | VARCHAR(20) | `public`, `private`, `pair_programming`, `evaluation` |
| `created_at` | TIMESTAMP | — |

### `messages` (histórico e auditoria)

| Coluna | Tipo | Descrição |
|---|---|---|
| `id` | UUID (PK) | — |
| `room_id` | UUID (FK → rooms) | — |
| `user_id` | INT (FK → users) | — |
| `content` | TEXT | — |
| `created_at` | TIMESTAMP | Indexado para queries cronológicas |

## Funcionalidades Core

- **Campus Mapping**: Cache da API da 42 → localização física em tempo real (ex: `e1z2m4`)
- **Evaluation Matchmaking**: Comando `/eval` para encontrar pares para avaliação
- **Salas Efêmeras**: Comando `/pair <login>` → sala temporária para pair programming
- **Moderação**: Rota de API ou comando TTY para suspensão de usuários (Kill Switch)
- **Auditoria**: Logs estruturados de todas as mensagens

## Ver Também

- [[references/42-chat-design-system|42 Chat Design System]] — Sistema visual e identidade
- [[references/42-chat-engineering-requirements|42 Chat Engineering Requirements]] — Requisitos de engenharia
- [[references/42-chat-architecture-diagram|42 Chat Architecture Diagram]] — Diagrama Mermaid
