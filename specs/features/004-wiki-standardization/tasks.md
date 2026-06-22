---
feature_id: "004"
tasks_for: "Wiki Standardization — Template, Validação & Chunking"
spec: "specs/features/004-wiki-standardization/spec.md"
plan: "specs/features/004-wiki-standardization/plan.md"
created: "2026-06-21"
author: phm-aguiar
graph-operators: enable
---

# Tasks — Wiki Standardization

## Fase 1: Template Canônico

### T001 — Criar template.md com 3 tiers de campos
- **Papel:** Dev
- **Dependências:** Nenhuma
- **Paralelizável:** false
- **Arquivos:**
  - `wiki/_meta/template.md` (novo)
- **Descrição:** Criar documento definindo campos obrigatórios (`title`, `tags`, `created`), por diretório (`category`, `summary`, `lifecycle`, `updated`), e opcionais. Incluir exemplos YAML para concepts/, references/, skills/, journal/, entities/, synthesis/. Template deve ser auto-documentado — cada campo com descrição, tipo e exemplo.

### T002 — Criar chunking.yaml com thresholds
- **Papel:** Dev
- **Dependências:** Nenhuma
- **Paralelizável:** true (arquivo disjunto de T001)
- **Arquivos:**
  - `wiki/_meta/chunking.yaml` (novo)
- **Descrição:** Arquivo YAML com thresholds de chunking: `max_lines: 500`, `max_bytes: 25600` (25KB), `split_on: "##"` (headings nível 2). Incluir `exclude_dirs: [_raw, _staging, _archives]` e `min_subpage_lines: 50` (não splitar seção muito curta).

## Fase 2: Correção dos 20 Problemáticos

### T003 — Script fix_frontmatter.py (YAML escaping)
- **Papel:** Dev
- **Dependências:** T001 (precisa do template.md pra saber campos esperados)
- **Paralelizável:** false
- **Arquivos:**
  - `.hermes/skills/wiki/wiki-lint/fix_frontmatter.py` (novo)
- **Descrição:** Script Python que: (a) detecta YAML quebrado por `:` não escapado em valores string — regex `^\w+:\s*.+:.+` sem aspas, (b) envolve o valor em aspas duplas, (c) modo `--dry-run` mostra diff, (d) modo normal aplica. Deve preservar todo conteúdo fora do frontmatter intacto (só mexe no bloco YAML entre `---`). Usar `ruamel.yaml` ou `pyyaml` com round-trip.

### T004 — Script fix_frontmatter.py (title ausente)
- **Papel:** Dev
- **Dependências:** T003 (mesmo arquivo, extender)
- **Paralelizável:** false
- **Arquivos:**
  - `.hermes/skills/wiki/wiki-lint/fix_frontmatter.py` (estender)
- **Descrição:** Adicionar lógica no `fix_frontmatter.py`: detecta páginas sem campo `title` no frontmatter. Deriva title de: (1) primeiro H1 (`# Título`) no corpo, (2) fallback: nome do arquivo sem extensão com hífens → espaços + title case. Insere `title: "..."` no frontmatter preservando ordem alfabética dos campos.

### T005 — Executar correção (dry-run + apply)
- **Papel:** QA
- **Dependências:** T003, T004
- **Paralelizável:** false
- **Arquivos:**
  - 20 arquivos problemáticos em `wiki/references/` (modificados)
- **Descrição:** Rodar `fix_frontmatter.py --dry-run` → inspecionar diffs → `fix_frontmatter.py` (apply). Verificar que 20/20 arquivos agora têm frontmatter válido (YAML parse OK + title presente). Verificar que 363 arquivos já válidos não foram alterados (zero diff).

### T006 — Reindex wiki pós-correção
- **Papel:** DevOps
- **Dependências:** T005
- **Paralelizável:** false
- **Arquivos:**
  - `~/.hermes/wiki_index.db` (atualizado)
- **Descrição:** Rodar `python3 .hermes/skills/wiki/experiential_memory/cli_index.py --full`. Verificar contagem de chunks (deve ser ≥ anterior, já que frontmatter corrigido pode expor mais metadados indexáveis).

## Fase 3: Validação Contínua

### T007 — Skill validate_template.py
- **Papel:** Dev
- **Dependências:** T001 (template.md define o que validar)
- **Paralelizável:** false
- **Arquivos:**
  - `.hermes/skills/wiki/wiki-lint/validate_template.py` (novo)
  - `.hermes/skills/wiki/wiki-lint/SKILL.md` (patch — documentar novo submódulo)
- **Descrição:** Script Python que audita todas as páginas contra o template.md: (a) campos obrigatórios presentes, (b) campos por diretório presentes, (c) YAML parse válido (sem `:` não escapado), (d) `tags` é lista não vazia, (e) `created` é data ISO 8601. Saída: relatório com contagem PASS/FAIL/WARN por página + sumário. Exit code 0 se tudo PASS, 1 se algum FAIL.

### T008 — Integrar validate_template ao wiki-lint
- **Papel:** Dev
- **Dependências:** T007
- **Paralelizável:** false (mesmo skill)
- **Arquivos:**
  - `.hermes/skills/wiki/wiki-lint/SKILL.md` (patch)
  - `.hermes/skills/wiki/wiki-lint/__main__.py` ou entry point (patch)
- **Descrição:** Adicionar flag `--validate-template` ao `wiki-lint`. Modo `--strict` inclui validação de template + chunking candidates. Atualizar SKILL.md com novos modos e exemplos.

### T009 — Smoke test da validação
- **Papel:** QA
- **Dependências:** T008, T005 (precisa dos arquivos corrigidos)
- **Paralelizável:** false
- **Arquivos:**
  - `.hermes/skills/wiki/wiki-lint/tests/test_validate_template.py` (novo)
- **Descrição:** Criar teste que: (a) cria página sem title → FAIL, (b) cria página com YAML quebrado → FAIL, (c) página válida → PASS, (d) verifica contagem de erros (20 corrigidos → 0 erros residuais). Usar tmpdir para não poluir wiki real.

## Fase 4: Chunking Inteligente

### T010 — Script chunk_split.py
- **Papel:** Dev
- **Dependências:** T002 (chunking.yaml define thresholds)
- **Paralelizável:** false
- **Arquivos:**
  - `.hermes/skills/wiki/wiki-lint/chunk_split.py` (novo)
- **Descrição:** Script Python que: (a) lê thresholds de `wiki/_meta/chunking.yaml`, (b) detecta arquivos > `max_lines` ou > `max_bytes`, (c) split por headings `##` preservando frontmatter original + adicionando `part_of: "caminho/arquivo-original.md"` em cada sub-página, (d) cria `_index.md` com lista de sub-páginas + descrição de 1 linha (extraída do heading), (e) modo `--dry-run`. Sub-páginas seguem naming: `<original>-<slug-da-secao>.md`.

### T011 — Adicionar chunk candidates ao validate_template
- **Papel:** Dev
- **Dependências:** T010, T007 (ambas precisam estar prontas)
- **Paralelizável:** false
- **Arquivos:**
  - `.hermes/skills/wiki/wiki-lint/validate_template.py` (patch)
- **Descrição:** Adicionar check ao `validate_template.py`: se arquivo > thresholds do `chunking.yaml`, emitir WARN com recomendação de split. Não fazer split automático — chunking é destrutivo e requer revisão humana.

### T012 — Split do Linters.md (Piloto)
- **Papel:** Dev
- **Dependências:** T010
- **Paralelizável:** false
- **Arquivos:**
  - `wiki/tools/golangci-lint/Linters.md` (splitado)
  - `wiki/tools/golangci-lint/linters/*.md` (~40 sub-páginas, novas)
  - `wiki/tools/golangci-lint/linters/_index.md` (novo)
- **Descrição:** Rodar `chunk_split.py` no `Linters.md` (164KB, 4313 linhas). Cada linter vira uma sub-página. Verificar: (a) índice lista todos os linters, (b) wikilinks do índice apontam para sub-páginas existentes, (c) busca híbrida (Feature 003) para "bodyclose linter" retorna a sub-página correta.

### T013 — Reindex pós-chunking
- **Papel:** DevOps
- **Dependências:** T012
- **Paralelizável:** false
- **Arquivos:**
  - `~/.hermes/wiki_index.db` (atualizado)
- **Descrição:** Rodar `cli_index.py --full` pós-split. Verificar: (a) sub-páginas indexadas, (b) `_index.md` indexado como página normal, (c) busca híbrida com query "gosec SARIF format" retorna sub-página do linter `gosec` em vez do documento monolítico.

## Fase 5: Finalização

### T014 — Atualizar llms.txt
- **Papel:** Dev
- **Dependências:** T005, T012 (correções + chunking concluídos)
- **Paralelizável:** false
- **Arquivos:**
  - `llms.txt` (patch)
- **Descrição:** Atualizar referências no `llms.txt`: adicionar `wiki/_meta/template.md` e `wiki/_meta/chunking.yaml`. Se `Linters.md` foi splitado, atualizar path ou adicionar entrada para `linters/_index.md`.

### T015 — Atualizar AGENTS.md
- **Papel:** Dev
- **Dependências:** T008 (wiki-lint com --validate-template)
- **Paralelizável:** true (arquivo disjunto de T014)
- **Arquivos:**
  - `AGENTS.md` (patch)
- **Descrição:** Adicionar menção ao `wiki-validate-template` na seção de skills. Atualizar tabela de gatilhos wiki se necessário.

### T016 — Smoke test fim a fim
- **Papel:** QA
- **Dependências:** T009, T013, T014, T015
- **Paralelizável:** false
- **Arquivos:**
  - `.hermes/skills/wiki/wiki-lint/tests/test_smoke_004.py` (novo)
- **Descrição:** Smoke test integrado: (a) `wiki-lint --validate-template` retorna 0 erros, (b) `cli_query.py --hybrid "gosec configuration"` retorna sub-página do linter no top-3, (c) 374 páginas têm frontmatter válido, (d) `template.md` e `chunking.yaml` existem.

---

## Coordination Graph (G₀)

```
T001 ──→ T003 ──→ T004 ──→ T005 ──→ T006
  │                                    │
  │                                    ├──→ T014
  │                                    │
T002 ──→ T010 ──→ T011                │
  │         │       │                  │
  │         │       └──→ T012 ──→ T013 ─┤
  │         │                           │
  │         └──→ T007 ──→ T008 ──→ T009 ─┤
  │                                     │
  └──→ T015 ────────────────────────────┤
                                         │
                                    T016 (smoke test)
```

## Paralelismo

| Batch | Tasks | Razão |
|-------|-------|-------|
| Batch 1 (paralelo) | T001 ∥ T002 | Arquivos disjuntos (template.md vs chunking.yaml) |
| Batch 2 (sequencial) | T003 | Depende de T001 |
| Batch 3 (sequencial) | T004 | Estende T003 (mesmo arquivo) |
| Batch 4 (sequencial) | T005 | Depende de T003+T004 |
| Batch 5 (sequencial) | T006 | Depende de T005 |
| Batch 6 (paralelo) | T007 ∥ T010 | Arquivos disjuntos (validate_template.py vs chunk_split.py) |
| Batch 7 (sequencial) | T008 | Depende de T007 |
| Batch 8 (sequencial) | T009 | Depende de T008+T005 |
| Batch 9 (sequencial) | T011 | Depende de T010+T007 |
| Batch 10 (sequencial) | T012 | Depende de T010 |
| Batch 11 (sequencial) | T013 | Depende de T012 |
| Batch 12 (paralelo) | T014 ∥ T015 | Arquivos disjuntos (llms.txt vs AGENTS.md) |
| Batch 13 (sequencial) | T016 | Depende de todos |

**Resumo:** 16 tasks, 13 batches. ~19% paralelizável (T001∥T002, T007∥T010, T014∥T015).
