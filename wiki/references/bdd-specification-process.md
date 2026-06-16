---
title: "BDD Specification Process"
category: references
tags:
  - bdd
  - gherkin
  - specification
  - reference
  - methodology
  - agile
  - testing
summary: "Processo completo de especificação BDD com Gherkin: fluxo do Gherkin Expert (7 etapas), design de cenários, estruturação de acceptance criteria (happy path → erro → borda), domain modeling, tri-path PromptWriter (English vs Gherkin vs TLA+), evidência empírica (+26% Gherkin sobre English), anti-padrões e templates."
aliases:
  - BDD
  - Gherkin
  - Processo de Especificação BDD
created: "2026-06-13"
updated: "2026-06-15"
lifecycle: reviewed
lifecycle_changed: "2026-06-15"
lifecycle_reason: "auto-promoted by wiki-lint: well-established reference page"
sources:
  - "/home/zeenyt__/Projetos/42_chat/qafiles/bdd-spec/"
  - "wiki/_raw/qa/bdd-spec/bdd-gherkin-specification.md"
  - "wiki/_raw/qa/bdd-spec/gherkin-expert-steps.md"
  - "wiki/_raw/qa/bdd-spec/gherkin-expert.md"
  - "wiki/_raw/qa/bdd-spec/prompt-writer.md"
  - "wiki/_raw/qa/bdd-spec/use_gherkin_expert.md"
---

# Processo de Especificação BDD com Gherkin
## O que é BDD?

**Behavior-Driven Development (BDD)** é uma metodologia para capturar requisitos que expressa o comportamento de features usando exemplos do mundo real. Ela preenche a lacuna entre stakeholders de negócio, desenvolvedores e testadores ao usar linguagem compartilhada e cenários concretos.

No coração do BDD está a ideia de que **cenários são conversas registradas**, não scripts de teste. Eles devem ser legíveis por product owners, desenvolvedores e testadores igualmente.

## O que é Gherkin?

**Gherkin** é uma linguagem de texto simples para escrever cenários BDD usando palavras-chave como `Feature`, `Scenario`, `Given`, `When`, `Then`. É legível por humanos, focada em negócios e executável como testes automatizados.

### Estrutura Básica

```gherkin
Feature: Login do Usuário

  Scenario: Login bem-sucedido com credenciais válidas
    Given o usuário está na página de login
    When o usuário insere credenciais válidas
    Then o usuário deve ser redirecionado ao dashboard
```

### Palavras-chave Principais

| Palavra-chave      | Propósito                                            |
| ------------------ | ---------------------------------------------------- |
| `Feature`          | Título e descrição de alto nível da funcionalidade   |
| `Scenario`         | Um comportamento específico e verificável            |
| `Given`            | Contexto / pré-condição                              |
| `When`             | Ação executada pelo ator                             |
| `Then`             | Resultado observável                                 |
| `And` / `But`      | Extensão de Given/When/Then                          |
| `Background`       | Pré-condição compartilhada entre todos os cenários   |
| `Scenario Outline` | Cenário parametrizado com tabela de exemplos         |
| `Rule`             | Agrupamento de cenários relacionados por regra       |
| `Examples:`        | Tabela de dados para o Scenario Outline              |
| `@tag`             | Metadados para organização (ex: `@smoke`, `@wip`)    |

### Convenção de Nomenclatura

Use minúsculas com underscores: `user_authentication.feature`, `shopping_cart_checkout.feature` — exceto quando o ecossistema do projeto ditar outra regra.

---

## Quando Usar (e Quando NÃO Usar)

### ✅ USE Gherkin Quando:

- **Fluxos comportamentais multi-passo** com muitos casos de borda
- **Interações multi-ator** (usuário → sistema → admin → serviço externo)
- **Regras de negócio com condições combinatórias** (cenários com tabelas de Examples)
- **Critérios de aceitação que stakeholders precisam validar**
- **Features onde "o que é feito" é ambíguo em linguagem natural**
- **Workflows que serão referenciados durante testes**
- **Documentação viva** que evolui com o código
- **Pontes de comunicação** entre equipes técnicas e não-técnicas

### ❌ NÃO USE Gherkin Quando:

- **Requisitos puramente técnicos** (arquitetura, refatoração)
- **Time pequeno e co-localizado** com comunicação constante
- **Features muito simples** para justificar especificação formal
- **CRUD simples** com comportamento óbvio
- **Utilitários internos** usados por um único desenvolvedor
- **Mudanças de configuração, estilo, documentação**
- **Problemas puramente algorítmicos** (considere TLA+ para concorrência)
- **Scripts descartáveis** ou código de uso único

> **Nota:** Gherkin é uma ferramenta, não uma regra. Use julgamento. Quando em dúvida, comece com inglês natural. Atualize para especificação formal apenas se a complexidade justificar.

---

## Fluxo do Gherkin Expert

O fluxo completo de trabalho do agente Gherkin Expert segue estas etapas:

### 1. Entender a Feature
- Analise os requisitos de negócio, user stories e contexto do domínio
- Identifique atores, ações e resultados esperados
- Pergunte: "Qual é o comportamento que queremos especificar?"

### 2. Escanear Feature Files Existentes
- Revise cenários já escritos no projeto
- Identifique padrões de linguagem existentes (linguagem ubíqua do domínio)
- Evite duplicação e inconsistência terminológica

### 3. Escrever Cenários
- Comece pelo **caminho feliz (happy path)**
- Adicione **casos de erro**
- Cubra **casos de borda**
- Inclua **condições de limite (boundaries)**
- Cada cenário deve testar **exatamente uma regra de negócio**

### 4. Apresentar ao Solicitante
- Compartilhe os cenários para validação com stakeholders
- Confirme que a linguagem é compreensível por não-técnicos
- Obtenha aprovação antes de prosseguir

### 5. Escrever / Apendar ao Feature File
- Crie um novo arquivo `.feature` ou adicione ao existente
- Siga a estrutura: Background → Happy Path → Erros → Bordas

### 6. Verificação de Glossário
- Revise a terminologia usada nos cenários
- Garanta consistência com a linguagem ubíqua do domínio
- Atualize o glossário do projeto se necessário

### 7. Resumo
- Documente decisões tomadas
- Registre suposições e limitações
- Atualize a documentação de referência

---

## Princípios de Design de Cenários

### 1. Um Comportamento por Cenário

Cada cenário testa **exatamente uma** regra de negócio. Se você precisa de "E" no título do cenário, divida-o.

```gherkin
# RUIM — testa múltiplos comportamentos
Scenario: Usuário faz login e vê o dashboard e recebe notificações

# BOM — um comportamento por cenário
Scenario: Login bem-sucedido com credenciais válidas
Scenario: Dashboard exibe últimas notificações após login
```

### 2. Declarativo (não Imperativo)

Descreva **O QUE** deve acontecer, não **COMO** é implementado.

```gherkin
# RUIM — imperativo (como)
Given navego para "/login"
And digito "user@example.com" no campo "email"
And digito "password123" no campo "senha"
And clico no botão "Entrar"

# BOM — declarativo (o quê)
Given sou um usuário registrado
When faço login com credenciais válidas
Then devo ver meu dashboard
```

### 3. Linguagem de Domínio

Cenários devem soar como conversas entre especialistas do domínio, usando a **linguagem ubíqua** do contexto delimitado (*bounded context*). Se um stakeholder não entender o cenário, ele está técnico demais.

### 4. Cenários Focados e Independentes

- Máximo de **5-7 passos** por cenário (se exceder, divida)
- Cenários **não devem depender uns dos outros**
- Cada cenário deve ser compreensível **isoladamente**
- Máximo de **20 cenários** por feature file (divida se maior)

### 5. Use Background para Setup Compartilhado

```gherkin
Feature: Gerenciamento de Pedidos

  Background:
    Given que existe um cliente cadastrado
    And que o cliente está logado no sistema

  Scenario: Cliente cria um novo pedido
    ...
```

### 6. Use Scenario Outline para Regras Combinatórias

```gherkin
Scenario Outline: Frete calculado por faixa de CEP
  Given um pedido com destino no CEP <cep>
  When o frete é calculado
  Then o valor do frete deve ser <valor>

  Examples:
    | cep    | valor  |
    | 01000  | R$ 15  |
    | 20000  | R$ 25  |
    | 30000  | R$ 35  |
```

---

## Estruturação de Acceptance Criteria

Ao estruturar critérios de aceitação, siga esta ordem:

```
1. Happy Path (caminho feliz)
2. Error Cases (casos de erro)
3. Edge Cases (casos de borda)
4. Boundaries (condições de limite)
```

### Exemplo Completo

```gherkin
Feature: Transferência Bancária

  # 1. HAPPY PATH
  Scenario: Transferência bem-sucedida entre contas
    Given que o cliente possui saldo de R$ 1.000
    When o cliente transfere R$ 200 para outra conta
    Then o saldo da conta de origem deve ser R$ 800
    And o saldo da conta de destino deve ser acrescido de R$ 200

  # 2. ERROR CASES
  Scenario: Transferência com saldo insuficiente
    Given que o cliente possui saldo de R$ 50
    When o cliente tenta transferir R$ 100
    Then a transferência deve ser rejeitada
    And o cliente deve ver uma mensagem de saldo insuficiente

  # 3. BOUNDARIES
  Scenario: Transferência de valor mínimo permitido
    Given que o cliente possui saldo de R$ 1.000
    When o cliente transfere R$ 0,01
    Then a transferência deve ser processada com sucesso

  Scenario: Transferência acima do limite diário
    Given que o limite diário de transferência é R$ 5.000
    When o cliente tenta transferir R$ 5.001
    Then a transferência deve ser rejeitada
```

> **Regra de ouro:** Se você só tem cenários de caminho feliz, você não terminou. Cada `When` deve ter pelo menos um cenário onde ele **falha**.

---

## Domain Modeling Através de Cenários

Cenários BDD revelam conceitos do domínio. Cada palavra-chave mapeia para um elemento do modelo:

| Elemento Gherkin | Artefato de Domínio     | Pergunta Guia                      |
| ---------------- | ----------------------- | ---------------------------------- |
| **Given**        | **Papéis e Estados**    | Quem são os atores? Em que estado? |
| **When**         | **Comandos e Ações**    | Que ações são tomadas?             |
| **Then**         | **Eventos e Consultas** | O que muda? O que é observável?    |
| Vocabulário      | **Linguagem Ubíqua**    | Que termos se repetem?             |

### Exemplo de Modelagem

```gherkin
Feature: Cancelamento de Assinatura

  # Given → Revela o papel "Assinante" no estado "ativa"
  Given que sou um assinante com assinatura ativa

  # When → Revela o comando "cancelar assinatura"
  When cancelo minha assinatura

  # Then → Revela o evento "assinatura cancelada" e a consulta "status"
  Then minha assinatura deve estar com status "cancelada"
  And devo receber um e-mail de confirmação de cancelamento
```

**Benefício:** O vocabulário compartilhado entre cenários revela a linguagem ubíqua do domínio e pode alimentar diretamente o glossário do projeto e os agregados no design do software.

---

## Evidência Empírica

### Gherkin-only vs English-only: +26% em Tarefas Comportamentais

Experimento controlado (N=3 consenso de agentes, tarefa de executor de passos de receita) demonstrou que especificações Gherkin produzem resultados **mensuravelmente superiores** a descrições em inglês para requisitos comportamentais.

| Variante de Prompt        | Pontuação Média | vs. English |
| ------------------------- | --------------- | ----------- |
| English only              | 0.713           | —           |
| **Gherkin only**          | **0.898**       | **+26%**    |
| Gherkin + English         | 0.842           | +18%        |
| Gherkin + Acceptance      | 0.856           | +20%        |

**Principais descobertas:**

1. **Gherkin-only** é a variante mais eficaz para requisitos comportamentais (0.898)
2. Diferente de TLA+ (onde a combinação híbrida degrada), Gherkin+English **também melhora** em relação a English-only
3. A especificação formal pura ainda supera qualquer combinação híbrida

**Fonte:** `experiments/hive_mind/gherkin_v2_recipe_executor/` (Issue #3939 do roadmap de integração de especificações formais)

---

## Tabela Comparativa: Gherkin vs. English vs. TLA+

### Para Requisitos Comportamentais

| Critério                | English Only              | Gherkin                              | TLA+                                    |
| ----------------------- | ------------------------- | ------------------------------------ | --------------------------------------- |
| **Ganho vs. English**   | —                         | **+26%**                             | +51% (sistemas concorrentes)            |
| **Melhor para**         | CRUD simples, tarefas óbvias | Requisitos comportamentais complexos | Invariantes de segurança, concorrência |
| **Pergunta-chave**      | "O que fazer?"            | "Qual é a aparência de 'pronto'?"    | "O que deve sempre/nunca ser verdade?"  |
| **Público-alvo**        | Desenvolvedores           | Stakeholders + Devs + Testers        | Engenheiros de sistemas                 |
| **Curva de aprendizado** | Nenhuma                  | Baixa                                | Alta                                    |
| **Executável como teste** | Não                     | Sim (Cucumber, SpecFlow, etc.)       | Sim (TLC model checker)                 |
| **Documentação viva**   | Não                       | Sim                                  | Parcial                                 |

### Guia de Decisão (Tri-Path do PromptWriter)

```
[Requisito Chegou]
       │
       ▼
┌──────────────────────────────────────┐
│ O problema principal é               │
│ comportamento ou estado?             │
└──────────────────────────────────────┘
       │                    │
       ▼                    ▼
  COMPORTAMENTAL        ESTADO/CONCORRÊNCIA
       │                    │
       ▼                    ▼
┌─────────────────┐  ┌─────────────────┐
│ Complexidade    │  │ Invariantes de  │
│ comportamental  │  │ segurança?      │
│ é alta?         │  │ Ordenação?      │
└─────────────────┘  │ Liveness?       │
       │       │     └────────┬────────┘
       ▼       ▼              ▼
   ENGLISH  GHERKIN        TLA+
   (default) (+26%)       (+51%)
```

### Critérios de Julgamento (Indicadores, Não Regras)

- Se a parte difícil é **"qual é a aparência de 'pronto'?"** → considere **Gherkin**
- Se a parte difícil é **"o que deve sempre/nunca ser verdade?"** → considere **TLA+**
- Se a parte difícil **não é nenhuma das duas** → **English** é suficiente
- Quando em dúvida, comece com **English**. Atualize se provar insuficiente.

---

## Anti-Padrões Comuns

### 1. Cenários que Testam Implementação

```gherkin
# RUIM — testa a UI, não o comportamento
Then a div com classe "error" deve estar visível
And o status HTTP deve ser 422

# BOM — testa o comportamento
Then devo ver uma mensagem de erro explicando o problema
```

### 2. Passos em Excesso

> Se um cenário tem mais de 7-8 passos, provavelmente está testando múltiplos comportamentos. **Divida-o.**

### 3. Detalhes Incidentais

```gherkin
# RUIM — detalhes irrelevantes
Given um usuário chamado "João Silva" com email "joao@exemplo.com" criado em "2024-01-15"

# BOM — apenas o que importa
Given um usuário registrado
```

### 4. Ausência de Cenários de Erro

> Se você só tem cenários de caminho feliz, você **não terminou**. Todo `When` precisa de pelo menos um cenário de falha.

### 5. Dependência Entre Cenários

```gherkin
# RUIM — depende de outro cenário
Scenario: Login após cadastro
  Given o cenário anterior de cadastro foi executado

# BOM — autossuficiente
Scenario: Login após cadastro
  Given que sou um usuário registrado
```

---

## Template de Feature File

```gherkin
@tag
Feature: [Descrição curta da funcionalidade]
  Como um [papel]
  Eu quero [capacidade]
  Para que [benefício]

  Background:
    Given [pré-condição compartilhada entre todos os cenários]

  Scenario: Happy path — [descrição clara do comportamento]
    Given [pré-condição específica]
    When [ação do ator]
    Then [resultado observável]

  Scenario: Caso de erro — [o que acontece quando X falha]
    Given [pré-condição]
    When [ação que dispara o erro]
    Then [comportamento de tratamento de erro]
    And [feedback visível ao usuário]

  Scenario Outline: [Regra de negócio com múltiplas condições]
    Given [pré-condição com <parâmetro>]
    When [ação com <entrada>]
    Then [resultado com <esperado>]

    Examples:
      | parâmetro | entrada | esperado |
      | valor1    | in1     | out1     |
      | valor2    | in2     | out2     |
```

---

## Tri-Path Judgment System (PromptWriter)

O agente **prompt-writer** (parte do ecossistema Gherkin Expert) usa um sistema de julgamento de três caminhos para decidir quando formalizar especificações. O default é **sempre English-only** — especificações formais (Gherkin ou TLA+) só entram quando a complexidade justifica.

### Path 1: English-Only (DEFAULT)

Use para a maioria das tarefas. Nenhuma especificação formal necessária.

- CRUD simples ou transformações sequenciais de valores
- Layout de UI, estilização, mudanças de configuração
- Requisitos onde a parte difícil é conhecimento de domínio, não espaço de estados
- Utilitários internos com um único desenvolvedor como audiência
- Bug fixes diretos com comportamento óbvio

### Path 2: Gherkin/BDD Scenarios

Considere quando a complexidade comportamental é alta. **Evidência:** gherkin_only AVG=0.898 vs english 0.713 (+26%) para requisitos comportamentais (N=3 consenso de agentes).

- Fluxos multi-passo complexos com muitos casos de borda
- Cenários multi-ator (usuário faz X, sistema responde Y, admin vê Z)
- Regras de negócio com condições combinatórias
- Critérios de aceitação que stakeholders precisam validar
- Features onde "o que é 'pronto'" é ambíguo em inglês

### Path 3: TLA+ Formal Predicates

Considere quando concorrência ou invariantes de segurança são a preocupação. **Evidência:** TLA+ 0.86 vs english 0.57 (+51%) para sistemas concorrentes (experimento #3497).

- Múltiplos atores/agentes modificando estado compartilhado concorrentemente
- Invariantes "nunca deve" / "sempre deve" / "eventualmente deve" no nível do sistema
- Correção de protocolos com requisitos de ordenação ou atomicidade
- State machines com transições válidas não-óbvias
- Protocolos distribuídos (fan-out/merge, quorum, tratamento de timeout)

### Indicadores de Julgamento (NÃO são regras)

- Se a parte difícil é **"qual é a aparência de 'pronto'?"** → considere Gherkin
- Se a parte difícil é **"o que deve sempre/nunca ser verdade?"** → considere TLA+
- Se a parte difícil **não é nenhuma das duas** → English é suficiente
- Quando em dúvida, comece com English. Atualize se provar insuficiente.

## Ecossistema Gherkin Expert

O Gherkin Expert é um subsistema com múltiplos artefatos que trabalham juntos para integrar especificações formais ao pipeline de desenvolvimento:

| Artefato | Tipo | Propósito |
|----------|------|-----------|
| `gherkin-expert` skill | Skill definition | Ativa quando o usuário menciona Gherkin/BDD/Given-When-Then |
| `gherkin-expert` agent | Agent persona | Especialista em sintaxe Gherkin, design de cenários, domain modeling |
| `prompt-writer` agent | Agent persona | Classifica requisitos (EXECUTABLE vs DOCUMENTATION) + julga necessidade de especificação formal (tri-path) |
| `bdd-gherkin-specification` skill | Skill definition | Skill guarda-chuva com recursos de referência (syntax, best-practices, examples, anti-patterns, organization) |

### Gherkin Expert Agent — Competências

O agent persona do Gherkin Expert cobre:
1. **Escrita de especificações Gherkin** — Feature/Scenario/Given/When/Then, Background, Scenario Outline
2. **Design de cenários** — um comportamento por cenário, declarativo sobre imperativo, linguagem de domínio
3. **Estruturação de acceptance criteria** — happy path → error cases → edge cases → boundaries
4. **Domain modeling através de cenários** — Given revela papéis, When revela comandos, Then revela eventos
5. **AI Prompt Improvement** — evidência empírica de que especificações Gherkin produzem código melhor

### PromptWriter Agent — Tri-Path na Prática

O prompt-writer segue uma sequência mandatória antes de gerar qualquer prompt:

1. **Task Classification** (MANDATORY) — Classifica como EXECUTABLE, DOCUMENTATION, ou AMBIGUOUS
2. **Complexity Assessment** (MANDATORY) — TRIVIAL (<10 linhas), SIMPLE (10-50), COMPLEX (50+)
3. **Specification Language Judgment** — Aplica o tri-path para decidir English vs Gherkin vs TLA+
4. **Template-based Prompt Generation** — Aplica o template correto (Feature, Bug Fix, Refactoring)
5. **Quality Validation** — Completeness Check + Clarity Check + Consistency Check (mínimo 80%)

## Referências

- [Documentação Cucumber](https://cucumber.io/docs/)
- ["Writing Better Gherkin" — Cucumber Blog](https://cucumber.io/blog/bdd/writing-better-gherkin/)
- *Specification by Example* — Gojko Adzic
- *BDD in Action* — John Ferguson Smart
- *Cucumber Reference* — [https://cucumber.io/docs/gherkin/reference/](https://cucumber.io/docs/gherkin/reference/)
- Experimentos: `experiments/hive_mind/gherkin_v2_recipe_executor/`
- Issue #3939: Roadmap de integração de especificações formais

---

## Resumo em Uma Linha

> **BDD + Gherkin transformam requisitos ambíguos em especificações executáveis, legíveis por humanos e 26% mais eficazes que linguagem natural para gerar código comportamental de qualidade.**

## Ver Também

- [[references/gherkin-syntax|Gherkin Syntax]] — Referência sintática
- [[references/gherkin-best-practices|Gherkin Best Practices]] — Anti-padrões e boas práticas
- [[references/gherkin-examples|Gherkin Examples]] — Exemplos de cenários bem escritos
- [[references/cucumber-basics|Cucumber Basics]] — Automação dos cenários
- [[references/tdd-methodology|TDD Methodology]] — Complemento: BDD define o que, TDD define como
