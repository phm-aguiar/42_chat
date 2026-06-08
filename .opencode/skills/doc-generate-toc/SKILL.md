---
name: doc-generate-toc
description: Use when the user asks to generate a table of contents for a markdown file. Scans the file for ATX headings and outputs a structured TOC with hierarchy levels. Trigger keywords: "gerar TOC", "tabela de conteúdo", "table of contents", "generate TOC", "índice do documento", "listar seções".
---

# Gerar Tabela de Conteúdo (TOC)

## Propósito

Gera uma tabela de conteúdo estruturada para qualquer arquivo markdown, listando todos os headings (H1-H6) com indentação hierárquica. Útil para navegação rápida em documentos grandes sem carregá-los inteiros no contexto.

## Pré-requisitos

- `grep` disponível (padrão Unix/Linux).

## Fluxo de Execução

### Passo 1: Identificar o arquivo

O usuário deve informar o caminho do arquivo markdown. Se não, pergunte.

### Passo 2: Executar extração de headings

```bash
grep -E '^#{1,6} ' <arquivo.md>
```

Alternativa com indentação hierárquica (usando `scripts/generate-toc.sh`):

```bash
bash .opencode/skills/doc-generate-toc/scripts/generate-toc.sh <arquivo.md>
```

O script adiciona indentação visual baseada no nível do heading.

### Passo 3: Analisar e reportar

Apresente o TOC. Destaque:
- Número total de seções
- Profundidade máxima (H1-H6)
- Seções sem conteúdo (headings consecutivos sem texto entre eles — possível problema de estrutura)

### Passo 4: Sugerir próximos passos

Se o usuário quiser ler uma seção específica, sugira usar `doc-extract` para extração cirúrgica.

## Guardrails

- **Apenas headings ATX**: o script detecta apenas headings no formato `# Título`, não headings setext (`===` ou `---`).
- **Headings em code blocks**: headings dentro de blocos ``` ``` ``` são falsos positivos. Avise o usuário se houver suspeita.
- **Encoding**: assuma UTF-8. Se o arquivo tiver encoding diferente, o grep pode falhar.
