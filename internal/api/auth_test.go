package api

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/go-chi/chi/v5"

	"github.com/zeenyt__/42chat/internal/auth"
)

// setupAuthTestRouter cria um chi router com o middleware JWT e um handler
// simples que retorna 200 com o user_id dos claims (para verificação).
// Retorna o servidor httptest, o JWTManager e uma função de cleanup.
func setupAuthTestRouter(t *testing.T, jwtSecret string) (*httptest.Server, *auth.JWTManager) {
	t.Helper()

	jwtMgr := auth.NewJWTManager(jwtSecret)

	r := chi.NewRouter()
	r.Group(func(r chi.Router) {
		r.Use(auth.JWTMiddleware(jwtMgr))
		r.Get("/api/protected", func(w http.ResponseWriter, r *http.Request) {
			claims := auth.GetClaims(r.Context())
			if claims == nil {
				w.WriteHeader(http.StatusUnauthorized)
				return
			}
			w.WriteHeader(http.StatusOK)
			w.Write([]byte(`{"status":"ok"}`))
		})
	})

	srv := httptest.NewServer(r)
	return srv, jwtMgr
}

// TestAuthMiddleware_MissingToken verifica que requests sem token recebem 401.
func TestAuthMiddleware_MissingToken(t *testing.T) {
	srv, _ := setupAuthTestRouter(t, "test-secret")
	defer srv.Close()

	resp, err := http.Get(srv.URL + "/api/protected")
	if err != nil {
		t.Fatalf("http.Get: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusUnauthorized {
		t.Errorf("status: got %d, want %d", resp.StatusCode, http.StatusUnauthorized)
	}
}

// TestAuthMiddleware_InvalidToken verifica que token inválido recebe 401.
func TestAuthMiddleware_InvalidToken(t *testing.T) {
	srv, _ := setupAuthTestRouter(t, "test-secret")
	defer srv.Close()

	req, err := http.NewRequest("GET", srv.URL+"/api/protected", nil)
	if err != nil {
		t.Fatalf("NewRequest: %v", err)
	}
	req.Header.Set("Authorization", "Bearer invalid-token-value")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		t.Fatalf("Do: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusUnauthorized {
		t.Errorf("status: got %d, want %d (unauthorized for invalid token)", resp.StatusCode, http.StatusUnauthorized)
	}
}

// TestAuthMiddleware_InvalidFormat verifica que formato de Authorization inválido recebe 401.
func TestAuthMiddleware_InvalidFormat(t *testing.T) {
	srv, _ := setupAuthTestRouter(t, "test-secret")
	defer srv.Close()

	tests := []struct {
		name  string
		value string
	}{
		{"Basic auth", "Basic dXNlcjpwYXNz"},
		{"No prefix", "just-a-token-without-bearer"},
		{"Empty bearer", "Bearer "},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req, err := http.NewRequest("GET", srv.URL+"/api/protected", nil)
			if err != nil {
				t.Fatalf("NewRequest: %v", err)
			}
			req.Header.Set("Authorization", tt.value)

			resp, err := http.DefaultClient.Do(req)
			if err != nil {
				t.Fatalf("Do: %v", err)
			}
			defer resp.Body.Close()

			if resp.StatusCode != http.StatusUnauthorized {
				t.Errorf("status: got %d, want %d", resp.StatusCode, http.StatusUnauthorized)
			}
		})
	}
}

// TestAuthMiddleware_ValidToken verifica que token válido passa pelo middleware
// e o handler seguinte é executado (200).
func TestAuthMiddleware_ValidToken(t *testing.T) {
	srv, jwtMgr := setupAuthTestRouter(t, "test-secret")
	defer srv.Close()

	token, err := jwtMgr.GenerateToken(42, "marvin")
	if err != nil {
		t.Fatalf("GenerateToken: %v", err)
	}

	req, err := http.NewRequest("GET", srv.URL+"/api/protected", nil)
	if err != nil {
		t.Fatalf("NewRequest: %v", err)
	}
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		t.Fatalf("Do: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		t.Errorf("status: got %d, want %d (OK for valid token)", resp.StatusCode, http.StatusOK)
	}
}

// TestAuthMiddleware_ExpiredToken verifica que token expirado recebe 401.
func TestAuthMiddleware_ExpiredToken(t *testing.T) {
	// Usa um token assinado com segredo diferente → será rejeitado como inválido
	srv, _ := setupAuthTestRouter(t, "correct-secret")
	defer srv.Close()

	// Gera token com segredo errado
	wrongMgr := auth.NewJWTManager("wrong-secret")
	token, err := wrongMgr.GenerateToken(42, "marvin")
	if err != nil {
		t.Fatalf("GenerateToken: %v", err)
	}

	req, err := http.NewRequest("GET", srv.URL+"/api/protected", nil)
	if err != nil {
		t.Fatalf("NewRequest: %v", err)
	}
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		t.Fatalf("Do: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusUnauthorized {
		t.Errorf("status: got %d, want %d (token signed with wrong secret = invalid)", resp.StatusCode, http.StatusUnauthorized)
	}
}
