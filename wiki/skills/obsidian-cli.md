---
title: "obsidian-cli"
category: skills
tags: [obsidian, skill, cli, tooling]
sources: [.hermes/skills/obsidian/obsidian-cli/SKILL.md]
summary: "CLI do Obsidian para operações no vault: abrir arquivos, buscar, navegar. Usado por skills que precisam interagir com o Obsidian como aplicação."
lifecycle: draft
created: "2026-06-13"
rag_score: 0.48
superseded_by: "[[skills/brain|brain]]"
updated: "2026-06-13"
---

# obsidian-cli

> Interface de linha de comando para o Obsidian. Abre, busca, navega no vault.

## Localização
`.hermes/skills/obsidian/obsidian-cli/SKILL.md`

## Quando usar
- Abrir o Obsidian em um arquivo/pasta específica
- Buscar notas por título ou conteúdo via CLI
- Automação de tarefas no vault

## Exemplos
```bash
obsidian-cli open "concepts/sdd"
obsidian-cli search "agent-dev"
obsidian-cli today
```

## Relacionado
- [[skills/obsidian-markdown|obsidian-markdown]] — Formato que a CLI manipula
- [[concepts/obsidian-flow|Fluxo Obsidian]] — Onde a CLI se encaixa

## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar operacoes batch documentadas, comandos de manutencao do vault, ou scripts CLI reutilizaveis antes de agir. O vault contem exemplos reais e decisoes documentadas que evitam retrabalho.