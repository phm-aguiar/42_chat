-- 001_init.sql
-- Initial schema: users and messages tables
-- 42_chat — Core schema migration

BEGIN;

-- ============================================================
-- users table
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id          SERIAL          PRIMARY KEY,
    login       VARCHAR(50)     NOT NULL UNIQUE,
    image_url   TEXT,
    current_host VARCHAR(20),
    level       NUMERIC(4,2)    NOT NULL DEFAULT 0,
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- ============================================================
-- messages table
-- ============================================================
CREATE TABLE IF NOT EXISTS messages (
    id          UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     INT             NOT NULL,
    content     TEXT            NOT NULL,
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    deleted_at  TIMESTAMPTZ,

    CONSTRAINT fk_messages_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE CASCADE,

    CONSTRAINT chk_content_length
        CHECK (char_length(content) <= 5000)
);

-- ============================================================
-- Indexes
-- ============================================================

-- Fast reverse-chronological message listing (latest first)
CREATE INDEX IF NOT EXISTS idx_messages_created_at_desc
    ON messages (created_at DESC);

-- Fast lookup of all messages by a given user
CREATE INDEX IF NOT EXISTS idx_messages_user_id
    ON messages (user_id);

-- Also helpful: soft-delete–aware queries that exclude deleted rows
CREATE INDEX IF NOT EXISTS idx_messages_active
    ON messages (created_at DESC)
    WHERE deleted_at IS NULL;

COMMIT;
