package api

import (
	"database/sql"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"
	"time"

	"github.com/go-chi/chi/v5"
	_ "github.com/lib/pq"

	"github.com/zeenyt__/42chat/internal/auth"
	"github.com/zeenyt__/42chat/internal/db"
	"github.com/zeenyt__/42chat/internal/model"
)

// ─── Stats Test Helpers ────────────────────────────────────────────────────

// setupStatsTestDB cria banco de teste com room_id (necessário para SelectUserStats).
func setupStatsTestDB(t *testing.T) (*sql.DB, *db.Queries, func()) {
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

	queries := db.NewQueries(conn)

	cleanup := func() {
		conn.Exec("TRUNCATE users, messages")
		conn.Close()
	}

	return conn, queries, cleanup
}

// setupStatsTestServer cria httptest.Server com chi router, JWT middleware e stats handler.
func setupStatsTestServer(t *testing.T, jwtSecret string) (*httptest.Server, *sql.DB, *auth.JWTManager, func()) {
	t.Helper()

	conn, queries, dbCleanup := setupStatsTestDB(t)
	jwtMgr := auth.NewJWTManager(jwtSecret)
	statsHandler := NewStatsHandler(queries)

	r := chi.NewRouter()

	// Grupo autenticado com rota de stats (mesmo padrão do main.go)
	r.Group(func(r chi.Router) {
		r.Use(auth.JWTMiddleware(jwtMgr))
		r.Get("/api/users/{id}/stats", statsHandler.ServeHTTP)
	})

	srv := httptest.NewServer(r)

	cleanup := func() {
		srv.Close()
		dbCleanup()
	}

	return srv, conn, jwtMgr, cleanup
}

// insertMessageWithRoom insere mensagem com room_id para teste de stats.
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

// createTestUser insere um usuário de teste via UpsertUser.
func createTestUser(t *testing.T, q *db.Queries, id int, login string) {
	t.Helper()
	user := &model.User{
		ID:        id,
		Login:     login,
		ImageURL:  "https://cdn.42.fr/" + login + ".jpg",
		Level:     5.0,
		CreatedAt: time.Now().UTC(),
	}
	if _, err := q.UpsertUser(user); err != nil {
		t.Fatalf("UpsertUser: %v", err)
	}
}

// ─── Stats Handler Tests ───────────────────────────────────────────────────

// TestStatsHandler_Success verifica que GET /api/users/{id}/stats
// retorna estatísticas corretas para usuário com mensagens.
func TestStatsHandler_Success(t *testing.T) {
	srv, conn, jwtMgr, cleanup := setupStatsTestServer(t, "stats-secret")
	defer cleanup()

	createTestUser(t, db.NewQueries(conn), 42, "marvin")

	// Inserir 5 mensagens em 2 rooms distintas
	roomA := "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
	roomB := "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
	for i := 0; i < 3; i++ {
		insertMessageWithRoom(t, conn, 42, "msg A"+string(rune('0'+i)), roomA)
	}
	for i := 0; i < 2; i++ {
		insertMessageWithRoom(t, conn, 42, "msg B"+string(rune('0'+i)), roomB)
	}

	token := genToken(t, jwtMgr, 42, "marvin")
	resp := authedGet(t, srv.URL+"/api/users/42/stats", token)
	body := readBody(t, resp)

	if resp.StatusCode != http.StatusOK {
		t.Fatalf("status: got %d, want %d. body: %s", resp.StatusCode, http.StatusOK, body)
	}

	var stats db.UserStats
	if err := json.Unmarshal(body, &stats); err != nil {
		t.Fatalf("json.Unmarshal: %v. body: %s", err, body)
	}

	if stats.UserID != 42 {
		t.Errorf("UserID: got %d, want 42", stats.UserID)
	}
	if stats.Login != "marvin" {
		t.Errorf("Login: got %s, want marvin", stats.Login)
	}
	if stats.TotalMessages != 5 {
		t.Errorf("TotalMessages: got %d, want 5", stats.TotalMessages)
	}
	if stats.ActiveRooms != 2 {
		t.Errorf("ActiveRooms: got %d, want 2", stats.ActiveRooms)
	}
	// 5 mensagens → tier iniciante
	if stats.Tier != "iniciante" {
		t.Errorf("Tier: got %s, want iniciante", stats.Tier)
	}
	if stats.MemberSince.IsZero() {
		t.Error("MemberSince não deveria ser zero")
	}
}

// TestStatsHandler_Novato verifica que usuário sem mensagens retorna tier "novato" e zeros.
func TestStatsHandler_Novato(t *testing.T) {
	srv, conn, jwtMgr, cleanup := setupStatsTestServer(t, "stats-secret")
	defer cleanup()

	// Criar usuário sem mensagens
	createTestUser(t, db.NewQueries(conn), 99, "novato")

	token := genToken(t, jwtMgr, 99, "novato")
	resp := authedGet(t, srv.URL+"/api/users/99/stats", token)
	body := readBody(t, resp)

	if resp.StatusCode != http.StatusOK {
		t.Fatalf("status: got %d, want %d. body: %s", resp.StatusCode, http.StatusOK, body)
	}

	var stats db.UserStats
	if err := json.Unmarshal(body, &stats); err != nil {
		t.Fatalf("json.Unmarshal: %v. body: %s", err, body)
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
		t.Errorf("Tier: got %s, want novato (0 mensagens)", stats.Tier)
	}
}

// TestStatsHandler_NotFound verifica que usuário inexistente retorna 404.
func TestStatsHandler_NotFound(t *testing.T) {
	srv, conn, jwtMgr, cleanup := setupStatsTestServer(t, "stats-secret")
	defer cleanup()

	// Criar um usuário qualquer para poder autenticar
	createTestUser(t, db.NewQueries(conn), 1, "marvin")

	token := genToken(t, jwtMgr, 1, "marvin")
	resp := authedGet(t, srv.URL+"/api/users/99999/stats", token)
	body := readBody(t, resp)

	if resp.StatusCode != http.StatusNotFound {
		t.Errorf("status: got %d, want %d. body: %s", resp.StatusCode, http.StatusNotFound, body)
	}
}

// TestStatsHandler_InvalidID verifica que ID não numérico retorna 400.
func TestStatsHandler_InvalidID(t *testing.T) {
	srv, conn, jwtMgr, cleanup := setupStatsTestServer(t, "stats-secret")
	defer cleanup()

	createTestUser(t, db.NewQueries(conn), 1, "marvin")

	token := genToken(t, jwtMgr, 1, "marvin")

	// Chi pode rejeitar "abc" no roteamento ou passar para o handler;
	// o handler deve retornar 400 se strconv.Atoi falhar.
	// Usamos "abc" — se chi não rotear, recebe 404; se rotear, 400.
	resp := authedGet(t, srv.URL+"/api/users/abc/stats", token)
	// Não usamos readBody aqui porque o body já é fechado por authedGet (via readBody interno)
	// mas authedGet chama readBody que fecha; para debug lemos manualmente se falhar
	if resp.StatusCode != http.StatusNotFound && resp.StatusCode != http.StatusBadRequest {
		t.Errorf("status: got %d, esperava 400 ou 404", resp.StatusCode)
	}
}

// TestStatsHandler_Unauthenticated verifica que requisição sem token retorna 401.
func TestStatsHandler_Unauthenticated(t *testing.T) {
	srv, _, _, cleanup := setupStatsTestServer(t, "stats-secret")
	defer cleanup()

	resp, err := http.Get(srv.URL + "/api/users/1/stats")
	if err != nil {
		t.Fatalf("http.Get: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusUnauthorized {
		t.Errorf("status: got %d, want %d", resp.StatusCode, http.StatusUnauthorized)
	}
}

// TestStatsHandler_InvalidToken verifica que token inválido retorna 401.
func TestStatsHandler_InvalidToken(t *testing.T) {
	srv, _, _, cleanup := setupStatsTestServer(t, "stats-secret")
	defer cleanup()

	resp := authedGet(t, srv.URL+"/api/users/1/stats", "invalid-token")
	body := readBody(t, resp)

	if resp.StatusCode != http.StatusUnauthorized {
		t.Errorf("status: got %d, want %d. body: %s", resp.StatusCode, http.StatusUnauthorized, body)
	}
}
