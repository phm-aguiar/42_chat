---
title: "ADR-006: Merge Strategy"
tags: [adr, latte, hardening]
status: accepted
created: "2026-06-20"
rag_score: 0.5
---

# ADR-006: Merge Strategy — Merge de resultados de agentes paralelos

## Status
Accepted

## Contexto

No LATTE original, após fan-out (múltiplos workers em paralelo), o merge dos resultados no dispatcher tendia a *over-indexar* no output mais detalhado. Por exemplo, em um cenário com 3 workers — financeiro (800 palavras), técnico (200), mercado (200) — o merge puxava desproporcionalmente para o domínio financeiro, sub-representando os outros.

O paper *Multi-Agent Systems in Production* recomenda equal-weighting explícito: *"We now explicitly instruct the synthesis agent to weight inputs equally."* O problema é de atenção do modelo, não de tamanho de input. Prompt engineering resolve com custo zero em complexidade de código.

## Decisão

Equal-weight merge como prompt engineering, não como lógica de merge:

- Prompt de merge no dispatcher inclui constraint explícita: "Weight each input equally regardless of length. Note when a domain was under-researched (< 100 words)."
- Nenhuma lógica de merge é alterada — é puro prompt engineering
- Custo: ~20 tokens adicionais no prompt de merge
- Sinalização de domínios sub-pesquisados para que o Lead ou usuário saiba que determinada área teve menos cobertura

## Consequências

### Positive
- Merge balanceado: outputs de 200 palavras têm mesmo peso que outputs de 800 palavras
- Custo zero em complexidade de código — apenas adição de constraint no prompt
- Transparência: domínios sub-pesquisados são explicitamente sinalizados
- ~20 tokens de overhead — negligible

### Negative
- Prompt engineering é frágil — modelos diferentes podem interpretar "weight equally" de formas diferentes
- Não garante equal weighting real (modelos podem ignorar a constraint)
- Domínios sub-pesquisados continuam sub-pesquisados (apenas sinalizados, não expandidos)

### Neutral
- Comportamento de merge original preservado (constraint é aditiva, não substitutiva)
- Não afeta workers individuais — apenas o prompt de síntese pós-fan-out

## Alternativas Consideradas

**Lógica de truncamento/padding para equalizar tamanhos**
- Rejeitado: (a) perderia informação no truncamento, (b) padding adiciona tokens sem valor, (c) o problema é de atenção do modelo, não de tamanho de input, (d) prompt engineering resolve com custo zero.

**Merge ponderado por qualidade (scoring prévio dos outputs)**
- Rejeitado: adiciona complexidade de scoring e depende de LLM-as-judge (que já sabemos ser leniente). Equal-weight é mais simples e suficiente.

**Fan-out sequencial em vez de paralelo (evitar merge)**
- Rejeitado: perde o benefício de paralelismo do LATTE (-41% wall-clock). Merge é necessário para consolidar resultados paralelos.

## References
- Paper: *Multi-Agent Systems in Production* (Kalvium Labs) — equal-weight merge instruction
- Feature 005 spec: `specs/features/005-latte-hardening/spec.md`
- Feature 005 plan: `specs/features/005-latte-hardening/plan.md` (ADR-012 original)
- Dispatcher module: `.hermes/skills/sdd/latte_coordination/dispatcher.py`
