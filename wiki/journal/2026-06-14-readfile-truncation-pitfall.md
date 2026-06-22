---
title: "read_file truncation causes incomplete document consolidation"
category: skills
tags:
  - wiki
  - ingest
  - pitfall
  - tools
created: "2026-06-14"
rag_score: 0.48
summary: "Arquivos >50K chars são truncados pelo read_file sem aviso explícito, causando consolidação incompleta. Verificar total_lines vs file_size antes de processar."
tier: supporting
capture_source: hermes-session
project: "42_chat"
base_confidence: 0.90
lifecycle: draft
lifecycle_changed: "2026-06-14"
provenance:
  extracted: 0.90
  inferred: 0.10
sources:
  - "42_chat session (2026-06-14)"
---

## Pitfall: read_file Silently Truncates Large Files

**Problem:** O `read_file` tool trunca arquivos acima de ~100K caracteres sem indicação visual clara no output. O campo `truncated: true` existe no JSON mas é fácil de ignorar quando se lê múltiplos arquivos em paralelo.

**Sintoma:** Documentos longos (ex: `pesquisa.md` com 56KB) aparecem truncados no meio do conteúdo. A primeira consolidação no vault capturou apenas ~30% do conteúdo real, perdendo tabelas comparativas, parâmetros exatos de tuning, heurísticas de matchmaking e a seção sobre BDD + Agente Hermes.

**Root cause:** O `read_file` tem limite de ~100K chars. Quando atinge o limite, trunca silenciosamente. O campo `truncated: true` no output JSON é o único indicador.

**Fix:**
- Sempre verificar `total_lines` e `file_size` no output do `read_file`
- Para arquivos grandes (>30KB), usar `offset` e `limit` para ler em chunks
- Após consolidar, verificar se o conteúdo capturado cobre todas as seções esperadas do documento fonte

**Confirmed by:** Segunda passagem de consolidação com o arquivo completo (anexado pelo usuário) revelou 8 seções faltantes na página `engineering-requirements`.
