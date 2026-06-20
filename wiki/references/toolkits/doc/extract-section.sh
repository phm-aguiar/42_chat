#!/usr/bin/env bash
# extract-section.sh — Extrai cirurgicamente uma seção de um arquivo markdown.
# Uso: extract-section.sh "<Nome da Seção>" <arquivo.md>
# Baseado em RAG determinística com chunking hierárquico (sem banco vetorial).

set -e

TARGET_HEADING="$1"
TARGET_FILE="$2"

if [ -z "$TARGET_HEADING" ] || [ -z "$TARGET_FILE" ]; then
  echo "Uso: extract-section.sh \"<Nome da Seção>\" <arquivo.md>"
  exit 1
fi

if [ ! -f "$TARGET_FILE" ]; then
  echo "Erro: arquivo '$TARGET_FILE' não encontrado."
  exit 1
fi

awk -v target="$TARGET_HEADING" '
  BEGIN { active = 0; baseline = 0 }

  /^#+ / {
    # Extrai nome do heading (após os # e espaço)
    heading = substr($0, index($0, " ") + 1)
    sub(/\r$/, "", heading)

    # Determina nível (número de #)
    match($0, /^#+/)
    level = RLENGTH

    # Ativa extração ao encontrar o alvo
    if (!active && heading == target) {
      active = 1
      baseline = level
      print ""
      next
    }

    # Desativa ao encontrar heading de nível igual ou superior
    if (active && level <= baseline) {
      active = 0
      exit
    }
  }

  active { print $0 }
' "$TARGET_FILE"
