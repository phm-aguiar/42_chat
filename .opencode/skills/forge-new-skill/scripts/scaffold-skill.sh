#!/usr/bin/env bash
# scaffold-skill.sh <nome_da_skill>
# Cria a estrutura padronizada de diretórios para uma nova skill opencode.

set -e

SKILL_NAME="$1"

if [ -z "$SKILL_NAME" ]; then
  echo "Uso: scaffold-skill.sh <nome_da_skill>"
  exit 1
fi

# Valida nome: lowercase, hyphens, digits only
if ! [[ "$SKILL_NAME" =~ ^[a-z0-9][a-z0-9-]*$ ]]; then
  echo "Erro: nome deve ser lowercase, hyphen-separated, max 64 chars."
  exit 1
fi

if [ ${#SKILL_NAME} -gt 64 ]; then
  echo "Erro: nome deve ter no máximo 64 caracteres."
  exit 1
fi

SKILL_DIR=".opencode/skills/$SKILL_NAME"

if [ -d "$SKILL_DIR" ]; then
  echo "Erro: a skill '$SKILL_NAME' já existe em $SKILL_DIR."
  exit 1
fi

mkdir -p "$SKILL_DIR"/{assets,scripts,references}
touch "$SKILL_DIR/SKILL.md"

echo "Skill '$SKILL_NAME' criada em $SKILL_DIR/"
echo "  ├── SKILL.md"
echo "  ├── assets/"
echo "  ├── scripts/"
echo "  └── references/"
