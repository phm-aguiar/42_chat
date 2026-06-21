#!/usr/bin/env bash
# setup-skills.sh — Configura symlinks das skills do projeto para o Hermes Agent
#
# Uso: ./scripts/setup-skills.sh
#
# Cria symlinks planos em ~/.hermes/skills/<categoria>/ apontando para
# .hermes/skills/<categoria>/<skill>/ no repositório.
# O Hermes Agent descobre skills pelos symlinks em ~/.hermes/skills/.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HERMES_SKILLS="${HOME}/.hermes/skills"

echo "==> Configurando skills do 42_chat..."
echo "    Repo: ${REPO_ROOT}"
echo "    Destino: ${HERMES_SKILLS}"
echo ""

# Mapa: categoria → skills
declare -A SKILLS=(
  ["sdd"]="brainstorm explore-tech generate-plan generate-tasks init-repo refactor-artifact validate"
  ["general"]="skill-forge"
  ["agent"]="agent-run"
  ["doc"]="extract generate-toc generate-llms-txt"
  ["github"]="git-conventional-commit"
)

count=0
for categoria in "${!SKILLS[@]}"; do
  mkdir -p "${HERMES_SKILLS}/${categoria}"
  for skill in ${SKILLS[$categoria]}; do
    src="${REPO_ROOT}/.hermes/skills/${categoria}/${skill}"
    dst="${HERMES_SKILLS}/${categoria}/${skill}"

    if [ ! -d "$src" ]; then
      echo "⚠️  SKIP: ${categoria}/${skill} — fonte não encontrada em ${src}"
      continue
    fi

    ln -sf "$src" "$dst"
    echo "✓ ${categoria}/${skill}"
    ((count++))
  done
done

echo ""
echo "==> ${count} skills configuradas."
echo ""
echo "Verifique com: hermes skills list | grep -E 'brainstorm|init-repo|skill-forge|agent-run'"
