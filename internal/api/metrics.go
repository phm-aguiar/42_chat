package api

import (
	"encoding/json"
	"net/http"
	"runtime"

	"github.com/zeenyt__/42chat/internal/db"
	"github.com/zeenyt__/42chat/internal/ws"
)

// MetricsHandler serve métricas no formato Prometheus.
type MetricsHandler struct {
	pg  *db.Postgres
	hub *ws.Hub
}

// NewMetricsHandler cria o handler de métricas.
func NewMetricsHandler(pg *db.Postgres, hub *ws.Hub) *MetricsHandler {
	return &MetricsHandler{pg: pg, hub: hub}
}

// ServeHTTP responde GET /metrics
func (h *MetricsHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	stats := h.pg.Stats()
	var mem runtime.MemStats
	runtime.ReadMemStats(&mem)

	metrics := map[string]interface{}{
		"goroutines":          runtime.NumGoroutine(),
		"heap_alloc_mb":       float64(mem.HeapAlloc) / 1024 / 1024,
		"heap_sys_mb":         float64(mem.HeapSys) / 1024 / 1024,
		"db_open_conns":       stats.OpenConnections,
		"db_in_use":           stats.InUse,
		"db_idle":             stats.Idle,
		"db_wait_count":       stats.WaitCount,
		"db_wait_duration_ms": stats.WaitDuration.Milliseconds(),
		"ws_connections":      h.hub.ConnectionCount(),
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(metrics)
}
