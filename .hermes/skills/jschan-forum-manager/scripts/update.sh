#!/usr/bin/env bash
# jschan-forum-manager: update — edita settings de um board
# Uso: update.sh --mongo-url <url> --uri <uri> [--name <name>] [--description <desc>] [--theme <t>] [--language <l>] [--db-name <db>]
set -euo pipefail

MONGO_URL="${MONGO_URL:-}"
DB_NAME="${MONGO_DB:-jschan}"
URI=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --mongo-url) MONGO_URL="$2"; shift 2 ;;
        --db-name) DB_NAME="$2"; shift 2 ;;
        --uri) URI="$2"; shift 2 ;;
        --name) NEW_NAME="$2"; shift 2 ;;
        --description) NEW_DESC="$2"; shift 2 ;;
        --theme) NEW_THEME="$2"; shift 2 ;;
        --language) NEW_LANG="$2"; shift 2 ;;
        --code-theme) NEW_CODE_THEME="$2"; shift 2 ;;
        --custom-css) NEW_CSS="$2"; shift 2 ;;
        --sfw) NEW_SFW="$2"; shift 2 ;;
        *) echo '{"error": "unknown option: '"$1"'", "code": "INVALID_ARGS"}' >&2; exit 1 ;;
    esac
done

if [[ -z "$MONGO_URL" ]]; then
    echo '{"error": "--mongo-url is required (or set MONGO_URL env var)", "code": "MISSING_PARAM"}' >&2
    exit 1
fi

if [[ -z "$URI" ]]; then
    echo '{"error": "--uri is required", "code": "MISSING_PARAM"}' >&2
    exit 1
fi

# Build $set object dynamically
SET_PARTS=""
CHANGED="["

if [[ -n "${NEW_NAME:-}" ]]; then
    SET_PARTS+="'settings.name': '${NEW_NAME}', "
    CHANGED+='"name", '
fi
if [[ -n "${NEW_DESC:-}" ]]; then
    SET_PARTS+="'settings.description': '${NEW_DESC}', "
    CHANGED+='"description", '
fi
if [[ -n "${NEW_THEME:-}" ]]; then
    SET_PARTS+="'settings.theme': '${NEW_THEME}', "
    CHANGED+='"theme", '
fi
if [[ -n "${NEW_LANG:-}" ]]; then
    SET_PARTS+="'settings.language': '${NEW_LANG}', "
    CHANGED+='"language", '
fi
if [[ -n "${NEW_CODE_THEME:-}" ]]; then
    SET_PARTS+="'settings.codeTheme': '${NEW_CODE_THEME}', "
    CHANGED+='"codeTheme", '
fi
if [[ -n "${NEW_CSS:-}" ]]; then
    SET_PARTS+="'settings.customCss': '${NEW_CSS}', "
    CHANGED+='"customCss", '
fi
if [[ -n "${NEW_SFW:-}" ]]; then
    SET_PARTS+="'settings.sfw': ${NEW_SFW}, "
    CHANGED+='"sfw", '
fi

# Remove trailing comma and space
SET_PARTS=$(echo "$SET_PARTS" | sed 's/, $//')
CHANGED=$(echo "$CHANGED" | sed 's/, $//')"]"

if [[ -z "$SET_PARTS" ]]; then
    echo '{"error": "No fields to update. Use --name, --description, --theme, --language, --code-theme, --custom-css, or --sfw", "code": "NO_FIELDS"}' >&2
    exit 1
fi

mongosh "$MONGO_URL" --quiet --eval "
const db = db.getSiblingDB('$DB_NAME');
const board = db.Boards.findOne({ _id: '$URI' });
if (!board) {
    print(JSON.stringify({ error: 'Board not found: $URI', code: 'NOT_FOUND' }));
    quit(1);
}
db.Boards.updateOne({ _id: '$URI' }, { \$set: { $SET_PARTS } });
print(JSON.stringify({ uri: '$URI', changed_fields: $CHANGED, status: 'updated' }));
" 2>&1 || exit $?
