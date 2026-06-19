package db

import (
	"database/sql"
	"os"
	"testing"
	"time"

	_ "github.com/lib/pq"

	"github.com/zeenyt__/42chat/internal/model"
)

// setupStatsTestDB cria um banco de teste PostgreSQL com a coluna room_id
// necessária para SelectUserStats. Pula o teste se PostgreSQL não disponível.
func setupStatsTestDB(t *testing.T) (*sql.DB, *Queries, func()) {
	t.Helper()

	databaseURL := os.Getenv("DATABASE_URL")
	if databaseURL == "" {
		databaseURL = "postgres://postgres:***@localhost:5432/42chat_test?sslmode=disable"
	}

	conn, err := sql.Open("postgres", databaseURL)
	if err != nil {
		t.Skipf("PostgreSQL não disponível: %v (pulando testes de integração)", err)
	}

	if err := conn.Ping(); err != nil {
		t.Skipf("PostgreSQL não acessível: %v (pulando testes de integração)", err)
	}

	_, err = conn.Exec(`
		CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
		CREATE TABLE IF NOT EXISTS users (
			id INT PRIMARY KEY,
			login VARCHAR(50) UNIQUE NOT NULL,
			image_url TEXT NOT NULL DEFAULT '',
			current_host VARCHAR(20) NOT NULL DEFAULT '',
			level NUMERIC(4,2) NOT NULL DEFAULT 0,
			created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
		);
		CREATE TABLE IF NOT EXISTS messages (
			id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
			user_id INT NOT NULL REFERENCES users(id),
			room_id UUID,
			content TEXT NOT NULL,
			created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
			deleted_at TIMESTAMP WITH TIME ZONE,
			CONSTRAINT chk_content_length CHECK (length(content) <= 5000)
		);
		ALTER TABLE messages ADD COLUMN IF NOT EXISTS room_id UUID;
		TRUNCATE users, messages;
	`)
	if err != nil {
		t.Fatalf("criar tabelas de teste: %v", err)
	}

	queries := NewQueries(conn)

	cleanup := func() {
		conn.Exec("TRUNCATE users, messages")
		conn.Close()
	}

	return conn, queries, cleanup
}

// insertMessageWithRoom insere uma mensagem com room_id para testes de stats.
// Usa SQL puro pois InsertMessage não suporta room_id.
func insertMessageWithRoom(t *testing.T, conn *sql.DB, userID int, content string, roomID string) {
	t.Helper()
	_, err := conn.Exec(
		`INSERT INTO messages (user_id, room_id, content, created_at) VALUES ($1, $2::uuid, $3, NOW())`,
		userID, roomID, content,
	)
	if err != nil {
		t.Fatalf("insertMessageWithRoom: %v", err)
	}
}

// ─── ComputeTier Tests (table-driven) ──────────────────────────────────────

func TestComputeTier(t *testing.T) {
	tests := []struct {
		name          string
		totalMessages int
		wantTier      string
	}{
		{
			name:          "zero messages → novato",
			totalMessages: 0,
			wantTier:      "novato",
		},
		{
			name:          "lower bound iniciante (1 msg)",
			totalMessages: 1,
			wantTier:      "iniciante",
		},
		{
			name:          "upper bound iniciante (50 msgs)",
			totalMessages: 50,
			wantTier:      "iniciante",
		},
		{
			name:          "lower bound participante (51 msgs)",
			totalMessages: 51,
			wantTier:      "participante",
		},
		{
			name:          "upper bound participante (200 msgs)",
			totalMessages: 200,
			wantTier:      "participante",
		},
		{
			name:          "lower bound veterano (201 msgs)",
			totalMessages: 201,
			wantTier:      "veterano",
		},
		{
			name:          "veterano com muitas mensagens (1000)",
			totalMessages: 1000,
			wantTier:      "veterano",
		},
		{
			name:          "25 mensagens → iniciante",
			totalMessages: 25,
			wantTier:      "iniciante",
		},
		{
			name:          "100 mensagens → participante",
			totalMessages: 100,
			wantTier:      "participante",
		},
		{
			name:          "500 mensagens → veterano",
			totalMessages: 500,
			wantTier:      "veterano",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := ComputeTier(tt.totalMessages)
			if got != tt.wantTier {
				t.Errorf("ComputeTier(%d): got %q, want %q", tt.totalMessages, got, tt.wantTier)
			}
		})
	}
}

// ─── SelectUserStats Tests ─────────────────────────────────────────────────

func TestSelectUserStats_Success(t *testing.T) {
	conn, q, cleanup := setupStatsTestDB(t)
	defer cleanup()

	// Criar usuário
	user := &model.User{
		ID:        42,
		Login:     "marvin",
		ImageURL:  "https://cdn.42.fr/marvin.jpg",
		Level:     9.87,
		CreatedAt: time.Now().UTC(),
	}
	if _, err := q.UpsertUser(user); err != nil {
		t.Fatalf("UpsertUser: %v", err)
	}

	// Inserir 5 mensagens em 2 rooms distintas
	roomA := "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
	roomB := "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
	for i := 0; i < 3; i++ {
		insertMessageWithRoom(t, conn, 42, "msg room A "+string(rune('0'+i)), roomA)
	}
	for i := 0; i < 2; i++ {
		insertMessageWithRoom(t, conn, 42, "msg room B "+string(rune('0'+i)), roomB)
	}

	stats, err := q.SelectUserStats(42)
	if err != nil {
		t.Fatalf("SelectUserStats: %v", err)
	}

	if stats.UserID != 42 {
		t.Errorf("UserID: got %d, want 42", stats.UserID)
	}
	if stats.Login != "marvin" {
		t.Errorf("Login: got %s, want marvin", stats.Login)
	}
	if stats.AvatarURL != "https://cdn.42.fr/marvin.jpg" {
		t.Errorf("AvatarURL: got %s", stats.AvatarURL)
	}
	if stats.TotalMessages != 5 {
		t.Errorf("TotalMessages: got %d, want 5", stats.TotalMessages)
	}
	if stats.ActiveRooms != 2 {
		t.Errorf("ActiveRooms: got %d, want 2", stats.ActiveRooms)
	}
	// 5 mensagens → tier iniciante (1-50)
	if stats.Tier != "iniciante" {
		t.Errorf("Tier: got %s, want iniciante", stats.Tier)
	}
	if stats.MemberSince.IsZero() {
		t.Error("MemberSince não deveria ser zero")
	}
}

func TestSelectUserStats_Novato(t *testing.T) {
	conn, q, cleanup := setupStatsTestDB(t)
	defer cleanup()

	_ = conn

	// Criar usuário sem mensagens
	user := &model.User{
		ID:        99,
		Login:     "novato",
		ImageURL:  "https://cdn.42.fr/novato.jpg",
		Level:     1.0,
		CreatedAt: time.Now().UTC(),
	}
	if _, err := q.UpsertUser(user); err != nil {
		t.Fatalf("UpsertUser: %v", err)
	}

	stats, err := q.SelectUserStats(99)
	if err != nil {
		t.Fatalf("SelectUserStats: %v", err)
	}

	if stats.UserID != 99 {
		t.Errorf("UserID: got %d, want 99", stats.UserID)
	}
	if stats.Login != "novato" {
		t.Errorf("Login: got %s, want novato", stats.Login)
	}
	if stats.TotalMessages != 0 {
		t.Errorf("TotalMessages: got %d, want 0", stats.TotalMessages)
	}
	if stats.ActiveRooms != 0 {
		t.Errorf("ActiveRooms: got %d, want 0", stats.ActiveRooms)
	}
	if stats.Tier != "novato" {
		t.Errorf("Tier: got %s, want novato", stats.Tier)
	}
}

func TestSelectUserStats_SoftDeleteExcluded(t *testing.T) {
	conn, q, cleanup := setupStatsTestDB(t)
	defer cleanup()

	user := &model.User{
		ID:        7,
		Login:     "ghost",
		ImageURL:  "https://cdn.42.fr/ghost.jpg",
		Level:     3.0,
		CreatedAt: time.Now().UTC(),
	}
	if _, err := q.UpsertUser(user); err != nil {
		t.Fatalf("UpsertUser: %v", err)
	}

	roomID := "cccccccc-cccc-cccc-cccc-cccccccccccc"

	// Inserir 3 mensagens
	for i := 0; i < 3; i++ {
		insertMessageWithRoom(t, conn, 7, "keep me", roomID)
	}

	// Soft-delete 1 mensagem
	var msgID string
	if err := conn.QueryRow(
		`SELECT id FROM messages WHERE user_id = $1 LIMIT 1`, 7,
	).Scan(&msgID); err != nil {
		t.Fatalf("buscar mensagem para soft-delete: %v", err)
	}

	if _, err := conn.Exec(
		`UPDATE messages SET deleted_at = NOW() WHERE id = $1`, msgID,
	); err != nil {
		t.Fatalf("soft-delete: %v", err)
	}

	stats, err := q.SelectUserStats(7)
	if err != nil {
		t.Fatalf("SelectUserStats: %v", err)
	}

	// Soft-deleted message deve ser excluída da contagem
	if stats.TotalMessages != 2 {
		t.Errorf("TotalMessages after soft-delete: got %d, want 2", stats.TotalMessages)
	}
}
