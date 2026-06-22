---
feature_id: "004"
title: "Wiki Standardization — Template Canônico, Validação Contínua & Chunking Inteligente"
status: draft
created: "2026-06-21"
author: phm-aguiar
tags: [sdd, wiki, standardization, template, validation, chunking, rag, frontmatter]
depends_on:
  - "002-experiential-memory (índice SQLite + embeddings)"
  - "003-hybrid-retrieval (BM25 + cosine fusion)"
  - "005-latte-hardening (verify determinístico)"
---

**Aprovado:** true

# Wiki Standardization — Template Canônico, Validação Contínua & Chunking Inteligente

> Padroniza o vault Obsidian com template canônico de frontmatter, skill de validação
> contínua e regras de chunking para arquivos grandes. Corrige os 20 arquivos problemáticos
> atuais e previne regressão futura.

## Propósito

O vault `wiki/` tem 374 páginas mas sofre de 3 problemas que degradam a eficiência
do pipeline SDD e da busca híbrida (Features 002/003):

1. **Frontmatter inconsistente:** 20 páginas com YAML quebrado (13 com `:` não escapado
   em campos como `summary`, 7 sem `title`). Campos opcionais (`category`, `lifecycle`,
   `summary`) com adoção entre 61-70%, sem enforcement.

2. **Arquivos gigantes:** 11 arquivos >20KB. O pior (`Linters.md`, 164KB, 4313 linhas)
   produz chunks ineficientes — o chunker atual gera pedaços de ~500 tokens que perdem
   contexto quando o documento é muito maior que a janela de similaridade.

3. **Sem validação contínua:** O `wiki-lint` existente audita wikilinks quebrados e
   estrutura de diretórios, mas não valida frontmatter contra template canônico nem
   sinaliza arquivos candidatos a chunking.

**Esta feature entrega:** template canônico, correção dos 20 problemáticos, skill de
validação integrada ao `wiki-lint`, e regras de chunking com threshold configurável.

## Escopo

### Dentro do escopo

- Template canônico de frontmatter com campos obrigatórios e opcionais por diretório
- Correção automatizada dos 20 arquivos problemáticos (YAML escaping + title)
- Skill `wiki-validate-template` integrada ao `wiki-lint` existente
- Regras de chunking: split de arquivos >500 linhas ou >25KB com índice
- Reindexação pós-correção via Feature 002
- Thresholds adaptativos por diretório (Feature 003)

### Fora do escopo

- Reescrita de conteúdo das páginas (só frontmatter e chunking estrutural)
- Migração de diretórios (a taxonomia atual é preservada)
- Deduplicação de conteúdo (já coberto por `wiki-dedup`)

## Critérios de Sucesso

1. **20/20 corrigidos:** todos os arquivos problemáticos com frontmatter válido
2. **Validação contínua:** `wiki-lint` reporta FAIL em páginas fora do template
3. **Chunking:** `Linters.md` split em sub-páginas com índice; busca híbrida retorna
   resultados mais precisos (ganho ≥15% em precision@5 para queries sobre linters)
4. **Zero regressão:** 363 páginas já válidas permanecem intactas
5. **Reindex:** índice da Feature 002 atualizado com chunks otimizados
