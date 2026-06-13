# TODO — Organização do Repositório 42_chat

Checklist de pendências identificadas na análise das skills Hermes do projeto.
Atualizado em: 2026-06-13 (após auditoria da skill brainstorm).

## Estrutura SDD
- [x] Rodar `sdd-validate` no repo — relatório: **20 PASS, 0 FAIL, 0 WARN** ✓
- [x] Garantir conformidade SDD no repo (3 features existentes: 001, 002, 003)

## Skills — Arquivos Referenciados Faltantes

Na auditoria inicial, vários arquivos pareciam faltar. Verificamos: TODOS já existem.
Mantidos no checklist apenas para histórico.

- [x] `sdd-validate` — `scripts/check-sdd.sh` (existe, agora executável)
- [x] `sdd-init-repo` — `scripts/scaffold-sdd.sh` (existe, agora executável)
- [x] `sdd-init-repo` — `assets/templates/constitution-template.md` (existe)
- [x] `sdd-init-repo` — `references/agents-md-sdd-section.md` (existe)
- [x] `sdd-explore-tech` — `assets/tech-template.md` (existe)
- [x] `doc-extract` — `scripts/extract-section.sh` (existe, agora executável)
- [x] `doc-generate-toc` — `scripts/generate-toc.sh` (existe, agora executável)
- [x] `sdd-refactor-artifact` — `references/canonical-templates.md` (existe)
- [x] `skill-forge` — `scripts/scaffold-skill.sh` (criado)
- [x] `skill-forge` — `assets/template-skill.md` (criado)
- [x] `skill-forge` — `references/skill-format.md` (criado)

## Agente — Contrato

- [x] `context.yaml` em `.hermes/agents/sdd-orchestrator/` (35 linhas, com
      `include.files` + `toolsets` — validado)
- [x] `agent-run` resolve o agente sdd-orchestrator (todos os arquivos de
      `include.files` existem)

## Adequação em massa das skills (2026-06-13)

- [x] Migrar layout flat → com categoria (sdd/, doc/, agent/, general/)
- [x] Recriar 12 symlinks em `~/.hermes/skills/<categoria>/<nome>/` (com
      categoria, alinhado com Hermes global — não flat)
- [x] chmod +x em 5 scripts .sh
- [x] Adicionar `metadata.hermes.resources` em 12 skills
- [x] Adicionar `metadata.hermes.category` em 12 skills
- [x] Adicionar "Use when" em agent-run (única sem)
- [x] Padronizar seção "## Quando usar (gatilhos)" em 12 skills
- [x] Padronizar seção "## Verificação" em 12 skills
- [x] Bump version 1.0.0 → 1.0.1 em 11 skills (brainstorm 0.1.0 → 0.1.1)
- [x] Remover skill duplicada `.hermes/skills/sdd-orchestrator/` (wrapper redundante — usar `agent-run`)
- [x] Atualizar `related_skills` em sdd-generate-tasks (sdd-orchestrator → agent-run)
- [x] Smoke-test de 5/5 scripts `.sh` (scaffold-sdd, check-sdd, extract-section,
      generate-toc, scaffold-skill) — todos passaram

## Convenções e Consistência (residual)

- [ ] Adicionar frontmatter YAML no `AGENT.md` do `sdd-orchestrator`
      (manter consistência com SKILL.md — pelo menos `name` e `description`)
- [ ] Encurtar as `description` longas do frontmatter (5+ linhas em várias skills)
      pra melhorar o roteamento automático do Hermes

## Melhorias na skill `sdd-brainstorm` (auditoria 2026-06-13)

A skill é a mais bem escrita do repo (8.5/10). Estas são melhorias incrementais
pra virar referência absoluta. Planejado bumpar versão 0.1.1 → 0.1.2.

### Prioridade alta (resolvem inconsistências reais)

- [ ] **Unificar placeholders.** O SKILL.md (linhas 157-202) usa `<...>` (ex:
      `<id incremental>`, `<YYYY-MM-DD>`), mas o `assets/spec-template.md` usa
      `{{...}}` (ex: `{{FEATURE_ID}}`, `{{DATE}}`). Adotar `{{...}}` em ambos
      (alinhado com o skill-forge e o spec-template externo).
- [ ] **Adicionar Passo 1.5 "Detectar feature existente".** O guardrail de
      idempotência (linha 278-279) menciona detecção mas o Passo 1 só LISTA
      `specs/features/`. Falta a lógica explícita: se a feature já existe,
      perguntar se quer refinar ou criar nova.
- [ ] **Detalhar o que "refinar" significa** quando uma feature já existe.
      Opções: editar spec.md in-place, criar nova versão (v2), adicionar como
      sub-feature (X.Y), ou começar do zero.

### Prioridade média (melhoram UX sem mudar comportamento)

- [ ] **Exemplo concreto no Passo 4.** O exemplo de `clarify()` para 2-3
      abordagens (linha 137-148) usa choices genéricas ("Abordagem A/B/C").
      Adicionar exemplo concreto: "Síncrono: simples mas bloqueante /
      Assíncrono com fila: robusto mas mais infra" pra guiar o agente.
- [ ] **Heurística pro Passo 2.** "Múltiplos subsistemas independentes"
      (linha 84) é vago. Adicionar regra: "Se as partes podem ser entregues
      e usadas independentemente sem a outra, é multi-subsistema."
- [ ] **Nota sobre feature já pronta.** Se o usuário já tem spec.md,
      redirecionar pra `sdd-generate-plan` (brainstorm não se aplica).
      Adicionar nota no topo da skill ou como pré-condição no Passo 1.

### Prioridade baixa (nice-to-have)

- [ ] **Sessões longas.** Brainstorm pode ser longo (8 passos, 6 dimensões).
      Adicionar nota: "Se a sessão ficar longa, salve o estado em notas
      intermediárias antes de gerar o spec.md."
- [ ] **Sincronizar SKILL.md com spec-template.** O template tem
      "## Dependências" e tabela "### Alternativas Consideradas" que o
      SKILL.md (Passo 5) não menciona. Ou adicionar no Passo 5 ou tirar do
      template.

## Validação Pós-Mudanças

- [x] Rodar `sdd-validate` no repo — 20/20 PASS
- [x] Confirmar que `agent-run` resolve o agente `sdd-orchestrator`
- [x] Smoke-test: `doc-generate-toc` rodou em AGENTS.md com sucesso
- [x] Smoke-test: `scaffold-skill.sh` criou skill + symlink com categoria

## Observações

- A skill wrapper `sdd-orchestrator` foi removida em 2026-06-13. O **agente**
  `sdd-orchestrator` em `.hermes/agents/sdd-orchestrator/` continua existindo —
  ele é spawnado via `agent-run`, não mais via skill wrapper dedicada.
- A skill `hermes-agent-skill-authoring` referenciada por `skill-forge` é global
  (vem do catálogo padrão do Hermes Agent), não versionada no repo. Não é
  pendência — apenas nota.
- Layout de skills: a partir de 2026-06-13, todas as skills vivem em
  `.hermes/skills/<categoria>/<nome>/`. Layout flat foi descontinuado.
- Symlinks em `~/.hermes/skills/`: a partir de 2026-06-13, também seguem
  layout com categoria (`~/.hermes/skills/<categoria>/<nome>/`), alinhado
  com o Hermes Agent global.
- A skill `sdd-brainstorm` é considerada a referência de qualidade do
  projeto (8.5/10 na auditoria). As melhorias pendentes estão em
  "Melhorias na skill `sdd-brainstorm`" acima.
