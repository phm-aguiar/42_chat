---
title: "ADR-004: Verify Deterministic"
tags: [adr, latte, hardening]
status: accepted
created: "2026-06-20"
rag_score: 0.5
---

# ADR-004: Verify Deterministic — Validação determinística de outputs de agentes

## Status
Accepted

## Contexto

O operador `Verify(v)` original usava exclusivamente LLM-as-judge para avaliar outputs de workers. O paper *Multi-Agent Systems in Production* alerta que LLM-as-judge é mal calibrado: *"We use deterministic checks (output format validation, citation existence checks, length constraints) instead of LLM evaluation at agent boundaries."* O LLM tende a ser leniente consigo mesmo (mesmo modelo) e crítico com modelos diferentes, resultando em falsos positivos e falsos negativos.

Checks determinísticos são objetivos, custam zero tokens, e pegam falhas estruturais que o LLM ignoraria (ex: arquivo vazio, anti-padrões de planejamento sem ação). No entanto, checks determinísticos não avaliam qualidade semântica — um worker pode gerar código que compila mas não implementa o que foi pedido.

## Decisão

Verify determinístico primeiro, LLM como fallback:

- `Verify(v)` primeiro executa 5 checks determinísticos:
  1. **Formato válido**: output é JSON válido? Campos esperados presentes?
  2. **Artefato existe**: arquivo criado? Não vazio?
  3. **Exit code**: `exit_code == 0`?
  4. **Tamanho mínimo**: output ≥ N chars?
  5. **Anti-padrões**: "I will create", "Let me plan" sem ação concreta?
- Se todos passam → approved sem LLM (zero tokens)
- Se algum falha → escala pro LLM (comportamento atual como fallback)
- Modo configurável: `verify_mode: "deterministic"` (default) ou `"llm"` (skip checks, comportamento original)

## Consequências

### Positive
- Zero tokens em verificação bem-sucedida (maioria dos casos)
- Objetivo e reproduzível — mesmos checks produzem mesmos resultados
- Pega falhas estruturais que LLM ignoraria (ex: arquivo vazio aprovado como "implementation complete")
- Benchmark: < 5% falsos positivos em cenário com falha real
- Fallback LLM cobre qualidade semântica que checks determinísticos não alcançam

### Negative
- Checks determinísticos são limitados a validação estrutural — não avaliam correção funcional
- Anti-padrões baseados em regex podem ter falsos positivos em outputs legítimos que mencionam planejamento
- Manutenção: novos anti-padrões precisam ser adicionados conforme novos modelos surgem

### Neutral
- `verify_mode="llm"` preserva comportamento original para compatibilidade
- Verify continua sendo um nó comum no grafo (ADR-005 original mantido)

## Alternativas Consideradas

**Verify só determinístico (sem fallback LLM)**
- Rejeitado: checks determinísticos não avaliam qualidade semântica — um worker pode gerar código que compila mas não implementa o que foi pedido. O LLM fallback cobre esse gap.

**Verify só LLM (manter comportamento original)**
- Rejeitado: LLM-as-judge é leniente e caro. O paper recomenda checks determinísticos como primeira linha.

**Verify com scoring numérico (0-100)**
- Rejeitado: adiciona complexidade sem ganho claro. Checks binários (pass/fail) são mais acionáveis e determinísticos.

## References
- Paper: *Multi-Agent Systems in Production* (Kalvium Labs) — deterministic checks pattern
- Feature 005 spec: `specs/features/005-latte-hardening/spec.md`
- Feature 005 plan: `specs/features/005-latte-hardening/plan.md` (ADR-009 original)
- Operador Verify: `.hermes/skills/sdd/latte_coordination/lead_operators.py`
- Coordenação LATTE: [[projects/42_Framework/features/001-latte-coordination|Feature 001: LATTE Coordination]]
