# Tier System para Commits

Referência para o `git_conventional_commit`. Absorvido de `dev-git-commit-message` (AI-Agents-public).

## Propósito

Nem todo commit merece o mesmo nível de detalhe. O tier system ajusta o formato da mensagem conforme a criticalidade da mudança.

## Os Três Tiers

### Tier 1: Commits Críticos (feat, fix, perf, security)

**Requer:** Documentação detalhada com declaração de impacto.

**Formato:**
```
<tipo>: <título curto> (max 50 chars)

<tipo>:
 - <item 1>
 - <item 2>
 - <item 3>

Impacto: <descrição do benefício ou risco para o usuário>

Arquivos afetados:
- path/to/file1
- path/to/file2
```

**Por quê:** Features, fixes e mudanças de performance afetam usuários diretamente e precisam de documentação completa pra referência futura e geração de changelog.

### Tier 2: Commits Padrão (refactor, test, build, ci)

**Requer:** Contexto breve e lista de arquivos.

**Formato:**
```
<tipo>: <título curto> (max 72 chars)

<tipo>:
 - <item 1>

Breve explicação do que mudou e por quê (1-2 frases).

Arquivos: path/to/file1, path/to/file2
```

**Por quê:** Melhorias internas precisam de contexto pra manutenibilidade mas não exigem documentação extensa.

### Tier 3: Commits Menores (docs, style, chore)

**Requer:** Linha de título, corpo opcional.

**Formato:**
```
<tipo>: <título curto> (max 72 chars)

[Opcional: contexto adicional se útil]
```

**Por quê:** Documentação e manutenção de rotina são auto-explicativas pelo diff; mensagens verbosas adicionam ruído.

## Regras de Detecção de Tipo

### feat Detection
- Arquivos novos em `specs/features/`, `.hermes/skills/`, `.hermes/agents/`
- Novas funções/types exportados
- Threshold: 20+ linhas adicionadas geralmente indica feature

### fix Detection
- Correções de bugs
- Adições de validação/error handling
- Palavras-chave: "bug", "fix", "corrige", "resolve"

### refactor Detection
- Mudanças balanceadas (adições ≈ deleções)
- Renomeação/movimentação de funções
- Sem features novas ou fixes
- Palavras-chave: "extrai", "move", "renomeia", "simplifica"

### docs Detection
- Apenas arquivos `.md`, `README`, `AGENTS.md`
- Mudanças puramente de documentação (sem código)

### test Detection
- Arquivos `*_test.go`, `*_test.py`
- Frameworks de teste: `TestXxx`, `func Test`

### chore Detection
- Dependências (`go.mod`, `go.sum`)
- Config (`.gitignore`, CI, symlinks)
- Palavras-chave: "deps", "upgrade", "bump", "cleanup"

### style Detection
- Formatação apenas (gofmt, goimports)
- Whitespace-only changes

## Tabela de Tier por Tipo

| Tipo | Tier | Exemplo |
|---|---|---|
| feat | 1 | `feat: adiciona pipeline SDD com brainstorm interativo` |
| fix | 1 | `fix: corrige race condition no message broker` |
| perf | 1 | `perf: reduz alocações no hot path de parsing` |
| security | 1 | `security: valida input contra path traversal` |
| refactor | 2 | `refactor: extrai lógica de auth para pacote dedicado` |
| test | 2 | `test: adiciona testes de integração para WebSocket` |
| build | 2 | `build: atualiza Go para 1.24` |
| ci | 2 | `ci: adiciona workflow de auto-PR` |
| docs | 3 | `docs: atualiza AGENTS.md com skills novas` |
| style | 3 | `style: gofmt em todos os arquivos` |
| chore | 3 | `chore: remove diretório .opencode/ obsoleto` |
