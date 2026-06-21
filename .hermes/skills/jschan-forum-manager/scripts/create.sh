#!/usr/bin/env bash
# jschan-forum-manager: create — cria um novo board no MongoDB
# Uso: create.sh --mongo-url <url> --db-name <db> --name <name> --uri <uri> --owner <owner> [--description <desc>] [--tags <tags>]
set -euo pipefail

MONGO_URL="${MONGO_URL:-}"
DB_NAME="${MONGO_DB:-jschan}"
NAME=""
URI=""
OWNER=""
DESCRIPTION=""
TAGS=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --mongo-url) MONGO_URL="$2"; shift 2 ;;
        --db-name) DB_NAME="$2"; shift 2 ;;
        --name) NAME="$2"; shift 2 ;;
        --uri) URI="$2"; shift 2 ;;
        --owner) OWNER="$2"; shift 2 ;;
        --description) DESCRIPTION="$2"; shift 2 ;;
        --tags) TAGS="$2"; shift 2 ;;
        *) echo '{"error": "unknown option: '"$1"'", "code": "INVALID_ARGS"}' >&2; exit 1 ;;
    esac
done

if [[ -z "$MONGO_URL" ]]; then
    echo '{"error": "--mongo-url is required (or set MONGO_URL env var)", "code": "MISSING_PARAM"}' >&2
    exit 1
fi

if [[ -z "$NAME" || -z "$URI" || -z "$OWNER" ]]; then
    echo '{"error": "--name, --uri, --owner are required", "code": "MISSING_PARAM"}' >&2
    exit 1
fi

# Reserved URIs
RESERVED="captcha forms randombanner all"
for r in $RESERVED; do
    if [[ "${URI,,}" == "$r" ]]; then
        echo "{\"error\": \"URI '$URI' is reserved\", \"code\": \"RESERVED_URI\"}" >&2
        exit 1
    fi
done

# Sanitize tags
TAGS_JSON="[]"
if [[ -n "$TAGS" ]]; then
    TAGS_JSON=$(echo "$TAGS" | tr ',' '\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | grep -v '^$' | jq -R . | jq -s .)
fi

# Default settings
LANGUAGE="${JSCHAN_LANGUAGE:-pt-BR}"
THEME="${JSCHAN_THEME:-yotsuba}"
CODE_THEME="${JSCHAN_CODE_THEME:-github}"

# Build owner permissions bitmap (BOARD_OWNER_DEFAULTS)
# jschan roleManager: all bits set = max permissions
MAX_PERMS_BITMAP="//////////8="

mongosh "$MONGO_URL" --quiet --eval "
const db = db.getSiblingDB('$DB_NAME');
const uri = '$URI';
const existing = db.Boards.findOne({ _id: uri });
if (existing) {
    print(JSON.stringify({ error: 'Board with URI \"' + uri + '\" already exists', code: 'DUPLICATE_URI' }));
    quit(1);
}
const tags = $TAGS_JSON;
const board = {
    _id: uri,
    owner: '$OWNER',
    tags: tags,
    banners: [],
    sequence_value: 1,
    pph: 0,
    ppd: 0,
    ips: 0,
    lastPostTimestamp: null,
    webring: false,
    staff: {},
    flags: {},
    assets: [],
    settings: {
        name: '$NAME',
        description: '$DESCRIPTION',
        language: '$LANGUAGE',
        theme: '$THEME',
        codeTheme: '$CODE_THEME',
        customCss: '',
        sfw: false,
        lockMode: 0,
        fileR9KMode: 0,
        messageR9KMode: 0,
        captchaMode: 0,
        unlistedLocal: false,
        unlistedWebring: false,
        reverseImageSearchLinks: true,
        archiveLinks: true,
        tphTrigger: 0,
        pphTrigger: 0,
        userPostDelete: true,
        userPostSpoiler: true,
        userPostUnlink: true,
        replyLimit: 0,
        deleteProtectionAge: 0,
        deleteProtectionCount: 0,
        announcement: { raw: '', markdown: '' }
    }
};
board.staff['$OWNER'] = {
    permissions: new BinData(0, '$MAX_PERMS_BITMAP'),
    addedDate: new Date()
};
db.Boards.insertOne(board);
db.Accounts.updateOne({ _id: '$OWNER' }, { \$addToSet: { ownedBoards: uri } });
// Add to modlog
db.Modlogs.insertOne({
    board: null,
    showLinks: true,
    postLinks: [{ board: uri }],
    actions: ['CREATE_BOARD'],
    public: false,
    date: new Date(),
    showUser: true,
    message: 'Created board /' + uri + '/',
    user: '$OWNER',
    ip: { cloak: '0.0.0.0', raw: '0.0.0.0' }
});
print(JSON.stringify({ uri: uri, name: '$NAME', owner: '$OWNER', status: 'created' }));
" 2>&1 || exit $?
