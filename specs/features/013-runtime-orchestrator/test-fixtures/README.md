# test-fixtures: Cenários de Teste — Feature 005

## T011 — Happy Path
**Fixture:** `specs/features/012-sdd-tasks-dag/tasks.md`
**Validação:** DAG válido, 0 ciclos, 0 deps quebradas, 0 órfãs, paralelismo com isolamento
**Status:** ✅ Validado na feature 004 (T007)

## T012 — Approval Gate
**Fixture:** `spec-not-approved.md`
**Cenário:** spec.md com `Aprovado: false`
**Comportamento esperado:** orchestrator lê spec, detecta false, aborta, ZERO subagentes spawnados
**Validação:** Verificar que o fluxo do AGENT.md Passo 1 cobre este caso
**Status:** ✅ AGENT.md Passo 1 cobre explicitamente

## T013 — Retry com Falha
**Fixture:** `failing-task/tasks.md`
**Cenário:** T001 falha 2x, passa na 3ª; T002 só roda após T001 passar
**Comportamento esperado:** 3 spawns de T001 com contexto enriquecido; T002 spawnado após sucesso de T001
**Validação:** AGENT.md Passo 3 + Edge case de retry cobrem
**Status:** ✅ Coberto no AGENT.md (retry com contexto enriquecido, timeout, 3 tentativas)

## T014 — Escalação
**Fixture:** `hard-fail-task/tasks.md`
**Cenário:** T001 falha 3x; T002 (dependente) pausada; T003 (independente) continua
**Comportamento esperado:** orchestrator reporta "Task T001 falhou 3x. Sub-árvore pausada: T002. Aguardando input."
**Validação:** AGENT.md Passo 6 cobre
**Status:** ✅ AGENT.md Passo 6 "Escalar bloqueios" cobre explicitamente

## T015 — Spawn Failure (infra)
**Cenário:** delegate_task falha com erro de API key/rate limit
**Comportamento esperado:** aborta feature inteira, NÃO aplica retry
**Validação:** AGENT.md Edge case "Spawn failure (infra)" cobre
**Status:** ✅ Coberto com "ABORTE a feature inteira imediatamente"
