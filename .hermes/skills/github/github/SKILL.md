---
name: github
description: "GitHub toolkit: auth, PR, review, issues, repo, commit, inspect — via gh CLI ou git+curl fallback."
version: 2.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Git, PR, Code-Review, Issues, Repo, Commit, LOC, Toolkit]
    absorbed:
      - github-auth
      - github-pr-workflow
      - github-code-review
      - github-issues
      - github-repo-management
      - git_conventional_commit
      - codebase-inspection
---

# GitHub Toolkit

Toolkit consolidado com 7 modos. Prefira `gh` CLI; fallback `git` + `curl` com token. Cada modo: gatilho, fluxo, pitfalls.

## Setup Compartilhado (Auth Bootstrap)

Execute antes de qualquer modo que acesse a API:

```bash
# Detecta auth method
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"
  [ -z "$GITHUB_TOKEN" ] && GITHUB_TOKEN=$(grep -s "^GITHUB_TOKEN=" "${HERMES_HOME:-$HOME/.hermes}/.env" | head -1 | cut -d= -f2 | tr -d '\n\r')
  [ -z "$GITHUB_TOKEN" ] && GITHUB_TOKEN=$(grep -s "github.com" ~/.git-credentials | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
fi

REMOTE_URL=$(git remote get-url origin 2>/dev/null)
if [ -n "$REMOTE_URL" ]; then
  OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
  OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
  REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
fi
```

---

## Modo 1: `auth` — Autenticação GitHub

**Gatilho:** "configurar GitHub", "gh auth", "token", "permission denied", "git push pede senha"

### Fluxo

1. **Diagnóstico:**
```bash
gh auth status 2>/dev/null && echo "OK: gh" || echo "gh não autenticado"
git config --global credential.helper 2>/dev/null || echo "sem credential helper"
```

2. **Se `gh` autenticado** → pronto.

3. **`gh` instalado mas não autenticado:**
```bash
echo "<TOKEN>" | gh auth login --with-token && gh auth setup-git
```

4. **Sem `gh` — HTTPS + token (recomendado):**
   - Usuário cria token em https://github.com/settings/tokens com scopes `repo`, `workflow`, `read:org`
   ```bash
   git config --global credential.helper store
   git config --global user.name "Nome"
   git config --global user.email "email@ex.com"
   # Primeiro push solicita user:token → salvo em ~/.git-credentials
   ```

5. **Alternativa SSH:**
```bash
ssh-keygen -t ed25519 -C "email" -f ~/.ssh/id_ed25519 -N ""
cat ~/.ssh/id_ed25519.pub    # → adicionar em https://github.com/settings/keys
ssh -T git@github.com
git config --global url."git@github.com:".insteadOf "https://github.com/"
```

6. **API sem gh (curl):**
```bash
export GITHUB_TOKEN="<token>"
curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
```

### Pitfalls
- GitHub desabilitou password auth — use token como "password"
- `fatal: Authentication failed` → credential stale: `git credential reject` + re-auth
- SSH port 22 bloqueado → `~/.ssh/config`: `Host github.com` + `Port 443` + `Hostname ssh.github.com`
- Múltiplas contas → SSH aliases por host ou token por repositório

---

## Modo 2: `pr` — Pull Request Lifecycle

**Gatilho:** "criar PR", "abrir pull request", "merge", "CI status", "auto-merge"

### Fluxo

1. **Branch + commit:**
```bash
git fetch origin && git checkout main && git pull origin main
git checkout -b feat/descricao     # prefixos: feat/, fix/, refactor/, docs/, ci/
# (faz alterações)
git add <files> && git commit -m "feat: descricao curta"
```

2. **Push + criar PR:**
```bash
git push -u origin HEAD
# gh:
gh pr create --title "feat: titulo" --body "## Summary\n...\n\nCloses #N" [--draft] [--reviewer user] [--label "label"]
# curl:
BRANCH=$(git branch --show-current)
curl -s -X POST -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls \
  -d "{\"title\":\"...\",\"body\":\"...\",\"head\":\"$BRANCH\",\"base\":\"main\"}"
```

3. **Monitorar CI:**
```bash
gh pr checks --watch          # polling automático
# curl: polling manual 30s × 20 iterações
SHA=$(git rev-parse HEAD)
for i in $(seq 1 20); do
  STATUS=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/status \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['state'])")
  [ "$STATUS" != "pending" ] && break
  sleep 30
done
```

4. **Auto-fix CI (loop, máx 3 tentativas):**
```bash
gh run view <ID> --log-failed           # ver logs
# curl: curl -sL -H "Authorization: token $GITHUB_TOKEN" \
#   https://api.github.com/repos/$OWNER/$REPO/actions/runs/<ID>/logs -o /tmp/ci-logs.zip
# Corrigir → commit → push → re-check
```

5. **Merge:**
```bash
gh pr merge --squash --delete-branch                     # squash merge
gh pr merge --auto --squash --delete-branch               # auto-merge
# curl: PUT /repos/$OWNER/$REPO/pulls/$N/merge -d '{"merge_method":"squash"}'
```

### Pitfalls
- Branch naming: `feat/`, `fix/`, `refactor/`, `docs/`, `ci/`
- Nunca push sem usuário pedir
- Auto-merge requer feature habilitada em repo Settings
- PRs >500 LOC → sugira split

---

## Modo 3: `review` — Code Review

**Gatilho:** "revisar código", "review PR", "revisar antes de push", "analisar diff"

### Fluxo

#### Revisão Local (pre-push)

1. **Escopo e análise:**
```bash
git diff main...HEAD --stat && git log main..HEAD --oneline
git diff main...HEAD
# Checks automáticos:
git diff main...HEAD | grep -nE "print\(|console\.log|TODO|FIXME|HACK|XXX|debugger"
git diff main...HEAD | grep -inE "password|secret|api_key|token\s*=|private_key"
git diff main...HEAD | grep -nE "<<<<<<|>>>>>>|======="
```

2. **Checklist:** Corretude (edge cases, errors) → Segurança (secrets, injection, XSS) → Qualidade (nomes, DRY, funções focadas) → Testes (happy + edge) → Performance (N+1, bloqueantes) → Documentação (APIs públicas)

3. **Output estruturado:**
```
## Code Review Summary
### 🔴 Critical
- **file:line** — descrição. Sugestão: ...
### ⚠️ Warnings
- **file:line** — descrição
### 💡 Suggestions
- **file:line** — descrição
### ✅ Looks Good
- ponto positivo
```

#### Revisão de PR no GitHub

1. **Coletar contexto:**
```bash
gh pr view N && gh pr diff N --name-only && gh pr checks N
# curl: GET /repos/$OWNER/$REPO/pulls/N
```

2. **Checkout local + testes:**
```bash
git fetch origin pull/N/head:pr-N && git checkout pr-N   # gh shortcut: gh pr checkout N
# Rodar testes: pytest / npm test / cargo test / go test
```

3. **Submeter review:**
```bash
# gh:
gh pr review N --approve --body "LGTM!"
gh pr review N --request-changes --body "Ver comentários inline."
gh pr review N --comment --body "Sugestões, nada bloqueante."

# curl — review atômica com inline comments:
HEAD_SHA=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/N \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['head']['sha'])")
curl -s -X POST -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/N/reviews \
  -d '{"commit_id":"'$HEAD_SHA'","event":"REQUEST_CHANGES","body":"...","comments":[
    {"path":"src/auth.py","line":45,"body":"SQL injection: use parameterized queries."}
  ]}'
```
Eventos: `APPROVE` (zero críticos), `REQUEST_CHANGES` (qualquer crítico/warning), `COMMENT` (sugestões)

4. **Limpeza:** `git checkout main && git branch -D pr-N`

### Pitfalls
- `line` = versão NOVA; use `"side":"LEFT"` para linhas removidas
- Inline comments precisam do `commit_id` do HEAD do PR
- Sempre complemente diff com `read_file` para contexto completo
- Rode testes locais quando disponíveis — catching issues antes de reportar

---

## Modo 4: `issues` — Gerenciamento de Issues

**Gatilho:** "criar issue", "listar issues", "triage", "fechar issue", "labels", "assign"

### Fluxo

1. **Listar:**
```bash
gh issue list --state open --label "bug"
gh issue list --assignee @me
gh issue list --search "termo"
# curl: GET /repos/$OWNER/$REPO/issues?state=open&labels=bug
# ⚠️ API retorna PRs também → filtrar: if 'pull_request' not in item
```

2. **Criar:**
```bash
# Bug report:
gh issue create --title "titulo" --body "## Description\n...\n## Steps\n1. ...\n## Expected\n...\n## Actual\n..." --label "bug,backend" --assignee "user"

# Feature request:
gh issue create --title "titulo" --body "## Feature\n...\n## Motivation\n...\n## Proposed Solution\n..." --label "enhancement"

# curl: POST /repos/$OWNER/$REPO/issues -d '{"title":"...","body":"...","labels":["bug"],"assignees":["user"]}'
```

3. **Gerenciar:**
```bash
gh issue edit N --add-label "priority:high" --remove-label "needs-triage"
gh issue edit N --add-assignee @me
gh issue comment N --body "texto"
gh issue close N --reason "completed"    # ou "not planned"
gh issue reopen N
# curl: PATCH /repos/$OWNER/$REPO/issues/N -d '{"state":"closed","state_reason":"completed"}'
```

4. **Triage:** Liste `needs-triage` → categorize → aplique labels/priority → atribua → comente

5. **Bulk:**
```bash
gh issue list --label "wontfix" --json number --jq '.[].number' | \
  xargs -I {} gh issue close {} --reason "not planned"
```

### Pitfalls
- API `/issues` inclui PRs — sempre filtrar
- `Closes #N` / `Fixes #N` no body do PR fecha issue ao mergear
- Branch de issue: `gh issue develop N --checkout`
- State reasons: `completed` (resolvida), `not_planned` (não será feita)

---

## Modo 5: `repo` — Gerenciamento de Repositórios

**Gatilho:** "clonar repo", "criar repositório", "fork", "release", "secrets", "workflow", "branch protection"

### Fluxo

1. **Clone:**
```bash
git clone https://github.com/owner/repo.git
git clone --depth 1 https://github.com/owner/repo.git     # shallow
git clone --branch develop https://github.com/owner/repo.git
gh repo clone owner/repo                                    # atalho
```

2. **Criar:**
```bash
gh repo create nome --public --clone --description "desc"
gh repo create nome --private --license MIT --clone
gh repo create org/nome --source . --public --push          # dir existente
# curl: POST /user/repos ou POST /orgs/{org}/repos
```

3. **Fork:**
```bash
gh repo fork owner/repo --clone
# curl: POST /repos/owner/repo/forks → clone → git remote add upstream URL
# Sync: git fetch upstream && git merge upstream/main && git push origin main
```

4. **Info & Settings:**
```bash
gh repo view owner/repo
gh repo edit --description "nova" --visibility public --enable-auto-merge
gh repo edit --add-topic "python,ml"
```

5. **Releases:**
```bash
gh release create v1.0.0 --title "v1.0.0" --generate-notes
gh release create v2.0.0-rc1 --draft --prerelease --generate-notes
gh release list && gh release download v1.0.0 --dir ./downloads
# curl: POST /repos/$OWNER/$REPO/releases → upload assets separado
```

6. **Secrets (prefira `gh` — curl requer encrypt PyNaCl):**
```bash
gh secret set API_KEY --body "valor"
gh secret list && gh secret delete API_KEY
```

7. **Branch Protection:** `curl -X PUT /repos/$OWNER/$REPO/branches/main/protection` com JSON de `required_status_checks`, `required_pull_request_reviews`, `enforce_admins`

### Pitfalls
- Secrets via curl = complexo (encrypt com libsodium) → use `gh secret set`
- Releases via curl: release (POST) + asset upload (POST uploads.github.com) separados
- Fork: sempre adicione `upstream` remote para sync
- Branch protection: requer repo público ou GitHub Pro/Team

---

## Modo 6: `commit` — Conventional Commits

**Gatilho:** "commitar", "git commit", "preparar commit", "mensagem de commit"

### Fluxo

1. **Analisar:**
```bash
git status --short && git diff --stat HEAD
```

2. **Agrupar por tipo semântico:**

| Tipo | Quando usar |
|------|------------|
| `feat` | Nova feature, spec, skill, funcionalidade |
| `fix` | Correção de bug |
| `docs` | Documentação (README, AGENTS.md) |
| `refactor` | Refatoração sem mudança de comportamento |
| `test` | Testes |
| `chore` | Deps, config, CI, symlinks, cleanup |
| `style` | Formatação, lint, whitespace |

3. **Formato squad:**
```
<tipo>: <título curto, max 72 chars, lowercase>

<tipo>:
 - <item 1>
 - <item 2>

<outro-tipo>:
 - <item 3>
```

4. **Executar e verificar:**
```bash
git add -A                              # ou git add <paths>
git commit -m "<mensagem formatada>"
git log --oneline -1
```

### Regras
- Título: max 72 chars, lowercase, sem ponto final
- Seções: só incluir com itens, nunca vazias
- Itens: dash + espaço, lowercase, sem ponto final
- Ordem: feat → fix → docs → refactor → test → chore → style
- **Nunca commitar/push sem usuário pedir**
- Sempre `git add -A` a menos que usuário especifique paths

### Exemplo
```
feat: adiciona pipeline SDD com brainstorm interativo

feat:
 - adiciona sdd-brainstorm com entrevista via clarify()
 - gera spec.md a partir de template canônico

docs:
 - atualiza AGENTS.md com seção SDD Workflow

chore:
 - remove diretório .opencode/ obsoleto
```

### Pitfalls
- Bloqueado: "fix bugs", "update", "wip", "." — seja específico
- Nunca mencione "tools" como ator nem inclua secrets/tokens
- Diff >20 arquivos → sugira splits ou alerte

---

## Modo 7: `inspect` — Inspeção de Codebase

**Gatilho:** "LOC", "linhas de código", "linguagens do projeto", "tamanho do repo"

### Fluxo

1. **Instalar:**
```bash
pip install --break-system-packages pygount 2>/dev/null || pip install pygount
```

2. **Resumo por linguagem:**
```bash
pygount --format=summary \
  --folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,.eggs,*.egg-info,.mypy_cache,.turbo,coverage,vendor,third_party" \
  .
```
Adicione/exclua pastas conforme o stack: Python + `.mypy_cache`, JS/TS + `.turbo,coverage,.next`, Go + `vendor`.

3. **Filtrar / detalhar:**
```bash
pygount --suffix=py --format=summary .                # só Python
pygount --suffix=py,yaml,yml --format=summary .        # Python + YAML
pygount . | sort -t$'\t' -k1 -nr | head -20            # top arquivos por LOC
pygount --format=json .                                 # JSON programático
```

### Colunas
Language | Files | Code | Comment | % — mais pseudo: `__empty__`, `__binary__`, `__generated__`, `__duplicate__`, `__unknown__`

### Pitfalls
- **Sempre usar `--folders-to-skip`** — sem isso pygount trava em node_modules/venv
- Markdown mostra 0 code lines (classificado como comment) — esperado
- JSON tem contagem conservadora — use `wc -l` para precisão
- Monorepos: use `--suffix` para linguagens específicas

---

## Referência Rápida

| Ação | gh | curl (prefixo: `/repos/$OWNER/$REPO`) |
|------|-----|---------------------------------------|
| Criar PR | `gh pr create ...` | `POST .../pulls` |
| Merge PR | `gh pr merge N` | `PUT .../pulls/N/merge` |
| PR checks | `gh pr checks` | `GET .../commits/{sha}/status` |
| Review | `gh pr review N ...` | `POST .../pulls/N/reviews` |
| Issues | `gh issue {create,list,close}` | `{POST,GET,PATCH} .../issues` |
| Criar repo | `gh repo create ...` | `POST /user/repos` |
| Fork | `gh repo fork o/r` | `POST /repos/o/r/forks` |
| Release | `gh release create ...` | `POST .../releases` |
| Secrets | `gh secret set K` | `PUT .../actions/secrets/K` |
| Rerun CI | `gh run rerun ID` | `POST .../actions/runs/ID/rerun` |
| Auth status | `gh auth status` | `GET /user` |
