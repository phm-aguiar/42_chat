package config

import (
	"os"
	"testing"
)

func TestLoadDefaults(t *testing.T) {
	// Salvar env vars originais
	orig := captureEnv()
	defer restoreEnv(orig)

	// Limpar todas as env vars relevantes
	os.Unsetenv("PORT")
	os.Unsetenv("DATABASE_URL")
	os.Unsetenv("JWT_SECRET")
	os.Unsetenv("FORTYTWO_CLIENT_ID")
	os.Unsetenv("FORTYTWO_CLIENT_SECRET")
	os.Unsetenv("FORTYTWO_API_URL")

	cfg, err := Load()
	if err != nil {
		t.Fatalf("Load() error: %v", err)
	}

	if cfg.Port != "8080" {
		t.Errorf("Port: got %s, want 8080", cfg.Port)
	}
	if cfg.DatabaseURL == "" {
		t.Errorf("DatabaseURL: got empty string")
	}
	if cfg.JWTSecret != "dev-secret-change-in-production" {
		t.Errorf("JWTSecret: got %s", cfg.JWTSecret)
	}
	if cfg.FortyTwoAPIURL != "https://api.intra.42.fr" {
		t.Errorf("FortyTwoAPIURL: got %s, want https://api.intra.42.fr", cfg.FortyTwoAPIURL)
	}
}

func TestLoadEnvOverrides(t *testing.T) {
	orig := captureEnv()
	defer restoreEnv(orig)

	os.Setenv("PORT", "3000")
	os.Setenv("JWT_SECRET", "prod-secret")
	os.Setenv("FORTYTWO_CLIENT_ID", "test-client-id")
	os.Setenv("FORTYTWO_CLIENT_SECRET", "test-client-secret")
	os.Setenv("FORTYTWO_API_URL", "https://test-api.42.fr")

	cfg, err := Load()
	if err != nil {
		t.Fatalf("Load() error: %v", err)
	}

	if cfg.Port != "3000" {
		t.Errorf("Port: got %s, want 3000", cfg.Port)
	}
	if cfg.JWTSecret != "prod-secret" {
		t.Errorf("JWTSecret: got %s", cfg.JWTSecret)
	}
	if cfg.FortyTwoClientID != "test-client-id" {
		t.Errorf("FortyTwoClientID: got %s", cfg.FortyTwoClientID)
	}
	if cfg.FortyTwoAPIURL != "https://test-api.42.fr" {
		t.Errorf("FortyTwoAPIURL: got %s", cfg.FortyTwoAPIURL)
	}
}

func TestLoadMissingFortyTwoCredentialsProduction(t *testing.T) {
	orig := captureEnv()
	defer restoreEnv(orig)

	os.Unsetenv("FORTYTWO_CLIENT_ID")
	os.Unsetenv("FORTYTWO_CLIENT_SECRET")
	os.Setenv("JWT_SECRET", "production-secret")

	_, err := Load()
	if err == nil {
		t.Error("esperava erro por credenciais 42 ausentes em produção")
	}
}

func TestLoadMissingFortyTwoCredentialsDev(t *testing.T) {
	orig := captureEnv()
	defer restoreEnv(orig)

	os.Unsetenv("FORTYTWO_CLIENT_ID")
	os.Unsetenv("FORTYTWO_CLIENT_SECRET")
	// JWT_SECRET com valor padrão → modo dev
	os.Setenv("JWT_SECRET", "dev-secret-change-in-production")

	cfg, err := Load()
	if err != nil {
		t.Fatalf("Load() error in dev mode: %v", err)
	}
	if cfg.FortyTwoClientID != "" {
		t.Error("ClientID deveria ser vazio em modo dev")
	}
}

// helpers
func captureEnv() map[string]string {
	m := make(map[string]string)
	for _, k := range []string{"PORT", "DATABASE_URL", "JWT_SECRET", "FORTYTWO_CLIENT_ID", "FORTYTWO_CLIENT_SECRET", "FORTYTWO_API_URL"} {
		m[k] = os.Getenv(k)
	}
	return m
}

func restoreEnv(orig map[string]string) {
	for k, v := range orig {
		if v == "" {
			os.Unsetenv(k)
		} else {
			os.Setenv(k, v)
		}
	}
}
