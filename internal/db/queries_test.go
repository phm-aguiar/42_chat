package db

import (
	"database/sql"
	"os"
	"testing"
	"time"

	_ "github.com/lib/pq"

	"github.com/zeenyt__/42chat/internal/model"
)

// setupTestDB cria um banco de teste em memória/cache.
// Requer PostgreSQL rodando localmente com DATABASE_URL de teste.
func setupTestDB(t *testing.T) (*Queries, func()) {
	t.Helper()

	databaseURL := os.Getenv("DATABASE_URL")
	if databaseURL == "" {
		databaseURL = "postgres://postgres:postgres@localhost:5432/42chat_test?sslmode=disable"
	}

	db, err := sql.Open("postgres", databaseURL)
	if err != nil {
		t.Skipf("PostgreSQL não disponível: %v (pulando testes de integração)", err)
	}

	if err := db.Ping(); err != nil {
		t.Skipf("PostgreSQL não acessível: %v (pulando testes de integração)", err)
	}

	// Criar tabelas de teste
	_, err = db.Exec(`
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
			content TEXT NOT NULL,
			created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
			deleted_at TIMESTAMP WITH TIME ZONE,
			CONSTRAINT chk_content_length CHECK (length(content) <= 5000)
		);
		TRUNCATE users, messages;
	`)
	if err != nil {
		t.Fatalf("criar tabelas: %v", err)
	}

	queries := NewQueries(db)

	cleanup := func() {
		db.Exec("TRUNCATE users, messages")
		db.Close()
	}

	return queries, cleanup
}

func createTestUser(q *Queries, id int, login string) error {
	_, err := q.UpsertUser(&model.User{
		ID:        id,
		Login:     login,
		ImageURL:  "https://cdn.42.fr/" + login + ".jpg",
		Level:     5.0,
		CreatedAt: time.Now().UTC(),
	})
	return err
}

func TestUpsertUser_Insert(t *testing.T) {
	q, cleanup := setupTestDB(t)
	defer cleanup()

	id, err := q.UpsertUser(&model.User{
		ID:        42,
		Login:     "marvin",
		ImageURL:  "https://cdn.42.fr/marvin.jpg",
		Level:     9.87,
		CreatedAt: time.Now().UTC(),
	})
	if err != nil {
		t.Fatalf("UpsertUser: %v", err)
	}
	if id != 42 {
		t.Errorf("id: got %d, want 42", id)
	}
}

func TestUpsertUser_Update(t *testing.T) {
	q, cleanup := setupTestDB(t)
	defer cleanup()

	// Insert inicial
	user := &model.User{
		ID:          1,
		Login:       "bocal",
		ImageURL:    "old.jpg",
		CurrentHost: "e1z1",
		Level:       1.0,
		CreatedAt:   time.Now().UTC(),
	}
	_, err := q.UpsertUser(user)
	if err != nil {
		t.Fatalf("UpsertUser insert: %v", err)
	}

	// Update
	user.ImageURL = "new.jpg"
	user.Level = 15.0
	id, err := q.UpsertUser(user)
	if err != nil {
		t.Fatalf("UpsertUser update: %v", err)
	}
	if id != 1 {
		t.Errorf("id: got %d", id)
	}

	// Verificar update
	got, err := q.SelectUserByID(1)
	if err != nil {
		t.Fatalf("SelectUserByID: %v", err)
	}
	if got.ImageURL != "new.jpg" {
		t.Errorf("ImageURL: got %s", got.ImageURL)
	}
	if got.Level != 15.0 {
		t.Errorf("Level: got %f", got.Level)
	}
}

func TestSelectUserByID_NotFound(t *testing.T) {
	q, cleanup := setupTestDB(t)
	defer cleanup()

	_, err := q.SelectUserByID(99999)
	if err == nil {
		t.Error("esperava erro para usuário inexistente")
	}
}

func TestInsertMessage(t *testing.T) {
	q, cleanup := setupTestDB(t)
	defer cleanup()

	if err := createTestUser(q, 42, "marvin"); err != nil {
		t.Fatalf("create test user: %v", err)
	}

	msg, err := q.InsertMessage(42, "Hello, 42!")
	if err != nil {
		t.Fatalf("InsertMessage: %v", err)
	}

	if msg.ID == "" {
		t.Error("ID não deveria estar vazio")
	}
	if msg.UserID != 42 {
		t.Errorf("UserID: got %d, want 42", msg.UserID)
	}
	if msg.Content != "Hello, 42!" {
		t.Errorf("Content: got %s", msg.Content)
	}
	if msg.CreatedAt.IsZero() {
		t.Error("CreatedAt não deveria ser zero")
	}
}

func TestSelectRecentMessages(t *testing.T) {
	q, cleanup := setupTestDB(t)
	defer cleanup()

	if err := createTestUser(q, 1, "marvin"); err != nil {
		t.Fatalf("create user: %v", err)
	}

	// Inserir algumas mensagens
	for i := 0; i < 5; i++ {
		_, err := q.InsertMessage(1, "test message")
		if err != nil {
			t.Fatalf("InsertMessage %d: %v", i, err)
		}
	}

	msgs, err := q.SelectRecentMessages(time.Time{}, 3)
	if err != nil {
		t.Fatalf("SelectRecentMessages: %v", err)
	}

	if len(msgs) != 3 {
		t.Errorf("len: got %d, want 3", len(msgs))
	}

	// Verificar que login está incluso via JOIN
	if msgs[0].Login != "marvin" {
		t.Errorf("Login: got %s, want marvin", msgs[0].Login)
	}
}

func TestSoftDeleteMessage(t *testing.T) {
	q, cleanup := setupTestDB(t)
	defer cleanup()

	if err := createTestUser(q, 1, "marvin"); err != nil {
		t.Fatalf("create user: %v", err)
	}

	msg, err := q.InsertMessage(1, "will be deleted")
	if err != nil {
		t.Fatalf("InsertMessage: %v", err)
	}

	if err := q.SoftDeleteMessage(msg.ID); err != nil {
		t.Fatalf("SoftDeleteMessage: %v", err)
	}

	// Verificar que não aparece no histórico
	msgs, err := q.SelectRecentMessages(time.Time{}, 10)
	if err != nil {
		t.Fatalf("SelectRecentMessages: %v", err)
	}

	for _, m := range msgs {
		if m.ID == msg.ID {
			t.Error("mensagem deletada ainda aparece no histórico")
		}
	}
}

func TestSelectUserByLogin(t *testing.T) {
	q, cleanup := setupTestDB(t)
	defer cleanup()

	if err := createTestUser(q, 1, "zeenyt__"); err != nil {
		t.Fatalf("create user: %v", err)
	}

	user, err := q.SelectUserByLogin("zeenyt__")
	if err != nil {
		t.Fatalf("SelectUserByLogin: %v", err)
	}

	if user.ID != 1 {
		t.Errorf("ID: got %d, want 1", user.ID)
	}
}

func TestSelectUserByLogin_NotFound(t *testing.T) {
	q, cleanup := setupTestDB(t)
	defer cleanup()

	_, err := q.SelectUserByLogin("nobody")
	if err == nil {
		t.Error("esperava erro para login inexistente")
	}
}
