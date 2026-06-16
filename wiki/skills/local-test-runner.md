1|---
2|title: "local-test-runner"
3|category: skills
4|tags: [qa, skill, go, test-runner, coverage]
5|summary: "Executa a suite de testes do QA: build, vet, test, cover. Formata o relatorio DONE/REJECTED para o ciclo QA."
6|lifecycle: draft
7|created: "2026-06-13"
8|updated: "2026-06-13"
9|sources: [.hermes/skills/qa/local-test-runner/SKILL.md]
10|---
11|
12|# local-test-runner
13|
14|> Skill procedural — passos 4-6 do ciclo QA: build → vet → test → cover → relatorio.
15|
16|## Localizacao
17|`.hermes/skills/qa/local-test-runner/SKILL.md`
18|
19|## Comandos por stack
20|| Stack | Build | Vet | Test | Cover |
21||---|---|---|---|---|
22|| Go | `go build` | `go vet` | `go test -v -count=1` | `go test -cover` |
23|| Python | `compileall` | `ruff check` | `pytest -v` | `pytest --cov` |
24|| Node | `npm run build` | `npm run lint` | `npm test` | `npm test -- --coverage` |
25|
26|## Relacionado
27|- [[skills/go-unit-tests]] — Passo anterior (escrever testes)
28|- [[skills/gherkin-scenarios]] — Inicio do ciclo QA
29|
## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar configuracoes de test runner, relatorios de execucao anteriores, ou integracoes CI documentadas antes de agir. O vault e a fonte de verdade sobre o que ja foi testado e como.