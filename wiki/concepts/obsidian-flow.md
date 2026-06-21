---
title: "Fluxo Obsidian — Integração com o Framework"
category: concepts
tags: [obsidian, wiki, fluxo, integracao]
aliases: [obsidian-flow, fluxo-wiki]
sources: []
summary: "Como o subsistema wiki/Obsidian se integra ao framework SDD: quem inicia cada operação, quando ela é disparada, e como o ciclo de vida do vault (ingest → cross-link → lint → query) se encaixa no pipeline de desenvolvimento."
lifecycle: draft
created: "2026-06-13"
updated: "2026-06-13"
---

# Fluxo Obsidian — Integração com o Framework

> O vault Obsidian não é um sistema à parte — é um **subsistema integrado** ao ciclo
> de vida do framework SDD. Este documento explica quem dispara o quê e quando.

## Visão Geral

```
Pipeline SDD                    Subsistema Wiki
─────────────                   ────────────────
brainstorm → spec.md
     ↓
generate-plan → plan.md
     ↓
generate-tasks → tasks.md
     ↓
agent-orchestrator              wiki-capture (salva sessão)
     ↓                              ↓
feature implementada ─────────→ wiki-ingest (cria/atualiza páginas)
     ↓                              ↓
sdd-validate                        ↓
     ↓                          cross-linker (descobre links faltantes)
commit + push                       ↓
     ↓                          wiki-lint (audita saúde)
     ↓                              ↓
PR merge                        wiki atualizado no repo
```

## Quem inicia o quê

O subsistema wiki é orquestrado pelo **agente principal** (o que interage com o humano).
Não é um agente separado — é um conjunto de skills que o agente principal invoca.

| Operação       | Quem inicia                | Quando                                                                           |
| -------------- | -------------------------- | -------------------------------------------------------------------------------- |
| `wiki-capture` | Agente principal           | Após sessão importante (decisão arquitetural, feature complexa)                  |
| `wiki-ingest`  | Agente principal           | Após feature implementada — destila spec/plan/tasks em página wiki               |
| `cross-linker` | Agente principal           | Após múltiplas páginas novas — descobre `[[skills/obsidian-markdown|wikilinks]]` faltantes                |
| `wiki-lint`    | Agente principal (ou cron) | Periodicamente ou após mudanças estruturais — audita saúde                       |
| `wiki-query`   | Agente principal           | Quando precisa buscar conhecimento compilado (ex: "o que já decidimos sobre X?") |
| `wiki-status`  | Agente principal           | Para ver delta do vault (o que mudou desde última ingest)                        |

## Ciclo de Vida do Vault

### 1. Setup inicial (uma vez)
```
wiki-setup → cria estrutura de diretórios + index.md + log.md + .manifest.json
```

### 2. Ingest (por feature/sessão)
```
wiki-ingest → lê source (spec.md, plan.md, tasks.md)
           → cria/atualiza página no vault
           → registra no .manifest.json
           → atualiza index.md e log.md
```

### 3. Cross-link (após múltiplos ingests)
```
cross-linker → escaneia vault por menções não-linkadas
             → adiciona [[skills/obsidian-markdown|wikilinks]] onde faz sentido
             → sugere novas conexões
```

### 4. Lint (periódico)
```
wiki-lint → verifica broken links
          → detecta páginas órfãs
          → checa frontmatter
          → reporta contradições
          → sugere correções
```

### 5. Query (sob demanda)
```
wiki-query → busca híbrida (lexical + vetorial)
           → retorna páginas relevantes + síntese
           → modo index-only (barato) ou full-read (profundo)
```

## Integração com o Pipeline SDD

### Durante o brainstorm
- `wiki-query` busca features similares já implementadas
- Ex: "Já fizemos algum agente leaf antes?" → consulta vault

### Após feature implementada
- `wiki-ingest` cria `projects/42_chat/features/<id>.md`
- `cross-linker` conecta com features relacionadas
- `log.md` registra a operação

### Após decisão arquitetural
- `wiki-capture` salva a sessão de discussão
- `concepts/` relevante é atualizado

### Antes do commit
- `wiki-lint` valida que não há broken links
- `constitution.md` exige vault fiel (portão de qualidade #4)

### No CI/CD (futuro)
- `wiki-lint --check` como gate de PR
- Bloqueia merge se vault estiver desatualizado

## Exemplo Real: Feature 006

```
1. Feature 006 implementada (agent-dev)
2. Agente principal invoca wiki-ingest:
   - Lê specs/features/006-agent-dev/{spec,plan,tasks}.md
   - Cria wiki/projects/42_chat/features/feature-006-agent-dev.md
   - Atualiza wiki/index.md (adiciona feature 006)
   - Atualiza wiki/log.md (registra operação)

3. Agente principal invoca cross-linker:
   - Descobre que feature-006-agent-dev deve linkar para agent-orchestrator
   - Adiciona [[skills/obsidian-markdown|wikilinks]] bidirecionais

4. Agente principal invoca wiki-lint:
   - 18 broken links encontrados (renomeações, páginas faltantes)
   - Corrige todos

5. Vault commitado junto com o código
```

## Skills do Subsistema Wiki

As skills vivem em `.hermes/skills/wiki/` e são invocadas via `skill_view()`:

| Skill | Função | Custo |
|---|---|---|
| `wiki-ingest` | Destila sources → páginas wiki | Alto (lê sources, escreve páginas) |
| `wiki-query` | Busca conhecimento compilado | Baixo (index-only) a Médio (full-read) |
| `wiki-lint` | Audita saúde do vault | Médio (lê todas as páginas) |
| `wiki-capture` | Salva conversa atual | Médio (processa transcrição) |
| `wiki/cross-linker` | Descobre [[skills/obsidian-markdown|wikilinks]] faltantes | Médio (escaneia vault) |
| `wiki-status` | Delta do vault | Baixo (lê .manifest.json) |
| `wiki-setup` | Inicializa vault | Alto (setup único) |
| `obsidian/obsidian-markdown` | Sintaxe OFM | Baixo (referência) |
| `obsidian/obsidian-cli` | CLI do Obsidian | Baixo |
| `obsidian/defuddle` | Extrai markdown limpo | Baixo |

> **Ver skills completas:** `concepts/tech.md` lista todas as 21 skills.

## Indexação Semântica e Retrieval Contextual (Feature 002)

> A Feature 002 (Wiki Experiential Memory) introduz indexação semântica no vault
> wiki, permitindo que o pipeline SDD consuma memória compilada de forma
> inteligente durante a geração de tarefas e sessões de brainstorm.

### 1. Fluxo de Indexação Semântica

O comando `hermes wiki index --full` dispara o pipeline completo de indexação:

```
hermes wiki index --full
  ├── 1. Coleta: lê todas as páginas do vault (wiki/**/*.md)
  ├── 2. Chunking: divide páginas em chunks semânticos (~512 tokens)
  ├── 3. Embedding: gera vetores para cada chunk (modelo configurado)
  ├── 4. Armazenamento: persiste no vector store (ChromaDB / FAISS)
  └── 5. Metadados: associa cada chunk à sua página fonte, tags e aliases
```

**Quando disparar:**
- Após `wiki-ingest` de novas features (automático ou manual)
- Após mudanças estruturais no vault (renomeações, reorganizações)
- Periodicamente (cron diário) para manter o índice sincronizado

**Custo:** Alto (lê todo o vault + gera embeddings), mas executado offline.

### 2. Retrieval Contextual

O comando `hermes wiki query --semantic` realiza busca semântica no índice:

```
hermes wiki query --semantic "padrão observer em agents"
  ├── 1. Embedding da query: converte a pergunta em vetor
  ├── 2. Similaridade: busca os top-K chunks mais próximos no vector store
  ├── 3. Re-ranking: reordena por relevância contextual (lexical + semântico)
  └── 4. Síntese: retorna chunks relevantes com links para páginas fonte
```

**Modos de operação:**

| Modo | Comando | Uso |
|---|---|---|
| Index-only (barato) | `hermes wiki query --semantic` | Retorna apenas referências e snippets |
| Full-read (profundo) | `hermes wiki query --semantic --full` | Lê páginas completas e sintetiza resposta |
| Híbrido (default) | `hermes wiki query` | Combina busca lexical + semântica |

### 3. Como o Pipeline SDD Consome o Índice

O índice semântico é consumido em dois pontos críticos do pipeline:

#### a) `generate-tasks --with-memory`

```
generate-tasks --with-memory
  ├── Lê spec.md e plan.md da feature atual
  ├── Consulta wiki (query --semantic): "features similares já implementadas"
  ├── Recupera padrões, decisões e pitfalls de features passadas
  └── Gera tasks.md com contexto histórico compilado
```

**Benefício:** Tasks geradas já incorporam lições aprendidas, evitando repetir
erros e acelerando a implementação com padrões conhecidos.

#### b) `brainstorm`

```
brainstorm (sessão interativa)
  ├── Agente recebe prompt do humano
  ├── Consulta wiki (query --semantic): busca conhecimento relevante
  ├── Recupera decisões arquiteturais passadas, features relacionadas
  └── Gera spec.md informada pelo histórico do projeto
```

**Benefício:** Brainstorms são fundamentados no que já foi decidido, evitando
rediscussão de tópicos resolvidos e mantendo coerência arquitetural.

### 4. Referência Cruzada — Feature 002

Esta seção implementa os requisitos da **Feature 002: Wiki Experiential Memory**
(`wiki/projects/42_chat/features/feature-002-sdd-templates.md`), que estabelece
o vault wiki como memória experiencial do framework:

- **Memória semântica:** Indexação vetorial para retrieval contextual
- **Memória procedural:** Templates SDD que guiam o pipeline
- **Memória episódica:** Log de sessões e decisões (`wiki-capture`)

> Consulte a [Feature 002](../projects/42_chat/features/feature-002-sdd-templates.md)
> para os requisitos completos e critérios de aceitação.

## Relacionado

- [[skills/brain|brain toolkit]] — Implementa este fluxo
- [[skills/sdd|sdd toolkit]] — Pipeline que aciona a wiki
- [[concepts/wiki-model|Wiki Model]] — O modelo de 3 camadas
- [[concepts/vault-taxonomy|Vault Taxonomy]] — Estrutura do vault

- [[concepts/wiki-model|Wiki Model]] — Por que adotamos esse modelo
- [[concepts/sdd|SDD]] — Regra do vault fiel (portão #4)
- [[concepts/sdd-workflow|SDD Workflow]] — Onde o wiki se encaixa
- [[concepts/onboarding|Onboarding]] — Setup inicial do vault
- [[journal/2026-06-14-readfile-truncation-pitfall|Pitfall: read_file truncation]] — Bug conhecido com read_file paginado
