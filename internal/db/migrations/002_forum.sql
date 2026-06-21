-- 002_forum.sql
-- Forum schema: boards, threads, posts
-- 42_chat — Tech forum feature
-- Primary keys: UUIDv7 (time-sortable, sem enumeration attack)
-- Inspired by jschan's board/thread/post model, but with real identities.

BEGIN;

-- ============================================================
-- boards table
-- Categorias do fórum (ex: /tech, /projects, /career)
-- UUIDv7 gerado no Go (time-sortable para performance de índice)
-- ============================================================
CREATE TABLE IF NOT EXISTS boards (
    id              UUID            PRIMARY KEY,            -- UUIDv7 (gerado no Go)
    slug            VARCHAR(50)     NOT NULL UNIQUE,       -- URI do board (ex: "tech")
    name            VARCHAR(100)    NOT NULL,               -- Nome humano
    description     TEXT            NOT NULL DEFAULT '',
    owner_id        INT             NOT NULL,               -- Dono (FK → users.id, que é INT da API 42)
    sfw             BOOLEAN         NOT NULL DEFAULT TRUE,
    theme           VARCHAR(50)     NOT NULL DEFAULT 'default',
    language        VARCHAR(10)     NOT NULL DEFAULT 'pt-BR',
    is_locked       BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_boards_owner
        FOREIGN KEY (owner_id) REFERENCES users (id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_board_slug_format
        CHECK (slug ~ '^[a-z0-9]([a-z0-9_-]*[a-z0-9])?$'),

    CONSTRAINT chk_board_slug_reserved
        CHECK (slug NOT IN ('admin', 'api', 'forum', 'chat', 'settings', 'all', 'new'))
);

-- ============================================================
-- board_staff table
-- Moderadores por board (owner/mod/admin)
-- ============================================================
CREATE TABLE IF NOT EXISTS board_staff (
    board_id        UUID            NOT NULL,
    user_id         INT             NOT NULL,
    role            VARCHAR(20)     NOT NULL DEFAULT 'mod',
    added_at        TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    added_by        INT             NOT NULL,

    PRIMARY KEY (board_id, user_id),

    CONSTRAINT fk_board_staff_board
        FOREIGN KEY (board_id) REFERENCES boards (id)
        ON DELETE CASCADE,

    CONSTRAINT fk_board_staff_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE CASCADE,

    CONSTRAINT fk_board_staff_added_by
        FOREIGN KEY (added_by) REFERENCES users (id)
        ON DELETE CASCADE,

    CONSTRAINT chk_staff_role
        CHECK (role IN ('owner', 'mod', 'admin'))
);

-- ============================================================
-- threads table
-- Tópicos dentro de um board (OP post do chan)
-- ============================================================
CREATE TABLE IF NOT EXISTS threads (
    id              UUID            PRIMARY KEY,            -- UUIDv7
    board_id        UUID            NOT NULL,
    author_id       INT             NOT NULL,
    title           VARCHAR(200)    NOT NULL,
    content         TEXT            NOT NULL,
    is_pinned       BOOLEAN         NOT NULL DEFAULT FALSE,
    is_locked       BOOLEAN         NOT NULL DEFAULT FALSE,
    post_count      INT             NOT NULL DEFAULT 1,
    last_post_at    TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ,

    CONSTRAINT fk_threads_board
        FOREIGN KEY (board_id) REFERENCES boards (id)
        ON DELETE CASCADE,

    CONSTRAINT fk_threads_author
        FOREIGN KEY (author_id) REFERENCES users (id)
        ON DELETE CASCADE,

    CONSTRAINT chk_thread_title_length
        CHECK (char_length(title) >= 3 AND char_length(title) <= 200),

    CONSTRAINT chk_thread_content_length
        CHECK (char_length(content) <= 10000)
);

-- ============================================================
-- posts table
-- Respostas dentro de uma thread (replies do chan)
-- ============================================================
CREATE TABLE IF NOT EXISTS posts (
    id              UUID            PRIMARY KEY,            -- UUIDv7
    thread_id       UUID            NOT NULL,
    author_id       INT             NOT NULL,
    content         TEXT            NOT NULL,
    reply_to        UUID,                                   -- Referência a outro post
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ,

    CONSTRAINT fk_posts_thread
        FOREIGN KEY (thread_id) REFERENCES threads (id)
        ON DELETE CASCADE,

    CONSTRAINT fk_posts_author
        FOREIGN KEY (author_id) REFERENCES users (id)
        ON DELETE CASCADE,

    CONSTRAINT fk_posts_reply_to
        FOREIGN KEY (reply_to) REFERENCES posts (id)
        ON DELETE SET NULL,

    CONSTRAINT chk_post_content_length
        CHECK (char_length(content) <= 10000)
);

-- ============================================================
-- Indexes
-- ============================================================

-- Boards: lookup por slug (URI)
CREATE UNIQUE INDEX IF NOT EXISTS idx_boards_slug
    ON boards (slug);

-- Threads: listar por board (bump order = last_post_at DESC)
CREATE INDEX IF NOT EXISTS idx_threads_board_recent
    ON threads (board_id, last_post_at DESC)
    WHERE deleted_at IS NULL;

-- Threads: pinned no topo
CREATE INDEX IF NOT EXISTS idx_threads_board_pinned
    ON threads (board_id, is_pinned DESC, last_post_at DESC)
    WHERE deleted_at IS NULL;

-- Threads: busca full-text em português
CREATE INDEX IF NOT EXISTS idx_threads_title_search
    ON threads USING gin (to_tsvector('portuguese', title));

-- Threads: autor
CREATE INDEX IF NOT EXISTS idx_threads_author
    ON threads (author_id);

-- Posts: ordem cronológica dentro da thread
CREATE INDEX IF NOT EXISTS idx_posts_thread_chrono
    ON posts (thread_id, created_at ASC)
    WHERE deleted_at IS NULL;

-- Posts: autor
CREATE INDEX IF NOT EXISTS idx_posts_author
    ON posts (author_id);

-- Posts: reply_to (tree view)
CREATE INDEX IF NOT EXISTS idx_posts_reply_to
    ON posts (reply_to)
    WHERE reply_to IS NOT NULL;

-- Board staff: lookup por usuário
CREATE INDEX IF NOT EXISTS idx_board_staff_user
    ON board_staff (user_id);

COMMIT;
