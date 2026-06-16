---
title: "Thinking × Architecture"
category: synthesis
tags: [thinking, architecture, synthesis, decision-making]
sources:
  - "references/socratic-questioning.md"
  - "references/pre-mortem-analysis.md"
  - "references/red-team-adversarial.md"
  - "references/adr-template.md"
  - "references/system-design.md"
created: "2026-06-16T00:00:00Z"
updated: "2026-06-16T00:00:00Z"
summary: "Como aplicar ferramentas de reasoning (socrático, adversarial, pre-mortem) nas decisões de arquitetura: ADRs mais robustos e designs que sobrevivem ao escrutínio."
provenance:
  extracted: 0.1
  inferred: 0.85
  ambiguous: 0.05
base_confidence: 0.59
lifecycle: draft
lifecycle_changed: "2026-06-16"
tier: core
---

# Thinking × Architecture

## The Connection

Decisões de arquitetura são exercícios de reasoning sob incerteza. Cada ADR
([[references/adr-template|ADR Template]]) é uma hipótese sobre o futuro do
sistema. As ferramentas de thinking — socrático, adversarial, pre-mortem —
são o método científico aplicado a essas hipóteses. ^[inferred]

Sem eles, ADRs viram justificativas retrospectivas. Com eles, cada ADR sobrevive
a um mini trial de fogo antes de ser commitado.

## Onde se Encontram

Cada ferramenta de thinking mapeia para uma fase da decisão arquitetural:

| Ferramenta | Fase da Decisão | Pergunta-chave |
|---|---|---|
| [[references/socratic-questioning|Socratic Questioning]] | Exploração do problema | "Quais premissas estamos assumindo?" |
| [[references/dialectic-synthesis|Dialectic Synthesis]] | Avaliação de alternativas | "Qual é o argumento mais forte contra nossa escolha?" |
| [[references/pre-mortem-analysis|Pre-Mortem]] | Validação do design | "Daqui a 6 meses, por que isso falhou?" |
| [[references/red-team-adversarial|Red Team]] | Stress-test de segurança | "Como um adversário quebraria isso?" |
| [[references/cognitive-bias-inventory|Bias Inventory]] | Revisão do ADR | "Quais vieses estão distorcendo essa decisão?" |

## Cross-cutting Insight

Um ADR que passou por socratic questioning + pre-mortem + red team é
qualitativamente diferente de um ADR escrito direto. O primeiro carrega
evidência de que alternativas foram consideradas e riscos foram antecipados.
O segundo é uma anotação de intenção. ^[inferred]

**Padrão recomendado:** Para ADRs de alto impacto (mudança de banco, escolha
de arquitetura, decisão de make-vs-buy), execute o ciclo completo:

1. **Escreva o rascunho do ADR** (contexto, decisão, alternativas).
2. **Passe o [[references/socratic-questioning|Socratic Questioning]]** —
   documento as respostas como "Premissas validadas" no ADR.
3. **Execute um [[references/pre-mortem-analysis|Pre-Mortem]]** —
   documente os riscos identificados como "Mitigações" no ADR.
4. **Se for security-critical, rode o [[references/red-team-adversarial|Red Team]]**.
5. **Revise o ADR final com o [[references/cognitive-bias-inventory|Bias Inventory]]**.

## Tensions and Trade-offs

- **Custo de tempo:** O ciclo completo pode levar horas. Reserve para decisões
  Type 1 (irreversíveis). Decisões Type 2 (reversíveis) podem pular o pre-mortem. ^[inferred]
- **Overthinking:** Aplicar todas as 5 ferramentas em toda decisão leva à
  paralisia analítica. Use o [[references/mode-selection-guide|Mode Selection Guide]]
  para calibrar a profundidade.

## Open Questions

- Como medir o ROI de aplicar thinking tools em ADRs?
- Existe um formato de ADR "aumentado" que inclua campos para socratic/pre-mortem/red-team?
- Em times ágeis, quem executa o papel de red team quando não há pentester dedicado?

## Related

- [[references/adr-template|ADR Template]]
- [[references/system-design|System Design Guide]]
- [[references/socratic-questioning|Socratic Questioning]]
- [[references/pre-mortem-analysis|Pre-Mortem Analysis]]
- [[references/red-team-adversarial|Red Team Adversarial]]
- [[references/dialectic-synthesis|Dialectic Synthesis]]
- [[references/cognitive-bias-inventory|Cognitive Bias Inventory]]
- [[references/mode-selection-guide|Mode Selection Guide]]
