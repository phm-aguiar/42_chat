package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"

	"github.com/zeenyt__/42chat/internal/api"
	"github.com/zeenyt__/42chat/internal/auth"
	"github.com/zeenyt__/42chat/internal/config"
	"github.com/zeenyt__/42chat/internal/db"
	"github.com/zeenyt__/42chat/internal/ws"
)

func main() {
	log.SetFlags(log.LstdFlags | log.Lshortfile)
	log.Println("[server] 42 Chat Core MVP — iniciando...")

	// 1. Config
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("[server] config: %v", err)
	}

	// 2. Database
	pg, err := db.NewPostgres(cfg.DatabaseURL)
	if err != nil {
		log.Fatalf("[server] database: %v", err)
	}
	defer pg.Close()

	queries := db.NewQueries(pg.DB)

	// 3. Auth
	oauth2 := auth.NewOAuth2(cfg, queries)
	jwtManager := auth.NewJWTManager(cfg.JWTSecret)

	// 4. WebSocket Hub
	hub := ws.NewHub()

	// 5. Handlers
	wsHandler := ws.NewHandler(hub, jwtManager, queries)
	messagesHandler := api.NewMessagesHandler(queries)
	usersHandler := api.NewUsersHandler(queries)
	metricsHandler := api.NewMetricsHandler(pg, hub)
	devLoginHandler := auth.NewDevLoginHandler(jwtManager, queries)

	// 6. Router Chi
	r := chi.NewRouter()

	// Middleware global
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)
	r.Use(middleware.RealIP)
	r.Use(middleware.RequestID)
	r.Use(corsMiddleware)

	// Rotas públicas
	r.Get("/api/auth/42/callback", func(w http.ResponseWriter, r *http.Request) {
		code := r.URL.Query().Get("code")
		if code == "" {
			http.Error(w, `{"error":"missing code"}`, http.StatusBadRequest)
			return
		}

		user, err := oauth2.ExchangeCode(code)
		if err != nil {
			log.Printf("[server] OAuth2 error: %v", err)
			http.Error(w, `{"error":"oauth exchange failed"}`, http.StatusInternalServerError)
			return
		}

		token, err := jwtManager.GenerateToken(user.ID, user.Login)
		if err != nil {
			log.Printf("[server] JWT error: %v", err)
			http.Error(w, `{"error":"token generation failed"}`, http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		w.Write([]byte(`{"token":"` + token + `","user":{` +
			`"id":` + itoa(user.ID) + `,` +
			`"login":"` + user.Login + `",` +
			`"image_url":"` + user.ImageURL + `"` +
			`}}`))
	})

	r.Get("/metrics", metricsHandler.ServeHTTP)

	// Dev mode: login sem OAuth2 (apenas desenvolvimento local)
	if cfg.DevMode {
		log.Println("[server] DEV_MODE ativo — /api/auth/dev/login disponível")
		r.Get("/api/auth/dev/login", devLoginHandler.ServeHTTP)
	}

	// Rotas autenticadas
	r.Group(func(r chi.Router) {
		r.Use(auth.JWTMiddleware(jwtManager))
		r.Get("/api/messages", messagesHandler.ServeHTTP)
		r.Get("/api/users/{id}", usersHandler.ServeHTTP)
	})

	// WebSocket
	r.Get("/ws", wsHandler.ServeHTTP)

	// 7. Servidor HTTP
	srv := &http.Server{
		Addr:         ":" + cfg.Port,
		Handler:      r,
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 10 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	// 8. Graceful shutdown
	go func() {
		sigChan := make(chan os.Signal, 1)
		signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
		sig := <-sigChan

		log.Printf("[server] sinal recebido: %v — iniciando graceful shutdown", sig)

		// Notificar clientes WebSocket
		hub.Shutdown()

		// Dar tempo para mensagens de shutdown chegarem
		time.Sleep(500 * time.Millisecond)

		// Fechar servidor HTTP
		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()

		if err := srv.Shutdown(ctx); err != nil {
			log.Printf("[server] shutdown error: %v", err)
		}

		log.Println("[server] graceful shutdown completo")
	}()

	// 9. Iniciar
	log.Printf("[server] ouvindo em :%s", cfg.Port)
	if err := srv.ListenAndServe(); err != http.ErrServerClosed {
		log.Fatalf("[server] ListenAndServe: %v", err)
	}
}

// corsMiddleware permite CORS para desenvolvimento.
func corsMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Authorization, Content-Type")

		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusNoContent)
			return
		}

		next.ServeHTTP(w, r)
	})
}

// itoa converte int para string (evita import fmt só pra isso).
func itoa(i int) string {
	if i == 0 {
		return "0"
	}
	var buf [20]byte
	pos := len(buf)
	neg := i < 0
	if neg {
		i = -i
	}
	for i > 0 {
		pos--
		buf[pos] = byte('0' + i%10)
		i /= 10
	}
	if neg {
		pos--
		buf[pos] = '-'
	}
	return string(buf[pos:])
}
