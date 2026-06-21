# Contrato LATTE — Protocolo de Coordenação

> **Base:** Seção 3.2 e Appendix A3 do paper *"Improving the Efficiency of Language Agent Teams with Adaptive Task Graphs"* (Mieczkowski et al., 2026).  
> **Feature:** `001-latte_coordination`  
> **Versão:** 1.0.0 — 2026-06-19  

---

## 1. Definições Fundamentais

### 1.1 Dynamic Coordination Graph

Um *coordination graph* $G_t$ no round $t \in \{1,\ldots,T\}$ é um DAG (Directed Acyclic Graph) definido como:

$$G_t = (V_t,\ E_t,\ \lambda_t)$$

Onde:

| Componente | Descrição |
|---|---|
| $V_t$ | Conjunto finito de nós, cada um representando uma subtask |
| $E_t \subseteq V_t \times V_t$ | Arestas de dependência: $(u, v) \in E_t$ implica que $v$ não pode iniciar até que $u$ esteja **done** |
| $\lambda_t : V_t \to (\mathcal{A} \cup \{\bot\}) \times S$ | Função de rotulagem que associa cada nó a um agente e um status |

**Conjunto de agentes:** $\mathcal{A} = \{\ell\} \cup \mathcal{W}$, onde $\ell$ é o Lead e $\mathcal{W}$ é o conjunto de Workers.

**Estados possíveis ($S$):**

```
pending → assigned → in_progress → done → verified
```

| Status | Significado |
|---|---|
| `pending` | Task criada, sem agente atribuído, aguardando dependências |
| `assigned` | Lead atribuiu a um Worker, mas Worker ainda não iniciou |
| `in_progress` | Worker reivindicou (Claim) e está executando ativamente |
| `done` | Worker finalizou com sucesso (Complete) ou Lead forçou encerramento (Close) |
| `verified` | Task passou por verificação (Verify concluído) — estado terminal estendido |

> **Nota:** $\bot$ denota *unassigned* (sem agente atribuído).

### 1.2 Frontier ($F_t$)

O *frontier* $F_t \subseteq V_t$ no round $t$ é o conjunto de nós `pending` com todas as dependências satisfeitas:

$$F_t := \{ v \in V_t \mid \text{status}(v) = \texttt{pending} \ \land \ \forall (u, v) \in E_t,\ \text{status}(u) = \texttt{done} \}$$

$F_t$ determina o paralelismo máximo no round $t$: $\min(|F_t|, |\mathcal{W}|)$ Workers podem ser despachados simultaneamente.

---

## 2. Os 7 Operadores de Mutação do Grafo

Cada operador possui **preconditions** (condições que devem ser verdadeiras para que o operador seja aplicável), **postconditions** (efeitos sobre $G_t$ após a aplicação bem-sucedida) e **invariantes** (propriedades preservadas).

### 2.1 Summary Table

| # | Operador | Chamador | Efeito Resumido |
|---|---|---|---|
| 1 | `Discover(v, deps)` | $\ell$, $w$ | Adiciona novo nó `pending` $v$ com dependências `deps` |
| 2 | `Assign(v, w)` | $\ell$ | Atribui nó `pending` $v$ ao Worker $w$ |
| 3 | `Claim(v)` | $w$ | Worker $w$ reivindica nó $v \in F_t$ do frontier |
| 4 | `Complete(v)` | $w$ | Worker $w$ marca seu nó `in_progress` como `done` |
| 5 | `Release(v)` | $\ell$ | Devolve nó travado para `pending` (libera para reassignment) |
| 6 | `Close(v)` | $\ell$ | Força `done` em nó cujo Worker está inativo mas trabalho foi concluído |
| 7 | `Verify(v)` | $\ell$ | Spawna nó de verificação $v_{ver}$ como dependente de $v$ |

---

### 2.2 Operador 1 — `Discover(v, deps)`

**Chamador:** Lead ($\ell$) ou Worker ($w$)  
**Propósito:** Adicionar uma nova subtask ao grafo durante a execução. É o **único** operador que modifica $V_t$ e $E_t$.

#### Preconditions

1. $v \notin V_t$ — o nó não pode já existir no grafo
2. $\text{deps} \subseteq V_t$ — todas as dependências declaradas devem ser nós existentes
3. A adição de $v$ com arestas de `deps` preserva a **aciclicidade** do grafo (i.e., o grafo resultante $G'_t$ permanece um DAG)

#### Postconditions

1. $V_t \leftarrow V_t \cup \{v\}$ — adiciona o novo nó
2. $E_t \leftarrow E_t \cup \{(d, v) \mid d \in \text{deps}\}$ — insere arestas de cada dependência para $v$
3. $\lambda_t(v) \leftarrow (\bot, \texttt{pending})$ — inicializa como unassigned e pending

#### Invariantes Preservados

- **DAG:** O novo grafo continua acíclico (garantido pela precondition 3)
- **Sem self-loops:** $v \notin V_t$ garante que $v \neq d$ para qualquer $d \in \text{deps}$, portanto $(v, v) \notin E_t$
- **Consistência de referências:** Todas as arestas apontam para nós existentes (garantido pela precondition 2)

#### Notas de Implementação

- Workers podem propor `Discover`; o Lead avalia e faz merge
- `Discover` é o operador mais frequente em execuções reais (paper: 36% dos trials)
- O Lead também usa `Discover` na Fase 0 (Planning) para inicializar $G_0$

---

### 2.3 Operador 2 — `Assign(v, w)`

**Chamador:** Lead ($\ell$) somente  
**Propósito:** Atribuir um nó `pending` do grafo a um Worker específico.

#### Preconditions

1. $\text{status}(v) = \texttt{pending}$ — o nó deve estar disponível para atribuição
2. $w \in \mathcal{W}$ — o Worker designado deve pertencer ao conjunto de Workers

#### Postconditions

1. $\lambda_t(v) \leftarrow (w, \texttt{assigned})$ — rotula o nó com o Worker e status `assigned`

#### Invariantes Preservados

- **Estrutura do grafo:** $V_t$ e $E_t$ não são alterados
- **Exclusividade:** Um nó só pode ter um Worker atribuído por vez (postcondition sobrescreve)

#### Notas de Implementação

- Exclusivo do Lead — Workers NÃO podem Assign
- Usado na Fase 0 (planejamento inicial) e durante execução para reassignment pós-Release
- Contrasta com `Claim`, onde o Worker se auto-atribui

---

### 2.4 Operador 3 — `Claim(v)`

**Chamador:** Worker ($w$)  
**Propósito:** Permitir que um Worker ocioso reivindique proativamente trabalho disponível no frontier, implementando *work-stealing* / self-scheduling.

#### Preconditions

1. $v \in F_t$ — o nó deve estar no frontier (todas as dependências satisfeitas)
2. $\text{agent}(v) \in \{\bot, w\}$ — o nó deve estar unassigned ($\bot$) ou já atribuído a este mesmo Worker $w$

#### Postconditions

1. $\lambda_t(v) \leftarrow (w, \texttt{in\_progress})$ — Worker assume o nó e inicia execução

#### Invariantes Preservados

- **DAG:** $V_t$ e $E_t$ inalterados
- **Frontier consistency:** Após Claim, $v \notin F_{t+1}$ (pois status não é mais `pending`)

#### Notas de Implementação

- Mecanismo de **work-stealing**: Workers ociosos podem Claim tarefas do frontier sem esperar o Lead
- Reduz overhead de coordenação e melhora wall-clock time (paper: high success rate)
- Claim duplo no mesmo round: resolvido por FIFO — ver Seção 5

---

### 2.5 Operador 4 — `Complete(v)`

**Chamador:** Worker ($w$)  
**Propósito:** Worker sinaliza que concluiu com sucesso a execução de sua subtask.

#### Preconditions

1. $\text{status}(v) = \texttt{in\_progress}$ — o Worker deve estar ativamente executando a task
2. $\text{agent}(v) = w$ — somente o Worker designado pode marcar como concluído

#### Postconditions

1. $\lambda_t(v) \leftarrow (w, \texttt{done})$ — mantém o agente e altera status para `done`

#### Invariantes Preservados

- **DAG:** $V_t$ e $E_t$ inalterados
- **Rastreabilidade:** O agente original é preservado para auditoria
- **Efeito cascata:** Nós que dependiam de $v$ podem agora entrar no $F_{t+1}$

#### Notas de Implementação

- Worker só deve emitir `Complete` após verificar que testes passam
- Se testes falham após implementação, Worker deve usar `Discover` para criar follow-up fix task, NÃO marcar como done
- É o mecanismo normal de progresso — desbloqueia dependentes

---

### 2.6 Operador 5 — `Release(v)`

**Chamador:** Lead ($\ell$) somente  
**Propósito:** Devolver um nó travado (straggler) para o estado `pending`, liberando-o para reassignment ou Claim por outro Worker.

#### Preconditions

1. $\text{status}(v) \in \{\texttt{assigned}, \texttt{in\_progress}\}$ — o nó deve estar atribuído ou em execução

#### Postconditions

1. $\lambda_t(v) \leftarrow (\bot, \texttt{pending})$ — remove o agente e retorna ao estado pendente

#### Invariantes Preservados

- **DAG:** $V_t$ e $E_t$ inalterados
- **Reentrada no frontier:** Se dependências de $v$ estão satisfeitas, $v \in F_{t+1}$

#### Notas de Implementação

- Exclusivo do Lead
- Disparado tipicamente após heartbeat detection de straggler (H rounds sem ação)
- Paper: Release foi invocado em 36% dos trials — mecanismo de fault tolerance que emerge na prática
- Após Release, Lead pode Assign para outro Worker, ou Workers podem Claim do frontier

---

### 2.7 Operador 6 — `Close(v)`

**Chamador:** Lead ($\ell$) somente  
**Propósito:** Forçar a conclusão de um nó quando o trabalho foi efetivamente realizado (ex: testes passam) mas o Worker esqueceu de emitir `Complete` ou está inativo.

#### Preconditions

1. $\text{status}(v) \in \{\texttt{assigned}, \texttt{in\_progress}\}$ — o nó deve estar em um estado ativo

#### Postconditions

1. $\lambda_t(v) \leftarrow (\text{agent}(v), \texttt{done})$ — preserva o agente original mas força status `done`

#### Invariantes Preservados

- **DAG:** $V_t$ e $E_t$ inalterados
- **Rastreabilidade:** Agente original mantido para auditoria (diferente de Release, que zera o agente)

#### Notas de Implementação

- **Diferente de Release:** Release devolve para `pending` (requer re-execução); Close assume que o trabalho JÁ foi feito
- Só deve ser usado quando `<run_tests />` confirma que os testes passam
- Cenário típico: Worker completou o código, testes estão verdes, mas Worker não emitiu `Complete` (esqueceu, crashou, ou ficou inativo)
- Paper: "Only use this after confirming with `<run_tests />` that tests pass"

---

### 2.8 Operador 7 — `Verify(v)`

**Chamador:** Lead ($\ell$) somente  
**Propósito:** Spawnar uma task de verificação para revisar output de alto risco/alta incerteza, inserindo um nó de verificação como dependente de $v$.

#### Preconditions

1. $\text{status}(v) = \texttt{done}$ — o nó a ser verificado deve estar concluído
2. $v_{ver} \notin V_t$ — o nó de verificação não pode já existir

#### Postconditions

1. $V_t \leftarrow V_t \cup \{v_{ver}\}$ — adiciona o nó de verificação
2. $E_t \leftarrow E_t \cup \{(v, v_{ver})\}$ — cria aresta de dependência: verificação só inicia após $v$ estar done
3. $\lambda_t(v_{ver}) \leftarrow (\bot, \texttt{pending})$ — nó de verificação começa como unassigned, pending
4. $\lambda_t(v)$ permanece inalterado em `(agent, done)` — **a task original NÃO é regredida**

#### Invariantes Preservados

- **DAG:** $v_{ver} \notin V_t$ garante que $(v, v_{ver})$ não cria self-loop; como $v_{ver}$ é folha (sem arestas de saída), não cria ciclo
- **Imutabilidade do histórico:** O status `done` de $v$ é preservado

#### Notas de Implementação

- **Verify NÃO reverte $v$ para pending** — apenas spawna uma NOVA task $v_{ver}$
- $v_{ver}$ é tratado como task normal: entra no grafo, pode ser Claim/Assign, e quando completado, status muda para `done` (ou `verified`)
- Paper: Leads invocaram Verify em 19% dos trials, principalmente em trials de alta incerteza (18.1 rounds vs 8.1 rounds sem verificação)
- Uso seletivo: não é verificação obrigatória de toda task — apenas nós *high-stakes* (upstream de muitas outras tasks, output difícil de validar posteriormente)

---

## 3. Formato de Mensagens Lead ↔ Workers

A comunicação entre Lead e Workers utiliza um formato baseado em tags XML-like. As ações são processadas pelo orchestrator, que aplica as mutações correspondentes no grafo.

### 3.1 Ações do Lead ($\ell$)

#### `<assign_task>`

Atribui uma task `pending` a um Worker.

```xml
<assign_task id="task-1" to="Dev2" />
```

**Atributos:**
- `id` (obrigatório): identificador do nó no grafo
- `to` (obrigatório): nome do Worker destino

**Processamento:** Aplica `Assign(v, w)`.

---

#### `<release_task>`

Devolve uma task travada ao estado `pending`.

```xml
<release_task id="task-3" />
```

**Atributos:**
- `id` (obrigatório): identificador do nó a ser liberado

**Processamento:** Aplica `Release(v)`.  
**Uso típico:** Após heartbeat detection de straggler ($H$ rounds sem ação).

---

#### `<close_task>`

Força `done` em task cujo Worker está inativo mas código foi concluído.

```xml
<close_task id="task-5" />
```

**Atributos:**
- `id` (obrigatório): identificador do nó a ser fechado

**Processamento:** Aplica `Close(v)`.  
**Pré-condição operacional:** Lead deve ter executado `<run_tests />` e confirmado que testes passam antes de usar Close.

---

#### `<verify_task>`

Spawna um nó de verificação como dependente da task alvo.

```xml
<verify_task id="task-2" />
```

**Atributos:**
- `id` (obrigatório): identificador do nó `done` a ser verificado

**Processamento:** Aplica `Verify(v)`, criando $v_{ver}$ com aresta $(v, v_{ver})$.

---

#### `<discover_task>` (Lead)

Adiciona uma nova task ao grafo.

```xml
<discover_task id="fix-index" title="Fix index() API bug"
    dependencies="task-2">
    Run <run_tests /> to see failures, fix search_lib.py,
    confirm all tests pass.
</discover_task>
```

**Atributos:**
- `id` (obrigatório): identificador único do novo nó
- `title` (obrigatório): título descritivo da task
- `dependencies` (opcional): lista de IDs separados por espaço; se omitido, sem dependências

**Conteúdo (inner text):** Descrição detalhada da task para o Worker.

**Processamento:** Aplica `Discover(v, deps)`.

---

### 3.2 Ações dos Workers ($w$)

#### `<claim_task>`

Worker reivindica uma task do frontier para execução.

```xml
<claim_task id="task-4" />
```

**Atributos:**
- `id` (obrigatório): identificador do nó no frontier

**Processamento:** Aplica `Claim(v)`. Se $v \notin F_t$ ou já foi claimed por outro Worker no mesmo round, retorna erro.

---

#### `<complete_task>`

Worker sinaliza conclusão bem-sucedida de sua task.

```xml
<complete_task id="task-4" />
```

**Atributos:**
- `id` (obrigatório): identificador do nó em `in_progress` pertencente a este Worker

**Processamento:** Aplica `Complete(v)`.  
**Pré-condição operacional:** Worker deve ter executado `<run_tests />` e confirmado que passam.

---

#### `<discover_task>` (Worker)

Worker propõe nova task descoberta durante execução.

```xml
<discover_task id="new-task-id" title="Short title"
    dependencies="only-if-truly-required">
    Clear description of what needs to be done and why.
</discover_task>
```

**Atributos e conteúdo:** Idêntico ao `<discover_task>` do Lead.

**Processamento:** Worker gera proposta; Lead avalia e faz merge no grafo. Aplicação final = `Discover(v, deps)`.

---

### 3.3 Ações Auxiliares

#### `<broadcast>` (Lead)

Mensagem para todos os Workers simultaneamente.

```xml
<broadcast>Your message here</broadcast>
```

#### `<request_status />` (Lead)

Solicita status dos Workers.

#### `<run_tests />` (Lead e Workers)

Executa a suíte de testes.

#### `<run_script path="script.py" />` (Lead e Workers)

Executa um script Python e retorna stdout/stderr.

#### `<read_file path="math_utils.py" />` (Workers)

Lê o conteúdo de um arquivo diretamente.

---

### 3.4 Resumo de Permissões por Ação

| Ação | Lead ($\ell$) | Worker ($w$) |
|---|---|---|
| `<assign_task>` | ✅ | ❌ |
| `<release_task>` | ✅ | ❌ |
| `<close_task>` | ✅ | ❌ |
| `<verify_task>` | ✅ | ❌ |
| `<discover_task>` | ✅ | ✅ (proposta; Lead avalia) |
| `<claim_task>` | ❌ | ✅ |
| `<complete_task>` | ❌ | ✅ |
| `<broadcast>` | ✅ | ❌ |

---

## 4. Invariantes do Grafo

### 4.1 Invariante DAG (Aciclicidade)

> **Em qualquer round $t$, $G_t$ é um DAG (Directed Acyclic Graph).**

**Mecanismo de preservação:**

| Operador | Como preserva a aciclicidade |
|---|---|
| `Discover` | **Único operador que adiciona arestas.** Precondition exige que `deps` $\subseteq V_t$ E que o grafo resultante seja acíclico. Como $v \notin V_t$, arestas só podem ser $(d, v)$ onde $d \in V_t$, $v$ é novo — direção sempre *forward*. |
| `Assign` | Não altera $V_t$ nem $E_t$ |
| `Claim` | Não altera $V_t$ nem $E_t$ |
| `Complete` | Não altera $V_t$ nem $E_t$ |
| `Release` | Não altera $V_t$ nem $E_t$ |
| `Close` | Não altera $V_t$ nem $E_t$ |
| `Verify` | Adiciona $v_{ver} \notin V_t$ e aresta $(v, v_{ver})$ onde $v$ é nó existente e $v_{ver}$ é folha — não pode criar ciclo |

**Validação de aciclicidade no `Discover`:** Antes de aceitar a proposta, o orchestrator executa verificação de ciclo (DFS ou topological sort) no grafo candidato $G'_t$. Se ciclo for detectado, a operação é rejeitada.

---

### 4.2 Invariante de Self-Loops

> **Para todo $v \in V_t$, $(v, v) \notin E_t$.**

**Preservação:** `Discover` é o único operador que adiciona arestas. Sua precondition $v \notin V_t$ garante que $v$ não pode aparecer em `deps` (pois `deps` $\subseteq V_t$ e $v \notin V_t$). Portanto, nenhuma aresta $(v, v)$ pode ser criada.

---

### 4.3 Invariante de Transições de Status Válidas

O diagrama de transições de status permitidas para qualquer nó $v$:

```
                 ┌─────────┐
                 │ pending │◄──────────────────────────┐
                 └────┬────┘                           │
                      │                                │
            Assign()  │  Claim()                       │
                      ▼                                │
              ┌──────────────┐                         │
              │   assigned   │                         │
              └──────┬───────┘                         │
                     │                                 │
          Claim()    │                                 │
                     ▼                                 │
             ┌──────────────┐        Release()         │
             │ in_progress  │──────────────────────────┘
             └──────┬───────┘
                    │
         Complete() │  Close()
                    ▼
                ┌──────┐
                │ done │
                └──┬───┘
                   │
        Verify()   │
                   ▼
            ┌────────────┐
            │  v_ver     │  (novo nó, vida independente)
            │  pending   │
            └────────────┘
```

**Transições proibidas (violariam invariantes):**

| Transição | Por que é inválida |
|---|---|
| `done` → `pending` | Imutabilidade do histórico: trabalho concluído não pode ser desfeito |
| `done` → `in_progress` | Idem |
| `pending` → `done` (direto) | Precisa passar por `assigned`/`in_progress` — Assign ou Claim primeiro |
| `in_progress` → `assigned` | Regressão não faz sentido (Worker já iniciou) |
| `assigned` → `pending` (sem Release) | Só Release pode devolver ao pool |
| Qualquer → `verified` diretamente | `verified` é status de $v_{ver}$, não do nó original $v$ |

---

### 4.4 Invariante de Consistência de Referências

> **Para toda aresta $(u, v) \in E_t$, ambos $u, v \in V_t$.**

Preservado porque:
- `Discover` exige `deps` $\subseteq V_t$ (precondition 2)
- Nenhum operador remove nós ou arestas de $G_t$
- `Verify` cria $v_{ver}$ novo e aresta $(v, v_{ver})$ onde $v \in V_t$

---

### 4.5 Invariante de Exclusividade de Agente

> **Em qualquer round $t$, para cada Worker $w \in \mathcal{W}$, existe no máximo um nó $v$ com $\text{agent}(v) = w$ e $\text{status}(v) \in \{\texttt{assigned}, \texttt{in\_progress}\}$.**

**Justificativa:** Um Worker só pode estar trabalhando em uma task por vez. O dispatch garante que Workers ociosos recebem no máximo uma task do frontier por round.

---

## 5. Protocolo de Claim Duplo (Race Condition)

### 5.1 Cenário

Dois (ou mais) Workers emitem `<claim_task id="v" />` para o **mesmo** nó $v \in F_t$ no **mesmo round** $t$.

### 5.2 Resolução: FIFO — Primeiro a Chegar, Primeiro a Vencer

O orchestrator processa os Workers **sequencialmente** dentro do round (ordem de iteração sobre $\mathcal{W}$):

1. **Worker A** emite `Claim(v)`: orchestrator verifica preconditions — $v \in F_t$ e $\text{agent}(v) \in \{\bot, w_A\}$ — ambas verdadeiras. Aplica `Claim(v)`: $\lambda_t(v) \leftarrow (w_A, \texttt{in\_progress})$. **Worker A vence.**

2. **Worker B** emite `Claim(v)` em seguida: orchestrator verifica preconditions — $v \in F_t$? **NÃO** (status agora é `in_progress`, não `pending`). Precondition falha. Claim é **rejeitado**.

3. **Worker B** recebe mensagem de erro: `"Task v is already claimed by another worker"` e deve **re-poll** o frontier ($F_t$ ou $F_{t+1}$) por outra task disponível.

### 5.3 Propriedades

| Propriedade | Valor |
|---|---|
| **Política** | FIFO (First-In-First-Out) por ordem de processamento |
| **Determinismo** | Sim — ordem de Workers é fixa dentro do round |
| **Starvation** | Não — Workers que perdem Claim podem Claim outras tasks de $F_t$ ou aguardar próximo round |
| **Sem deadlock** | Workers perdedores são notificados imediatamente e podem agir |
| **Sem duas atribuições** | Garantido: após primeiro Claim bem-sucedido, precondition $v \in F_t$ falha para todos os subsequentes |

### 5.4 Exemplo

```
Round t:
  F_t = {task-4, task-7}
  Workers: Dev1, Dev2, Dev3

  Dev1 emite: <claim_task id="task-4" />     → SUCESSO (task-4 → in_progress, agent=Dev1)
  Dev2 emite: <claim_task id="task-4" />     → FALHA (já claimed)
  Dev2 emite: <claim_task id="task-7" />     → SUCESSO (task-7 → in_progress, agent=Dev2)
  Dev3 emite: <claim_task id="task-7" />     → FALHA (já claimed)
  Dev3: sem ação (ocioso este round)
```

---

## 6. Heartbeat Monitoring (Straggler Detection)

### 6.1 Definição

**Heartbeat** é o mecanismo de monitoramento de liveness que detecta Workers que estão travados (stalled) e notifica o Lead para intervenção.

### 6.2 Parâmetro $H$ (Heartbeat Threshold)

- **Default:** $H = 4$ rounds
- **Configurável via:** `heartbeat-threshold` no frontmatter do `tasks.md`
- **Semântica:** Se um Worker atribuído (status `assigned` ou `in_progress`) não emite **nenhuma ação** por $H$ rounds consecutivos, ele é classificado como **straggler**.

### 6.3 Algoritmo (por Round)

```
Para cada round t:
  1. Para cada Worker w ∈ W com task v atribuída (status ∈ {assigned, in_progress}):
     a. Incrementa contador de inatividade de w
     b. Se w emitiu ação neste round → reseta contador para 0
     c. Se contador ≥ H:
        - Flag w como STRAGGLER
        - Notifica Lead ℓ: "Worker w has been inactive on task v for H rounds"
        - Lead pode emitir <release_task id="v" /> para liberar a task
  2. Lead age sobre notificações de straggler
```

### 6.4 Ações do Lead ao Detectar Straggler

1. **Release:** `<release_task id="v" />` — devolve task ao estado `pending`
2. **Reassign:** `<assign_task id="v" to="DevY" />` — atribui a outro Worker (ou mesmo Worker com instruções mais claras)
3. **Broadcast:** Explicar o que o novo Worker deve fazer diferente

### 6.5 Propriedades do Heartbeat

| Propriedade | Descrição |
|---|---|
| **Unidade** | Rounds (não wall-clock time) — determinístico e reproduzível |
| **Gatilho** | $H$ rounds consecutivos sem ação do Worker |
| **Reset** | Qualquer ação do Worker (Claim, Complete, Discover) reseta o contador |
| **Escopo** | Apenas Workers com task atribuída (`assigned` ou `in_progress`) |
| **Lead** | Também monitorado: se Lead fica $H$ rounds sem ação, é reengajado |

### 6.6 Evidência do Paper

- $H = 4$ usado em todos os experimentos
- Release invocado em **36% dos trials**
- Redução de **2.3×** no p95 de tempo de conclusão (130s LATTE vs 294s static)
- Tempo médio de conclusão: 39.2s (LATTE) vs 75.6s (static), $p < 0.01$

---

## 7. Protocolo de Execução (Algorithm A4.5)

### 7.1 Visão Geral

```
Algoritmo: LATTE Execution
Entrada:  task description τ, agents A = {ℓ} ∪ W, max rounds T, heartbeat threshold H
Saída:    coordination graph final G_T

Fase 0: Planning
  G_0 ← ℓ.Discover(τ)     // Lead inicializa coordination graph

Fase 1: Execution
  for t = 1 to T do
    // 1. Heartbeat monitoring
    Flag para ℓ qualquer w ∈ W sem ações por H rounds consecutivos

    // 2. Frontier identification
    F_t ← {v ∈ G_t : status(v) = pending ∧ ∀(u,v) ∈ E_t, status(u) = done}

    // 3. Agent dispatching
    Re-engaja Workers ocupados com novo contexto desde último round
    Atribui Workers ociosos a tasks em F_t (máximo 1 Worker por task)
    Invoca ℓ se G_t mudou, heartbeat foi flagged, ou ℓ ocioso por H rounds

    // 4. Parallel execution
    Todos os agentes selecionados agem em paralelo:
      ℓ recebe grafo completo G_t
      Workers recebem task atribuída ou F_t
      Cada agente emite ações ⊆ {Discover, Claim, Complete}
    G_t ← Apply(G_{t-1}, todas as ações emitidas)

    // 5. Termination check
    if ∀v ∈ G_t : status(v) = done then
      return G_t
    end if
  end for

  return G_T
```

### 7.2 Observações

- **Max rounds ($T$):** 40 rounds (configurável via `max-rounds` no frontmatter)
- **Paralelismo máximo:** $\min(|F_t|, |\mathcal{W}|)$ Workers despachados por round
- **Context scoping:** Workers recebem apenas sua task + outputs das dependências diretas; Lead recebe $G_t$ + mensagens de agentes, sem traces completos
- **Planning (Fase 0):** Lead tem até 5 turns para produzir $G_0$ via `Discover`
- **Concurrency intra-round:** Lead roda primeiro, depois Workers em paralelo; resultados coletados antes de avançar round

---

## 8. Sumário de Permissões e Responsabilidades

### Lead ($\ell$) — Responsabilidades

| Responsabilidade | Descrição |
|---|---|
| Inicializar $G_0$ | Planejamento inicial (Fase 0, até 5 turns) |
| Assign | Atribuir tasks pending a Workers |
| Release | Liberar tasks de stragglers |
| Close | Forçar done em tasks concluídas mas não sinalizadas |
| Verify | Spawnar verificação para nós de alto risco |
| Discover | Adicionar novas tasks ao grafo |
| Avaliar propostas | Avaliar e merge de `Discover` propostos por Workers |
| Heartbeat response | Agir sobre notificações de straggler |
| Monitoramento | Visão global de $G_t$ |

### Workers ($w$) — Responsabilidades

| Responsabilidade | Descrição |
|---|---|
| Claim | Self-scheduling: pegar tasks do frontier |
| Complete | Sinalizar conclusão com sucesso |
| Discover | Propor novas tasks descobertas durante execução |
| Executar | Implementar código, rodar testes, verificar qualidade |
| Comunicar | Reportar bloqueios ou necessidade de esclarecimento ao Lead |

### Fronteiras Claras (NÃO Permitido)

- ❌ Workers NÃO podem `Assign`, `Release`, `Close`, `Verify`
- ❌ Workers NÃO têm visão global do grafo (apenas sua task + deps diretas)
- ❌ Lead NÃO edita arquivos diretamente (foco em coordenação)
- ❌ Lead NÃO pode `Claim` ou `Complete` tasks de Workers

---

## 9. Referências

1. Mieczkowski, E., Ku, A., Eisape, T., Arumugam, D., Matters, J., Collins, K. M., Sucholutsky, I., & Griffiths, T. L. (2026). *Improving the Efficiency of Language Agent Teams with Adaptive Task Graphs*. arXiv:2605.06320.
2. Appendix A3 — Graph Mutation Operators (definições formais dos 7 operadores)
3. Appendix A4.5 — LATTE Execution Protocol (algoritmo completo de rounds)
4. Appendix A4.4 — Heartbeat monitoring ($H=4$) e Claim tie-breaking (FIFO)
5. Seção 3.2 — Graph mutation operators (visão geral e tabela)
6. Seção 3.4 — Coordination properties (D1-D4)
