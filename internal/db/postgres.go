package db

import (
	"database/sql"
	"fmt"
	"log"
	"time"

	_ "github.com/lib/pq"
)

// Postgres gerencia o pool de conexões com o PostgreSQL.
type Postgres struct {
	DB *sql.DB
}

// NewPostgres cria um pool de conexões e verifica conectividade.
func NewPostgres(databaseURL string) (*Postgres, error) {
	db, err := sql.Open("postgres", databaseURL)
	if err != nil {
		return nil, fmt.Errorf("sql.Open: %w", err)
	}

	// Pool tuning para 300 conexões simultâneas em t2.micro (1GB RAM)
	db.SetMaxOpenConns(25)
	db.SetMaxIdleConns(10)
	db.SetConnMaxLifetime(30 * time.Minute)
	db.SetConnMaxIdleTime(5 * time.Minute)

	if err := db.Ping(); err != nil {
		return nil, fmt.Errorf("db.Ping: %w", err)
	}

	log.Println("[db] PostgreSQL conectado com sucesso")
	return &Postgres{DB: db}, nil
}

// Close fecha o pool de conexões.
func (p *Postgres) Close() error {
	return p.DB.Close()
}

// Stats retorna estatísticas do pool para /metrics.
func (p *Postgres) Stats() sql.DBStats {
	return p.DB.Stats()
}
