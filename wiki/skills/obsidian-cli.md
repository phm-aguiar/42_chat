1|---
2|title: "obsidian-cli"
3|category: skills
4|tags: [obsidian, skill, cli, tooling]
5|sources: [.hermes/skills/obsidian/obsidian-cli/SKILL.md]
6|summary: "CLI do Obsidian para operações no vault: abrir arquivos, buscar, navegar. Usado por skills que precisam interagir com o Obsidian como aplicação."
7|lifecycle: draft
8|created: "2026-06-13"
9|updated: "2026-06-13"
10|---
11|
12|# obsidian-cli
13|
14|> Interface de linha de comando para o Obsidian. Abre, busca, navega no vault.
15|
16|## Localização
17|`.hermes/skills/obsidian/obsidian-cli/SKILL.md`
18|
19|## Quando usar
20|- Abrir o Obsidian em um arquivo/pasta específica
21|- Buscar notas por título ou conteúdo via CLI
22|- Automação de tarefas no vault
23|
24|## Exemplos
25|```bash
26|obsidian-cli open "concepts/sdd"
27|obsidian-cli search "agent-dev"
28|obsidian-cli today
29|```
30|
31|## Relacionado
32|- [[skills/obsidian-markdown|obsidian-markdown]] — Formato que a CLI manipula
33|- [[concepts/obsidian-flow|Fluxo Obsidian]] — Onde a CLI se encaixa
34|
## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar operacoes batch documentadas, comandos de manutencao do vault, ou scripts CLI reutilizaveis antes de agir. O vault contem exemplos reais e decisoes documentadas que evitam retrabalho.