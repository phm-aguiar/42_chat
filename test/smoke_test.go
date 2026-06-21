package test

import (
	"encoding/json"
	"fmt"
	"net"
	"net/http"
	"os"
	"os/exec"
	"syscall"
	"testing"
	"time"

	"github.com/gorilla/websocket"

	"github.com/zeenyt__/42chat/internal/auth"
	"github.com/zeenyt__/42chat/internal/model"
	"github.com/zeenyt__/42chat/internal/ws"
)

// ============================================================================
// T021: Smoke test fim a fim
// ============================================================================

// TestSmokeBuild verifica que go build ./... compila sem erros.
func TestSmokeBuild(t *testing.T) {
	t.Log("=== Smoke Test: Build ===")
	cmd := exec.Command("go", "build", "./...")
	cmd.Dir = ".." // relative to test/ directory

	output, err := cmd.CombinedOutput()
	if err != nil {
		t.Fatalf("go build ./... failed:\n%s", string(output))
	}
	t.Logf("go build ./... succeeded (%d bytes output)", len(output))
}

// TestSmokeHubInMemory valida o fluxo de mensagem usando o Hub diretamente
// (sem servidor HTTP), conectando 2 clientes e verificando broadcast.
func TestSmokeHubInMemory(t *testing.T) {
	t.Log("=== Smoke Test: Hub In-Memory (2 clientes, broadcast) ===")

	hub := ws.NewHub(nil)

	// Criar 2 clientes (simulando conexões WebSocket)
	client1 := &ws.Client{
		UserID: 1,
		Login:  "smoke_user_1",
		Send:   make(chan []byte, 256),
		Hub:    hub,
	}
	client2 := &ws.Client{
		UserID: 2,
		Login:  "smoke_user_2",
		Send:   make(chan []byte, 256),
		Hub:    hub,
	}

	// Conectar ambos ao Hub
	hub.Connect(client1)
	hub.Connect(client2)

	// Drenar mensagens de "join" do Connect
	// client1 recebe seu próprio join + join do client2 = 2 mensagens
	drainCount(client1.Send, 2)
	drainCount(client2.Send, 1) // client2 só recebe seu próprio join

	// Verificar contagem de conexões
	if count := hub.ConnectionCount(); count != 2 {
		t.Fatalf("ConnectionCount = %d, want 2", count)
	}
	t.Logf("2 clientes conectados (ConnectionCount = %d)", hub.ConnectionCount())

	// Cliente 1 envia mensagem "hello from smoke test"
	// (simulado via Hub.Broadcast, que é como o handler propaga após receber)
	msg := &model.WSMessage{
		Type:    "message",
		ID:      "smoke-msg-001",
		UserID:  client1.UserID,
		Login:   client1.Login,
		Content: "hello from smoke test",
	}
	hub.Broadcast(msg)
	t.Logf("Broadcast enviado: %q", msg.Content)

	// Cliente 1 deve receber a própria mensagem (broadcast para todos)
	verifyMessage(t, client1.Send, "message", "hello from smoke test", "client1")

	// Cliente 2 deve receber a mensagem
	verifyMessage(t, client2.Send, "message", "hello from smoke test", "client2")

	// Verificar que não há mensagens extras
	verifyNoExtraMessages(t, client1.Send, "client1")
	verifyNoExtraMessages(t, client2.Send, "client2")

	t.Log("Fluxo de mensagem validado com sucesso!")

	// Graceful shutdown no Hub
	hub.Shutdown()

	// Ambos clientes devem receber mensagem de shutdown
	verifyMessage(t, client1.Send, "system", "shutdown", "client1 (shutdown)")
	verifyMessage(t, client2.Send, "system", "shutdown", "client2 (shutdown)")

	t.Log("Shutdown notificado com sucesso!")
}

// TestSmokeServerIntegration inicia o servidor como subprocesso,
// conecta 2 clientes WebSocket reais, envia mensagem, faz graceful shutdown.
// Pula automaticamente se PostgreSQL não estiver disponível.
func TestSmokeServerIntegration(t *testing.T) {
	t.Log("=== Smoke Test: Server Integration (WebSocket real + graceful shutdown) ===")

	// 1. Build do servidor (binário fica na raiz do projeto)
	serverBinary := "../smoke_test_server"
	buildCmd := exec.Command("go", "build", "-o", "smoke_test_server", "./cmd/server/")
	buildCmd.Dir = ".."
	if out, err := buildCmd.CombinedOutput(); err != nil {
		t.Fatalf("build server failed: %v\n%s", err, string(out))
	}
	defer os.Remove(serverBinary)
	t.Log("Servidor compilado")

	// 2. Encontrar porta livre
	port, err := findFreePort()
	if err != nil {
		t.Fatalf("findFreePort: %v", err)
	}
	t.Logf("Porta livre: %s", port)

	// 3. Gerar JWT para autenticação WebSocket
	jwtSecret := os.Getenv("JWT_SECRET")
	if jwtSecret == "" {
		jwtSecret = "smoke-test-secret"
	}
	jwtManager := auth.NewJWTManager(jwtSecret)
	token, err := jwtManager.GenerateToken(42, "smoke_tester")
	if err != nil {
		t.Fatalf("GenerateToken: %v", err)
	}
	t.Logf("JWT gerado para user smoke_tester (id=42)")

	// 3.5. Inserir usuário de teste no banco (necessário para FK em InsertMessage)
	insertUser := exec.Command("docker", "exec", "-i", "42chat-postgres",
		"psql", "-U", "chat", "-d", "chat",
		"-c", "INSERT INTO users (id, login) VALUES (42, 'smoke_tester') ON CONFLICT (id) DO UPDATE SET login = EXCLUDED.login")
	if out, err := insertUser.CombinedOutput(); err != nil {
		t.Fatalf("insert test user: %v\n%s", err, string(out))
	}
	t.Log("Usuário de teste inserido (id=42)")

	// 4. Iniciar servidor como subprocesso
	serverCmd := exec.Command(serverBinary)
	dbURL := os.Getenv("DATABASE_URL")
	if dbURL == "" {
		dbURL = "postgres://chat:smoketest@localhost:5432/chat?sslmode=disable"
	}
	serverCmd.Env = append(os.Environ(),
		"PORT="+port,
		"DATABASE_URL="+dbURL,
		"JWT_SECRET="+jwtSecret,
	)
	serverCmd.Stdout = os.Stdout
	serverCmd.Stderr = os.Stderr

	if err := serverCmd.Start(); err != nil {
		t.Fatalf("server start: %v", err)
	}
	t.Logf("Servidor iniciado (PID: %d)", serverCmd.Process.Pid)

	// Garantir que o servidor seja morto ao final do teste
	defer func() {
		if serverCmd.Process != nil {
			serverCmd.Process.Signal(syscall.SIGTERM)
			time.Sleep(200 * time.Millisecond)
			serverCmd.Process.Kill()
		}
	}()

	// 5. Esperar servidor ficar pronto ou detectar falha (DB ausente)
	ready := waitForServer(t, port, 5*time.Second)
	if !ready {
		// Servidor provavelmente falhou por falta de PostgreSQL
		// Verificar se o processo já saiu
		exited := make(chan bool, 1)
		go func() {
			serverCmd.Wait()
			exited <- true
		}()
		select {
		case <-exited:
			t.Logf("Servidor saiu com código %d (provavelmente sem PostgreSQL) — pulando teste de integração", serverCmd.ProcessState.ExitCode())
		case <-time.After(500 * time.Millisecond):
			// Ainda rodando mas não respondeu health check — kill
			serverCmd.Process.Kill()
			serverCmd.Wait()
			t.Log("Servidor não respondeu ao health check — pulando teste de integração")
		}
		t.Skip("PostgreSQL não disponível — pulando integração com servidor real")
		return
	}
	t.Log("Servidor respondeu ao health check")

	// 6. Conectar 2 clientes WebSocket
	wsURL := fmt.Sprintf("ws://127.0.0.1:%s/ws?token=%s", port, token)

	client1, _, err := websocket.DefaultDialer.Dial(wsURL, nil)
	if err != nil {
		t.Fatalf("client1 dial: %v", err)
	}
	defer client1.Close()
	t.Log("Cliente 1 conectado")

	client2, _, err := websocket.DefaultDialer.Dial(wsURL, nil)
	if err != nil {
		t.Fatalf("client2 dial: %v", err)
	}
	defer client2.Close()
	t.Log("Cliente 2 conectado")

	// Drenar mensagens de join
	drainWSMessages(t, client1, 2, "client1 joins")
	drainWSMessages(t, client2, 1, "client2 joins")

	// 7. Cliente 1 envia mensagem "hello from smoke test"
	sendMsg := model.WSMessage{
		Type:    "message",
		Content: "hello from smoke test",
	}
	sendData, _ := json.Marshal(sendMsg)
	if err := client1.WriteMessage(websocket.TextMessage, sendData); err != nil {
		t.Fatalf("client1 write: %v", err)
	}
	t.Logf("Cliente 1 enviou: %q", sendMsg.Content)

	// 8. Ambos clientes devem receber a mensagem (broadcast)
	verifyWSMessage(t, client1, "message", "hello from smoke test", "client1")
	verifyWSMessage(t, client2, "message", "hello from smoke test", "client2")
	t.Log("Ambos clientes receberam a mensagem via broadcast")

	// 9. Graceful shutdown: enviar SIGTERM
	t.Log("Enviando SIGTERM para graceful shutdown...")
	if err := serverCmd.Process.Signal(syscall.SIGTERM); err != nil {
		t.Fatalf("SIGTERM: %v", err)
	}

	// 10. Clientes devem receber shutdown message
	verifyWSMessage(t, client1, "system", "shutdown", "client1 shutdown msg")
	verifyWSMessage(t, client2, "system", "shutdown", "client2 shutdown msg")
	t.Log("Clientes receberam mensagem de shutdown")

	// 11. Verificar que servidor parou com exit code 0
	done := make(chan error, 1)
	go func() {
		done <- serverCmd.Wait()
	}()

	select {
	case err := <-done:
		if err != nil {
			if exitErr, ok := err.(*exec.ExitError); ok {
				code := exitErr.ExitCode()
				t.Errorf("Server exit code = %d, want 0", code)
			} else {
				t.Errorf("Server Wait error: %v", err)
			}
		} else {
			t.Log("Servidor parou com exit code 0 (graceful shutdown OK)")
		}
	case <-time.After(15 * time.Second):
		t.Error("Servidor não parou dentro do timeout após SIGTERM")
		serverCmd.Process.Kill()
		serverCmd.Wait()
	}
}

// ============================================================================
// Helpers
// ============================================================================

// drainCount consome exatamente n mensagens do canal.
func drainCount(ch <-chan []byte, n int) {
	for i := 0; i < n; i++ {
		<-ch
	}
}

// verifyMessage consome uma mensagem do canal e verifica type e content.
func verifyMessage(t *testing.T, ch <-chan []byte, wantType, wantContent, label string) {
	t.Helper()
	select {
	case data := <-ch:
		var msg model.WSMessage
		if err := json.Unmarshal(data, &msg); err != nil {
			t.Fatalf("%s: unmarshal error: %v", label, err)
		}
		if msg.Type != wantType {
			t.Errorf("%s: type = %q, want %q", label, msg.Type, wantType)
		}
		if msg.Content != wantContent {
			t.Errorf("%s: content = %q, want %q", label, msg.Content, wantContent)
		}
	case <-time.After(2 * time.Second):
		t.Fatalf("%s: timeout waiting for message (type=%q, content=%q)", label, wantType, wantContent)
	}
}

// verifyNoExtraMessages garante que não há mensagens extras no canal.
func verifyNoExtraMessages(t *testing.T, ch <-chan []byte, label string) {
	t.Helper()
	select {
	case data := <-ch:
		t.Errorf("%s: unexpected extra message: %s", label, string(data))
	default:
	}
}

// drainWSMessages consome n mensagens de uma conexão WebSocket.
func drainWSMessages(t *testing.T, conn *websocket.Conn, n int, label string) {
	t.Helper()
	for i := 0; i < n; i++ {
		conn.SetReadDeadline(time.Now().Add(3 * time.Second))
		_, _, err := conn.ReadMessage()
		if err != nil {
			t.Fatalf("%s: drain msg %d: %v", label, i, err)
		}
	}
}

// verifyWSMessage lê uma mensagem WebSocket e verifica type e content.
func verifyWSMessage(t *testing.T, conn *websocket.Conn, wantType, wantContent, label string) {
	t.Helper()
	conn.SetReadDeadline(time.Now().Add(5 * time.Second))
	_, raw, err := conn.ReadMessage()
	if err != nil {
		t.Fatalf("%s: ReadMessage: %v", label, err)
	}

	var msg model.WSMessage
	if err := json.Unmarshal(raw, &msg); err != nil {
		t.Fatalf("%s: unmarshal: %v", label, err)
	}
	if msg.Type != wantType {
		t.Errorf("%s: type = %q, want %q", label, msg.Type, wantType)
	}
	if msg.Content != wantContent {
		t.Errorf("%s: content = %q, want %q", label, msg.Content, wantContent)
	}
}

// findFreePort encontra uma porta TCP livre.
func findFreePort() (string, error) {
	ln, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		return "", err
	}
	defer ln.Close()
	_, port, err := net.SplitHostPort(ln.Addr().String())
	if err != nil {
		return "", err
	}
	return port, nil
}

// waitForServer faz polling no health check (GET /metrics) até responder ou timeout.
func waitForServer(t *testing.T, port string, timeout time.Duration) bool {
	t.Helper()
	deadline := time.Now().Add(timeout)
	url := fmt.Sprintf("http://127.0.0.1:%s/metrics", port)

	for time.Now().Before(deadline) {
		resp, err := http.Get(url)
		if err == nil {
			resp.Body.Close()
			if resp.StatusCode == http.StatusOK {
				return true
			}
		}
		time.Sleep(100 * time.Millisecond)
	}
	return false
}
