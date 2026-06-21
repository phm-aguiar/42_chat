#!/usr/bin/env bash
# generate-toc.sh — Gera tabela de conteúdo hierárquica de um arquivo markdown.
# Uso: generate-toc.sh <arquivo.md>

set -e

TARGET_FILE="$1"

if [ -z "$TARGET_FILE" ]; then
  echo "Uso: generate-toc.sh <arquivo.md>"
  exit 1
fi

if [ ! -f "$TARGET_FILE" ]; then
  echo "Erro: arquivo '$TARGET_FILE' não encontrado."
  exit 1
fi

grep -E '^#{1,6} ' "$TARGET_FILE" | while IFS= read -r line; do
  # Extrai nível e título
  level=$(echo "$line" | sed -E 's/^(#+).*/\1/' | wc -c)
  level=$((level - 1))
  title=$(echo "$line" | sed -E 's/^#+ //' | tr -d '\r')

  # Indentação hierárquica
  indent=""
  for ((i=1; i<level; i++)); do
    indent="  $indent"
  done

  echo "${indent}- H${level}: ${title}"
done
