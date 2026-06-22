# Tutorial — Feature 001: LATTE Coordination

> **Status:** ✅ Implementado em `.hermes/skills/sdd/latte_coordination/`
> **Testes:** 39/39 passando

A 001 é uma feature de **infraestrutura do pipeline** — ela muda **como** o
orquestrador SDD roda, não o que tu chama diretamente.

---

## Modo 1: Uso transparente (default)

Quando o `tasks.md` de uma feature tiver `graph-operators: enabled`, o
orquestrador automaticamente usa LATTE em vez do DAG estático.

**Exemplo de tasks.md:**

```yaml
---
feature_id: "010"
title: "SDD Templates"
graph-operators: enabled
heartbeat-threshold: 4
max-rounds: 40
---
```

Aí tu roda normalmente:

```bash
hermes run feature 010
```

Por baixo dos panos o orchestrator:

1. Parseia G₀ do tasks.md
2. Entra no loop de rounds: heartbeat → frontier → dispatch → exec → merge
3. Workers podem fazer **Discover** (propor tasks novas), **Claim** (auto-assign),
   **Complete**
4. Lead detecta stragglers, faz **Release** e reassign automático
5. No final: **G_final** salvo em `wiki/projects/<feature>/coordination-graph.md`

Tu não muda nada no fluxo. Só ativa a flag e o pipeline fica inteligente.

---

## Modo 2: Interagindo com os operadores

### Discover — worker descobre task não prevista

```
Worker em T002 detectou que precisa de migration extra
  → Emite Discover(T007, deps=[T002])
  → Lead avalia, aceita, T007 entra no grafo
  → Próximo round, T007 aparece no frontier
```

### Claim — worker ocioso pega task sem esperar Assign

```
Worker Y terminou T001, vê T003 no frontier, dá Claim(T003)
  → Lead reconhece, T003 vai pra Y
```

### Straggler detection — heartbeat detecta worker parado

```
[Heartbeat] Worker X stalled em T004 por 4 rounds
[Lead] Release(T004) → volta pra pending
[Lead] Assign(T004, WorkerY)
```

### Close forçado — worker esqueceu Complete mas testes passam

```
[Lead] Close(T003) → força done
```

---

## Como ativar/desativar

| Situação | `tasks.md` |
|---|---|
| Quer LATTE (dinâmico) | `graph-operators: enabled` |
| Quer DAG estático (legacy) | `graph-operators: disabled` ou omitir |
| Heartbeat mais sensível | `heartbeat-threshold: 2` (mínimo 2) |
| Heartbeat mais relaxado | `heartbeat-threshold: 6` |
| Timeout global | `max-rounds: 30` |

---

## Resumo

- **Default:** bota `graph-operators: enabled` em todo tasks.md novo
- **Só lembrar:** o orchestrator passa a ser mais inteligente sozinho
- **Se algo estranho:** `heartbeat-threshold: 6` reduz Releases falsos
- **Debug:** o coordination graph final fica na wiki pra audit trail

---

## Rodar os testes

```bash
cd /home/zeenyt__/Projetos/42_chat
PYTHONPATH=.hermes/skills/sdd python3 -m pytest \
  .hermes/skills/sdd/latte_coordination/tests/ -v
```
