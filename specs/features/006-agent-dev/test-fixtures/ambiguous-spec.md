# Test Fixture: Spec Ambígua (BLOCKED)

> Fixture para T004. Spec com ambiguidade intencional para validar que o agent-dev
> reporta BLOCKED com pergunta específica em vez de inferir.

## Contexto (o que o orchestrator enviaria)

### Spec relevante (AMBÍGUA propositalmente)
Seção 3.1: O sistema deve implementar autenticação de usuários.

Seção 3.2: As credenciais devem ser validadas antes de qualquer operação.

### Task
- **ID:** T002
- **Papel:** Dev
- **Descrição:** Implementar autenticação de usuários
- **Arquivos:** `internal/auth/auth.go`

### Skills injetadas
- Nenhuma (modo força bruta)

### Tentativa: 1/3

## Critérios de sucesso (o que verificar após execução)

1. **Agent-dev lê a spec e detecta ambiguidade** na seção 3.1
2. **NÃO implementa nada** — não cria arquivos, não escreve código
3. **Reporta BLOCKED** com:
   - Identificação exata da ambiguidade (seção 3.1)
   - Pergunta específica: "Qual mecanismo de autenticação usar?"
   - Opções sugeridas (ou pergunta aberta)

## Comportamento ESPERADO (BLOCKED)

```
BLOCKED

Ambiguidade na spec:
Seção 3.1: "implementar autenticação de usuários" não especifica o mecanismo.

Pergunta:
Qual mecanismo de autenticação usar? (JWT, OAuth2, session-based, API key?)
```

## Comportamento REJEITADO (FAIL)

Se o agent-dev **inferir** e implementar qualquer coisa (ex: JWT sem perguntar), o teste **FALHA**.
Isso viola a regra de ouro #1: "Nunca infira."
