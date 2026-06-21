# Spec: Reavaliação e Consolidação de Skills

## Metadados
- **ID:** 008
- **Status:** approved
- **Aprovado:** true
- **Autor:** phm-aguiar
- **Data:** 2026-06-19
- **Feature Anterior:** 007-agent-qa (subagente de QA implementado)

## Propósito

O framework SDD acumulou ~130 skills em 17 categorias. A granularidade atual é insustentável:
skills de mesmo domínio estão fragmentadas em operações atômicas (ex: `wiki-cross-linker`,
`wiki-dedup`, `wiki-synthesize` são 3 skills que fazem "operações de tecer o grafo de
conhecimento"). Subagentes precisam carregar 5-10 skills para tarefas correlatas, inflando
o prompt e tornando a orquestração frágil.

**Metáfora RPG:** Skills são ferramentas da "classe" do subagente. Hoje, ao invés de
equipar o Dev com uma `toolkit-dev` (que contém padrões Go, React, smoke-test), ele
precisa equipar 6 skills separadas. É como ter `ler-capitulo-1`, `ler-capitulo-2` ao
invés de `ler-livro`.

**Objetivo:** Consolidar skills em **toolkits coesos por domínio** (~7-10 toolkits),
reduzindo a fragmentação sem perder especialização. Subagentes carregam 1-2 toolkits
ao invés de 5-10 skills.

## Escopo

### Dentro do escopo

- Auditar as ~130 skills atuais e classificá-las por: (a) uso real por subagentes,
  (b) redundância entre skills, (c) granularidade (atômica vs. toolkit)
- Consolidar skills de mesmo domínio em toolkits com modos/subcomandos
- Reduzir duplicatas explícitas (ex: `cross-linker` + `wiki-cross-linker`)
- Demover skills de "formato/referência" (ex: `obsidian-markdown`, `doc-extract`) a
  páginas de referência no vault, carregadas sob demanda por `brain-query`
- Atualizar `AGENTS.md` dos subagentes afetados (`agent-dev`, `agent-qa`) para usar
  os novos toolkits
- Atualizar `wiki/` com a nova arquitetura de skills
- Garantir retrocompatibilidade: symlinks e referências existentes não quebram

### Fora do escopo (explicitamente)

- Criar novas skills do zero (feature é de consolidação, não expansão)
- Alterar o runtime do Hermes Agent (`agent-run`, `delegate_task`)
- Modificar agentes que não usam skills (`agent-orchestrator`, `onboard` — apenas
  referenciam skills, não as carregam)
- Consolidar skills que não têm sobreposição de domínio (ex: juntar `github-auth`
  com `xurl`)

## Comportamento Esperado

### Cenário Principal (Happy Path)

1. Auditoria: lista todas as skills, mapeia uso por subagente, identifica redundâncias
2. Proposta de consolidação: agrupa skills por domínio em toolkits (~7-10)
3. Aprovação do usuário sobre o mapa final de toolkits
4. Implementação: cria toolkits (merge de SKILL.md), atualiza symlinks, remove skills
   absorvidas, demove skills de formato a referências no vault
5. Atualização dos agentes: `agent-dev` e `agent-qa` referenciam os novos toolkits
6. Smoke test: cada toolkit carrega sem erro via `skill_view(name=...)`
7. Wiki atualizado: `wiki/skills/` reflete nova estrutura, `wiki/index.md` atualizado

### Cenários Alternativos

- **Toolkit multi-modo:** Um toolkit pode expor modos (ex: `brain-weave --cross-link`
  vs. `brain-weave --dedup`). O subagente carrega o toolkit uma vez e escolhe o modo
  conforme necessário
- **Skill de formato permanece ativa:** Se uma skill de formato (ex: `obsidian-cli`)
  for usada programaticamente por outras skills, ela permanece como dependência interna,
  não como skill de entry-point
- **Rollback:** Se um toolkit consolidado ficar grande demais (>20KB), split em 2
  toolkits do mesmo domínio

## Edge Cases

- **Skill absorvida ainda referenciada:** Se `cross-linker` for absorvido em
  `brain-weave`, skills que referenciam `cross-linker` devem ser atualizadas. Symlink
  antigo pode ser mantido como alias por 1 ciclo de transição
- **Toolkit com sobreposição parcial:** Duas skills de categorias diferentes que
  compartilham 30% do domínio — consolidar na categoria predominante, referenciar
  da outra
- **Skill que é usada por humanos e agentes:** `wiki-query` é usado pelo agente
  principal e por subagentes. O toolkit deve servir ambos os perfis
- **Skill de terceiro (plugin):** Skills que vieram de plugins Hermes não são
  versionadas no repo e não entram no escopo de consolidação
- **Agente que referencia skill por nome hardcoded:** `agent-qa` tem `gherkin-scenarios`
  como string no context.yaml. Atualizar para o nome do toolkit

## Constraints

- **Retrocompatibilidade:** Symlinks existentes em `~/.hermes/skills/` não podem
  quebrar subagentes em execução. Período de transição com aliases
- **Tamanho de toolkit:** Máximo ~15KB por SKILL.md. Toolkits maiores perdem o
  benefício de consolidação (custo de prompt anula ganho de carregar 1 vs. 5 skills)
- **Preservação semântica:** Nenhuma capacidade é perdida na consolidação — toda
  operação que existia em skill separada deve existir como modo/subcomando no toolkit
- **Constitution compliance:** Portão 3 (smoke test), portão 4 (vault fiel),
  restrição 2 (skills versionadas)

## Critérios de Sucesso

- [ ] Número de skills de entry-point reduzido de ~130 para ≤ 15 toolkits
- [ ] Subagentes (`agent-dev`, `agent-qa`) carregam no máximo 3 toolkits cada
- [ ] Cada toolkit carrega sem erro via `skill_view(name=...)`
- [ ] Nenhum symlink quebrado em `~/.hermes/skills/`
- [ ] `wiki/index.md` reflete a nova estrutura
- [ ] `wiki-lint` passa sem broken links
- [ ] Skills absorvidas têm `absorbed_into` apontando para o toolkit destino
- [ ] `AGENTS.md` dos subagentes atualizado com os novos nomes de toolkit

## Abordagem Escolhida

**Toolkits por domínio com modos internos.** Cada domínio (Wiki, QA, Dev, SDD, etc.)
vira um toolkit coeso. O toolkit expõe modos via subcomandos ou seções internas;
o subagente carrega o toolkit uma vez e referencia o modo conforme necessário.

**Exemplo — Domínio Wiki (27 skills → 7 toolkits → 1 toolkit `brain`):**
```
Antes: wiki-ingest, wiki-query, wiki-lint, wiki-capture, wiki-cross-linker,
       wiki-dedup, wiki-synthesize, wiki-dashboard, wiki-status, wiki-digest,
       wiki-export, wiki-setup, wiki-tag-taxonomy, vault-health, cross-linker,
       tag-taxonomy, wiki-hermes-history-ingest, wiki-llm-wiki,
       hermes-wiki-setup, document-consolidation, obsidian-markdown,
       obsidian-cli, obsidian-bases, json-canvas, defuddle,
       doc-extract, doc-generate-toc, doc-generate-llms-txt
       (27 entry-points)

Depois: brain (1 toolkit com modos: ingest, query, lint, weave, report, init, format)
        + referências no vault (ofm-spec, doc-tools)
        (1 entry-point + 2 refs)
```

**Toolkits propostos (preliminar, a ser refinado no plan.md):**
| Toolkit | Absorve | Subagentes que usam |
|---|---|---|
| `brain` | 27 skills wiki/obsidian/docs | Principal (humano) |
| `sdd` | 9 skills pipeline SDD | Principal |
| `qa-toolkit` | 8 skills QA/testes | agent-qa |
| `dev-toolkit` | 8 skills dev/build/agent-runtime | agent-dev |
| `github` | 6 skills GitHub | Principal |
| `devops` | 11 skills DevOps/infra | Principal |
| `visual` | 14 skills design/criativas | Principal |
| `ml` | 7 skills MLOps | Principal |
| `research` | 5 skills pesquisa | Principal |
| `productivity` | 8 skills produtividade | Principal |

### Alternativas Consideradas

| Abordagem | Trade-off | Por que não |
|---|---|---|
| Manter tudo como está, apenas documentar melhor | Zero esforço de migração | Não resolve a fragmentação. Subagentes continuam carregando 5-10 skills. A dor permanece |
| Consolidar apenas as duplicatas explícitas (cross-linker, tag-taxonomy) | Esforço mínimo (~4 merges) | Ganho marginal. Reduz de 130 pra ~125. A fragmentação estrutural permanece |
| Um mega-toolkit `hermes` com todas as skills | Um entry-point, zero fragmentação | SKILL.md ficaria >100KB, inviável de carregar no prompt. Perde especialização |

## Dependências

- `agent-run`: toolkits consolidados devem ser carregáveis via `skill_view(name=...)`
- `skill-forge`: criação/atualização de skills segue o formato Hermes
- `wiki-ingest` + `wiki-lint`: atualização do vault pós-consolidação
- `sdd-validate`: validação da estrutura SDD pós-mudanças

## Checklist de Prontidão

- [ ] Propósito claro e sem ambiguidade
- [ ] Escopo delimitado (dentro/fora)
- [ ] Cenários cobrem happy path e alternativos
- [ ] Edge cases identificados com comportamento esperado
- [ ] Constraints explícitas
- [ ] Critérios de sucesso mensuráveis
- [ ] Abordagem escolhida justificada
