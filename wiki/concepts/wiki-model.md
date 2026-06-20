---
title: "Wiki Model — Knowledge Management do Framework"
category: concepts
tags: [wiki, obsidian, knowledge-management, arquitetura]
aliases: [modelo-wiki, [[skills/wiki-llm-wiki|llm-wiki]]]
sources: []
summary: "O framework adota o modelo LLM Wiki (Karpathy) de 3 camadas: raw sources → wiki compilado → schema. Explica por que compilar conhecimento é superior a recuperar, e como o vault Obsidian versionado elimina amnésia cross-sessão."
lifecycle: draft
created: "2026-06-13"
updated: "2026-06-13"
---

# Wiki Model — Knowledge Management do Framework

> O framework SDD autônomo não só implementa código — ele **compila conhecimento**.
> O vault Obsidian (`wiki/`) é a memória de longo prazo do framework. Sem ele, cada
> sessão começa do zero.

## Por que um wiki?

Agentes de IA sofrem de **amnésia cross-sessão**. O que foi decidido na feature 004
não está disponível na feature 007. O histórico de chat é volátil. A memória do
Hermes Agent (Honcho) é boa para preferências, mas não para conhecimento estruturado.

O modelo wiki resolve isso com **compilação, não recuperação**:

| Abordagem | Como funciona | Problema |
|---|---|---|
| **Recuperação** (chat history) | Busca no histórico quando perguntado | Depende de saber a pergunta certa. Contexto se perde com o tempo |
| **Compilação** (wiki) | Conhecimento é destilado e interligado proativamente | Custa tokens no momento da escrita, mas economiza em todas as sessões futuras |

**Exemplo concreto:** Quando implementamos a feature 006 (agent-dev), o vault ganhou:
- `projects/42_chat/features/feature-006-agent-dev.md` — spec, plan, tasks, ADRs
- `concepts/sdd-workflow.md` — atualizado com exemplo real
- `log.md` — registro temporal

Na feature 007 (agent-qa), o agente **já sabe** que o agent-dev é leaf, que skills
são plugáveis, que o contrato é DONE/FAIL/BLOCKED. Não precisa re-derivar nada.

## As 3 Camadas

O modelo é baseado no [LLM Wiki](https://github.com/karpathy/[[skills/wiki-llm-wiki|llm-wiki]]) de Andrej Karpathy:

```
Layer 1: Raw Sources (imutável)
  ↓
Layer 2: Wiki (compilado, interligado)
  ↓
Layer 3: Schema (regras de como compilar)
```

### Layer 1: Raw Sources
Os artefatos do framework: `spec.md`, `plan.md`, `tasks.md`, `AGENT.md`, `constitution.md`.
São a "fonte da verdade" — nunca modificados pelo sistema wiki.

### Layer 2: Wiki Compilado
O vault Obsidian (`wiki/`) versionado no repo. Cada página tem:
- Frontmatter YAML (title, category, tags, sources, timestamps)
- `[[skills/obsidian-markdown|wikilinks]]` conectando conceitos relacionados
- Provenance: cada claim rastreável a uma source

### Layer 3: Schema
As skills em `.hermes/skills/wiki/` que governam COMO o wiki é mantido:
- `wiki-ingest` — destila sources em páginas
- `wiki-lint` — audita saúde do vault
- `wiki-query` — busca híbrida (lex + vec)
- `wiki-capture` — salva conversa atual
- `cross-linker` — descobre links faltantes

## O que ganhamos

### 1. Memória cross-sessão
Cada feature implementada enriquece o vault. Features futuras herdam esse conhecimento.
O agente não precisa re-descobrir que "skills são trilhos, não jaulas" — está no wiki.

### 2. Rastreabilidade
Toda decisão arquitetural (ADR) está linkada à feature que a motivou.
`[[skills/obsidian-markdown|wikilinks]]` formam um grafo navegável de decisões.

### 3. Onboarding zero-atrito
Um novo colaborador abre `wiki/index.md` e navega:
`concepts/sdd-workflow` → `concepts/onboarding` → `concepts/constitution`
Em 10 minutos entende o framework.

### 4. Auditoria automática
`wiki-lint` detecta links quebrados, páginas órfãs, contradições.
O vault se auto-corrige.

### 5. Versionamento
O vault é versionado no Git junto com o código.
Cada commit carrega specs + conhecimento compilado.
Rollback de código = rollback de conhecimento.

## Quando o wiki é atualizado

O fluxo é disparado pelo **agente principal** (o que está conversando com o humano):

| Gatilho | O que acontece |
|---|---|
| **Feature implementada** | Cria/atualiza `projects/42_chat/features/<id>.md` |
| **Decisão arquitetural** | Atualiza `concepts/` relevante |
| **Nova regra no constitution** | Atualiza `concepts/constitution.md` |
| **Sessão importante** | `wiki-capture` salva a conversa |
| **Periodicamente** | `wiki-lint` audita saúde do vault |

> **Regra constitucional:** "Vault Obsidian fiel: após qualquer mudança estrutural,
> o vault deve ser atualizado. Vault desatualizado bloqueia PR."

## Relacionado

- [[skills/brain|brain toolkit]] — Toolkit consolidado wiki/obsidian/docs
- [[concepts/vault-taxonomy|Vault Taxonomy]] — Estrutura canônica de diretórios
- [[concepts/obsidian-flow|Fluxo Obsidian]] — Integração wiki ↔ pipeline
- [[references/toolkits/wiki/karpathy-pattern|Karpathy Pattern]] — Fundação teórica

- [[concepts/obsidian-flow|Fluxo Obsidian]] — Como o subsistema wiki opera no dia a dia
- [[concepts/sdd|SDD]] — Regra do vault fiel
- [[concepts/sdd-workflow|SDD Workflow]] — Onde o wiki se encaixa no pipeline
