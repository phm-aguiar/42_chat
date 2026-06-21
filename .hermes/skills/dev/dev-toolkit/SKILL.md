---
name: dev-toolkit
description: >
  Toolkit consolidado do agent-dev. 15 modos: go, react, build-check, plan, spike,
  debug, code-review, simplify, node-debug, python-debug, claude-code, codex,
  opencode, hermes-config, skill-forge. Carregue sempre que o agent-dev receber
  qualquer task de desenvolvimento. Trigger keywords: implementar, build, debug,
  review, simplify, delegar, configurar hermes, criar skill.
version: 1.0.0
author: phm-aguiar
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [dev, toolkit, agent-dev, go, react, build, debug, code-review, autonomous]
    related_skills: [qa-toolkit, github, sdd]
    category: dev
    resources:
      - SKILL.md
      - references/consolidation-patterns.md
    umbrella_for:
      - go-implement
      - react-implement
      - build-check
      - plan
      - spike
      - systematic-debugging
      - requesting-code-review
      - simplify-code
      - node-inspect-debugger
      - python-debugpy
      - claude-code
      - codex
      - opencode
      - hermes-agent
      - skill-forge
---

# dev-toolkit — 15 Modos do Agent-Dev

Toolkit unificado de desenvolvimento. Cada modo é acionado pelo tipo de task.
Use `brain query "referencia X"` para consultas detalhadas além do condensado aqui.
Consulte `references/consolidation-patterns.md` para workarounds de skill_view e técnicas de compressão.

## `go` — Implementar Go (Chi, WebSocket, PostgreSQL)

**Gatilhos:** implementar Go, Go backend, criar modulo Go, Chi router, gorilla websocket, PostgreSQL Go.

**Stack:** Go 1.21+, Chi router, gorilla/websocket, database/sql + PostgreSQL, log/slog, JWT.

**Fluxo:**
1. Ler spec + ADRs do contexto da task antes de codar.
2. Estrutura: `cmd/server/main.go` + `internal/{auth,chat,api,repository,cache,observability}/`.
3. `main.go`: carregar config → conectar DB → criar Hub → Chi router → graceful shutdown (SIGINT/SIGTERM, 30s timeout).
4. WebSocket Hub híbrido: `sync.RWMutex` no mapa de clients + `send chan` (buffer 256) por client. Ping 30s, read deadline 60s.
5. OAuth2 42: authorize → callback → `/v2/me` → upsert PostgreSQL → JWT 12h.
6. PostgreSQL: `SetMaxOpenConns(100)`, `SetMaxIdleConns(25)`, migrations no startup, queries parametrizadas.
7. Erros: `fmt.Errorf("contexto: %w", err)`. Nunca panic para erros recuperáveis.
8. JWT secret via `os.Getenv("JWT_SECRET")`, nunca hardcoded.

**Pitfalls:** Nunca implementar sem spec. CORS explícito (`https://chat.42sp.org.br`), não wildcard. `go get` para dependências, nunca editar `go.mod` manualmente.

**Verificação:** `go build ./...` compila, `go vet ./...` limpo.

## `react` — Implementar React (Vite, Tailwind, Shadcn, Zustand)

**Gatilhos:** implementar React, frontend, Vite, Tailwind, Shadcn, Zustand, WebSocket hook.

**Stack:** Vite + React 18 + TypeScript, Tailwind v4 brutalista 42, Shadcn/ui (rounded-none), Zustand.

**Design System 42:** Cores #000, #FFF, #D4ED31 (lime), #00E5FF (ciano), #FF007A (magenta). Montserrat/Poppins Black/Extra-Bold CAIXA ALTA. border-radius: 0. Dot grid bg: `radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px)`.

**Fluxo:**
1. Usar `useEffect` para WebSocket — NUNCA chamar `connect()` no corpo do render (causa cascata de reconexão).
2. Guard `connecting` + verificar `readyState === CONNECTING`.
3. Handlers usar `useCallback` para evitar acúmulo em Sets de listeners.
4. Zustand stores: `authStore` (token, user) + `chatStore` (messages, connected).

**Pitfalls:** WebSocket render cascade — centenas de `[ws] client conectado` por segundo. Inline handlers acumulam em Sets sem `useCallback`.

**Verificação:** `npx tsc --noEmit`, `npm run build`, Network tab mostra 1 única conexão WS, tema brutalista aplicado.

## `build-check` — Smoke Test (go build + vet + npm build)

**Gatilhos:** build check, smoke test, verificar build, compilar, go vet.

**Portão de qualidade obrigatório antes de reportar DONE.**

**Fluxo:**
1. Detectar escopo: `test -f go.mod` (Go), `test -f web/package.json` (React).
2. `go build ./...` — exit 0 = OK.
3. `go vet ./...` — corrigir warnings antes do DONE.
4. `cd web && npm run build` (se frontend existir).
5. Opcional: verificar estrutura de diretórios (`cmd/server/main.go`, `internal/auth/`, etc.).

**Pitfalls:** exit code ≠ 0 bloqueia DONE. `go vet` warnings corrigir mesmo que não bloqueiem. Não confundir com testes unitários (isso é agent-qa). Executar da raiz do projeto.

**Verificação:** `go build ./...` exit 0, `go vet ./...` exit 0.

## `plan` — Plano Markdown (sem execução)

**Gatilhos:** fazer plano, planejar, /plan, antes de implementar.

**Modo somente-planejamento:** não implementar, não editar código, não rodar comandos mutantes.

**Fluxo:**
1. Inspecionar repo (read-only).
2. Escrever plano em `.hermes/plans/YYYY-MM-DD_HHMMSS-<slug>.md`.
3. Conteúdo: Goal, Context, Approach, Step-by-step, Files, Tests, Risks.
4. Tarefas bite-sized (2-5 min cada). Caminhos exatos. Código completo (copy-pasteable).
5. Princípios: DRY, YAGNI, TDD, commits frequentes.

**Pitfalls:** Tarefas vagas ("Add authentication"), código incompleto, sem verificação.

## `spike` — Experimento Throwaway

**Gatilhos:** spike, prototipar, testar ideia, "isso funciona?", "antes de commitar".

**Spikes são descartáveis.** Validar viabilidade, não construir produção.

**Fluxo:**
1. Decompor em 2-5 questões de viabilidade (Given/When/Then).
2. Ordenar por risco (mais arriscado primeiro).
3. Criar `spikes/NNN-descricao/` com `README.md` + código mínimo.
4. Construir algo interativo (CLI > HTML > server > unit test).
5. Veredito: VALIDATED | PARTIAL | INVALIDATED no README.

**Pitfalls:** Não usar para resposta documental (pesquise, não builde). Não limpar spike para produção. Hardcode tudo, evite configs complexas.

## `debug` — Debug Sistemático de 4 Fases

**Gatilhos:** debugar, bug, erro, test falhou, crash, investigar.

**Lei de Ferro:** NUNCA corrigir sem investigar causa raiz primeiro.

**Fases:**
1. **Root Cause:** ler erros → reproduzir → `git log -10` → instrumentar componentes → rastrear fluxo de dados.
2. **Pattern Analysis:** encontrar código similar funcionando → comparar diferenças.
3. **Hypothesis:** formar UMA hipótese → testar minimamente → se falhar, nova hipótese.
4. **Implementation:** criar teste de regressão → corrigir causa raiz → verificar suite completa.

**Regra dos 3:** se 3+ fixes falharam, questionar a ARQUITETURA, não continuar remendando.

**Pitfalls:** "Quick fix" é armadilha. Multi-componentes: instrumentar cada fronteira. Não pular fases.

## `code-review` — Pre-Commit Review (segurança + qualidade)

**Gatilhos:** review, revisar, verificar antes de commit, pre-commit.

**Nenhum agente revisa o próprio código.** Fresh context acha o que você não vê.

**Fluxo:**
1. `git diff --cached` (ou `git diff` se vazio).
2. Static scan: secrets hardcoded, shell injection, eval, pickle, SQL injection.
3. Baseline tests + lint (pytest/npm test, ruff/eslint, mypy/tsc). Só NEW failures bloqueiam.
4. Self-review checklist: secrets, input validation, parametrized SQL, path traversal, error handling, debug prints.
5. Reviewer subagent (`delegate_task`) — recebe SÓ o diff + scan results. Retorna JSON: `passed`, `security_concerns`, `logic_errors`, `suggestions`.
6. Se reprovado → auto-fix loop (máx 2 ciclos) com terceiro agente.
7. Se aprovado → `git add -A && git commit -m "[verified] ..."`.

**Pitfalls:** Diff vazio → check `git status`. Diff >15k chars → split por arquivo. Reviewer não-JSON → retry 1x, depois FAIL.

## `simplify` — Cleanup Paralelo de 3 Agentes

**Gatilhos:** simplify, simplificar, limpar código, /simplify.

**3 revisores narrow batem 1 revisor broad.** Cada um busca uma classe de problema.

**Fluxo:**
1. Capturar diff: `git diff` (uncommitted) ou `git diff HEAD~1`.
2. Lançar 3 revisores em paralelo (`delegate_task` batch):
   - **Reuse:** código duplicado com utils existentes.
   - **Quality:** estado redundante, parâmetro sprawl, copy-paste, leaky abstractions, stringly-typed.
   - **Efficiency:** trabalho desnecessário, concorrência perdida, hot-path bloat, N+1, memory leaks.
3. Cada revisor usa `search_files` + `read_file` para evidência real (não adivinha).
4. Agregar, deduplicar, resolver conflitos (correctness > readability > micro-perf).
5. Aplicar com `patch`/`write_file`, verificar tests nos arquivos tocados.
6. Reportar: fixes aplicados + achados descartados e por quê.

**Pitfalls:** Não dar diff fragmentado (cross-file issues se perdem). Achados sem `file:line` = ruído, descartar. Não é licença para refatorar o módulo inteiro.

## `node-debug` — Debug Node.js (CDP + node inspect)

**Gatilhos:** debug Node, node inspect, --inspect, CDP, breakpoint JS/TS.

**Ferramentas:** `node inspect` (built-in CLI) e `chrome-remote-interface` (scriptável).

**Fluxo rápido:**
1. `node --inspect-brk script.js` + `node inspect -p <pid>`.
2. Comandos: `sb('file.js', 42)`, `c`, `n`, `s`, `repl`, `bt`.
3. Attach: `kill -SIGUSR1 <pid>` → `node inspect -p <pid>`.
4. TS: `node --inspect-brk --import tsx script.ts` (breakpoints batem no JS).
5. Vitest: `--no-file-parallelism` com `--inspect-brk`.

**Pitfalls:** TS source maps não funcionam no CLI. `--inspect` sem `-brk` corre antes do attach. Port default 9229 colide. Child processes: `NODE_OPTIONS='--inspect'`.

## `python-debug` — Debug Python (pdb + debugpy)

**Gatilhos:** debug Python, pdb, breakpoint(), debugpy, DAP, post-mortem.

**Ferramentas:** `breakpoint()` (local), `python -m pdb` (sem editar), `debugpy`/`remote-pdb` (remote).

**Fluxo rápido:**
1. **Mais simples:** `breakpoint()` no source → `n`, `s`, `p expr`, `pp obj`, `w`, `interact`.
2. **Pytest:** `pytest --pdb -p no:xdist` (xdist quebra pdb).
3. **Post-mortem:** `python -m pdb -c continue script.py`.
4. **remote-pdb** (preferir sobre debugpy DAP): `from remote_pdb import set_trace; set_trace(host="127.0.0.1", port=4444)` → `nc 127.0.0.1 4444`.
5. **debugpy** (quando precisa IDE): `debugpy.listen(("127.0.0.1", 5678)); debugpy.wait_for_client()`.

**Pitfalls:** pdb + xdist = hang. `PYTHONBREAKPOINT=0` desabilita breakpoints. `scripts/run_tests.sh` strip credentials. Forking — cada child precisa do próprio breakpoint.

## `claude-code` — Delegar para Claude Code CLI

**Gatilhos:** usar Claude, claude code, delegar para Claude, @claude.

**Pré-requisitos:** `npm install -g @anthropic-ai/claude-code`, `claude auth login`.

**Modo preferido: Print Mode (`-p`) — non-interactive, sem PTY.**

```bash
claude -p 'Add error handling' --allowedTools 'Read,Edit' --max-turns 10
git diff HEAD~3 | claude -p 'Summarize' --max-turns 1        # pipe
claude -p 'Analyze' --output-format json --max-turns 5        # JSON
```

**Interativo (tmux):** `tmux new-session -d -s claude`, `tmux send-keys -t claude 'claude' Enter`.

**Flags chave:** `--dangerously-skip-permissions`, `--allowedTools`, `--max-turns`, `--model`, `--effort`, `--bare`.

**Diálogos PTY:** Trust → Enter. Permissions bypass → Down + Enter.

**Pitfalls:** Print mode skipa diálogos (ideal). `--max-budget-usd` mín ~$0.05. `--bare` pula OAuth. Contexto >70% degrada.

## `codex` — Delegar para OpenAI Codex CLI

**Gatilhos:** usar Codex, codex exec, delegar para Codex, @codex.

**Pré-requisitos:** `npm install -g @openai/codex`, auth configurada. **Requer git repo.**

```bash
codex exec 'Add dark mode toggle'                    # pty=true
codex exec --full-auto 'Refactor auth module'        # auto-approve
codex exec --yolo 'Fix all lint errors'              # sem sandbox
codex review --base origin/main                      # PR review
```

**Flags:** `--full-auto` (sandboxed auto-approve), `--yolo` (sem sandbox), `--sandbox danger-full-access` (quando bubblewrap falha no gateway).

**Paralelo com worktrees:** `git worktree add -b fix/issue-N /tmp/issue-N main` + rodar Codex em cada.

**Pitfalls:** SEMPRE `pty=true`. Precisa de git repo (use `mktemp -d && git init` para scratch). Gateway: preferir `--sandbox danger-full-access`.

## `opencode` — Delegar para OpenCode CLI

**Gatilhos:** usar OpenCode, opencode run, delegar para OpenCode, @opencode.

**Pré-requisitos:** `npm i -g opencode-ai@latest`, `opencode auth login`.

```bash
opencode run 'Add retry logic to API calls'              # one-shot, sem pty
opencode run 'Review config' -f config.yaml              # com contexto
opencode run 'Refactor' --model openrouter/anthropic/claude-sonnet-4
opencode pr 42                                           # PR review
```

**Interativo (pty=true):** `opencode` em background, `process(action="submit")` para enviar prompts.

**Sair:** Ctrl+C (`\x03`), nunca `/exit` (abre seletor de agentes).

**Pitfalls:** `opencode run` NÃO precisa de pty; TUI sim. `/exit` inválido (use Ctrl+C). PATH mismatch. Evitar mesmo workdir para paralelos.

## `hermes-config` — Configurar/Estender Hermes Agent

**Gatilhos:** configurar Hermes, setup Hermes, hermes config, hermes tools, spawn Hermes.

**Docs:** https://hermes-agent.nousresearch.com/docs/

**Comandos essenciais:**
```bash
hermes setup              # Wizard interativo
hermes model              # Trocar modelo/provider
hermes config set KEY VAL # Ex: hermes config set approvals.mode smart
hermes tools              # TUI enable/disable toolsets
hermes doctor             # Health check
```

**Spawning:** `hermes chat -q 'task'` (one-shot), ou tmux para interativo: `tmux new-session -d -s agent 'hermes'`.

**Toolsets comuns:** `web`, `terminal`, `file`, `vision`, `delegation`, `memory`, `skills`.

**Pitfalls:** Mudanças de tools/config só aplicam no `/reset` (nova sessão). Gateway requer `systemctl --user` no Linux. `security.redact_secrets` precisa de restart do processo.

## `skill-forge` — Criar Nova Skill

**Gatilhos:** criar skill, nova skill, forge skill, criar habilidade.

**Convenção 42_chat:** skills versionadas no repo `.hermes/skills/<cat>/<nome>/` com symlink em `~/.hermes/skills/`.

**Fluxo:**
1. Coletar: nome (lowercase-hyphen, max 64), categoria, descrição com gatilhos.
2. Validar: nome `^[a-z0-9][a-z0-9-]*$`, skill não pode já existir.
3. Consultar templates na wiki: `brain query "spec template skill"` para o formato canônico de SKILL.md. A wiki tem os templates e referências de formato no vault.
4. Preencher `SKILL.md`: Propósito, Pré-requisitos, Fluxo, Guardrails.
5. Frontmatter obrigatório: `name`, `description` (sem description = skill ignorada).
6. Verificar symlink: `readlink -f ~/.hermes/skills/<cat>/<nome>` → aponta pro repo.

**Referências na wiki:**
- `[[skills/brain|brain]]` modo `format` — sintaxe OFM, callouts, frontmatter, embeds
- `[[references/toolkits/sdd/spec-template|Spec Template]]` — template canônico de spec.md (adaptável para SKILL.md)
- `[[references/toolkits/wiki/karpathy-pattern|Karpathy Pattern]]` — padrão de destilação de conhecimento

**Pitfalls:** Nunca sobrescrever skill existente. Nunca criar direto em `~/.hermes/skills/` (sempre repo primeiro). `description` é obrigatório. Consulte a wiki para formatos antes de inventar estrutura.

## Referência Rápida: Qual Modo Usar?

| Situação | Modo |
|----------|------|
| Task de código Go | `go` |
| Task de frontend React | `react` |
| Antes de reportar DONE | `build-check` |
| Planejar antes de implementar | `plan` |
| Testar viabilidade de ideia | `spike` |
| Bug / teste falhando | `debug` |
| Revisar antes de commit | `code-review` |
| Limpar código pós-implementação | `simplify` |
| Debug Node.js/TS | `node-debug` |
| Debug Python | `python-debug` |
| Delegar para Claude Code | `claude-code` |
| Delegar para Codex CLI | `codex` |
| Delegar para OpenCode | `opencode` |
| Configurar Hermes | `hermes-config` |
| Criar nova skill | `skill-forge` |
