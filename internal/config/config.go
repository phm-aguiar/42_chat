package config

import (
	"fmt"
	"os"
)

// Config agrega todas as variáveis de ambiente do serviço.
// Valores default são seguros para desenvolvimento local.
type Config struct {
	Port                 string
	DatabaseURL          string
	JWTSecret            string
	FortyTwoClientID     string
	FortyTwoClientSecret string
	FortyTwoAPIURL       string
	FortyTwoRedirectURI  string
	DevMode              bool
}

// Load lê variáveis de ambiente e retorna Config validada.
// Retorna erro se alguma obrigatória estiver ausente.
func Load() (*Config, error) {
	cfg := &Config{
		Port:                 envOrDefault("PORT", "8080"),
		DatabaseURL:          envOrDefault("DATABASE_URL", "postgres://chat:chat@localhost:5432/chat?sslmode=disable"),
		JWTSecret:            envOrDefault("JWT_SECRET", "dev-secret-change-in-production"),
		FortyTwoClientID:     os.Getenv("FORTYTWO_CLIENT_ID"),
		FortyTwoClientSecret: os.Getenv("FORTYTWO_CLIENT_SECRET"),
		FortyTwoAPIURL:       envOrDefault("FORTYTWO_API_URL", "https://api.intra.42.fr"),
		FortyTwoRedirectURI:  envOrDefault("FORTYTWO_REDIRECT_URI", fmt.Sprintf("http://localhost:%s/api/auth/42/callback", envOrDefault("PORT", "8080"))),
		DevMode:              os.Getenv("DEV_MODE") == "true",
	}

	// Validação: credenciais 42 obrigatórias em produção
	if cfg.FortyTwoClientID == "" || cfg.FortyTwoClientSecret == "" {
		// Em dev, permite sem credenciais (útil pra testar sem OAuth real)
		if cfg.JWTSecret == "dev-secret-change-in-production" {
			// Modo dev: credenciais vazias são aceitáveis
		} else {
			return nil, fmt.Errorf("FORTYTWO_CLIENT_ID e FORTYTWO_CLIENT_SECRET são obrigatórios")
		}
	}

	return cfg, nil
}

func envOrDefault(key, defaultVal string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return defaultVal
}
