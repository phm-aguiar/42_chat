# Constituição Arquitetural — Framework SDD Autônomo

> Este arquivo define as regras incontornáveis do framework.
> **Sempre pergunte ao usuário antes de adicionar ou modificar regras neste arquivo.**

## Portões de Qualidade
<!-- Regras automatizadas que bloqueiam PRs se violadas -->

1. **Validação SDD obrigatória:** Todo PR deve passar `sdd-validate` — features sem `spec.md` + `plan.md` + `tasks.md` são rejeitadas.
2. **Aprovação humana:** Nenhum código é implementado sem `Aprovado: true` no `spec.md`.
3. **Smoke test:** Toda skill/agente deve ter smoke test verificável (execução real, não simulação).
4. **Vault Obsidian fiel:** Após qualquer mudança estrutural no projeto (nova feature, agente, skill, decisão arquitetural), o vault Obsidian (`wiki/`) deve ser atualizado para refletir o estado atual. Vault desatualizado bloqueia PR.

## Restrições Arquiteturais
<!-- Decisões estruturais que não podem ser violadas -->

1. **Agentes versionados:** Agentes vivem em `.hermes/agents/` versionados no repo. Symlinks em `~/.hermes/agents/` apontam pra cá.
2. **Skills versionadas:** Skills vivem em `.hermes/skills/` versionadas no repo. Symlinks em `~/.hermes/skills/` apontam pra cá.
3. **Pipeline imutável:** O fluxo SDD é `spec → plan → tasks → orchestrator`. Pular etapas é proibido.
4. **Isolamento de agentes:** Subagentes spawnados pelo orchestrator são leaf (não delegam). Contexto é compilado limpo, sem corrosão de sessões anteriores.

## Regras de Negócio Transversais
<!-- Regras que afetam múltiplas features -->

1. **Framework primeiro, app depois:** O produto é o framework SDD autônomo. O app de chat (42_chat) é um smoke-test futuro, não o produto.
2. **Specs são do framework:** Toda spec em `specs/features/` descreve capacidades do framework, não do app de chat.
3. **Knowledge management é first-class:** O vault Obsidian (`wiki/`) é parte do framework, versionado como código. Deve refletir fielmente o estado atual do projeto — novas features, agentes, skills e decisões arquiteturais devem ser documentadas no vault imediatamente após implementação.

## Preferências de Ferramentas
<!-- Ferramentas homologadas para o framework -->

1. **Hermes Agent** como runtime de agentes (não OpenCode, não Claude Code standalone).
2. **Honcho** como camada de memória (self-hosted, Docker).
3. **Obsidian** como vault de conhecimento (formato OFM, versionado).
4. **DeepSeek V4 Pro** como provider primário dos agentes.
5. **GitHub Actions** como CI/CD.

## Anti-Padrões Proibidos
<!-- Abordagens vetadas no framework -->

1. **Implementar sem spec aprovada:** Nunca escreva código antes de `Aprovado: true`.
2. **Corrosão de contexto:** Nunca passe histórico bruto de sessão para subagentes. Use `agent-run` que compila contexto limpo.
3. **Agentes que delegam:** Subagentes são leaf — não podem spawnar outros agentes (profundidade máxima = 1).
4. **Skills fora do padrão:** Toda skill deve seguir o formato Hermes (SKILL.md com frontmatter YAML + corpo markdown).
5. **Ferramentas inventadas:** Nunca invente APIs, imports, ou ferramentas. Use o que existe no `tech.md`.
6. **Vault desatualizado:** Implementar features, agentes ou skills sem atualizar o vault Obsidian (`wiki/`) correspondente. O vault é a memória de longo prazo do framework — deixá-lo desatualizado corrompe o conhecimento acumulado.
