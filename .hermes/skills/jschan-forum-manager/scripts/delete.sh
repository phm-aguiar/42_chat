#!/usr/bin/env bash
# jschan-forum-manager: delete — remove board em cascata (requer --force)
# Uso: delete.sh --mongo-url <url> --uri <uri> --force [--db-name <db>]
set -euo pipefail

MONGO_URL="${MONGO_URL:-}"
DB_NAME="${MONGO_DB:-jschan}"
URI=""
FORCE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --mongo-url) MONGO_URL="$2"; shift 2 ;;
        --db-name) DB_NAME="$2"; shift 2 ;;
        --uri) URI="$2"; shift 2 ;;
        --force) FORCE=true; shift ;;
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

if [[ "$FORCE" != "true" ]]; then
    echo '{"error": "This operation is DESTRUCTIVE and IRREVERSIBLE. Use --force to confirm.", "code": "CONFIRMATION_REQUIRED"}' >&2
    exit 1
fi

mongosh "$MONGO_URL" --quiet --eval "
const db = db.getSiblingDB('$DB_NAME');
const uri = '$URI';

const board = db.Boards.findOne({ _id: uri });
if (!board) {
    print(JSON.stringify({ error: 'Board not found: ' + uri, code: 'NOT_FOUND' }));
    quit(1);
}

const owner = board.owner;
const staffList = board.staff ? Object.keys(board.staff) : [];

// Count posts
const postsCount = db.Posts.countDocuments({ board: uri });

// Delete posts (this also handles file references)
const postResult = db.Posts.deleteMany({ board: uri });

// Delete board
db.Boards.deleteOne({ _id: uri });

// Cleanup related collections
db.Modlogs.deleteMany({ board: uri });
db.Bans.deleteMany({ board: uri });
db.Filters.deleteMany({ board: uri });
db.Stats.deleteMany({ board: uri });
db.CustomPages.deleteMany({ board: uri });

// Remove board from owner's ownedBoards
if (owner) {
    db.Accounts.updateOne({ _id: owner }, { \$pull: { ownedBoards: uri } });
}

// Remove board from all staff accounts
if (staffList.length > 0) {
    db.Accounts.updateMany(
        { _id: { \$in: staffList } },
        { \$pull: { staffBoards: uri } }
    );
}

print(JSON.stringify({
    uri: uri,
    status: 'deleted',
    posts_deleted: postsCount,
    cascaded: ['Modlogs', 'Bans', 'Filters', 'Stats', 'CustomPages', 'Accounts.ownedBoards', 'Accounts.staffBoards']
}));
" 2>&1 || exit $?
