---
name: doc-generate_llms_txt
description: >
  Use when the user asks to create, generate, or update the llms.txt file for the repository.
  Generates a structured navigation guide for LLMs following the llms.txt protocol, including
  repository overview, directory structure, key files, and links to constitution/tech docs.
  Trigger keywords: gerar llms.txt, criar llms.txt, generate llms.txt, criar llms,
  update llms.txt, documentacao para LLM.
version: 1.0.1
author: phm-aguiar
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Doc, LLM, Navigation, llms.txt]
    related_skills: [wiki-query, doc-extract, doc-generate_toc, sdd-validate]
    category: doc
    resources:
      - SKILL.md
---

# Gerar llms.txt

## Propósito

Gera ou atualiza o arquivo `llms.txt` na raiz do repositório — um guia de navegação para ferramentas de IA e LLMs, seguindo o protocolo emergente `llms.txt`.

## Pré-requisitos

- O repositório deve ter estrutura SDD (`specs/`, `.github/memory/`). Se não tiver, execute `sdd-init_repo` primeiro.
- Consulte `specs/features/002-sdd-templates/spec.md` para o template canônico de llms.txt.

## Quando usar (gatilhos)

Carregue esta skill quando o usuário disser algo como:

- "gerar llms.txt", "criar llms.txt", "generate llms.txt"
- "criar llms", "update llms.txt", "documentacao para LLM"

## Estrutura do llms.txt

```markdown
# {{NOME_DO_PROJETO}}

> {{descrição de uma frase do projeto}}

## Navegação do Repositório e Especificações

- `/specs/features/`: Fonte da Verdade (SSOT). Features modeladas aqui antes do código.
- `/specs/domain-events/`: Contratos formais (AsyncAPI, OpenAPI).
- `/specs/infra/`: Requisitos de infraestrutura genéricos.
- `.github/memory/constitution.md`: Princípios invioláveis.
- `.github/memory/tech.md`: Stack homologado.

## Camadas de Código (Derivadas)

- {{listar diretórios de código com propósito}}

## Skills e Agentes

- Skills disponíveis em `~/.hermes/skills/` (sdd-*, doc-*).
- Subagentes via `delegate_task` do Hermes.

## Links e Regras

- [Constituição](.github/memory/constitution.md)
- [Stack Tecnológica](.github/memory/tech.md)
- [Guia do Agente](AGENTS.md)
```

## Fluxo de Execução

### Passo 1: Coletar contexto do repositório

1. Leia `README.md` para o nome e descrição do projeto.
2. Liste diretórios de código (`src/`, `app/`, `cmd/`, `internal/`, `pkg/`).
3. Liste features em `specs/features/` (IDs e títulos dos `spec.md`).

### Passo 2: Montar a seção de features

Para cada feature em `specs/features/`, leia o título do `spec.md` (primeiro `#`) e liste:

```markdown
- `/specs/features/001-nome/` — {{título do spec.md}} [spec](spec.md) [plan](plan.md) [tasks](tasks.md)
```

### Passo 3: Montar o llms.txt

Preencha o template com os dados coletados. Regras:
- Se um diretório não existe, omita a linha.
- Links devem ser relativos à raiz (ex: `.github/memory/constitution.md`).

### Passo 4: Salvar e reportar

Escreva `llms.txt` na raiz. Mostre o resumo do que foi incluído.

## Guardrails

- **Idempotência**: se `llms.txt` já existe, pergunte se deve sobrescrever ou atualizar (merge).
- **Sincronia**: sempre baseie a lista de features no estado atual de `specs/features/`.
- **Links funcionais**: verifique se todos os arquivos referenciados existem. Se não, omita o link.

## Verificação

- [ ] `llms.txt` foi criado/atualizado na raiz do repo
- [ ] Cada feature listada em `/specs/features/` tem entrada com links funcionais
- [ ] Links apontam para caminhos relativos que existem de fato
- [ ] Se algum link está quebrado, foi omitido (não mantido quebrado)
