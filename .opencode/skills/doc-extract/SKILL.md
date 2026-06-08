---
name: doc-extract
description: Use when the user asks to extract, retrieve, or read a specific section from a large markdown file by heading name. Uses grep + awk to surgically extract only the relevant section without loading the entire file into context. Trigger keywords: "extrair seção", "extract section", "ler seção", "read section", "recuperar trecho", "fetch heading", "surgical extract", "buscar no documento".
---

# Extrair Seção de Documento Markdown

## Propósito

Extrai cirurgicamente uma seção específica de um arquivo markdown grande, usando apenas ferramentas POSIX (`grep` + `awk`). Evita carregar o arquivo inteiro no contexto do agente, implementando um mecanismo de RAG determinística sem banco vetorial — baseado em chunking hierárquico por headings.

## Pré-requisitos

- `grep` e `awk` disponíveis (padrão em qualquer sistema Unix/Linux).

## Operações disponíveis

### Operação 1: Gerar Tabela de Conteúdo (TOC)

Mapeia a estrutura do documento para o agente decidir qual seção extrair.

Comando:
```bash
grep -E '^#{1,6} ' <arquivo.md>
```

O resultado lista todos os headings com seus níveis hierárquicos.

### Operação 2: Extração cirúrgica

Extrai uma seção específica e todo seu conteúdo até o próximo heading de mesmo nível ou superior.

Script: `scripts/extract-section.sh`

```bash
bash .opencode/skills/doc-extract/scripts/extract-section.sh "<Nome da Seção>" <arquivo.md>
```

O script retorna APENAS o conteúdo da seção solicitada, parando ao encontrar um heading de nível igual ou superior.

## Fluxo de Execução

### Passo 1: Identificar o arquivo e a seção

O usuário deve informar:
- Caminho do arquivo markdown
- Nome da seção desejada (ex: "## 3. Decisões Arquiteturais")

Se não informar, pergunte.

### Passo 2: Gerar TOC (se necessário)

Se o usuário não souber o nome exato da seção, execute a Operação 1 para mostrar a estrutura do documento.

### Passo 3: Extrair a seção

Execute `scripts/extract-section.sh` com o nome da seção alvo. O script:
1. Localiza o heading exato (match exato de nome)
2. Captura o nível do heading (número de `#`)
3. Extrai todas as linhas até encontrar um heading de nível igual ou superior
4. Retorna apenas o conteúdo relevante

### Passo 4: Entregar o resultado

Apresente o conteúdo extraído ao usuário (ou use-o para a tarefa em questão).

## Guardrails

- **Match exato**: o nome da seção passado ao script deve corresponder exatamente ao texto após os `#`. Ex: `"Decisões Arquiteturais"`, não `"## Decisões Arquiteturais"`.
- **Se não encontrado**: o script retorna vazio. Nesse caso, execute o TOC para verificar os nomes exatos.
- **Arquivos grandes**: o script lê em stream (não carrega tudo em RAM). Seguro para arquivos de qualquer tamanho.
- **Fallback Python**: se `awk` não estiver disponível, use o script Python em `scripts/extract-section.py` como alternativa.
