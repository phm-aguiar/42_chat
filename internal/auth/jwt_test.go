package auth

import (
	"testing"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

func TestJWT_GenerateAndValidate(t *testing.T) {
	jwtManager := NewJWTManager("test-secret-key-42")

	token, err := jwtManager.GenerateToken(42, "marvin")
	if err != nil {
		t.Fatalf("GenerateToken: %v", err)
	}

	if token == "" {
		t.Fatal("token está vazio")
	}

	claims, err := jwtManager.ValidateToken(token)
	if err != nil {
		t.Fatalf("ValidateToken: %v", err)
	}

	if claims.UserID != 42 {
		t.Errorf("UserID: got %d, want 42", claims.UserID)
	}
	if claims.Login != "marvin" {
		t.Errorf("Login: got %s, want marvin", claims.Login)
	}
	if claims.Issuer != "42chat" {
		t.Errorf("Issuer: got %s, want 42chat", claims.Issuer)
	}
}

func TestJWT_Expiration(t *testing.T) {
	jwtManager := NewJWTManager("test-secret")

	token, err := jwtManager.GenerateToken(1, "test")
	if err != nil {
		t.Fatalf("GenerateToken: %v", err)
	}

	claims, err := jwtManager.ValidateToken(token)
	if err != nil {
		t.Fatalf("ValidateToken: %v", err)
	}

	// Verificar que expira em ~12h
	now := time.Now().UTC()
	exp := claims.ExpiresAt.Time

	diff := exp.Sub(now)
	if diff < 11*time.Hour || diff > 13*time.Hour {
		t.Errorf("expiração ~12h esperada, mas diff=%v", diff)
	}

	// Verificar que não está expirado ainda
	if claims.ExpiresAt.Before(now) {
		t.Error("token já está expirado")
	}
}

func TestJWT_InvalidToken(t *testing.T) {
	jwtManager := NewJWTManager("secret-a")

	// Token assinado com chave diferente
	otherManager := NewJWTManager("secret-b")
	token, _ := otherManager.GenerateToken(1, "test")

	_, err := jwtManager.ValidateToken(token)
	if err == nil {
		t.Error("esperava erro por chave inválida")
	}
}

func TestJWT_WrongAlgorithm(t *testing.T) {
	jwtManager := NewJWTManager("secret")

	// Criar token com algoritmo não-HMAC
	token := jwt.NewWithClaims(jwt.SigningMethodRS256, Claims{
		RegisteredClaims: jwt.RegisteredClaims{
			Issuer: "42chat",
		},
		UserID: 1,
		Login:  "test",
	})
	tokenStr, _ := token.SignedString([]byte("dummy"))

	_, err := jwtManager.ValidateToken(tokenStr)
	if err == nil {
		t.Error("esperava erro por algoritmo não-HMAC")
	}
}

func TestJWT_MalformedToken(t *testing.T) {
	jwtManager := NewJWTManager("secret")

	_, err := jwtManager.ValidateToken("not.a.jwt")
	if err == nil {
		t.Error("esperava erro por token malformado")
	}
}
