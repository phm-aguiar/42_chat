1|---
2|title: "001: Estrutura do Repositório"
3|category: projects
4|tags: [sdd, infra, github-actions, ci]
5|summary: "Inicialização do repo 42_chat: estrutura SDD, CI/CD, templates base."
6|created: "2026-06-13"
7|updated: "2026-06-13"
8|sources:
9|  - repo:specs/features/001-start-repo/
10|lifecycle: implemented
11|lifecycle_changed: "2026-06-13"
12|base_confidence: 0.9
13|provenance:
14|  extracted: 0.9
15|  inferred: 0.1
16|  ambiguous: 0.0
17|---
18|
19|# 001: Estrutura do Repositório
20|
21|> Feature fundadora. Estabelece a estrutura SDD e CI/CD do projeto.
22|
23|## Status
24|
25|**Implementada.** Tasks concluídas: 6/8.
26|
27|## O que entregou
28|
29|- `.github/memory/` com `constitution.md` e `tech.md` (templates)
30|- Árvore `specs/` (domain-events, features, infra)
31|- `AGENTS.md` com seção SDD Workflow
32|- 4 workflows GitHub Actions: CI, enforce-branch-flow, auto-PR feature→develop, auto-PR develop→main
33|- Script `check-sdd.sh` e template de `constitution.md`
34|
35|## Tasks pendentes
36|
37|- **T006:** Criar `llms.txt` na raiz
38|- **T007:** Documentar fluxo SDD no README.md
39|
40|## Relacionado
41|
42|- [[constitution]] — Template criado nesta feature
43|- [[tech]] — Stack mapeada nesta feature
44|- [[projects/42_chat/42_chat]] — Projeto principal
45|- [[sdd]] — Metodologia
46|