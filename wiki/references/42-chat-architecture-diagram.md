---
title: "42 Chat — Architecture Diagram"
category: references
tags: [42_chat, architecture, diagram, mermaid]
sources:
  - wiki/_raw/42-chat-research.md
summary: "Diagrama Mermaid da arquitetura completa do 42 Chat: fluxo de autenticação, WebSocket hub, microfrontends, e infraestrutura AWS."
provenance:
  extracted: 0.0
  inferred: 1.0
  ambiguous: 0.0
base_confidence: 0.42
lifecycle: draft
lifecycle_changed: "2026-06-14"
tier: supporting
created: "2026-06-14"
rag_score: 0.48
updated: "2026-06-14"
---

# 42 Chat — Architecture Diagram

> Diagrama gerado a partir da documentação de arquitetura. Renderiza nativamente no Obsidian.

## Fluxo de Autenticação e Conexão

```mermaid
sequenceDiagram
    participant U as Aluno
    participant F as Frontend (React)
    participant B as Backend (Go)
    participant A as API 42 (OAuth2)
    participant D as PostgreSQL

    U->>F: Acessa o chat
    F->>A: Redireciona para 42 OAuth2
    A-->>F: Código de autorização
    F->>B: Envia código
    B->>A: Troca código por token
    A-->>B: Token de acesso + dados do aluno
    B->>D: Upsert usuário (id, login, level, host)
    B-->>F: JWT assinado
    F->>B: WebSocket connect (JWT)
    B-->>F: Conexão estabelecida
    Note over U,F: Chat em tempo real
```

## Arquitetura do Sistema

```mermaid
graph TB
    subgraph client["Frontend (React + Vite)"]
        direction TB
        shell["Shell/Host<br/>OAuth2 + JWT + Zustand"]
        chat["Microapp Chat<br/>WebSocket Client"]
        radar["Microapp Radar<br/>Campus Map"]
        shell --> chat
        shell --> radar
    end

    subgraph server["Backend (Go) — AWS EC2"]
        direction TB
        router["Chi/Gin Router<br/>REST API"]
        auth["Auth Middleware<br/>JWT Validation"]
        ws["WebSocket Hub<br/>gorilla/websocket"]
        cache["Cache Layer<br/>in-memory map"]
        obs["Metrics Endpoint<br/>/metrics"]

        router --> auth
        auth --> ws
        ws --> cache
        router --> obs
    end

    subgraph external["Serviços Externos"]
        api42["API 42 Intra<br/>OAuth2 + dados"]
    end

    subgraph data["Persistência"]
        pg["PostgreSQL<br/>Docker Container"]
    end

    client -->|"HTTPS + WSS"| server
    server -->|"OAuth2 / REST"| api42
    server -->|"SQL"| pg
```

## Infraestrutura de Deploy

```mermaid
graph TB
    subgraph ci["CI/CD — GitHub Actions"]
        commit["git push"]
        test["Testes + Build"]
        deploy["Deploy"]
        commit --> test --> deploy
    end

    subgraph aws["AWS Cloud"]
        ec2["EC2 t2.micro<br/>Go Backend + Docker"]
        s3["S3 + CloudFront<br/>Frontend Estático"]
    end

    subgraph alt["Alternativas Frontend"]
        vercel["Vercel"]
        netlify["Netlify"]
    end

    subgraph secrets["Gerenciamento de Segredos"]
        bw["Bitwarden CLI<br/>Client ID/Secret 42"]
    end

    deploy --> ec2
    deploy --> s3
    deploy --> vercel
    deploy --> netlify
    bw -.->|"injecta no CI"| deploy
```

## Fluxo de Mensagens no WebSocket Hub

```mermaid
graph TB
    subgraph hub["WebSocket Hub (goroutine dedicada)"]
        register["register chan"]
        unregister["unregister chan"]
        broadcast["broadcast chan"]
        clients["map Client → bool<br/>(protegido por channel)"]

        register --> clients
        unregister --> clients
        broadcast --> clients
    end

    subgraph conn["Conexões WebSocket"]
        c1["Client 1<br/>readPump + writePump"]
        c2["Client 2<br/>readPump + writePump"]
        c3["Client N<br/>readPump + writePump"]
    end

    c1 -->|"mensagem"| broadcast
    broadcast -->|"entrega"| c2
    broadcast -->|"entrega"| c3
    c1 -->|"connect"| register
    c1 -->|"disconnect"| unregister
```

## Ver Também

- [[references/42-chat-platform-architecture|42 Chat Platform Architecture]] — Documentação completa da stack
- [[references/42-chat-engineering-requirements|42 Chat Engineering Requirements]] — Requisitos de engenharia
- [[references/42-chat-design-system|42 Chat Design System]] — Sistema visual
