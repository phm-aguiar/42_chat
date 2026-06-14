# AGENTS.md — Framework SDD Autônomo

> **Produto:** Framework SDD autônomo com agentes IA.
> **Não é um projeto Go.** O app 42_chat é um smoke-test futuro.

## Linguagens do Framework
- **Python** — Skills (runtime das tools), scripts de validação
- **YAML** — Config de agentes (`context.yaml`), frontmatter de skills
- **Markdown** — Specs, docs, wiki vault (`wiki/`)
- **Shell (bash)** — Scripts auxiliares, CI/CD

## Comandos
- Validar estrutura SDD: `sdd-validate`
- Validar vault Obsidian: `wiki-lint`
- Rodar smoke tests (quando existirem): verificar que agentes carregam sem erro
- Não há `go test` — o framework não é Go

## Knowledge Base — Consulte antes de agir

Este repositório mantém uma **base de conhecimento compilada** no vault Obsidian (`wiki/`) e
um índice navegável para LLMs (`llms.txt`). Antes de implementar, decidir ou sugerir qualquer
coisa, **consulte a base**. Não reinvente conhecimento que já foi compilado.

### Entry points
| Recurso | Caminho | Quando usar |
|---|---|---|
| `llms.txt` | Raiz do repo | Navegação inicial — lista specs, agentes, skills e links |
| `wiki/index.md` | `wiki/index.md` | Catálogo completo do vault com seções por categoria |
| `wiki-query` | Skill | Busca conhecimento compilado (ex: "o que já decidimos sobre X?") |
| `wiki-lint` | Skill | Audita saúde do vault (broken links, órfãos, frontmatter) |

### Fluxo de consulta
1. **Antes de implementar:** `wiki-query` para ver se já existe decisão/documentação sobre o tema
2. **Após implementar:** `wiki-ingest` para destilar spec/plan/tasks em página wiki
3. **Após mudança estrutural:** `wiki-lint` para validar integridade do vault
4. **Periodicamente:** `doc-generate-llms-txt` para manter `llms.txt` atualizado

> **Regra de ouro:** O vault é a memória de longo prazo do framework.
> Toda decisão arquitetural, feature implementada, ou mudança estrutural
> deve ser refletida no vault. Vault desatualizado bloqueia PR.

## Branch Strategy
- `main` — produção. PRs devem vir de `develop`.
- `develop` — integração. PRs devem vir de `feature/*` branches.
- `feature/*` — feature work. PR para `develop` é auto-criado no push.
- Branch flow é enforced automaticamente (`feature/*` → `develop` → `main`).

## CI (GitHub Actions)
- Branch flow enforcement em todos os PRs.
- Auto-PR workflows: push em `feature/*` → PR para `develop`; push em `develop` → PR para `main`.
- Validação SDD (`sdd-validate`) será adicionada ao pipeline quando houver smoke tests.

## SDD Workflow

Este projeto segue **Spec-Driven Development (SDD)**. Toda feature segue o fluxo:

1. `specs/features/<id>-<nome>/spec.md` — Especificação funcional (o QUE, não o COMO)
2. `specs/features/<id>-<nome>/plan.md` — Plano arquitetural (decisões técnicas, ADR)
3. `specs/features/<id>-<nome>/tasks.md` — Tarefas atômicas em formato DAG (Papel, Dependências, Paralelizável, Arquivos)
4. Aprovação: `Aprovado: true` no spec.md → `agent-run agent-orchestrator` executa
5. Implementação — Subagentes (Dev, QA, DevOps, Pentester) spawnados em paralelo pelo orchestrator

### Regras
- **Nunca implemente sem spec.md e plan.md aprovados** pelo usuário.
- **Consulte a base antes de decidir:** use `llms.txt` ou `wiki-query` antes de implementar, sugerir arquitetura, ou adicionar dependências. Não reinvente conhecimento já compilado no vault.
- Leia `constitution.md` antes de qualquer alteração de código.
- Consulte `tech.md` antes de adicionar dependências.
- Valide a estrutura com `sdd-validate` periodicamente.
- Valide o vault com `wiki-lint` após mudanças estruturais.
- Pergunte ao usuário ANTES de modificar `constitution.md`.
- **Vault fiel:** após implementar feature, agente, ou skill, atualize o vault (`wiki-ingest` + `wiki-lint`).

### Skills SDD (Hermes Agent — `.hermes/skills/` no repo)
- Inicializar estrutura: `sdd-init-repo`
- Mapear stack: `sdd-explore-tech`
- Validar conformidade: `sdd-validate`
- Refatorar artefatos: `sdd-refactor-artifact`
- Brainstorm de features: `sdd-brainstorm`
- Gerar plano (plan.md): `sdd-generate-plan`
- Gerar tarefas (tasks.md com DAG): `sdd-generate-tasks`

### Skills de documentação
- Extrair seção de markdown: `doc-extract`
- Gerar tabela de conteúdo: `doc-generate-toc`
- Gerar llms.txt: `doc-generate-llms-txt`

### Skills de Wiki (knowledge management)
- Pipeline de destilação: `wiki-ingest`
- Busca híbrida: `wiki-query`
- Auditoria de saúde: `wiki-lint`
- Salvar conversa: `wiki-capture`
- Auto-wikilinks: `wiki/cross-linker`
- Setup do vault: `wiki-setup`
- Status/delta: `wiki-status`
- Dashboards: `wiki-dashboard`
- Resumo periódico: `wiki-digest`
- Exportar grafo: `wiki-export`
- Síntese cross-cutting: `wiki-synthesize`
- Deduplicação: `wiki-dedup`
- Taxonomia de tags: `wiki/tag-taxonomy`
- Histórico Hermes: `wiki/hermes-history-ingest`
- Fundação teórica: `wiki/llm-wiki`

### Skills de Obsidian (formato + tooling)
- Sintaxe OFM: `obsidian/obsidian-markdown`
- CLI do Obsidian: `obsidian/obsidian-cli`
- Bases (.base): `obsidian/obsidian-bases`
- Canvas (.canvas): `obsidian/json-canvas`
- Extrair markdown limpo: `obsidian/defuddle`

### Skills visuais
- Diagramas Mermaid: `visual/mermaid-visualizer`

### Skills de tooling
- Criar nova skill Hermes: `skill-forge`
- Executar agente com contexto limpo: `agent-run`
- Commit convencional: `git-conventional-commit`

### Agentes (`.hermes/agents/` — invocados via `agent-run`)
- `onboard` — Inicializa projeto no framework SDD (init repo, explore tech, brainstorm features).
- `agent-orchestrator` — Executor runtime. Lê `tasks.md` com DAG e spawna subagentes em paralelo via `delegate_task`.
- `agent-dev` — ✅ Implementado. Persona fixa com skills plugáveis por stack. Spawnado pelo orchestrator como subagente leaf. Ciclo: lê contexto → planeja → implementa → smoke-test → reporta (DONE/FAIL/BLOCKED). Skills são trilhos, não jaulas.
- `agent-qa` (007) — Pendente. Testes, Gherkin, lint.
- `agent-devops` (008) — Pendente. CI/CD, Docker, deploy.
- `agent-pentester` (009) — Pendente. Segurança, OWASP, secrets.

> **Nota:** Agentes e skills vivem em `.hermes/agents/` e `.hermes/skills/`, versionados no repo,
> com symlinks em `~/.hermes/`. O `agent-run` compila contexto limpo (sem corrosão de sessão)
> e spawna subagentes isolados via `delegate_task`.

## Environment
- `.env` files são gitignored.
- Homelab: RPi 5 (zeenyt-1), Docker, Tailscale.
- Memory: Honcho self-hosted.
- Wiki vault: `wiki/` versionado como parte do framework.
