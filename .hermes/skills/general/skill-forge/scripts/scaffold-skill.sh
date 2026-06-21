#!/usr/bin/env bash
# scaffold-skill.sh — Cria o esqueleto de uma nova skill Hermes.
#
# Convenção do 42_chat:
#   <repo>/.hermes/skills/<categoria>/<nome>/   ← versionado (fonte da verdade)
#   ~/.hermes/skills/<categoria>/<nome>/        → symlink para o caminho acima
#
# Uso:
#   bash scaffold-skill.sh --name <nome> [--category <cat>] [--repo-root <path>]
#                         [--description "<desc>"] [--author "<nome>"]
#                         [--no-category] [--no-symlink]
#
# Saída: imprime o resumo do que foi criado.

set -euo pipefail

# --- Defaults ---------------------------------------------------------------
CATEGORY="general"
REPO_ROOT="$(pwd)"
DESCRIPTION="TODO: preencher description com gatilhos (use when... / trigger keywords: ...)"
AUTHOR="$(git config user.name 2>/dev/null || echo 'phm-aguiar')"
NO_CATEGORY=0
NO_SYMLINK=0
NAME=""

# --- Help -------------------------------------------------------------------
usage() {
  cat <<EOF
scaffold-skill.sh — Cria o esqueleto de uma nova skill Hermes no repo + symlink na home.

Uso:
  $(basename "$0") --name <nome> [opções]

Opções:
  --name <nome>           Nome da skill (obrigatório). lowercase, hífens, max 64 chars.
  --category <categoria>  Categoria (default: general). lowercase, hífens, max 32 chars.
  --repo-root <path>      Raiz do repo (default: CWD).
  --description "<desc>"  Description do frontmatter (default: placeholder).
  --author "<nome>"       Author do frontmatter (default: git config user.name).
  --no-category           Cria skill direto em .hermes/skills/<nome>/ (sem categoria).
  --no-symlink            Não cria symlink em ~/.hermes/skills/.
  -h, --help              Mostra esta ajuda.

Exemplo:
  $(basename "$0") --name review-code --category devops \\
                   --description "Code review automatizado. Trigger keywords: review, code review, PR review."
EOF
}

# --- Parse ------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --name)        NAME="$2"; shift 2 ;;
    --category)    CATEGORY="$2"; shift 2 ;;
    --repo-root)   REPO_ROOT="$2"; shift 2 ;;
    --description) DESCRIPTION="$2"; shift 2 ;;
    --author)      AUTHOR="$2"; shift 2 ;;
    --no-category) NO_CATEGORY=1; shift ;;
    --no-symlink)  NO_SYMLINK=1; shift ;;
    -h|--help)     usage; exit 0 ;;
    *)             echo "ERRO: argumento desconhecido: $1" >&2; usage; exit 2 ;;
  esac
done

# --- Validações -------------------------------------------------------------
NAME_REGEX='^[a-z0-9][a-z0-9-]*$'

if [[ -z "$NAME" ]]; then
  echo "ERRO: --name é obrigatório." >&2
  usage
  exit 2
fi
if [[ ${#NAME} -gt 64 ]]; then
  echo "ERRO: --name tem ${#NAME} chars (max 64)." >&2; exit 2
fi
if ! [[ "$NAME" =~ $NAME_REGEX ]]; then
  echo "ERRO: --name '$NAME' não bate ^[a-z0-9][a-z0-9-]*$." >&2; exit 2
fi

if [[ $NO_CATEGORY -eq 0 ]]; then
  if [[ ${#CATEGORY} -gt 32 ]]; then
    echo "ERRO: --category tem ${#CATEGORY} chars (max 32)." >&2; exit 2
  fi
  if ! [[ "$CATEGORY" =~ $NAME_REGEX ]]; then
    echo "ERRO: --category '$CATEGORY' não bate ^[a-z0-9][a-z0-9-]*$." >&2; exit 2
  fi
fi

if [[ ! -d "$REPO_ROOT" ]]; then
  echo "ERRO: --repo-root '$REPO_ROOT' não é diretório." >&2; exit 2
fi
REPO_ROOT="$(cd "$REPO_ROOT" && pwd)"

# --- Caminhos ---------------------------------------------------------------
if [[ $NO_CATEGORY -eq 1 ]]; then
  SKILL_DIR="$REPO_ROOT/.hermes/skills/$NAME"
  SKILL_HOME_DIR="$HOME/.hermes/skills/$NAME"
else
  SKILL_DIR="$REPO_ROOT/.hermes/skills/$CATEGORY/$NAME"
  SKILL_HOME_DIR="$HOME/.hermes/skills/$CATEGORY/$NAME"
fi

# --- Guard: skill já existe -------------------------------------------------
if [[ -d "$SKILL_DIR" ]] && [[ -n "$(ls -A "$SKILL_DIR" 2>/dev/null)" ]]; then
  echo "ERRO: skill já existe (não vazia) no repo: $SKILL_DIR" >&2
  echo "      Nada foi criado. Remova manualmente se quiser recriar." >&2
  exit 3
fi
if [[ -e "$SKILL_HOME_DIR" ]] && [[ ! -L "$SKILL_HOME_DIR" ]]; then
  echo "ALERTA: existe um diretório real (não symlink) em $SKILL_HOME_DIR." >&2
  echo "        Pode ser uma skill local de outro projeto. Abortando pra não sobrescrever." >&2
  exit 3
fi

# --- Criação no repo --------------------------------------------------------
mkdir -p "$SKILL_DIR/assets"
mkdir -p "$SKILL_DIR/scripts"
mkdir -p "$SKILL_DIR/references"

# Caminho do template: relativo a este script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$SCRIPT_DIR/../assets/template-skill.md"

if [[ ! -f "$TEMPLATE" ]]; then
  echo "ERRO: template não encontrado em $TEMPLATE" >&2
  echo "      Esperado em <skill>/assets/template-skill.md" >&2
  exit 4
fi

# Substitui placeholders e escreve SKILL.md
# Uso de awk pra evitar dependência de sed com -i (que difere entre GNU e BSD)
awk \
  -v name="$NAME" \
  -v description="$DESCRIPTION" \
  -v author="$AUTHOR" \
  -v category="$CATEGORY" \
  -v date="$(date -u +%Y-%m-%d)" \
  '
  {
    gsub(/\{\{NAME\}\}/, name);
    gsub(/\{\{DESCRIPTION\}\}/, description);
    gsub(/\{\{AUTHOR\}\}/, author);
    gsub(/\{\{CATEGORY\}\}/, category);
    gsub(/\{\{DATE\}\}/, date);
    print;
  }
  ' "$TEMPLATE" > "$SKILL_DIR/SKILL.md"

# --- Symlink na home --------------------------------------------------------
SYMLINK_STATUS="não criado (--no-symlink)"
if [[ $NO_SYMLINK -eq 0 ]]; then
  mkdir -p "$(dirname "$SKILL_HOME_DIR")"
  # Se já existe como symlink pra esse destino, é no-op
  if [[ -L "$SKILL_HOME_DIR" ]]; then
    CURRENT_TARGET="$(readlink -f "$SKILL_HOME_DIR" 2>/dev/null || true)"
    if [[ "$CURRENT_TARGET" == "$SKILL_DIR" ]]; then
      SYMLINK_STATUS="já existia e aponta pro lugar certo (no-op)"
    else
      # Apaga e recria
      rm -f "$SKILL_HOME_DIR"
      ln -s "$SKILL_DIR" "$SKILL_HOME_DIR"
      SYMLINK_STATUS="atualizado (apontava pra outro lugar)"
    fi
  else
    ln -s "$SKILL_DIR" "$SKILL_HOME_DIR"
    SYMLINK_STATUS="criado"
  fi
fi

# --- Relatório --------------------------------------------------------------
cat <<EOF

✓ Skill '$NAME' scaffolded

Repo (versionado):
  $SKILL_DIR/
  ├── SKILL.md
  ├── assets/
  ├── scripts/
  └── references/

Home (symlink):
  $SKILL_HOME_DIR → $SKILL_DIR   [$SYMLINK_STATUS]

Frontmatter preenchido:
  name:         $NAME
  category:     $CATEGORY
  author:       $AUTHOR
  description:  $DESCRIPTION

Próximos passos:
  1. Edite $SKILL_DIR/SKILL.md (preencha Propósito, Fluxo, Guardrails).
  2. Se a skill usar scripts/templates/references, coloque em assets/,
     scripts/ ou references/ e liste em metadata.hermes.resources.
  3. Recarregue o índice de skills do Hermes (CLI: /reload-skills).

EOF
