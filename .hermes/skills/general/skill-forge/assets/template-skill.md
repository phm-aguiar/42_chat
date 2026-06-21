---
name: {{NAME}}
description: >
  {{DESCRIPTION}}
version: 0.1.0
author: {{AUTHOR}}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: []
    related_skills: []
    category: {{CATEGORY}}
    created: {{DATE}}
    resources:
      - SKILL.md
---

# {{NAME}}

> Categoria: `{{CATEGORY}}` — criada em {{DATE}}

## Propósito

> Descreva em 1-3 parágrafos:
> - O que esta skill faz
> - Quando ela deve ser carregada (condições / gatilhos)
> - Que problema ela resolve

## Pré-requisitos

> Liste dependências externas: binários, env vars, ferramentas, skills relacionadas.
> Use "Nenhum." se for o caso.

## Quando usar (gatilhos)

> Liste os trigger keywords que devem acionar esta skill. Ex:
> - criar X
> - fazer Y
> - "palavra-chave em português", "keyword in english"

## Fluxo de Execução

### Passo 1: <nome do passo>

> Descreva a ação. Se houver comando, use bloco de código.

```bash
# comando exato
```

### Passo 2: <nome do passo>

> Próximo passo. Repita conforme necessário.

## Guardrails

- **Regra 1**: descrição curta da regra. Por que ela existe.
- **Regra 2**: ...
- **Idempotência**: o que acontece se rodar duas vezes?
- **Erros comuns**: liste pitfallls reais já vistos.

## Verificação

> Como saber que funcionou? Liste os sinais de sucesso:
> - Arquivo X foi criado em Y
> - Comando Z retornou status 0
> - Log W apareceu
