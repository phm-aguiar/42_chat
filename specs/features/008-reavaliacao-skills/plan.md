# Plano Arquitetural: Reavaliação e Consolidação de Skills

## 1. Metadados do Plano

- **Stack Tecnológico:** Python (skills runtime), YAML (frontmatter), Markdown (docs), Shell (scripts auxiliares)
- **Feature Fonte:** `specs/features/008-reavaliacao-skills/spec.md`
- **Escopo:** Consolidar ~130 skills fragmentadas em ≤15 toolkits coesos por domínio, reduzindo a carga de prompt dos subagentes e eliminando redundâncias. Skills de formato/referência viram páginas no vault, não entry-points ativos.

## 2. Design de Contratos e Fronteiras

### 2.1 Contrato de Toolkit

Todo toolkit consolidado segue este contrato:

```yaml
# SKILL.md frontmatter
name: <toolkit-name>
description: >-
  Toolkit consolidado do domínio <domain>. Modos: <mode1>, <mode2>, ...
version: 1.0.0
metadata:
  hermes:
    category: <domain>
    absorbed_from: [skill-a, skill-b, ...]  # skills que foram absorvidas
    modes: [mode1, mode2, mode3]            # modos disponíveis
```

**Corpo do SKILL.md:**
```markdown
# <Toolkit Name>

> Toolkit consolidado. Carregue UMA vez. Use `--mode <name>` para operações específicas.

## Modo: <mode1>
### Gatilho
...quando usar este modo...
### Fluxo
...passos...
### Pitfalls
...armadilhas conhecidas...

## Modo: <mode2>
...
```

### 2.2 Contrato de Transição

Skills absorvidas seguem este protocolo:

1. `skill_manage(action='delete', name='<old-skill>', absorbed_into='<toolkit>')`
2. Symlink antigo removido de `~/.hermes/skills/`
3. `AGENTS.md` dos subagentes atualizado para referenciar o toolkit
4. Página wiki da skill antiga marcada como `superseded_by: "[[skills/<toolkit>]]"`

**Período de transição:** 1 ciclo (até o próximo `wiki-lint --consolidate`). Após isso, symlinks e páginas órfãs são removidos.

### 2.3 Fronteiras

- **Skills de plugin Hermes:** Fora do escopo. Não versionadas no repo, não são consolidadas.
- **Skills que são dependências internas:** Se uma skill de formato (ex: `obsidian-cli`) for usada programaticamente por outra skill, ela NÃO vira referência — permanece como dependência interna, mas sem entry-point direto.
- **Toolkits não se referenciam circularmente:** Um toolkit pode referenciar outro como `related_skills`, mas nunca como dependência hard.

## 3. Decisões Arquiteturais e Justificativas (ADR)

### ADR-1: Toolkits com modos ao invés de skills atômicas

- **Decisão:** Consolidar skills de mesmo domínio em toolkits com modos internos (ex: `brain --mode ingest` ao invés de `wiki-ingest` separado).
- **Justificativa:** A granularidade atual (130 skills, muitas com sobreposição de domínio) força subagentes a carregar 5-10 skills para tarefas correlatas. Cada skill carregada adiciona ~2-5KB ao prompt. Um toolkit de ~15KB com 5-7 modos substitui 5-10 skills de ~3KB cada, reduzindo o prompt total em 40-60%.
- **Alternativa Rejeitada:** Manter skills atômicas mas com "meta-skill" que as referencia. Rejeitada porque ainda exige múltiplos `skill_view()` — a economia de prompt só acontece se o conteúdo é carregado UMA vez.

### ADR-2: Skills de formato/referência viram páginas no vault

- **Decisão:** Skills que descrevem formatos (OFM, JSON Canvas), ferramentas (obsidian-cli, defuddle) ou operações puramente sintáticas (doc-extract, doc-generate-toc) viram páginas de referência no vault (`references/ofm-spec.md`, `references/doc-tools.md`), carregadas sob demanda via `brain-query`, não como skills ativas no prompt.
- **Justificativa:** Essas skills não contêm workflows decisionais — são documentação de referência. Carregá-las como skills ativas polui o prompt sem benefício. Quando um subagente precisa saber sintaxe OFM, ele consulta o vault, não carrega uma skill.
- **Alternativa Rejeitada:** Manter como skills ativas mas marcadas como `tier: peripheral`. Rejeitada porque o problema não é tier, é categoria — elas não são skills (procedural), são docs (declarativo).

### ADR-3: Transição com aliases e período de 1 ciclo

- **Decisão:** Skills absorvidas mantêm página wiki com `superseded_by` e têm `absorbed_into` no `skill_manage delete`. Symlinks antigos são removidos imediatamente (subagentes spawnam com contexto limpo), mas referências em docs são atualizadas gradualmente.
- **Justificativa:** Subagentes spawnam com `agent-run` que compila contexto limpo — não há "cache" de skill antiga. Mas agentes que referenciam skills por nome em `context.yaml` (ex: `agent-qa` referencia `gherkin-scenarios` como string) precisam ser atualizados atomicamente com a migração.
- **Alternativa Rejeitada:** Manter symlinks fantasmas apontando para toolkits. Rejeitada porque o Hermes não suporta aliases de skill — causaria confusão sobre qual nome usar.

### ADR-4: Tamanho máximo de toolkit = 15KB

- **Decisão:** Nenhum SKILL.md de toolkit pode exceder ~15KB (aproximadamente 4000 tokens). Se um domínio for grande demais, split em 2 toolkits complementares (ex: `brain-core` + `brain-weave`).
- **Justificativa:** O benefício da consolidação (carregar 1 skill ao invés de N) é anulado se o toolkit for tão grande quanto a soma das skills originais. 15KB é o ponto de equilíbrio onde 5-7 skills de ~3KB são substituídas por 1 toolkit de ~12-15KB.
- **Alternativa Rejeitada:** Limite rígido de 10KB. Rejeitada porque forçaria splits artificiais em domínios naturalmente coesos (ex: 8 skills de QA formam um toolkit natural de ~12KB).

### ADR-5: Consolidação guiada por uso real, não por categorização teórica

- **Decisão:** Antes de consolidar, auditar quais skills são efetivamente carregadas por cada subagente (via `context.yaml` e `AGENTS.md`). Skills que existem mas nunca foram carregadas por nenhum subagente são candidatas a arquivamento, não consolidação.
- **Justificativa:** Categorização teórica (ex: "todas as skills de DevOps") pode juntar skills que nunca são usadas juntas. A consolidação deve refletir padrões de uso real: se `agent-dev` sempre carrega `go-implement` + `build-check` + `react-implement` juntos, essas viram um toolkit `dev-toolkit`.
- **Alternativa Rejeitada:** Consolidar puramente por taxonomia de diretórios. Rejeitada porque a taxonomia atual é organizacional, não funcional — `docker-dev-environment` e `linux-audio` estão em `devops/` mas nunca são usados juntos.

## 4. Auditoria de Constituição

| Regra | Status | Como o plano respeita |
|---|---|---|
| Portão 1: Validação SDD obrigatória | ✅ | Feature segue pipeline spec→plan→tasks. `sdd-validate` rodará ao final |
| Portão 2: Aprovação humana | ✅ | Spec aguarda `Aprovado: true` antes de implementar |
| Portão 3: Smoke test | ✅ | Cada toolkit terá smoke test: `skill_view(name=...)` carrega sem erro |
| Portão 4: Vault Obsidian fiel | ✅ | `wiki/` atualizado pós-consolidação. `wiki-lint` passa sem broken links |
| Restrição 1: Agentes versionados | N/A | Não altera agentes, apenas referências em `context.yaml` |
| Restrição 2: Skills versionadas | ✅ | Toolkits versionados em `.hermes/skills/` com symlinks |
| Restrição 3: Pipeline imutável | ✅ | Feature segue spec→plan→tasks→orchestrator |
| Restrição 4: Isolamento de agentes | ✅ | Subagentes continuam leaf. Toolkits são injetados como skills normais |
| Regra 1: Framework primeiro | ✅ | Feature melhora o framework (skills), não o app |
| Regra 3: Knowledge management first-class | ✅ | Consolidação inclui atualização completa do vault |
| Anti-padrão 4: Skills fora do padrão | ✅ | Toolkits seguem formato Hermes (SKILL.md com frontmatter YAML) |
| Anti-padrão 6: Vault desatualizado | ✅ | Vault atualizado como parte da feature |

## 5. Riscos e Mitigações

| Risco | Prob. | Impacto | Mitigação |
|---|---|---|---|
| Toolkit fica grande demais (>15KB) e perde benefício | Média | Médio | ADR-4: split em 2 toolkits complementares |
| Subagente não encontra skill após renomeação | Baixa | Alto | ADR-3: atualização atômica de `context.yaml` + `AGENTS.md` |
| Skill absorvida ainda referenciada em docs externos | Média | Baixo | Páginas wiki marcadas com `superseded_by`. Links quebrados detectados pelo `wiki-lint` |
| Resistência à mudança: usuário acostumado com nomes antigos | Média | Médio | Período de transição com aliases documentados. `brain-query` sabe mapear nome antigo → toolkit |
