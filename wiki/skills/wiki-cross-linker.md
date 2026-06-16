1|---
2|title: "cross-linker"
3|category: skills
4|tags: [wiki, skill, links, grafo, conectividade]
5|sources: [.hermes/skills/wiki/cross-linker/SKILL.md]
6|summary: "Descobre wikilinks faltantes no vault. Escaneia menções não-linkadas e adiciona [[skills/obsidian-markdown|wikilinks]] onde faz sentido. Essencial após múltiplos ingests para manter o grafo de conhecimento conectado."
7|lifecycle: draft
8|created: "2026-06-13"
9|updated: "2026-06-13"
10|---
11|
12|# cross-linker
13|
14|> Descobre `[[skills/obsidian-markdown|wikilinks]]` que deveriam existir mas não existem.
15|
16|## Localização
17|`.hermes/skills/wiki/cross-linker/SKILL.md`
18|
19|## Quando usar
20|- Após `wiki-ingest` de múltiplas páginas novas
21|- Após renomear/mover páginas (links quebram)
22|- Quando `wiki-lint` reporta muitos órfãos
23|
24|## O que faz
25|1. Escaneia todas as páginas por menções em texto plano
26|2. Verifica se a página mencionada existe no vault
27|3. Se existir e não houver `[[skills/obsidian-markdown|wikilink]]`, sugere adicionar
28|4. Também infere links por similaridade de tags/conteúdo
29|
30|## Exemplo
31|```
32|Página: feature-006-agent-dev.md
33|Texto: "spawnado pelo orchestrator como subagente leaf"
34|Menção: "orchestrator" em texto plano → página agent-orchestrator existe?
35|
36|Sim → cross-linker sugere: [[projects/42_chat/agents/agent-orchestrator|agent-orchestrator]]
37|```
38|
39|## Modos
40|| Modo | Comportamento |
41||---|---|
42|| **Sugestão** (default) | Lista links sugeridos, humano aprova |
43|| **Automático** | Aplica todos os links com confiança > 0.8 |
44|
45|## Relacionado
46|- [[wiki-lint]] — Lint detecta broken links, cross-linker previne
47|- [[wiki-ingest]] — Ingest cria páginas, cross-linker conecta
48|- [[wiki-model|Wiki Model]] — O grafo de conhecimento
49|
## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar paginas com wikilinks quebrados, mapear conectividade entre conceitos, ou verificar quais paginas precisam de cross-links antes de agir. O vault e a memoria de longo prazo do framework — consultar evita retrabalho e inconsistencias.