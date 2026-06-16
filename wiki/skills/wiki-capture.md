---
title: "wiki-capture"
category: skills
tags: [wiki, skill, sessao, captura, memoria]
sources: [.hermes/skills/wiki/capture/SKILL.md]
summary: "Salva a conversa atual como página wiki. Preserva decisões, contexto e raciocínio para referência futura. Essencial para sessões de brainstorm e decisões arquiteturais."
lifecycle: draft
created: "2026-06-13"
updated: "2026-06-13"
---

# wiki-capture

> Salva a conversa atual no vault. "Essa discussão foi importante — guarda."

## Localização
`.hermes/skills/wiki/capture/SKILL.md`

## Quando usar
- Após brainstorm de feature (decisões de design)
- Após decisão arquitetural (o "porquê" da ADR)
- Após debugging complexo (solução não óbvia)
- Sessões que o usuário marca como importantes

## O que faz
1. Processa a transcrição da sessão
2. Extrai decisões, perguntas, respostas
3. Cria página wiki estruturada
4. Adiciona `[[skills/obsidian-markdown|wikilinks]]` para contexto
5. Registra no `log.md`

## Exemplo
```
Sessão: brainstorm da feature 006 (agent-dev)
→ wiki-capture
→ Output: journal/2026-06-13-brainstorm-agent-dev.md
→ Conteúdo: perguntas do clarify(), respostas, decisões
```

## Relacionado
- [[wiki-ingest]] — Para fontes estruturadas (specs, docs)
- [[wiki-query]] — Recupera sessões passadas
- [[obsidian-flow|Fluxo Obsidian]] — Quando usar
