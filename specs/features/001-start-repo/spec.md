# spec.md: Estrutura de Repositório SDD

## 1. Visão Geral e Intenção de Negócios

- **Funcionalidade:** Definição da estrutura de diretórios e do modelo organizacional de um repositório orientado a Spec-Driven Development (SDD).
- **Objetivo:** Estabelecer fronteiras claras entre diretrizes globais (`.github/memory/`), especificações de funcionalidades como Fonte Única da Verdade (`/specs`) e o código derivado (`/src`, `/app`, `/infra`), otimizando o fluxo de trabalho com agentes de IA.

## 2. Histórias de Usuário e Comportamento (BDD)

- **Como** arquiteto de software, **Quero** uma estrutura de diretórios padronizada para SDD, **Para que** todo novo projeto comece com as mesmas convenções e agentes de IA possam navegar previsivelmente.
- **Como** agente de IA, **Quero** encontrar specs, planos e tarefas em locais canônicos, **Para que** eu possa validar a completude dos artefatos antes de iniciar a implementação.
- **Cenário Principal:**
  - *Dado* que um repositório é inicializado com `sdd-init-repo`,
  - *Quando* a estrutura é criada,
  - *Então* `.github/memory/`, `specs/features/`, `specs/domain-events/` e `specs/infra/` existem com os arquivos template apropriados.

## 3. Limites, Restrições e Não-Funcionais

- **Spec-as-Source:** Modificações humanas diretas nas camadas de implementação (`/src`, `/app`, `/infra`) constituem violação no pipeline SDD estrito. O código é resultado terminal do processamento dos diretórios superiores.
- **Separação de Concerns:** `.github/memory/` contém apenas regras e stack. `specs/` contém apenas intenção e planejamento. O código derivado fica nas camadas de implementação.
- **Agnóstico de Linguagem:** A estrutura SDD é independente da stack. O mesmo layout funciona para Go, Java, Python, etc.

## 4. Checklist de Ambiguidade para a IA

- [ ] O diretório de código derivado deve ser `/src`, `/app` ou detectado automaticamente conforme a linguagem?
- [ ] Os contratos formais (`domain-events/`) devem ser obrigatórios desde o início ou apenas quando houver integração entre sistemas?
- [ ] O `infrastructure.yaml` em `specs/infra/` deve ser genérico (multi-cloud) ou específico do provedor?

---

# Notas Adicionais

## Memória de Contexto Global (`.github/memory`)

O nível mais alto da hierarquia define as leis constitutivas e premissas operacionais que governam a base de código:

- **Constituição Arquitetural (`constitution.md`)**: A diretiva suprema. Impõe restrições incontornáveis (portões de qualidade) a cada modificação. Ex: obrigatoriedade de injeção de dependência via construtores, *Simplicity Gate* (limitar criação de novos serviços), *Anti-Abstraction Gate* (proibir abstrações preemptivas).
- **Diretrizes de Ecossistema (`tech.md`)**: Centraliza o controle do stack tecnológico. Define versões exatas de linguagens, frameworks permitidos e regras de linting.

## Diretório de Especificações (`/specs`)

Substitui PRDs e tickets de rastreamento. Compartimentado de forma modular:

| Artefato | Arquivo(s) | Propósito |
|---|---|---|
| Especificação Funcional | `spec.md` ou `requirements.md` | Critérios de aceite, intenção de negócios. Sem detalhes de implementação. |
| Plano Arquitetural | `plan.md` ou `design.md` | Topologia técnica (ADR vivo). Estruturas de dados, integração, banco. |
| Matriz de Execução | `tasks.md` | Lista ordenada e granular de passos atômicos. |
| Contratos de Interface | `domain-events/*.yaml` | OpenAPI, AsyncAPI — elo inegociável de conectividade. |

## Camada de Implementação Derivada

Estruturas clássicas (`/src`, `/app`, `/infra`) sem autonomia decisória. Os arquivos são resultados terminais do processamento dos diretórios superiores.

---

# Apêndice: Exemplo de Estrutura (Aplicação Kafka Consumer em Java)

```
sdd-kafka-consumer/
├── .github/
│   └── memory/
│       ├── constitution.md
│       └── tech.md
├── specs/
│   ├── domain-events/
│   │   └── asyncapi.yaml
│   ├── features/
│   │   └── 001-processar-pagamento/
│   │       ├── spec.md
│   │       ├── plan.md
│   │       └── tasks.md
│   └── infra/
│       └── infrastructure.yaml
├── app/
│   ├── pom.xml
│   ├── src/main/java/.../
│   │   ├── core/
│   │   └── adapters/
│   └── target/generated-sources/
├── infra/
│   ├── main.tf
│   └── modules/
└── tests/
    └── contracts/
        └── KafkaContractTest.java
```
