1|# Feature 006: Agent Dev
2|
3|> Persona implementadora do framework SDD. Braço executor — spawnado pelo orchestrator.
4|
5|## Status
6|✅ **Implementado** — 2026-06-13
7|
8|## Artefatos
9|- **Spec:** `specs/features/006-agent-dev/spec.md`
10|- **Plan:** `specs/features/006-agent-dev/plan.md`
11|- **Tasks:** `specs/features/006-agent-dev/tasks.md` (6 tasks, 3 fases)
12|- **Agente:** `.hermes/agents/agent-dev/AGENT.md` + `context.yaml`
13|
14|## Arquitetura
15|- **Tipo:** Agente Hermes nativo (AGENT.md + context.yaml)
16|- **Runtime:** Subagente leaf via `delegate_task` (não delega)
17|- **Toolsets:** `terminal` + `file`
18|- **Timeout:** 30 minutos (gerenciado pelo orchestrator)
19|
20|## Contrato com Orchestrator
21|- **Entrada:** Contexto compilado (spec, plan, task, skills, tentativa N/3)
22|- **DONE:** Evidência rastreável (função X → requisito Y, seção Z) + smoke-test output
23|- **FAIL:** Stack trace + arquivo + linha + possível causa
24|- **BLOCKED:** Pergunta específica sobre ambiguidade na spec (nunca infere)
25|
26|## Skills
27|- **Plugáveis por stack:** Injetadas pelo orchestrator conforme `tech.md`
28|- **Trilhos, não jaulas:** Usa templates como guia, adapta criativamente se necessário
29|- **Modo força bruta:** Funciona sem skills (qualidade pode ser menor)
30|
31|## Regras de Ouro
32|1. Nunca infere — ambiguidade = BLOCKED
33|2. Rastreabilidade sempre — todo DONE linka código → spec
34|3. Smoke-test obrigatório — sem exit code 0, sem DONE
35|4. Cirúrgico — modifica apenas o necessário
36|5. Aceita re-spawn — lê erro anterior e ajusta abordagem
37|
38|## Decisões Arquiteturais (ADRs)
39|- **ADR-1:** Agente Hermes nativo (mesmo padrão do onboard e orchestrator)
40|- **ADR-2:** Skills como parâmetro de entrada, não hardcoded (multi-stack)
41|- **ADR-3:** Comunicação via relatório textual (DONE/FAIL/BLOCKED)
42|- **ADR-4:** Nunca inferir — reportar BLOCKED
43|
44|## Dependências
45|- [[projects/42_chat/features/feature-005-agent-orchestrator]] — Orchestrator spawna o agent-dev
46|- Skills de stack (futuro): `go-implement`, `python-implement`, `smoke-check`
47|
48|## Relacionado
49|- [[projects/42_chat/agents/agent-orchestrator]] — Quem invoca
50|- [[feature-007-agent-qa]] — QA futuro pode rejeitar e forçar re-spawn
51|