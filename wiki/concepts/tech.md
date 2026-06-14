1|---
2|title: "Stack Tecnológica"
3|category: concepts
4|tags: [tech, stack, go, postgresql, docker]
5|aliases: [tech, tecnologia]
6|summary: "Stack tecnológica homologada do 42_chat: Go, PostgreSQL, Docker, GitHub Actions."
7|created: "2026-06-13"
8|updated: "2026-06-13"
9|sources:
10|  - repo:.github/memory/tech.md
11|lifecycle: draft
12|lifecycle_changed: "2026-06-13"
13|base_confidence: 0.6
14|provenance:
15|  extracted: 0.4
16|  inferred: 0.6
17|  ambiguous: 0.0
18|---
19|
20|# Stack Tecnológica
21|
22|> Arquivo canônico: `../.github/memory/tech.md` (repo)
23|> Stack homologada para o projeto 42_chat.
24|
25|## Linguagens
26|
27|| Linguagem | Versão | Status |
28||---|---|---|
29|| Go | a definir | go.mod pendente |
30|| JavaScript/TypeScript | a definir | package.json pendente |
31|
32|## Backend
33|
34|| Lib | Propósito |
35||---|---|
36|| Gorilla WebSocket | WebSocket server |
37|| pgx | Driver PostgreSQL |
38|
39|## Frontend (planejado)
40|
41|| Lib | Propósito |
42||---|---|
43|| Vite | Build tool / dev server |
44|| Chatscope | Componentes de chat |
45|| Tailwind CSS | Estilização |
46|
47|## Banco de Dados
48|
49|| Componente | Propósito |
50||---|---|
51|| PostgreSQL | Banco principal |
52|| pgx | Driver Go |
53|
54|## CI/CD
55|
56|| Workflow | Gatilho |
57||---|---|
58|| go-ci.yml | PRs → develop, main |
59|| enforce-branch-flow.yml | PRs → main, develop |
60|| auto-pr-feature-to-develop.yml | push → feature/* |
61|| auto-pr-to-main.yml | push → develop |
62|
63|## Infraestrutura (planejado)
64|
65|- Docker + Docker Compose (Dockerfile pendente)
66|
67|## Relacionado
68|
69|- [[constitution]] — Regras arquiteturais
70|- [[sdd]] — Metodologia de desenvolvimento
71|- [[projects/42_chat/42_chat|42_chat]] — Projeto principal
72|