---
title: "Spec-Driven Development — Série DSA Academy"
category: references
tags:
  - sdd
  - spec-driven-development
  - dsa-academy
  - ears
  - gears
  - vibe-coding
summary: >-
  Série de 5 artigos da Data Science Academy sobre Spec-Driven Development
  como nova arquitetura de engenharia de software na era dos Agentes de IA.
  Cobre a transição do Vibe Coding para engenharia guiada por intenção,
  anatomia de especificações executáveis (EARS, GEARS), ecossistema de
  ferramentas e orquestração agêntica.
status: approved
lifecycle: reviewed
created: 2026-06-21
sources:
  - https://blog.dsacademy.com.br/spec-driven-development-a-nova-arquitetura-de-engenharia-de-software-na-era-dos-agentes-de-ia-parte-1/
  - https://blog.dsacademy.com.br/spec-driven-development-a-nova-arquitetura-de-engenharia-de-software-na-era-dos-agentes-de-ia-parte-2/
---

# Spec-Driven Development — Série DSA Academy

> Série de 5 artigos da Equipe DSA (Data Science Academy) explorando o
> Spec-Driven Development como a nova arquitetura de engenharia de software
> na era dos Agentes de IA. Disponíveis apenas as Partes 1 e 2 nesta wiki.

## Estrutura da Série

- **Parte 1** — Sai o "Vibe Coding" Entra a Engenharia Guiada Por Intenção
- **Parte 2** — Anatomia de Uma Especificação Executável: EARS, GEARS e Markdown Estruturado
- **Parte 3** — O Ecossistema de Ferramentas: Spec Kit, Tessl, Claude Code e skills.md
- **Parte 4** — A Arquitetura Agêntica: Orquestrando LLMs com Contexto Rígido e Validação
- **Parte 5** — O Futuro do Desenvolvimento: A Redefinição do Papel do Engenheiro de Software

---

## Parte 1 — Sai o "Vibe Coding" Entra a Engenharia Guiada Por Intenção

O argumento central da série é que estamos migrando de um modelo centrado em
código como artefato principal para um modelo centrado em especificação como
fonte primária de verdade.

Em vez de tratar LLMs como assistentes improvisando soluções a partir de
prompts vagos, passamos a utilizá-los como executores de intenções formalizadas,
operando dentro de contratos explícitos, restrições verificáveis e estruturas
semânticas bem definidas.

### O Fenômeno do "Vibe Coding"

Com a evolução da IA Generativa, surgiu a prática do "Vibe Coding": você envia
um prompt para a IA, vê se o resultado "parece" funcionar, ajusta e segue.
É programação por tentativa e erro, guiada mais por intuição do que por
compreensão real do que está acontecendo.

> Para um script rápido ou um protótipo? Funciona. Para um sistema empresarial
> que vai rodar por anos? É uma receita para o desastre.

O problema não é a IA escrever código ruim — é que não estamos sabendo dizer
para ela o que queremos com clareza suficiente.

### Código Gerado por IA Dura Mais

Pesquisas mostram que código gerado por IA tende a sobreviver mais tempo nos
repositórios (taxa de modificação ~16 pontos percentuais menor por linha), mas
precisa de mais correções de bugs ao longo do tempo. O código fica parado,
carregando problemas sutis — não é um problema de execução, é de especificação.

### SDD — Spec-Driven Development

O SDD coloca a especificação no centro de tudo. Ela vira a fonte da verdade.
O código passa a ser um produto derivado dela, algo que pode ser regenerado
sempre que a especificação mudar.

> Na construção civil, a planta do engenheiro tem mais autoridade do que a
> parede que o pedreiro levantou. Se a parede não está de acordo com a planta,
> a parede é refeita. No SDD, a lógica é a mesma.

### SDD vs TDD vs BDD

O SDD não substitui TDD ou BDD — ele opera em um nível acima, orquestrando
o processo:

| Prática | Foco |
|---------|------|
| **TDD** | Validar a implementação |
| **BDD** | Descrever comportamentos esperados |
| **SDD** | Definir a intenção e planejar a construção |

Uma boa especificação SDD pode incluir instruções para gerar testes TDD ou
cenários BDD como parte do plano.

### Da Ambiguidade à Precisão

Requisitos vagos sempre foram um problema. Mas quando um desenvolvedor humano
encontra algo ambíguo, ele pergunta. A IA não faz isso — ela tenta adivinhar
em silêncio. Essas suposições silenciosas se acumulam como dívida técnica
invisível.

O SDD exige "desacelerar para acelerar": escrever uma boa especificação dá
trabalho, mas esse investimento se paga em menos idas e vindas, menos bugs,
menos retrabalho — o conceito de **correção por construção**.

---

## Parte 2 — Anatomia de Uma Especificação Executável

### Os Componentes Essenciais da Arquitetura SDD

| Artefato | Propósito |
|----------|-----------|
| **SPEC.md** | Define o "O Quê" e o "Porquê" — histórias de usuário, regras de negócio, critérios de aceitação |
| **PLAN.md** | A estratégia técnica — stack, schema, APIs, estrutura de diretórios |
| **TASKS.md** | Tarefas atômicas, sequenciais e verificáveis para execução por agentes |
| **constitution.md** | Leis imutáveis — guardrails éticos e técnicos permanentes |

### EARS e GEARS

Linguagens de especificação para reduzir ambiguidade no parsing por LLMs:

- **EARS** (Easy Approach to Requirements Syntax) — originalmente desenvolvida
  na Rolls-Royce para engenharia aeroespacial, redescoberta para SDD
- **GEARS** (Generalized Expression for AI-Ready Specs) — adaptação do EARS
  otimizada para tokenização e raciocínio lógico de modelos de IA modernos

Padrão unificado: `O <sujeito> deve <comportamento>`.

A precisão sintática funciona como uma "linguagem de programação para
requisitos", permitindo que agentes detectem conflitos lógicos antes de
escrever código.

### Markdown como Língua Franca da IA

- **Eficiência de tokens**: menos tokens que JSON/XML/YAML para mesma densidade
- **Hierarquia semântica**: cabeçalhos criam árvore hierárquica que modelos
  Transformer usam para ponderar importância
- **Natureza híbrida**: permite misturar linguagem natural com blocos de código,
  tabelas e diagramas (Mermaid.js)

### Arquivos de Contexto

- **`.cursorrules` / `CLAUDE.md` / `AGENTS.md`**: injetam instruções de sistema
  em cada prompt. No SDD avançado, o conteúdo é derivado dinamicamente da
  constitution.md e PLAN.md ativos
- **Memory Banks**: armazenam decisões arquiteturais passadas, lições aprendidas
  e preferências, simulando continuidade cognitiva sem reprocessar histórico

### Exemplo Prático

Pedido vago: "Crie uma app de lista de tarefas"

1. **Entrevista**: O agente questiona — multiusuário ou local? Precisa
   funcionar offline? Prioridade: velocidade ou consistência?
2. **Formalização EARS**:
   - "Quando o usuário adicionar uma nova tarefa, o sistema deve salvá-la
     imediatamente no banco local (SQLite) para latência zero"
   - "Enquanto houver conectividade, o sistema deve sincronizar alterações
     do banco local com a API remota"
3. **Validação e congelamento**: SPEC.md revisado e aprovado serve como input
   imutável para a fase de planejamento

---

## Relacionado

- [[concepts/sdd|Spec-Driven Development (conceito)]]
- [[concepts/sdd-workflow|Fluxo de Trabalho SDD]]
- [[skills/sdd-brainstorm|SDD Brainstorm]]
- [[skills/sdd-generate-plan|SDD Generate Plan]]
- [[skills/sdd-generate-tasks|SDD Generate Tasks]]
