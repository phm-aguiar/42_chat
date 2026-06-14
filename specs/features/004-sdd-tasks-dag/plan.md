# Plano Arquitetural: Tasks com DAG (sdd-generate-tasks upgrade)

## 1. Metadados do Plano

- **Stack Tecnológico:** Hermes Agent skill (Markdown + YAML frontmatter). Zero dependências de runtime — pura skill procedural.
- **Feature Fonte:** `specs/features/004-sdd-tasks-dag/spec.md`
- **Escopo:** Upgrade do `sdd-generate-tasks` para gerar `tasks.md` com formato DAG (fases, dependências, paralelismo, isolamento de arquivos). Sem mudança de arquitetura — é um patch na skill existente.

## 2. Design de Contratos e Fronteiras

- **Contrato:** Nenhum contrato formal neste estágio. O formato DAG do `tasks.md` é o contrato implícito com o `agent-orchestrator` (feature 005).
- **Convenção:**
  - Tasks numeradas `T001`, `T002`, ... sequencialmente
  - Metadados por task: `Papel`, `Dependências`, `Paralelizável`, `Arquivos`
  - Fases nomeadas (Fase 1: Fundação, Fase 2: Implementação, etc.)
  - Formato Markdown parseável, sem dependência de parser externo

### Estrutura do DAG no tasks.md

```markdown
## Fase N: Nome da Fase
- [ ] **Tnnn:** Descrição da task
  - **Papel:** Dev | QA
  - **Dependências:** Txxx, Tyyy | Nenhuma
  - **Paralelizável:** true | false
  - **Arquivos:** `path/to/file.go`, `path/to/other.go`
```

## 3. Decisões Arquiteturais e Justificativas (ADR)

### ADR-001: Validação de DAG inline na skill (sem script externo)

- **Decisão:** Lógica de validação de ciclos, dependências quebradas e tasks órfãs implementada como instruções procedurais na própria SKILL.md, sem script Python/Go externo.
- **Justificativa:** A validação de DAG é um grafo pequeno (tipicamente < 30 tasks). A complexidade é O(N+E) para detecção de ciclos (DFS) e O(N) para órfãs/dependências quebradas — trivial para um LLM executar passo a passo. Um script externo adicionaria dependência de runtime e quebraria a constraint de "skill pura".
- **Alternativa Rejeitada:** Script Python standalone. Rejeitado por adicionar runtime dependency — a skill deve funcionar apenas com interpretação do LLM + ferramentas padrão (leitura/escrita de arquivos).

### ADR-002: Isolamento de arquivos como regra primária de paralelismo

- **Decisão:** Duas tasks da mesma fase são marcadas como `Paralelizável: true` se e somente se seus conjuntos de `Arquivos` forem disjuntos. Esta é a regra ÚNICA de detecção de paralelismo — não depende de heurísticas de papel ou complexidade.
- **Justificativa:** Conflito de escrita em arquivo é a única causa real de falha em paralelismo de código. Papéis diferentes (Dev vs QA) naturalmente tocam arquivos diferentes (`.go` vs `.feature`), então a regra de disjunção captura o paralelismo real sem falsos positivos.
- **Alternativa Rejeitada:** Heurística por papel (Dev nunca paralelo com Dev). Rejeitada por ser conservadora demais — dois Devs podem trabalhar em arquivos diferentes da mesma fase.

### ADR-003: Interação fase por fase via clarify()

- **Decisão:** O usuário aprova/ajusta cada fase antes da skill avançar para a próxima. Uma chamada de `clarify()` por fase.
- **Justificativa:** A decomposição de tasks é crítica demais para ser fully automated. Uma task mal dimensionada ou com dependência errada gera retrabalho em toda a execução. O custo de 3-5 interações é insignificante comparado ao risco de DAG incorreto.
- **Alternativa Rejeitada:** Geração fully automated sem interação. Rejeitada — spec 004 lista isso como "Alto risco de tasks mal dimensionadas".

### ADR-004: Retrocompatibilidade com formato flat

- **Decisão:** Tasks.md antigos (formato flat, sem metadados) continuam sendo lidos pelo agent-orchestrator, mas tratados como 100% sequenciais (sem paralelismo).
- **Justificativa:** Features 001-003 usam o formato antigo. Não faz sentido migrá-las retroativamente — são features experimentais. O agent-orchestrator detecta ausência de metadados e aplica modo sequencial.
- **Alternativa Rejeitada:** Migrar tasks.md antigos para DAG. Rejeitada — custo desnecessário para features que não serão executadas pelo orchestrator.

## 4. Auditoria de Constituição

- [ ] Constitution.md está vazio — nenhuma regra para auditar.
