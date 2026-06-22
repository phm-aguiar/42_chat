# AGENTS.md — 42_chat

## Onboarding (primeira ação ao entrar no repo)

1. Leia `.github/memory/constitution.md` — portões de qualidade, restrições, anti-padrões
2. Leia `.github/memory/tech.md` — stack homologada (Hermes Agent, DeepSeek V4 Pro, Honcho, Obsidian, Go, Python)
3. Leia `llms.txt` — entry point com paths de todos os specs, wiki, papers e referências
4. Leia `wiki/index.md` — inventário completo do vault (365+ páginas, 3.221 chunks)

## Fluxo SDD

Toda feature segue: brainstorm → spec → plan → tasks → orchestrator.
Artefatos em `specs/features/<NNN>-<slug>/`. Pipeline imutável — pular etapas é proibido.

- `spec.md`: **HARD-GATE:** `Aprovado: true` antes de implementar
- `plan.md`: ADRs, contratos, auditoria de constituição
- `tasks.md`: DAG atômico. Se `graph-operators: enabled` → LATTE (coordination graph dinâmico, 7 operadores)
- Subagentes são leaf (profundidade máxima = 1)
- Skill mestre: `skill_view(name='sdd')`

## Manutenção da Wiki

A wiki é o cérebro do framework. Mantenha-a saudável com este fluxo:

### Antes de trabalhar (setup único ou após grandes mudanças)
```bash
# 1. Indexar a wiki (SQLite + embeddings)
python3 .hermes/skills/wiki/experiential_memory/cli_index.py --full

# 2. Sincronizar scores do índice → frontmatter (campo rag_score)
python3 .hermes/skills/wiki/lint/sync_scores.py
```

### Durante o trabalho (a cada sessão ou pré-commit)
```bash
# Validar frontmatter contra template canônico
python3 .hermes/skills/wiki/lint/validate_template.py

# Corrigir YAML quebrado e campos ausentes
python3 .hermes/skills/wiki/lint/fix_frontmatter.py --dry-run  # preview
python3 .hermes/skills/wiki/lint/fix_frontmatter.py             # aplicar

# Verificar candidatos a chunking (>500 linhas ou >25KB)
python3 .hermes/skills/wiki/lint/validate_template.py --strict
```

### Quando a wiki crescer (manutenção periódica)
```bash
# Destilar chunks redundantes (>30 acumulados)
python3 .hermes/skills/wiki/experiential_memory/cli_distill.py

# Splitar arquivos grandes (>500 linhas) em sub-páginas
python3 .hermes/skills/wiki/lint/chunk_split.py --dry-run       # preview
python3 .hermes/skills/wiki/lint/chunk_split.py                  # aplicar

# Reindexar pós-split
python3 .hermes/skills/wiki/experiential_memory/cli_index.py --full
python3 .hermes/skills/wiki/lint/sync_scores.py
```

### Templates e configuração
- `wiki/_meta/template.md` — template canônico de frontmatter (3 tiers: obrigatório/diretório/opcional)
- `wiki/_meta/chunking.yaml` — thresholds de chunking (500 linhas / 25KB) e overrides por diretório

## Git

### Antes de todo commit
```bash
# Validação estrutural SDD
# (sdd-validate é skill LLM-driven, não script)

# Validação da wiki
python3 .hermes/skills/wiki/lint/validate_template.py

# Testes do framework (84 testes)
PYTHONPATH=.hermes/skills/sdd python3 -m pytest .hermes/skills/sdd/latte_coordination/tests/ -q
```

### O que NUNCA commitar
- `.env`, credenciais, tokens, secrets
- `~/.hermes/wiki_index.db` (cache local, reconstruível)
- Arquivos `.bak` de chunking (adicione `*.bak` ao `.gitignore`)

### O que SEMPRE commitar
- `specs/features/*/` (spec, plan, tasks)
- `wiki/` (todo o vault — é código, não documentação)
- `.hermes/skills/` (skills versionadas)
- `.github/memory/` (constitution, tech)
- `AGENTS.md`, `llms.txt`

### Convenção de commits
- `feat:` nova feature ou capacidade
- `fix:` correção de bug
- `chore:` manutenção (wiki, skills, config)
- `docs:` documentação pura (spec, plan, ADRs)

## Skills locais

```bash
# Pipeline SDD
skill_view(name='sdd')

# Wiki
python3 .hermes/skills/wiki/lint/validate_template.py
python3 .hermes/skills/wiki/lint/fix_frontmatter.py --dry-run
python3 .hermes/skills/wiki/lint/sync_scores.py

# Testes
PYTHONPATH=.hermes/skills/sdd python3 -m pytest .hermes/skills/sdd/latte_coordination/tests/ -q
```
