---
title: "42 Chat — Relatório de Arquitetura e Viabilidade"
category: references
tags:
  - 42_chat
  - arquitetura
  - backend
  - frontend
  - pesquisa
summary: "Relatório de arquitetura e viabilidade da plataforma de chat P2P para a 42 SP. Stack: Go, WebSocket, PostgreSQL, React, Vite, AWS EC2."
sources:
  - "wiki/_raw/42-chat-research.md"
base_confidence: 0.55
lifecycle: draft
lifecycle_changed: "2026-06-15"
tier: supporting
provenance:
  extracted: 0.10
  inferred: 0.85
  ambiguous: 0.05
created: "2026-06-15"
updated: "2026-06-15"
---

> [!abstract] Resumo
> Plataforma de chat em tempo real e matchmaking P2P para o ecossistema 42, projetada para 300 conexões simultâneas sobre AWS EC2 Free Tier (t2.micro, 1 vCPU, 1GB RAM). Stack: Go + WebSocket + PostgreSQL + React/Vite microfrontends. Pipeline BDD orquestrado pelo Agente Hermes.
>
> **Relatório completo dividido em 9 subpáginas por seção:**

- [[references/42-chat-sec1-fundamentacao|Sec 1: Fundamentação e Contexto Operacional no Ecossistema 42]]
- [[references/42-chat-sec2-backend-concorrencia|Sec 2: Arquitetura de Backend e Gestão de Concorrência Extrema]]
- [[references/42-chat-sec3-graceful-shutdown|Sec 3: Desligamento Gracioso (Graceful Shutdown) e Prevenção de Perda de Dados]]
- [[references/42-chat-sec4-infra-tuning|Sec 4: Infraestrutura, Tuning Extremo do SO e Gerenciamento de Descritores de Arquivo]]
- [[references/42-chat-sec5-api-42-rate-limits|Sec 5: Integração com a API da 42, Estratégia de Autenticação e Prevenção de Rate Limits]]
- [[references/42-chat-sec6-campus-locations|Sec 6: Mapeamento de Campus e Consumo Otimizado do Endpoint de Locations]]
- [[references/42-chat-sec7-microfrontends|Sec 7: Arquitetura de Microfrontends e Gerenciamento Global de Estado]]
- [[references/42-chat-sec8-matchmaking-p2p|Sec 8: Lógica de Algoritmos P2P: Matchmaking (Evals) e Salas Efêmeras]]
- [[references/42-chat-sec9-observabilidade-bdd|Sec 9: Observabilidade Estrutural e Engenharia de Software BDD]]

## Ver Também

- [[references/42-chat-platform-architecture|42 Chat — Platform Architecture]]
- [[references/42-chat-design-system|42 Chat — Design System]]
- [[references/42-chat-engineering-requirements|42 Chat — Engineering Requirements]]
- [[references/42-chat-architecture-diagram|42 Chat — Architecture Diagram]]
