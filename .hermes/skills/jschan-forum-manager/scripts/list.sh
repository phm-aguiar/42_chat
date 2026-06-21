#!/usr/bin/env bash
# jschan-forum-manager: list — lista todos os boards
# Uso: list.sh --mongo-url <url> [--db-name <db>]
set -euo pipefail

MONGO_URL="${MONGO_URL:-}"
DB_NAME="${MONGO_DB:-jschan}"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --mongo-url) MONGO_URL="$2"; shift 2 ;;
        --db-name) DB_NAME="$2"; shift 2 ;;
        *) echo '{"error": "unknown option: '"$1"'", "code": "INVALID_ARGS"}' >&2; exit 1 ;;
    esac
done

if [[ -z "$MONGO_URL" ]]; then
    echo '{"error": "--mongo-url is required (or set MONGO_URL env var)", "code": "MISSING_PARAM"}' >&2
    exit 1
fi

mongosh "$MONGO_URL" --quiet --eval "
const db = db.getSiblingDB('$DB_NAME');
const boards = db.Boards.find({}, {
    _id: 1,
    'settings.name': 1,
    owner: 1,
    sequence_value: 1,
    pph: 1,
    ppd: 1,
    lastPostTimestamp: 1
}).sort({ _id: 1 }).toArray();
const result = boards.map(b => ({
    uri: b._id,
    name: (b.settings && b.settings.name) || '',
    owner: b.owner,
    posts: b.sequence_value - 1,
    pph: b.pph || 0,
    ppd: b.ppd || 0,
    last_post: b.lastPostTimestamp
}));
print(JSON.stringify(result));
" 2>&1 || exit $?
