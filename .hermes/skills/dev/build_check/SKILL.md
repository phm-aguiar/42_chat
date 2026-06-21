---
name: build_check
description: >
  Use when the agent-dev needs to run smoke tests and build verification.
  Runs go build ./..., go vet ./..., and npm run build (when frontend exists),
  checks for compilation errors and basic code health. The mandatory smoke-test
  gate before reporting DONE. Also verifies that the project structure follows
  the conventions defined in the feature plan. Trigger keywords: build check,
  smoke test, smoke check, go build, verificar build, compilar projeto,
  go vet, build verification.
version: 0.1.0
author: phm-aguiar
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [dev, testing, build, verification, smoke-test, ci]
    related_skills: [go_implement, react_implement, local_test_runner]
    category: dev
    created: 2026-06-16
    resources:
      - SKILL.md
---

# build_check — Smoke test e verificação de build

> Categoria: `dev` — criada em 2026-06-16. Portão de qualidade obrigatório do agent-dev.

## Propósito

Esta skill é o **portão de qualidade** que o agent-dev deve cruzar antes de
reportar DONE em qualquer task. Ela executa verificações de compilação e sanidade
do código para garantir que o que foi implementado não quebrou o projeto.

É a implementação do passo 4 (Smoke-test) do ciclo de trabalho do agent-dev:
"Smoke-test deve passar com **exit code 0**."

## Pré-requisitos

- Go 1.21+ instalado e no PATH (`go version`)
- `go.mod` na raiz do projeto (se for backend Go)
- Node.js 20+ e npm (se houver frontend em `web/`)
- `package.json` em `web/` (se houver frontend)
- Diretório de trabalho = raiz do projeto

## Quando usar (gatilhos)

- Passo 4 do ciclo do agent-dev: "Smoke-test"
- Antes de reportar DONE em qualquer task
- "verificar build", "compilar", "smoke test"
- Após implementar ou modificar qualquer arquivo

## Fluxo de Execução

### Passo 1: Determinar escopo

Inspecione o que existe no projeto:

```bash
# Verificar se é projeto Go
test -f go.mod && echo "GO" || echo "NO_GO"

# Verificar se tem frontend React
test -f web/package.json && echo "REACT" || echo "NO_REACT"
```

Com base no que existe, execute os checks relevantes. Se for task de backend puro (ex: T004-T011), execute apenas Go. Se for frontend (T012-T014), execute ambos se `go.mod` existir.

### Passo 2: Go build

```bash
go build ./...
```

**Interpretação:**
- `exit code 0` → ✅ Compilação OK
- `exit code != 0` → ❌ Erro de compilação. Leia o erro, corrija, repita.

Erros comuns e soluções:
| Erro | Causa | Solução |
|-------|-------|---------|
| `undefined: X` | Símbolo não definido | Verificar imports, nome do pacote, ou dependência de task anterior |
| `imported and not used` | Import não usado | Remover import ou usar `_` |
| `cannot use X as Y` | Tipo incompatível | Verificar assinatura da função |
| `no required module provides package` | Dependência faltando | `go get <pacote>` |

### Passo 3: Go vet

```bash
go vet ./...
```

**Interpretação:**
- `exit code 0` → ✅ Sem problemas detectáveis estaticamente
- `exit code != 0` → ⚠️ Problemas de código (não necessariamente bloqueantes, mas devem ser corrigidos)

`go vet` detecta:
- Chamadas suspeitas (ex: `Printf` com argumentos errados)
- Goroutines com variáveis de loop capturadas incorretamente
- Struct tags inválidas
- Código inalcançável

### Passo 4: npm build (se houver frontend)

```bash
cd web && npm run build
```

**Interpretação:**
- `exit code 0` → ✅ Frontend compila
- `exit code != 0` → ❌ Erro no build. Verificar mensagens de erro.

Erros comuns:
- `Module not found` → `npm install` faltando
- `Tailwind CSS class not found` → classe mal escrita ou não definida no config
- `JSX error` → sintaxe inválida ou import faltando

### Passo 5: Verificações de estrutura (opcional, quando relevante)

Se a task envolveu criar novos diretórios, verifique:

```bash
# Estrutura backend esperada (após T001-T011)
test -f cmd/server/main.go && echo "✓ main.go"
test -d internal/auth && echo "✓ internal/auth/"
test -d internal/chat && echo "✓ internal/chat/"
test -d internal/api && echo "✓ internal/api/"
test -d internal/repository && echo "✓ internal/repository/"

# Estrutura frontend esperada (após T012-T014)
test -f web/src/App.jsx && echo "✓ App.jsx"
test -d web/src/components && echo "✓ components/"
test -d web/src/store && echo "✓ store/"
test -d web/src/hooks && echo "✓ hooks/"
```

### Passo 6: Reportar resultado

Formato padrão do agent-dev para smoke-test:

```
Smoke-test:
$ go build ./...
exit code: 0

$ go vet ./...
exit code: 0
```

Se houver frontend:
```
$ cd web && npm run build
exit code: 0
```

**Se falhar:**
```
Smoke-test:
$ go build ./...
exit code: 1

Erro:
internal/chat/hub.go:42:15: undefined: Client

Possível causa:
Struct Client não foi definida. Dependência T008 (WebSocket Client) pode não estar concluída.
```

## Guardrails

- **Exit code 0 é obrigatório para DONE**: sem `go build ./...` passando, não reporte DONE.
- **go vet warnings não bloqueiam, mas corrija**: se `go vet` falhar, corrija antes de reportar DONE. É um sinal de código frágil.
- **npm build só se existir frontend**: não execute `npm run build` se `web/package.json` não existir.
- **Erros de dependência ausente**: se `go build` falhar com "no required module", execute `go get <pacote>` e repita o build.
- **Não confunda smoke-test com testes unitários**: esta skill só verifica **compilação**. Testes unitários (`go test`) são responsabilidade do agent-qa (`local_test_runner`).
- **Contexto importa**: se a task é T001 (só estrutura de diretórios), `go build` pode falhar legitimamente. Adapte o check ao estágio do projeto.
- **Sempre execute da raiz do projeto**: `go build ./...` usa o `go.mod` da raiz. Executar de subdiretórios pode falhar.

## Verificação

- [ ] `go build ./...` retornou exit code 0 (ou falhou com erro esperado para a fase atual)
- [ ] `go vet ./...` retornou exit code 0 (ou warnings foram analisados e são aceitáveis)
- [ ] `npm run build` retornou exit code 0 (se `web/package.json` existe)
- [ ] Nenhum arquivo `.go` tem erros de sintaxe não resolvidos
- [ ] Estrutura de diretórios segue o plano (se task for de scaffolding)
