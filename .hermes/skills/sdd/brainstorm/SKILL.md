---
name: sdd-brainstorm
description: >
  Use when the user wants to discuss, refine, or brainstorm a new feature idea
  before writing a spec. Conducts an interactive interview using clarify() to
  gather requirements, constraints, and success criteria one question at a time,
  then generates spec.md in the SDD format under specs/features/<id>-<slug>/.
  Trigger keywords: brainstorm, brain storm, discutir ideia, refinar ideia,
  pensar feature, nova feature, nova ideia, discutir feature, entrevista,
  interview, discovery, bora pensar, vamos pensar, como voce faria.
version: 0.3.0
author: phm-aguiar
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [SDD, Brainstorm, Spec, Discovery, Interactive-Interview, Clarify]
    related_skills: [wiki-query, wiki-experiential_memory, sdd-init_repo, sdd-explore_tech, sdd-generate_plan, sdd-generate_tasks, sdd-validate, sdd-refactor_artifact]
    category: sdd
    created: "2026-06-12"
    resources:
      - SKILL.md
      - references/interview-dimensions.md
      - assets/spec-template.md
---

# Brainstorm Interativo → Spec SDD

> Entry point do pipeline SDD. Transforma ideias em `spec.md` via entrevista com `clarify()`.

## Propósito

Conduz entrevista interativa com `clarify()` — uma pergunta por vez, múltipla escolha —
para extrair propósito, escopo, constraints, critérios de sucesso e trade-offs de uma feature.
Gera `spec.md` e transiciona para `sdd-generate_plan`.

**HARD-GATE:** Nunca implemente antes do spec aprovado. Vale pra TODA feature, incluindo as "simples".

## Pré-requisitos

- Repo inicializado com SDD (`sdd-init_repo`): `.github/memory/`, `specs/features/`.
- Ferramenta `clarify` habilitada (default).
- Se `tech.md` ou `constitution.md` estiverem vazios, alerte mas prossiga.

## Fluxo de Execução

9 passos. Use `todo` para trackear.

### Passo 1: Explorar contexto

```bash
read_file(path=".github/memory/tech.md")
read_file(path=".github/memory/constitution.md")
search_files(pattern="*", target="files", path="specs/features/")
```

### Passo 2: Avaliar escopo — decompor se necessário

Se a ideia descreve múltiplos subsistemas independentes, alerte e use `clarify()` para
confirmar decomposição. Cada subsistema vira feature própria com ciclo completo.

### Passo 3: Query experiential memory

Consulte o índice semântico do Wiki Experiential Memory para recuperar
**features similares** já especificadas ou discutidas anteriormente. Este
passo enriquece a entrevista com conhecimento prévio — padrões, edge cases
e trade-offs que surgiram em features parecidas.

```bash
# Carrega o modelo de embeddings e importa search_similar
# O script está em .hermes/skills/wiki/experiential_memory/search.py
python3 -c "
import sys
sys.path.insert(0, '.hermes/skills/wiki/experiential_memory')
from search import search_similar
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
# Usa o tópico da feature como query (extraído da ideia do usuário no Passo 2)
results = search_similar(query_text='<tópico da feature>', model=model, k=3)
for r in results:
    print(f\"[{r['similarity']:.3f}] [{r['source']}] {r['heading']}\")
    print(f\"    {r['content'][:300]}...\")
    print()
"
```

**Query:** Use o resumo do propósito da feature (extraído no Passo 2) como
`query_text`. Se a feature foi decomposta, consulte uma vez para a feature
principal; repita por subsistema se relevante.

**Resultados:** Recupere os **top-3 chunks** mais similares. Cada chunk
contém: `source` (origem), `heading` (título da seção), `content` (texto),
`similarity` (score 0–1), `tags`.

#### Formato dos hints no contexto da entrevista

Injete os chunks recuperados como **hints contextuais** ANTES de iniciar a
entrevista. Apresente-os internamente como bloco de referência:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXPERIENTIAL MEMORY — Features similares recuperadas
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[similarity] source > heading
Resumo: <2-3 frases extraindo o insight relevante do content>

[similarity] source > heading
Resumo: <2-3 frases...>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Como usar os hints durante a entrevista (Passo 4):**
- **Propósito:** Se feature similar resolveu problema análogo, pergunte se
  há sobreposição ou diferenciação necessária.
- **Escopo:** Se feature similar teve escopo X, confirme se a feature atual
  expande, substitui ou coexiste.
- **Edge cases:** Se feature similar encontrou edge case Y, pergunte se o
  mesmo se aplica aqui.
- **Constraints/Trade-offs:** Se feature similar teve constraint Z, alerte
  o usuário e valide se a constraint ainda é válida.
- **Critérios de sucesso:** Se feature similar usou métrica W, sugira como
  baseline ou ponto de partida.

**Fallback:** Se o índice não existir (`wiki_index.db` ausente ou vazio), ou
se `search_similar()` retornar lista vazia, registre `[Experiential memory:
índice vazio ou indisponível]` e prossiga sem hints.

### Passo 4: Entrevista interativa

Carregue as dimensões da entrevista:

```
skill_view(name="sdd-brainstorm", file_path="references/interview-dimensions.md")
```

Cubra cada dimensão com `clarify()` — **uma pergunta por vez**, múltipla escolha quando possível.
Só avance para a próxima dimensão quando a atual estiver clara.

**Loop de reavaliação:** após cada resposta, avalie se já tem insumos para um spec sem
ambiguidades. Se sim, avance. Se não, continue perguntando. Se o usuário disser "confio
em você", preencha com defaults razoáveis e valide no Passo 5.

### Passo 5: Propor 2-3 abordagens

Use `clarify()` para apresentar abordagens com trade-offs e recomendação.

### Passo 6: Gerar spec.md

Carregue o template canônico:

```
skill_view(name="sdd-brainstorm", file_path="assets/spec-template.md")
```

Substitua os placeholders `{{...}}` pelos insumos coletados. Naming: próximo ID
incremental de `specs/features/`, slug curto (max 3 palavras, lowercase, hífens).

```
write_file(path="specs/features/<id>-<slug>/spec.md", content="<spec gerada>")
```

### Passo 7: Spec self-review

Revise o `spec.md`: placeholders? contradições? escopo focado? ambiguidades?
Corrija inline e avance.

### Passo 8: Gate de aprovação

Use `clarify()` para aprovação explícita. Se o usuário pedir ajustes, faça e re-apresente.

### Passo 9: Transição para pipeline SDD

```
skill_view(name="sdd-generate_plan")
```

Pipeline: brainstorm → spec.md → sdd-generate_plan → plan.md → sdd-generate_tasks → tasks.md

## Guardrails

- **HARD-GATE:** sem implementação antes de spec aprovado.
- **Uma pergunta por `clarify()`:** nunca empilhe. Quebre tópicos em múltiplas chamadas.
- **Múltipla escolha sempre que possível:** "Other" como escape para resposta livre.
- **YAGNI implacável:** spec com mínimo viável, não máximo possível.
- **Reavaliação contínua:** avance quando tiver clareza, não continue perguntando por inércia.
- **Respeite constitution.md:** spec não pode violar portões/anti-padrões definidos.
  Se inevitável, alerte o usuário e peça autorização explícita.
- **Idempotência:** detecte spec existente e pergunte se quer refinar ou começar do zero.
- **Id incremental:** derive do que existe em `specs/features/`. Vazio = comece em `001`.

## Verificação

- [ ] `spec.md` existe em `specs/features/<id>-<slug>/`
- [ ] Seções canônicas preenchidas (sem "TODO" ou "TBD")
- [ ] Propósito, escopo, cenários, edge cases, constraints e critérios de sucesso presentes
- [ ] Usuário aprovou explicitamente (via `clarify`)
- [ ] `sdd-generate_plan` invocado ou pronto para aprovação
