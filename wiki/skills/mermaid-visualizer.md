1|---
2|title: "mermaid-visualizer"
3|category: skills
4|tags: [visual, skill, mermaid, diagramas]
5|sources: [.hermes/skills/visual/mermaid-visualizer/SKILL.md]
6|summary: "Transforma texto em diagramas Mermaid profissionais: flowchart, sequence, class, ERD, Gantt. Usado para documentar arquitetura, fluxos e pipelines."
7|lifecycle: draft
8|created: "2026-06-13"
9|updated: "2026-06-13"
10|---
11|
12|# mermaid-visualizer
13|
14|> Transforma descrições textuais em diagramas Mermaid. Documentação visual sem sair do markdown.
15|
16|## Localização
17|`.hermes/skills/visual/mermaid-visualizer/SKILL.md`
18|
19|## Quando usar
20|- Documentar arquitetura de features
21|- Visualizar pipeline SDD
22|- Diagramas de sequência para cenários BDD
23|- Mapas mentais de conceitos
24|
25|## Tipos de diagrama
26|
27|| Tipo | Quando usar |
28||---|---|
29|| Flowchart | Fluxos de decisão, pipelines |
30|| Sequence | Interações entre agentes/sistemas |
31|| Class | Estrutura de dados, modelos |
32|| ERD | Banco de dados, entidades |
33|| Gantt | Cronograma de features |
34|
35|## Exemplo
36|```mermaid
37|flowchart LR
38|    A[Brainstorm] --> B[Spec]
39|    B --> C[Plan]
40|    C --> D[Tasks DAG]
41|    D --> E[Orchestrator]
42|```
43|
44|## Relacionado
45|- [[skills/json-canvas|json-canvas]] — Canvas nativo do Obsidian
46|- [[concepts/sdd-workflow|SDD Workflow]] — Pipeline que o mermaid documenta
47|- [[concepts/obsidian-flow|Fluxo Obsidian]] — Onde os diagramas vivem
48|
## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar diagramas Mermaid existentes no vault, padroes visuais, ou conceitos que precisam de visualizacao antes de agir.