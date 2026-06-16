---
title: "Vault Taxonomy"
category: concepts
tags: [meta, wiki, taxonomy, estrutura]
summary: "Taxonomia de diretórios do vault Obsidian: concepts, references, skills, projects, _raw, journal, synthesis, entities — função e exemplos de cada um."
base_confidence: 0.95
lifecycle: draft
lifecycle_changed: "2026-06-14"
tier: core
created: "2026-06-14"
updated: "2026-06-14"
---

# Vault Taxonomy

> Estrutura canônica de diretórios do vault. Toda página deve pertencer a exatamente um destes diretórios.

## Diretórios

| Diretório | Função | Exemplo |
|---|---|---|
| `concepts/` | Padrões, metodologia, arquitetura de conhecimento | [[concepts/sdd|SDD]], [[concepts/wiki-model|wiki-model]], [[concepts/onboarding|onboarding]] |
| `references/` | Documentação técnica destilada de fontes externas | [[references/42-chat-design-system|Design System]], [[references/gherkin-syntax|Gherkin Syntax]], [[references/tdd-methodology|TDD]] |
| `skills/` | Documentação das skills Hermes (procedural, how-to) | [[skills/wiki-ingest|wiki-ingest]], [[skills/gherkin-scenarios|gherkin-scenarios]], [[skills/doc-extract|doc-extract]] |
| `projects/` | Conhecimento escopo por projeto (`projects/<nome>/`) | [[projects/42_chat/42_chat|42_chat]], `features/`, `agents/`, `skills/` |
| `_raw/` | Fontes brutas históricas (originais não-destilados) | `pesquisa.md`, `qafiles/` originais, descrições de imagens |
| `journal/` | Sessões capturadas e registros cronológicos | `wiki-capture` por data, `digest-YYYY-MM-DD.md` |
| `synthesis/` | Conexões cross-cutting entre conceitos | TDD × Observabilidade, Scaling Laws × Hardware |
| `entities/` | Glossário de termos técnicos e definições | JWT, WebSocket Hub, Module Federation, RWMutex |

## Regras

1. **Uma página = um diretório.** Nada solto na raiz (exceto `index.md`, `log.md`, `hot.md`, `.manifest.json`)
2. **`_raw/` = imutável.** Fontes originais não são editadas — só destiladas para `references/` ou `concepts/`
3. **`projects/` aninhado.** Cada projeto tem sua própria miniatura da taxonomia: `projects/<nome>/concepts/`, `projects/<nome>/features/`, etc.
4. **`journal/` é cronológico.** Nomes com data ISO: `2026-06-14-captura.md`
5. **`synthesis/` conecta.** Toda página em `synthesis/` deve referenciar pelo menos 2 categorias diferentes
6. **`entities/` define.** Cada termo do glossário tem definição em uma frase + "Ver Também"

## Ver Também

- [[concepts/wiki-model|Wiki Model]] — Modelo de 3 camadas (sources → wiki → schema)
- [[concepts/obsidian-flow|Fluxo Obsidian]] — Ciclo de vida do vault
- [[skills/wiki-setup|wiki-setup]] — Inicialização do vault
