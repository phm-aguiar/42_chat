---
name: qa_toolkit
description: >
  Toolkit consolidado de QA e testes. 8 modos cobrindo o ciclo completo:
  BDD discovery → Gherkin → step definitions → unit tests → execução →
  E2E → TDD → dogfood exploratório. Carregado pelo agent-qa.
version: 2.0.0
author: phm-aguiar (consolidação feature 008-reavaliacao-skills)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [QA, Testing, BDD, TDD, Gherkin, Playwright, Go, Dogfood]
    category: qa
    modes:
      - bdd-spec
      - gherkin
      - cucumber
      - unit-tests
      - test-runner
      - e2e
      - tdd
      - dogfood
    resources:
      - SKILL.md
      - references/gherkin-syntax.md
      - references/gherkin-best-practices.md
      - references/gherkin-anti-patterns.md
      - references/table-driven.md
      - references/edge-cases.md
      - references/issue-taxonomy.md
      - templates/dogfood-report-template.md
---

# qa_toolkit — Qualidade e Testes (8 modos)

> Toolkit unificado do agent-qa. Cada modo cobre uma fase do ciclo de qualidade.

## Índice de Modos

| Modo | Gatilho | Fase QA |
|---|---|---|
| `bdd-spec` | Discovery workshop com stakeholders | Pré-implementação |
| `gherkin` | Escrever .feature files | Especificação |
| `cucumber` | Step definitions Go (Godog) | Conexão spec↔código |
| `unit-tests` | Testes unitários Go (table-driven) | Validação de código |
| `test-runner` | Build + vet + test + cover | Execução |
| `e2e` | Playwright + BDD end-to-end | Integração |
| `tdd` | Ciclo RED-GREEN-REFACTOR | Desenvolvimento |
| `dogfood` | QA exploratória de web apps | Validação exploratória |

---

## Modo: bdd-spec

**Gatilho:** Discovery workshop — refinar requisitos com exemplos antes de implementar.

### Fluxo

1. **Example Mapping**: reúna stakeholders; para cada user story, liste rules, examples e questions.
2. **Formular cenários**: converta exemplos em cenários Gherkin (um exemplo = um cenário). Use linguagem ubíqua do domínio.
3. **Refinar edge cases**: para cada happy path, pergunte "o que pode dar errado?" — adicione cenários de erro, validação, limites.
4. **Validar com stakeholders**: "Se o sistema fizer exatamente isso, está pronto?" Ajuste até concordância.
5. **Integrar ao pipeline SDD**: cenários vão para `spec.md` → depois `sdd-generate_plan` e `sdd-generate_tasks`.

### Pitfalls

- Pular validação com stakeholders e assumir que os exemplos estão corretos
- Usar linguagem técnica em vez de termos do domínio
- Esquecer edge cases porque "o happy path é suficiente"

---

## Modo: gherkin

**Gatilho:** Transformar cenários BDD da spec em arquivos `.feature` válidos.

### Fluxo

1. **Identificar cenários na spec**: para cada um, extraia contexto (Dado), ação (Quando), resultado (Então).
2. **Escrever o .feature**:
   ```gherkin
   # language: pt
   Funcionalidade: <nome>
     <descrição breve>

     Cenario: <nome descritivo>
       Dado <contexto>
       Quando <ação>
       Então <resultado>
   ```
3. **Aplicar boas práticas**:
   - Cenários focados: um comportamento por cenário
   - Declarativo: "Dado que estou logado", não "Dado que clico no botão X"
   - Nomes descritivos: "Cadastro com email inválido retorna erro 400"
   - Background para pré-condições comuns
   - Esquema do Cenário (`Scenario Outline`) para dados variados
   - Tags: `@smoke`, `@regression` para categorizar
4. **Validar contra anti-patterns**: remova cenários com múltiplos When/Then, steps imperativos, dados hardcoded, asserções vagas, cenários >7 steps.
5. **Salvar**: em `<specs/features/NNN-nome/acceptance/>`.

### Pitfalls

- Multiplos When/Then no mesmo cenário (quebre em cenários separados)
- Steps imperativos com detalhes de UI em vez de comportamento
- Cenários sem asserção clara
- Dados irrelevantes poluindo o cenário
- Testar implementação ("função X foi chamada") em vez de comportamento

---

## Modo: cucumber

**Gatilho:** Implementar step definitions Go que conectam .feature files a código executável (Godog).

### Fluxo

1. **Setup**: `go get github.com/cucumber/godog/cmd/godog@latest`
2. **Mapear steps para funções Go**: cada linha do .feature vira uma função com regex:
   ```go
   func InitializeScenario(ctx *godog.ScenarioContext) {
       ctx.Step(`^nao existe usuario com email "([^"]*)"$`, naoExisteUsuarioComEmail)
       ctx.Step(`^envio POST /users com email "([^"]*)" e senha "([^"]*)"$`, envioPOSTComEmailESenha)
       ctx.Step(`^o status code e (\d+)$`, oStatusCodeE)
   }
   ```
3. **Executar**: `godog run ./features`
4. **Reusar steps**: steps bem escritos são reutilizáveis entre cenários (ex: "o status code e 201" serve para qualquer verificação HTTP).

### Pitfalls

- Regex que não captura grupos corretamente → step nunca encontra a função
- Esquecer de inicializar o contexto (`ctx.Step`) no `InitializeScenario`
- Criar steps duplicados em vez de reutilizar os existentes

---

## Modo: unit-tests

**Gatilho:** Escrever testes unitários Go a partir do código implementado pelo Dev.

### Fluxo

1. **Identificar funções a testar**: liste funções exportadas, assinatura, comportamento esperado pela spec.
2. **Escrever table-driven test**: struct com `name`, campos de entrada, `want`, `wantErr bool`; loop com `t.Run(tt.name, ...)`. Ver template completo em `references/table-driven.md`.
3. **Cobrir edge cases**:
   - Strings: vazia, muito longa, caracteres especiais, apenas espaços
   - Inteiros: zero, 1, -1, MaxInt, MinInt
   - Slices: vazio (nil), um elemento, muitos, duplicados
   - Ponteiros: nil
   - Erros: contexto cancelado, timeout, validação
4. **Organizar**: arquivo `xxx_test.go` no mesmo pacote, função `TestXxx`, subtests com `t.Run()`.
5. **Comandos**: `go test ./...`, `go test -v ./...`, `go test -run TestXxx`, `go test -cover ./...`

### Pitfalls

- Testar implementação em vez de comportamento
- Esquecer edge cases (zero values, nil, limites)
- Mocks excessivos que escondem bugs reais
- Nomes de teste vagos ("Teste 1", "funciona")

---

## Modo: test-runner

**Gatilho:** Executar suite de testes — build, vet, test, cover — e formatar relatório.

### Fluxo

1. **Build check**: `go build ./...` → falhou = **FAIL imediato**
2. **Vet check**: `go vet ./...` → warnings = **REJECTED**
3. **Executar testes**: `go test ./... -v -count=1` (sem cache, verbose) → exit ≠ 0 = **REJECTED**
4. **Cobertura**: `go test ./... -cover` → abaixo de 80% = **REJECTED**
5. **Formatar relatório**:
   ```
   DONE
   Testes: [output do go test -v]
   Vet: [output do go vet]
   Cobertura: [output do go test -cover]
   ```

### Comandos por stack

| Stack | Build | Vet/Lint | Test | Cover |
|---|---|---|---|---|
| Go | `go build ./...` | `go vet ./...` | `go test ./... -v -count=1` | `go test ./... -cover` |
| Python | `python -m compileall .` | `ruff check .` | `pytest -v` | `pytest --cov` |
| Node | `npm run build` | `npm run lint` | `npm test` | `npm test -- --coverage` |

### Pitfalls

- Esquecer `-count=1` e pegar cache do Go (falso positivo)
- Não rodar `go vet` — compila mas tem bugs sutis
- Aceitar cobertura abaixo do threshold sem justificativa

---

## Modo: e2e

**Gatilho:** Testes end-to-end com Playwright + BDD/Gherkin para browser automation.

### Fluxo

1. **Setup**:
   ```bash
   npm init -y
   npm install @playwright/test @cucumber/cucumber playwright-bdd
   npx playwright install
   ```
2. **Escrever .feature E2E**:
   ```gherkin
   # language: pt
   Funcionalidade: Login
     Cenario: Login com credenciais válidas
       Dado que estou na página de login
       Quando preencho email "teste@email.com" e senha "123456"
       E clico em "Entrar"
       Então vejo a dashboard
   ```
3. **Implementar step definitions** em TypeScript:
   ```typescript
   import { Given, When, Then } from '@cucumber/cucumber';
   import { expect } from '@playwright/test';

   Given('que estou na página de login', async function () {
       await this.page.goto('/login');
   });
   When('preencho email {string} e senha {string}', async function (email, senha) {
       await this.page.fill('#email', email);
       await this.page.fill('#senha', senha);
   });
   Then('vejo a dashboard', async function () {
       await expect(this.page.locator('.dashboard')).toBeVisible();
   });
   ```
4. **Executar**: `npx cucumber-js` ou `npx playwright test`

### Pitfalls

- Usar seletores frágeis (CSS classes dinâmicas) em vez de data-testid
- Não esperar por elementos assíncronos (use `waitForSelector` ou `expect(...).toBeVisible()`)
- Esquecer de limpar estado entre cenários

---

## Modo: tdd

**Gatilho:** Aplicar TDD estrito — implementar features, bug fixes ou refactors com RED-GREEN-REFACTOR.

### A Lei de Ferro

```
NENHUM CÓDIGO DE PRODUÇÃO SEM UM TESTE FALHANDO PRIMEIRO
```

Escreveu código antes do teste? Delete. Comece de novo. Sem exceções.

### Fluxo RED-GREEN-REFACTOR

**Fase RED — Escreva um teste que falha**
1. Leia a spec e identifique o próximo comportamento
2. Escreva um teste unitário que define o comportamento esperado
3. Execute → deve falhar (RED). Se passar sem implementação, refine o teste.
4. **NUNCA pule a verificação do RED.** Teste passando de primeira = você não sabe se ele testa algo real.

**Fase GREEN — Código mínimo para passar**
1. Escreva a implementação mais simples que faz o teste passar
2. Não implemente além do necessário (YAGNI). Vale hardcode, copy-paste, duplicação.
3. Execute o teste → deve passar (GREEN)
4. Execute **todos** os testes → sem regressões
5. Se falhar, corrija a implementação, não o teste

**Fase REFACTOR — Melhore sem mudar comportamento**
1. Com todos os testes passando: renomeie, extraia, simplifique
2. Execute os testes a cada passo → devem continuar passando
3. Se quebrar → desfaça imediatamente, dê passos menores

**Repetir**: volte para RED com o próximo comportamento.

### Regras de Ouro

- Teste define comportamento, não implementação
- Testes testam código real, não mocks (mock só se inevitável)
- Um comportamento por teste (nome com "and"? divida)
- Commite após cada ciclo GREEN
- Bug encontrado? Escreva teste que reproduz → corrija → commit

### Racionalizações Comuns

| Desculpa | Realidade |
|---|---|
| "Muito simples para testar" | Código simples quebra. Teste leva 30s. |
| "Testo depois" | Teste pós-código passa de primeira → não prova nada. |
| "Já testei manualmente" | Ad-hoc ≠ sistemático. Sem registro, não re-executável. |
| "Deletar X horas é desperdício" | Sunk cost. Código não-verificável = dívida técnica. |
| "TDD é dogmático" | TDD É pragmático: encontra bugs antes do commit. |

### Checklist de Verificação

- [ ] Cada função/método novo tem teste
- [ ] Assistiu cada teste falhar antes de implementar
- [ ] Cada teste falhou pelo motivo certo (feature ausente, não erro de sintaxe)
- [ ] Código mínimo para passar cada teste
- [ ] Todos os testes passam, output limpo
- [ ] Edge cases e erros cobertos

### Pitfalls

- Escrever teste que já passa (não testa feature nova)
- Implementar mais do que o teste exige na fase GREEN
- Refatorar sem testes passando
- Testar mocks em vez de comportamento real
- Pular verificação do RED "porque é óbvio que vai falhar"
- Racionalizar "só dessa vez" — é assim que começa

---

## Modo: dogfood

**Gatilho:** QA exploratória sistemática de web apps com ferramentas de browser.

### Fluxo (5 fases)

**Fase 1: Planejar**
1. Criar estrutura: `{output_dir}/screenshots/` e `{output_dir}/report.md`
2. Mapear escopo: homepage, navegação, fluxos-chave, formulários, edge cases (404, estados vazios)

**Fase 2: Explorar**
1. **Navegar**: `browser_navigate(url=...)`
2. **Snapshot**: `browser_snapshot()` — entenda a árvore de acessibilidade
3. **Console**: `browser_console()` — SEMPRE após navegação e interações. Erros JS silenciosos são achados de alto valor.
4. **Visão anotada**: `browser_vision(annotate=true, question="...")` — labels `[N]` nos elementos para comandos seguintes
5. **Interagir sistematicamente**:
   - Cliques: `browser_click(ref="@eN")`
   - Preenchimento: `browser_type(ref="@eN", text="...")`
   - Navegação por teclado: `browser_press(key="Tab")`, `browser_press(key="Enter")`
   - Scroll: `browser_scroll(direction="down")`
   - Testar inputs inválidos, submissões vazias, caracteres especiais

**Fase 3: Coletar Evidências**
Para cada issue:
- Screenshot: `browser_vision(question="...", annotate=false)` → salve `screenshot_path`
- Registrar: URL, steps to reproduce, expected vs actual, console errors
- Classificar severidade: **Critical** (crash/data loss), **High** (funcionalidade quebrada), **Medium** (UX afetada), **Low** (polimento)

**Fase 4: Categorizar**
- De-duplicar issues (mesmo bug em lugares diferentes)
- Atribuir categoria: Functional, Visual, Accessibility, Console, UX, Content
- Ordenar por severidade (Critical → Low)

**Fase 5: Reportar**
Gerar `report.md` com:
- Sumário executivo (contagem por severidade)
- Per-issue: número, título, severidade, categoria, URL, descrição, steps, expected/actual, screenshot (`MEDIA:<path>`), console errors
- Tabela sumária, cobertura de testes, blockers, notas

### Ferramentas de Browser

`browser_navigate`(url), `browser_snapshot`(DOM/a11y tree), `browser_click`(ref `@eN`), `browser_type`(ref, text), `browser_scroll`(dir), `browser_back`(), `browser_press`(key), `browser_vision`(annotate=true para labels `[N]`), `browser_console`(erros JS)

### Pitfalls

- Não checar console após cada interação — erros JS são os achados mais valiosos
- Usar `browser_vision` sem `annotate=true` quando precisa identificar elementos clicáveis
- Esquecer edge cases: campos vazios, texto muito longo, cliques rápidos, estados de erro
- Não de-duplicar issues antes do report final
- Classificação de severidade inconsistente (use a taxonomia)

---

## Referências e Templates

Os arquivos de referência das skills originais são mantidos no diretório do toolkit:

- `references/gherkin-syntax.md` — Palavras-chave e estrutura Gherkin
- `references/gherkin-best-practices.md` — Cenários focados, declarativos, Background, Esquema
- `references/gherkin-anti-patterns.md` — Múltiplos When/Then, steps imperativos, dados irrelevantes
- `references/table-driven.md` — Padrão table-driven tests em Go
- `references/edge-cases.md` — Checklist de edge cases por tipo (strings, ints, slices, errors)
- `references/issue-taxonomy.md` — Taxonomia de severidade e categoria para dogfood
- `templates/dogfood-report-template.md` — Template de relatório dogfood QA
