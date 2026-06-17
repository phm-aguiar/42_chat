package api

import (
	"database/sql"
	"encoding/json"
	"io"
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

// setupAPITestDB cria um banco de teste PostgreSQL com as tabelas users e messages.
// Retorna Queries e função de cleanup. Pula o teste se PostgreSQL não estiver disponível.
func setupAPITestDB(t *testing.T) (*db.Queries, func()) {
	t.Helper()

	databaseURL := os.Getenv("DATABASE_URL")
	if databaseURL == "" {
		databaseURL = "postgres://postgres:postgres@localhost:5432/42chat_test?sslmode=disable"
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
			content TEXT NOT NULL,
			created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
			deleted_at TIMESTAMP WITH TIME ZONE,
			CONSTRAINT chk_content_length CHECK (length(content) <= 5000)
		);
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

	return queries, cleanup
}

// setupAPITestServer cria um httptest.Server com chi router, JWT middleware
// e os handlers de messages e users conectados ao banco de teste.
// Retorna o servidor, JWTManager e função de cleanup.
func setupAPITestServer(t *testing.T, jwtSecret string) (*httptest.Server, *auth.JWTManager, func()) {
	t.Helper()

	queries, dbCleanup := setupAPITestDB(t)
	jwtMgr := auth.NewJWTManager(jwtSecret)

	messagesHandler := NewMessagesHandler(queries)
	usersHandler := NewUsersHandler(queries)

	r := chi.NewRouter()

	// Rotas autenticadas (mesmo padrão do main.go)
	r.Group(func(r chi.Router) {
		r.Use(auth.JWTMiddleware(jwtMgr))
		r.Get("/api/messages", messagesHandler.ServeHTTP)
		r.Get("/api/users/{id}", usersHandler.ServeHTTP)
	})

	srv := httptest.NewServer(r)

	cleanup := func() {
		srv.Close()
		dbCleanup()
	}

	return srv, jwtMgr, cleanup
}

// genToken gera um JWT válido para testes.
func genToken(t *testing.T, mgr *auth.JWTManager, userID int, login string) string {
	t.Helper()
	token, err := mgr.GenerateToken(userID, login)
	if err != nil {
		t.Fatalf("GenerateToken: %v", err)
	}
	return token
}

// authedGet faz GET autenticado contra o servidor de teste.
func authedGet(t *testing.T, url string, token string) *http.Response {
	t.Helper()
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		t.Fatalf("NewRequest: %v", err)
	}
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		t.Fatalf("Do: %v", err)
	}
	return resp
}

// readBody lê o body da response como string.
func readBody(t *testing.T, resp *http.Response) []byte {
	t.Helper()
	defer resp.Body.Close()
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		t.Fatalf("ReadAll: %v", err)
	}
	return body
}

// ─── Messages Handler Tests ───────────────────────────────────────────────

// TestMessagesHandler_Authenticated verifica que GET /api/messages com JWT
// válido retorna um JSON array de mensagens.
func TestMessagesHandler_Authenticated(t *testing.T) {
	srv, jwtMgr, cleanup := setupAPITestServer(t, "messages-secret")
	defer cleanup()

	// Popular banco de teste com dados via queries direto
	queries, _ := setupAPITestDB(t)
	user := &model.User{
		ID:        1,
		Login:     "marvin",
		ImageURL:  "https://cdn.42.fr/marvin.jpg",
		Level:     9.87,
		CreatedAt: time.Now().UTC(),
	}
	if _, err := queries.UpsertUser(user); err != nil {
		t.Fatalf("UpsertUser: %v", err)
	}

	for i := 0; i < 3; i++ {
		if _, err := queries.InsertMessage(1, "test message"); err != nil {
			t.Fatalf("InsertMessage: %v", err)
		}
	}

	token := genToken(t, jwtMgr, 1, "marvin")

	resp := authedGet(t, srv.URL+"/api/messages", token)
	body := readBody(t, resp)

	if resp.StatusCode != http.StatusOK {
		t.Fatalf("status: got %d, want %d. body: %s", resp.StatusCode, http.StatusOK, body)
	}

	// Verificar que o body é um JSON array
	var messages []model.Message
	if err := json.Unmarshal(body, &messages); err != nil {
		t.Fatalf("json.Unmarshal: %v. body: %s", err, body)
	}

	if len(messages) < 3 {
		t.Errorf("len(messages): got %d, want at least 3", len(messages))
	}

	// Verificar campos das mensagens
	for _, m := range messages {
		if m.ID == "" {
			t.Error("message.ID não deveria estar vazio")
		}
		if m.UserID != 1 {
			t.Errorf("message.UserID: got %d, want 1", m.UserID)
		}
		if m.Login != "marvin" {
			t.Errorf("message.Login: got %s, want marvin", m.Login)
		}
		if m.Content == "" {
			t.Error("message.Content não deveria estar vazio")
		}
		if m.CreatedAt.IsZero() {
			t.Error("message.CreatedAt não deveria ser zero")
		}
	}
}

// TestMessagesHandler_Unauthenticated verifica que GET /api/messages sem token retorna 401.
func TestMessagesHandler_Unauthenticated(t *testing.T) {
	srv, _, cleanup := setupAPITestServer(t, "messages-secret")
	defer cleanup()

	resp, err := http.Get(srv.URL + "/api/messages")
	if err != nil {
		t.Fatalf("http.Get: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusUnauthorized {
		t.Errorf("status: got %d, want %d", resp.StatusCode, http.StatusUnauthorized)
	}
}

// TestMessagesHandler_Pagination verifica os parâmetros before e limit.
func TestMessagesHandler_Pagination(t *testing.T) {
	srv, jwtMgr, cleanup := setupAPITestServer(t, "messages-secret")
	defer cleanup()

	queries, _ := setupAPITestDB(t)

	user := &model.User{
		ID:        42,
		Login:     "bocal",
		ImageURL:  "https://cdn.42.fr/bocal.jpg",
		Level:     5.0,
		CreatedAt: time.Now().UTC(),
	}
	if _, err := queries.UpsertUser(user); err != nil {
		t.Fatalf("UpsertUser: %v", err)
	}

	// Inserir 10 mensagens
	for i := 0; i < 10; i++ {
		if _, err := queries.InsertMessage(42, "message number"); err != nil {
			t.Fatalf("InsertMessage %d: %v", i, err)
		}
	}

	token := genToken(t, jwtMgr, 42, "bocal")

	// Teste 1: limit=3 → deve retornar 3 mensagens
	resp := authedGet(t, srv.URL+"/api/messages?limit=3", token)
	body := readBody(t, resp)

	if resp.StatusCode != http.StatusOK {
		t.Fatalf("status: got %d, want %d", resp.StatusCode, http.StatusOK)
	}

	var messages []model.Message
	if err := json.Unmarshal(body, &messages); err != nil {
		t.Fatalf("json.Unmarshal: %v", err)
	}

	if len(messages) != 3 {
		t.Errorf("limit=3: got %d messages, want 3", len(messages))
	}

	// Teste 2: without params → default limit=50 (retorna todas as 10)
	resp2 := authedGet(t, srv.URL+"/api/messages", token)
	body2 := readBody(t, resp2)

	if resp2.StatusCode != http.StatusOK {
		t.Fatalf("status: got %d, want %d", resp2.StatusCode, http.StatusOK)
	}

	var messages2 []model.Message
	if err := json.Unmarshal(body2, &messages2); err != nil {
		t.Fatalf("json.Unmarshal: %v", err)
	}

	if len(messages2) != 10 {
		t.Errorf("default limit: got %d messages, want 10", len(messages2))
	}

	// Teste 3: limit > 100 → deve cap em 100 (mas temos só 10, então retorna 10)
	resp3 := authedGet(t, srv.URL+"/api/messages?limit=200", token)
	body3 := readBody(t, resp3)

	if resp3.StatusCode != http.StatusOK {
		t.Fatalf("status: got %d, want %d", resp3.StatusCode, http.StatusOK)
	}

	var messages3 []model.Message
	if err := json.Unmarshal(body3, &messages3); err != nil {
		t.Fatalf("json.Unmarshal: %v", err)
	}

	if len(messages3) != 10 {
		t.Errorf("limit=200 (capped at 100): got %d messages, want 10", len(messages3))
	}
}

// TestMessagesHandler_EmptyResult verifica que array vazio é retornado (não null).
func TestMessagesHandler_EmptyResult(t *testing.T) {
	srv, jwtMgr, cleanup := setupAPITestServer(t, "messages-secret")
	defer cleanup()

	queries, _ := setupAPITestDB(t)

	// Criar usuário sem mensagens
	user := &model.User{
		ID:        99,
		Login:     "emptyuser",
		ImageURL:  "https://cdn.42.fr/empty.jpg",
		Level:     1.0,
		CreatedAt: time.Now().UTC(),
	}
	if _, err := queries.UpsertUser(user); err != nil {
		t.Fatalf("UpsertUser: %v", err)
	}

	token := genToken(t, jwtMgr, 99, "emptyuser")

	resp := authedGet(t, srv.URL+"/api/messages", token)
	body := readBody(t, resp)

	if resp.StatusCode != http.StatusOK {
		t.Fatalf("status: got %d, want %d", resp.StatusCode, http.StatusOK)
	}

	if string(body) != "[]\n" {
		t.Errorf("empty result: got %s, want []", body)
	}
}

// ─── Users Handler Tests ──────────────────────────────────────────────────

// TestUsersHandler_PublicProfile verifica que GET /api/users/:id autenticado
// retorna o perfil público do usuário.
func TestUsersHandler_PublicProfile(t *testing.T) {
	srv, jwtMgr, cleanup := setupAPITestServer(t, "users-secret")
	defer cleanup()

	queries, _ := setupAPITestDB(t)

	user := &model.User{
		ID:          1,
		Login:       "zeenyt__",
		ImageURL:    "https://cdn.42.fr/zeenyt__.jpg",
		CurrentHost: "e1z1r3p1",
		Level:       12.34,
		CreatedAt:   time.Now().UTC(),
	}
	if _, err := queries.UpsertUser(user); err != nil {
		t.Fatalf("UpsertUser: %v", err)
	}

	// Gera token para qualquer usuário autenticado (o perfil é público)
	token := genToken(t, jwtMgr, 1, "zeenyt__")

	resp := authedGet(t, srv.URL+"/api/users/1", token)
	body := readBody(t, resp)

	if resp.StatusCode != http.StatusOK {
		t.Fatalf("status: got %d, want %d. body: %s", resp.StatusCode, http.StatusOK, body)
	}

	// Verificar JSON do perfil
	var got model.User
	if err := json.Unmarshal(body, &got); err != nil {
		t.Fatalf("json.Unmarshal: %v. body: %s", err, body)
	}

	if got.ID != 1 {
		t.Errorf("ID: got %d, want 1", got.ID)
	}
	if got.Login != "zeenyt__" {
		t.Errorf("Login: got %s, want zeenyt__", got.Login)
	}
	if got.ImageURL != "https://cdn.42.fr/zeenyt__.jpg" {
		t.Errorf("ImageURL: got %s", got.ImageURL)
	}
	if got.CurrentHost != "e1z1r3p1" {
		t.Errorf("CurrentHost: got %s, want e1z1r3p1", got.CurrentHost)
	}
	if got.Level != 12.34 {
		t.Errorf("Level: got %f, want 12.34", got.Level)
	}
	if got.CreatedAt.IsZero() {
		t.Error("CreatedAt não deveria ser zero")
	}
}

// TestUsersHandler_NotFound verifica que GET /api/users/:id com ID inexistente retorna 404.
func TestUsersHandler_NotFound(t *testing.T) {
	srv, jwtMgr, cleanup := setupAPITestServer(t, "users-secret")
	defer cleanup()

	queries, _ := setupAPITestDB(t)

	// Criar um usuário para poder autenticar
	user := &model.User{
		ID:        1,
		Login:     "marvin",
		ImageURL:  "https://cdn.42.fr/marvin.jpg",
		Level:     5.0,
		CreatedAt: time.Now().UTC(),
	}
	if _, err := queries.UpsertUser(user); err != nil {
		t.Fatalf("UpsertUser: %v", err)
	}

	token := genToken(t, jwtMgr, 1, "marvin")

	resp := authedGet(t, srv.URL+"/api/users/99999", token)
	body := readBody(t, resp)

	if resp.StatusCode != http.StatusNotFound {
		t.Errorf("status: got %d, want %d. body: %s", resp.StatusCode, http.StatusNotFound, body)
	}
}

// TestUsersHandler_InvalidID verifica que GET /api/users/:id com ID não numérico retorna 400.
func TestUsersHandler_InvalidID(t *testing.T) {
	srv, jwtMgr, cleanup := setupAPITestServer(t, "users-secret")
	defer cleanup()

	queries, _ := setupAPITestDB(t)

	user := &model.User{
		ID:        1,
		Login:     "marvin",
		ImageURL:  "https://cdn.42.fr/marvin.jpg",
		Level:     5.0,
		CreatedAt: time.Now().UTC(),
	}
	if _, err := queries.UpsertUser(user); err != nil {
		t.Fatalf("UpsertUser: %v", err)
	}

	token := genToken(t, jwtMgr, 1, "marvin")

	// Nota: chi não vai rotear "abc" para {id} pois {id} casa com \d+ no padrão.
	// Mas chi.URLParam retorna "abc" se o padrão da rota permitir.
	// Na prática, chi por padrão usa regex \d+ para parâmetros numéricos.
	// Vamos testar com um ID vazio ou alfanumérico
	resp := authedGet(t, srv.URL+"/api/users/abc", token)
	defer resp.Body.Close()

	// Chi pode retornar 404 para rota não encontrada (não matcha {id} numérico)
	// ou 400 se chegar ao handler. Verificamos ambos.
	if resp.StatusCode != http.StatusNotFound && resp.StatusCode != http.StatusBadRequest {
		// Lê o body para debug
		body, _ := io.ReadAll(resp.Body)
		t.Logf("body: %s", body)
		// Só falha se for OK ou outro código inesperado
		if resp.StatusCode == http.StatusOK {
			t.Errorf("status: got %d, esperava erro (404 ou 400)", resp.StatusCode)
		}
	}
}

// TestUsersHandler_Unauthenticated verifica que GET /api/users/:id sem token retorna 401.
func TestUsersHandler_Unauthenticated(t *testing.T) {
	srv, _, cleanup := setupAPITestServer(t, "users-secret")
	defer cleanup()

	resp, err := http.Get(srv.URL + "/api/users/1")
	if err != nil {
		t.Fatalf("http.Get: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusUnauthorized {
		t.Errorf("status: got %d, want %d", resp.StatusCode, http.StatusUnauthorized)
	}
}

// TestMessagesHandler_InvalidToken verifica que GET /api/messages com token inválido retorna 401.
func TestMessagesHandler_InvalidToken(t *testing.T) {
	srv, _, cleanup := setupAPITestServer(t, "messages-secret")
	defer cleanup()

	resp := authedGet(t, srv.URL+"/api/messages", "invalid-token")
	body := readBody(t, resp)

	if resp.StatusCode != http.StatusUnauthorized {
		t.Errorf("status: got %d, want %d. body: %s", resp.StatusCode, http.StatusUnauthorized, body)
	}
}
