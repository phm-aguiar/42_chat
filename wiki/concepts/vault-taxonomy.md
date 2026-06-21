---
title: "Vault Taxonomy"
tags: [concept]
created: 2026-06-20
---
1|---
2|title: "Vault Taxonomy"
3|category: concepts
4|tags: [meta, wiki, taxonomy, estrutura]
5|summary: "Taxonomia de diretórios do vault Obsidian: concepts, references, skills, projects, _raw, journal, synthesis, entities — função e exemplos de cada um."
6|base_confidence: 0.95
7|lifecycle: draft
8|lifecycle_changed: "2026-06-14"
9|tier: core
10|created: "2026-06-14"
11|updated: "2026-06-14"
12|---
13|
14|# Vault Taxonomy
15|
16|> Estrutura canônica de diretórios do vault. Toda página deve pertencer a exatamente um destes diretórios.
17|
18|## Diretórios
19|
20|| Diretório | Função | Exemplo |
21||---|---|---|
22|| `concepts/` | Padrões, metodologia, arquitetura de conhecimento | [[concepts/sdd|SDD]], [[concepts/wiki-model|wiki-model]], [[concepts/onboarding|onboarding]] |
23|| `references/` | Documentação técnica destilada de fontes externas | [[references/42-chat-design-system|Design System]], [[references/gherkin-syntax|Gherkin Syntax]], [[references/tdd-methodology|TDD]] |
24|| `skills/` | Documentação das skills Hermes (procedural, how-to) | [[skills/wiki-ingest|wiki-ingest]], [[skills/gherkin-scenarios|gherkin-scenarios]], [[skills/doc-extract|doc-extract]] |
25|| `projects/` | Conhecimento escopo por projeto (`projects/<nome>/`) | [[projects/42_chat/42_chat|42_chat]], `features/`, `agents/`, `skills/` |
26|| `_raw/` | Fontes brutas históricas (originais não-destilados) | `pesquisa.md`, `qafiles/` originais, descrições de imagens |
27|| `journal/` | Sessões capturadas e registros cronológicos | `wiki-capture` por data, `digest-YYYY-MM-DD.md` |
28|| `synthesis/` | Conexões cross-cutting entre conceitos | TDD × Observabilidade, Scaling Laws × Hardware |
29|| `entities/` | Glossário de termos técnicos e definições | JWT, WebSocket Hub, Module Federation, RWMutex |
30|
31|## Regras
32|
33|1. **Uma página = um diretório.** Nada solto na raiz (exceto `index.md`, `log.md`, `hot.md`, `.manifest.json`)
34|2. **`_raw/` = imutável.** Fontes originais não são editadas — só destiladas para `references/` ou `concepts/`
35|3. **`projects/` aninhado.** Cada projeto tem sua própria miniatura da taxonomia: `projects/<nome>/concepts/`, `projects/<nome>/features/`, etc.
36|4. **`journal/` é cronológico.** Nomes com data ISO: `2026-06-14-captura.md`
37|5. **`synthesis/` conecta.** Toda página em `synthesis/` deve referenciar pelo menos 2 categorias diferentes
38|6. **`entities/` define.** Cada termo do glossário tem definição em uma frase + "Ver Também"
39|
40|## Ver Também
41|
42|- [[concepts/wiki-model|Wiki Model]] — Modelo de 3 camadas (sources → wiki → schema)
43|- [[concepts/obsidian-flow|Fluxo Obsidian]] — Ciclo de vida do vault
44|- [[skills/wiki-setup|wiki-setup]] — Inicialização do vault
45|

## Relacionado

- [[skills/brain|brain toolkit]] — Opera sobre esta taxonomia
- [[concepts/wiki-model|Wiki Model]] — Por que 3 camadas
- [[concepts/obsidian-flow|Fluxo Obsidian]] — Como a taxonomia é usada no pipeline