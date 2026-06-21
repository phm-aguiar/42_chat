package auth

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestJWTMiddleware_ValidToken(t *testing.T) {
	jwtMgr := NewJWTManager("test-secret")
	token, err := jwtMgr.GenerateToken(42, "marvin")
	if err != nil {
		t.Fatalf("GenerateToken: %v", err)
	}

	handler := JWTMiddleware(jwtMgr)(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		claims := GetClaims(r.Context())
		if claims == nil {
			t.Error("claims não deveriam ser nil")
			w.WriteHeader(http.StatusInternalServerError)
			return
		}
		if claims.UserID != 42 {
			t.Errorf("UserID: got %d, want 42", claims.UserID)
		}
		w.WriteHeader(http.StatusOK)
	}))

	req := httptest.NewRequest("GET", "/api/messages", nil)
	req.Header.Set("Authorization", "Bearer "+token)
	rec := httptest.NewRecorder()

	handler.ServeHTTP(rec, req)

	if rec.Code != http.StatusOK {
		t.Errorf("status: got %d, want %d", rec.Code, http.StatusOK)
	}
}

func TestJWTMiddleware_MissingHeader(t *testing.T) {
	jwtMgr := NewJWTManager("test-secret")

	handler := JWTMiddleware(jwtMgr)(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		t.Error("handler não deveria ser chamado")
	}))

	req := httptest.NewRequest("GET", "/api/messages", nil)
	rec := httptest.NewRecorder()

	handler.ServeHTTP(rec, req)

	if rec.Code != http.StatusUnauthorized {
		t.Errorf("status: got %d, want %d", rec.Code, http.StatusUnauthorized)
	}
}

func TestJWTMiddleware_InvalidToken(t *testing.T) {
	jwtMgr := NewJWTManager("test-secret")

	handler := JWTMiddleware(jwtMgr)(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		t.Error("handler não deveria ser chamado")
	}))

	req := httptest.NewRequest("GET", "/api/messages", nil)
	req.Header.Set("Authorization", "Bearer invalid-token")
	rec := httptest.NewRecorder()

	handler.ServeHTTP(rec, req)

	if rec.Code != http.StatusUnauthorized {
		t.Errorf("status: got %d, want %d", rec.Code, http.StatusUnauthorized)
	}
}

func TestJWTMiddleware_BadFormat(t *testing.T) {
	jwtMgr := NewJWTManager("test-secret")

	handler := JWTMiddleware(jwtMgr)(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		t.Error("handler não deveria ser chamado")
	}))

	req := httptest.NewRequest("GET", "/api/messages", nil)
	req.Header.Set("Authorization", "Basic sometoken")
	rec := httptest.NewRecorder()

	handler.ServeHTTP(rec, req)

	if rec.Code != http.StatusUnauthorized {
		t.Errorf("status: got %d, want %d", rec.Code, http.StatusUnauthorized)
	}
}

func TestGetClaims_NilContext(t *testing.T) {
	claims := GetClaims(context.Background())
	if claims != nil {
		t.Error("claims deveria ser nil em contexto vazio")
	}
}
