---
title: "Tag Taxonomy"
category: _meta
tags: [meta, taxonomy]
summary: "Taxonomia canônica de tags do vault. Use estas tags ao criar/editar páginas."
lifecycle: reviewed
created: "2026-06-19"
updated: "2026-06-19"
---

# Tag Taxonomy

> Vocabulário controlado para tags do vault. Toda página deve usar tags desta lista.

## Domain Tags (max 5 por página)

| Tag Canonica | Aliases | Descricao |
|---|---|---|
| `sdd` | `spec-driven-development` | Spec-Driven Development, pipeline, features |
| `wiki` | `knowledge-management`, `obsidian` | Vault, conhecimento, brain |
| `qa` | `testing`, `qualidade` | Testes, BDD, Gherkin, qualidade |
| `dev` | `desenvolvimento`, `implementacao` | Código, Go, React, build |
| `github` | `git`, `versionamento` | GitHub, PR, issues, commits |
| `devops` | `infra`, `docker` | Infraestrutura, deploy, Honcho |
| `visual` | `design`, `diagramas` | Design, diagramas, criatividade |
| `ml` | `machine-learning`, `ai` | MLOps, modelos, inferencia |
| `research` | `pesquisa`, `papers` | Pesquisa, arXiv, papers |
| `productivity` | `produtividade` | Ferramentas de produtividade |
| `media` | `audio`, `video`, `musica` | Audio, video, musica, ComfyUI |
| `toolkit` | — | Paginas de toolkit consolidado |
| `concepts` | — | Conceitos, padroes, metodologia |
| `skills` | — | Documentacao de skills/toolkits |
| `references` | — | Material de referencia externo |
| `journal` | — | Sessoes, decisoes, linha do tempo |
| `meta` | — | Meta-informacao sobre o vault |

## Type Tags

| Tag | Descricao |
|---|---|
| `spec` | Especificacao de feature |
| `plan` | Plano arquitetural |
| `tasks` | Matriz de tarefas DAG |
| `adr` | Decisao arquitetural |
| `template` | Template reutilizavel |
| `pitfall` | Armadilhas e licoes aprendidas |
| `formato` | Documentacao de formato/sintaxe |
| `arquitetura` | Design de sistema |
| `skill` | Skill ou toolkit Hermes |
| `agente` | Subagente do framework |

## System Tags (nao contam no limite de 5)

| Tag | Descricao |
|---|---|
| `visibility/pii` | Contem dados pessoais |
| `visibility/internal` | Uso interno, nao publico |
| `visibility/public` | Publico (default) |

## Regras

1. **Max 5 domain tags por pagina.** System tags nao contam.
2. **Use a forma canonica.** `sdd`, nao `spec-driven-development`.
3. **Nao invente tags.** Se precisar de uma nova, proponha aqui primeiro.
4. **`visibility/` tags sao system tags.** Nao aparecem na taxonomia de domain tags.
5. **Tags no frontmatter YAML.** Ex: `tags: [sdd, wiki, concepts]`
