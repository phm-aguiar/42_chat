package auth

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"
	"time"

	"github.com/zeenyt__/42chat/internal/config"
	"github.com/zeenyt__/42chat/internal/db"
	"github.com/zeenyt__/42chat/internal/model"
)

// OAuth2 gerencia a troca de código de autorização por dados do usuário 42.
type OAuth2 struct {
	cfg     *config.Config
	queries *db.Queries
	client  *http.Client
}

// NewOAuth2 cria o handler de autenticação OAuth2.
func NewOAuth2(cfg *config.Config, queries *db.Queries) *OAuth2 {
	return &OAuth2{
		cfg:     cfg,
		queries: queries,
		client:  &http.Client{Timeout: 10 * time.Second},
	}
}

// tokenResponse é a resposta do POST /oauth/token da API 42.
type tokenResponse struct {
	AccessToken string `json:"access_token"`
	TokenType   string `json:"token_type"`
	ExpiresIn   int    `json:"expires_in"`
}

// userResponse é a resposta do GET /v2/me da API 42.
type userResponse struct {
	ID       int     `json:"id"`
	Login    string  `json:"login"`
	ImageURL string  `json:"image_url"`
	Location string  `json:"location"` // pode ser null
	Level    float64 `json:"level"`
}

// ExchangeCode troca authorization code por token de acesso e dados do usuário.
// Retorna o usuário upserted (criado ou atualizado no PostgreSQL).
func (o *OAuth2) ExchangeCode(code string) (*model.User, error) {
	// 1. Trocar code por access_token
	token, err := o.fetchToken(code)
	if err != nil {
		return nil, fmt.Errorf("fetchToken: %w", err)
	}

	// 2. Buscar dados do usuário em /v2/me
	fortyTwoUser, err := o.fetchUser(token.AccessToken)
	if err != nil {
		return nil, fmt.Errorf("fetchUser: %w", err)
	}

	// 3. Converter para model.User e upsert
	user := &model.User{
		ID:          fortyTwoUser.ID,
		Login:       fortyTwoUser.Login,
		ImageURL:    fortyTwoUser.ImageURL,
		CurrentHost: fortyTwoUser.Location,
		Level:       fortyTwoUser.Level,
		CreatedAt:   time.Now().UTC(),
	}

	if _, err := o.queries.UpsertUser(user); err != nil {
		return nil, fmt.Errorf("upsertUser: %w", err)
	}

	return user, nil
}

// fetchToken troca o authorization code pelo access_token da API 42.
func (o *OAuth2) fetchToken(code string) (*tokenResponse, error) {
	data := url.Values{
		"grant_type":    {"authorization_code"},
		"client_id":     {o.cfg.FortyTwoClientID},
		"client_secret": {o.cfg.FortyTwoClientSecret},
		"code":          {code},
		"redirect_uri":  {fmt.Sprintf("http://localhost:%s/api/auth/42/callback", o.cfg.Port)},
	}

	req, err := http.NewRequest("POST",
		fmt.Sprintf("%s/oauth/token", o.cfg.FortyTwoAPIURL),
		strings.NewReader(data.Encode()))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")

	resp, err := o.client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("oauth/token: status %d: %s", resp.StatusCode, string(body))
	}

	var token tokenResponse
	if err := json.NewDecoder(resp.Body).Decode(&token); err != nil {
		return nil, err
	}

	return &token, nil
}

// fetchUser busca dados do usuário autenticado na API 42.
func (o *OAuth2) fetchUser(accessToken string) (*userResponse, error) {
	req, err := http.NewRequest("GET",
		fmt.Sprintf("%s/v2/me", o.cfg.FortyTwoAPIURL), nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", accessToken))

	resp, err := o.client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("v2/me: status %d: %s", resp.StatusCode, string(body))
	}

	var user userResponse
	if err := json.NewDecoder(resp.Body).Decode(&user); err != nil {
		return nil, err
	}

	return &user, nil
}
