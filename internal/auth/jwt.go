package auth

import (
	"fmt"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

// Claims representa os claims do JWT usado internamente.
type Claims struct {
	jwt.RegisteredClaims
	UserID int    `json:"user_id"`
	Login  string `json:"login"`
}

// JWTManager gerencia geração e validação de tokens JWT.
type JWTManager struct {
	secret []byte
}

// NewJWTManager cria um gerenciador de JWT.
func NewJWTManager(secret string) *JWTManager {
	return &JWTManager{secret: []byte(secret)}
}

// GenerateToken cria um JWT HS256 com expiração de 12 horas.
func (m *JWTManager) GenerateToken(userID int, login string) (string, error) {
	now := time.Now().UTC()
	claims := Claims{
		RegisteredClaims: jwt.RegisteredClaims{
			IssuedAt:  jwt.NewNumericDate(now),
			ExpiresAt: jwt.NewNumericDate(now.Add(12 * time.Hour)),
			Issuer:    "42chat",
		},
		UserID: userID,
		Login:  login,
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString(m.secret)
}

// ValidateToken valida um token JWT e retorna as claims.
func (m *JWTManager) ValidateToken(tokenStr string) (*Claims, error) {
	token, err := jwt.ParseWithClaims(tokenStr, &Claims{},
		func(t *jwt.Token) (interface{}, error) {
			if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
				return nil, fmt.Errorf("método de assinatura inesperado: %v", t.Header["alg"])
			}
			return m.secret, nil
		})
	if err != nil {
		return nil, fmt.Errorf("jwt.ParseWithClaims: %w", err)
	}

	claims, ok := token.Claims.(*Claims)
	if !ok || !token.Valid {
		return nil, fmt.Errorf("token inválido")
	}

	return claims, nil
}
