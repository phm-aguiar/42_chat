# AGENTS.md

## Language & toolchain
- **Go** project. Use `go.mod` when it exists. Currently no source code.
- `.gitignore` follows the standard Go template (binaries, `.test`, coverage artifacts, `go.work`, `.env`).

## Commands
- Run tests: `go test ./...`
- To run tests for a single package: `go test ./path/to/package/...`

## Branch strategy
- `main` — production. PRs must come from `develop`.
- `develop` — integration. PRs must come from `feature/*` branches.
- `feature/*` — feature work. A PR to `develop` is auto-created on push.
- Only branches from users other than `Copilot` are blocked by the enforce-branch-flow workflow.

## CI (GitHub Actions)
- `go test ./...` runs on all PRs targeting `develop` and `main`.
- Branch flow is enforced automatically — don't open PRs that violate `main <- develop <- feature/*` unless you're `Copilot`.
- Auto-PR workflows run on push: `feature/*` → `develop` and `develop` → `main`.

## SDD Workflow

Este projeto segue **Spec-Driven Development (SDD)**. Toda feature segue o fluxo:

1. `specs/features/<id>-<nome>/spec.md` — Especificação funcional (o QUE, não o COMO)
2. `specs/features/<id>-<nome>/plan.md` — Plano arquitetural (decisões técnicas, ADR)
3. `specs/features/<id>-<nome>/tasks.md` — Tarefas atômicas ordenadas
4. Implementação — Código derivado dos artefatos acima

### Regras
- **Nunca implemente sem spec.md e plan.md aprovados** pelo usuário.
- Leia `constitution.md` antes de qualquer alteração de código.
- Consulte `tech.md` antes de adicionar dependências.
- Valide a estrutura com `sdd-validate` periodicamente.
- Pergunte ao usuário ANTES de modificar `constitution.md`.

### Skills SDD disponíveis
- Inicializar estrutura: `sdd-init-repo`
- Mapear stack: `sdd-explore-tech`
- Validar conformidade: `sdd-validate`
- Refatorar artefatos: `sdd-refactor-artifact`
- Gerar plano (plan.md): `sdd-generate-plan`
- Gerar tarefas (tasks.md): `sdd-generate-tasks`

## Environment
- `.env` files are gitignored. No `.env.example` exists yet.
