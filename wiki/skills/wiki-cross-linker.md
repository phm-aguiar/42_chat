---
title: "cross-linker"
category: skills
tags: [wiki, skill, links, grafo, conectividade]
sources: [.hermes/skills/wiki/cross-linker/SKILL.md]
summary: "Descobre wikilinks faltantes no vault. Escaneia menções não-linkadas e adiciona [[skills/obsidian-markdown|wikilinks]] onde faz sentido. Essencial após múltiplos ingests para manter o grafo de conhecimento conectado."
lifecycle: draft
created: "2026-06-13"
superseded_by: "[[skills/brain|brain]]"
updated: "2026-06-13"
---

# cross-linker

> Descobre `[[skills/obsidian-markdown|wikilinks]]` que deveriam existir mas não existem.

## Localização
`.hermes/skills/wiki/cross-linker/SKILL.md`

## Quando usar
- Após `wiki-ingest` de múltiplas páginas novas
- Após renomear/mover páginas (links quebram)
- Quando `wiki-lint` reporta muitos órfãos

## O que faz
1. Escaneia todas as páginas por menções em texto plano
2. Verifica se a página mencionada existe no vault
3. Se existir e não houver `[[skills/obsidian-markdown|wikilink]]`, sugere adicionar
4. Também infere links por similaridade de tags/conteúdo

## Exemplo
```
Página: feature-006-agent-dev.md
Texto: "spawnado pelo orchestrator como subagente leaf"
Menção: "orchestrator" em texto plano → página agent-orchestrator existe?

Sim → cross-linker sugere: [[projects/42_chat/agents/agent-orchestrator|agent-orchestrator]]
```

## Modos
| Modo | Comportamento |
|---|---|
| **Sugestão** (default) | Lista links sugeridos, humano aprova |
| **Automático** | Aplica todos os links com confiança > 0.8 |

## Relacionado
- [[wiki-lint]] — Lint detecta broken links, cross-linker previne
- [[wiki-ingest]] — Ingest cria páginas, cross-linker conecta
- [[wiki-model|Wiki Model]] — O grafo de conhecimento

## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar paginas com wikilinks quebrados, mapear conectividade entre conceitos, ou verificar quais paginas precisam de cross-links antes de agir. O vault e a memoria de longo prazo do framework — consultar evita retrabalho e inconsistencias.