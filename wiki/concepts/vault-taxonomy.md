---
title: "Taxonomia do Vault"
category: concepts
tags: [wiki, taxonomia, organizacao, diretorios]
summary: "Explica a funcao de cada diretorio do vault Obsidian: concepts/, references/, skills/, projects/, _raw/, journal/, synthesis/ com exemplos reais do vault 42_chat."
lifecycle: draft
created: "2026-06-14"
updated: "2026-06-14"
---

# Taxonomia do Vault

> O que vai em cada diretório e por quê. Baseado no modelo `llm-wiki`.

## Visão Geral

```
wiki/
├── index.md          ← Catálogo completo (entry point)
├── log.md            ← Activity log (timeline de operações)
├── concepts/         ← CONCEITOS: padrões, metodologia, arquitetura
├── references/       ← REFERÊNCIAS: documentação técnica destilada
├── skills/           ← SKILLS: documentação das skills do Hermes
├── projects/         ← PROJETOS: conhecimento específico de cada projeto
├── _raw/             ← FONTES BRUTAS: originais históricos (não navegável)
├── journal/          ← DIÁRIO: sessões capturadas, notas temporais
├── synthesis/        ← SÍNTESE: páginas que conectam múltiplos conceitos
└── entities/         ← ENTIDADES: glossário de termos do domínio
```

## Diretórios

### `concepts/` — Conceitos Cross-Project

**O que vai:** Padrões arquiteturais, metodologia, decisões de design que se aplicam
a QUALQUER projeto. É o "como pensamos" do framework.

**Não vai:** Documentação de ferramenta específica (ex: sintaxe Gherkin).
Isso é `references/`.

**Exemplos do nosso vault:**
| Página | O que explica |
|---|---|
| [[concepts/sdd]] | Metodologia SDD e pipeline |
| [[concepts/sdd-workflow]] | Fluxo completo com exemplo real |
| [[concepts/onboarding]] | Como começar um projeto do zero |
| [[concepts/wiki-model]] | Modelo de 3 camadas (sources → wiki → schema) |
| [[concepts/obsidian-flow]] | Ciclo de vida do vault integrado ao pipeline |

---

### `references/` — Referências Técnicas

**O que vai:** Documentação técnica destilada sobre ferramentas, stacks, sintaxes,
frameworks. Conteúdo "de consulta" — você lê quando precisa implementar algo.

**Não vai:** Conceitos abstratos (é `concepts/`). Docs de skills (é `skills/`).

**Exemplos do nosso vault:**
| Página | O que referencia |
|---|---|
| [[references/42-chat-design-system]] | Cores, tipografia, CSS do 42 Chat |
| [[references/42-chat-engineering-requirements]] | Concorrência, tuning, cache |
| [[references/gherkin-syntax]] | Sintaxe Gherkin (Given/When/Then) |
| [[references/tdd-methodology]] | Metodologia TDD |
| [[references/cucumber-basics]] | Fundamentos de Cucumber |

> **Regra:** `references/` é conteúdo DESTILADO — processado, estruturado, com frontmatter.
> As fontes brutas (antes da destilação) ficam em `_raw/`.

---

### `skills/` — Documentação de Skills

**O que vai:** Uma página por skill do Hermes, descrevendo localização, propósito,
quando usar, e links para referências relacionadas.

**Não vai:** O código da skill em si (está em `.hermes/skills/`). Documentação
técnica referenciada (está em `references/`).

**Exemplos do nosso vault:**
| Página | Skill |
|---|---|
| [[skills/wiki-ingest]] | Destila sources em páginas wiki |
| [[skills/gherkin-scenarios]] | Escreve cenários Gherkin (.feature) |
| [[skills/go-unit-tests]] | Testes unitários table-driven em Go |
| [[skills/sdd-brainstorm]] | Entrevista interativa → spec.md |

> **Regra:** Skills referenciam `[[references/...]]` em vez de duplicar conteúdo.
> Ex: `gherkin-scenarios` referencia `[[references/gherkin-syntax]]`.

---

### `projects/` — Conhecimento por Projeto

**O que vai:** Tudo que é específico de um projeto: features, agentes, skills SDD.
Aninhado em `projects/<nome>/` com subdiretórios.

**Não vai:** Conceitos cross-project (é `concepts/`). Skills globais (é `skills/`).

**Exemplos do nosso vault:**
```
projects/42_chat/
├── 42_chat.md              ← Overview do framework SDD
├── features/               ← Specs implementadas (001-007, 100)
├── agents/                 ← Agentes (onboard, orchestrator)
└── skills/                 ← Skills SDD (brainstorm, generate-plan, generate-tasks)
```

---

### `_raw/` — Fontes Brutas

**O que vai:** Documentos originais que foram usados como fonte para destilação.
Mantidos para rastreabilidade histórica. NÃO são navegáveis no grafo de conhecimento.

**Não vai:** Conteúdo destilado (já está em `references/` ou `concepts/`).

**Exemplos do nosso vault:**
| Página | Origem |
|---|---|
| `_raw/42-chat-research.md` | Pesquisa original do 42 Chat (antes de virar 4 referências) |
| `_raw/qa/gherkin-syntax/` | Fontes brutas de sintaxe Gherkin |
| `_raw/qa/tdd/` | Fontes brutas de TDD |

> **Regra:** `_raw/` é o "backup histórico". As páginas em `references/` devem
> ter `sources:` apontando pra `_raw/` (rastreabilidade). Não se navega em `_raw/`
> — se navega em `references/`.

---

### `journal/` — Diário de Sessões

**O que vai:** Capturas de sessões importantes (brainstorms, decisões, debugging).
Criado via `wiki-capture`. Organizado por data.

**Exemplos:**
```
journal/2026-06-13-brainstorm-agent-qa.md
journal/2026-06-14-debug-websocket-hub.md
```

> **Regra:** `journal/` é temporal, não temático. Se o conteúdo for reutilizável,
> deve ser destilado para `concepts/` ou `references/`.

---

### `synthesis/` — Síntese Cross-Cutting

**O que vai:** Páginas que conectam múltiplos conceitos que co-ocorrem em várias
páginas mas não têm uma página dedicada conectando-os. Criado via `wiki-synthesize`.

**Exemplos:**
```
synthesis/testing-and-observability.md  ← conecta [[references/tdd-methodology]] × [[references/42-chat-engineering-requirements]]
```

---

### `entities/` — Glossário de Domínio

**O que vai:** Definições curtas de termos do domínio. Pense num dicionário técnico.

**Exemplos:**
```
entities/websocket-hub.md     ← "O que é um WebSocket Hub?"
entities/jwt.md               ← "O que é JWT?"
```

---

## Regras de Ouro

1. **Conceitos cross-project → `concepts/`.** Se serve pra qualquer projeto, vai aqui
2. **Documentação técnica → `references/`.** Sintaxe, APIs, stacks, tuning
3. **Skills → `skills/`.** Uma página por skill, linkando pra `references/`
4. **Projeto-específico → `projects/<nome>/`.** Features, agentes, skills do projeto
5. **Fontes brutas → `_raw/`.** Histórico, não navegável
6. **Sessões → `journal/`.** Temporal, capturado via `wiki-capture`
7. **Conexões → `synthesis/`.** Quando dois conceitos co-ocorrem em várias páginas
8. **Definições → `entities/`.** Glossário de termos

## Relacionado

- [[concepts/wiki-model|Wiki Model]] — O modelo de 3 camadas
- [[concepts/obsidian-flow|Fluxo Obsidian]] — Como o vault é mantido
