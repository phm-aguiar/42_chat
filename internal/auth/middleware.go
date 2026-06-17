package auth

import (
	"context"
	"net/http"
	"strings"
)

// contextKey é um tipo privado para chaves de contexto (evita colisões).
type contextKey string

const (
	// ClaimsKey é a chave de contexto onde as claims JWT são armazenadas.
	ClaimsKey contextKey = "claims"
)

// JWTMiddleware retorna um middleware Chi que extrai e valida o JWT do header Authorization.
// Adiciona Claims ao contexto da request.
func JWTMiddleware(jwtManager *JWTManager) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			authHeader := r.Header.Get("Authorization")
			if authHeader == "" {
				http.Error(w, `{"error":"missing Authorization header"}`, http.StatusUnauthorized)
				return
			}

			parts := strings.SplitN(authHeader, " ", 2)
			if len(parts) != 2 || !strings.EqualFold(parts[0], "Bearer") {
				http.Error(w, `{"error":"invalid Authorization format"}`, http.StatusUnauthorized)
				return
			}

			tokenStr := parts[1]
			claims, err := jwtManager.ValidateToken(tokenStr)
			if err != nil {
				http.Error(w, `{"error":"invalid or expired token"}`, http.StatusUnauthorized)
				return
			}

			ctx := context.WithValue(r.Context(), ClaimsKey, claims)
			next.ServeHTTP(w, r.WithContext(ctx))
		})
	}
}

// GetClaims extrai as Claims JWT do contexto da request.
// Retorna nil se não encontradas.
func GetClaims(ctx context.Context) *Claims {
	claims, ok := ctx.Value(ClaimsKey).(*Claims)
	if !ok {
		return nil
	}
	return claims
}
