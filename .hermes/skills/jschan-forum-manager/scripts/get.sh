#!/usr/bin/env bash
# jschan-forum-manager: get — busca board por URI
# Uso: get.sh --mongo-url <url> --uri <uri> [--db-name <db>]
set -euo pipefail

MONGO_URL="${MONGO_URL:-}"
DB_NAME="${MONGO_DB:-jschan}"
URI=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --mongo-url) MONGO_URL="$2"; shift 2 ;;
        --db-name) DB_NAME="$2"; shift 2 ;;
        --uri) URI="$2"; shift 2 ;;
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

mongosh "$MONGO_URL" --quiet --eval "
const db = db.getSiblingDB('$DB_NAME');
const board = db.Boards.findOne({ _id: '$URI' });
if (!board) {
    print(JSON.stringify({ error: 'Board not found: $URI', code: 'NOT_FOUND' }));
    quit(1);
}
// Convert Binary to hex string for readability
function binToHex(bin) {
    if (!bin) return '';
    return bin.hex ? bin.hex() : bin.toString('hex');
}
// Clean up output for JSON
const result = {
    uri: board._id,
    owner: board.owner,
    tags: board.tags || [],
    sequence_value: board.sequence_value,
    pph: board.pph || 0,
    ppd: board.ppd || 0,
    ips: board.ips || 0,
    webring: board.webring || false,
    lastPostTimestamp: board.lastPostTimestamp,
    settings: board.settings || {},
    staff_count: board.staff ? Object.keys(board.staff).length : 0,
    flags_count: board.flags ? Object.keys(board.flags).length : 0,
    assets_count: (board.assets || []).length,
    banners_count: (board.banners || []).length
};
print(JSON.stringify(result, null, 2));
" 2>&1 || exit $?
