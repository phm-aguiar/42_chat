---
title: Wiki Insights
category: synthesis
tags: [meta, insights, status]
sources: []
summary: "Auto-generated wiki structure analysis: 182 nodes, 597 edges, top hubs, bridge pages, cluster cohesion, surprising connections, and tier suggestions."
lifecycle: draft
lifecycle_changed: "2026-06-17"
tier: peripheral
created: "2026-06-17"
updated: "2026-06-17"
---

# Wiki Insights — 2026-06-17

Vault: 185 pages | Sources ingested: 148 | Token footprint: ~256K

## Anchor Pages (top 10 hubs)

| Page | Incoming | Outgoing | Note |
|---|---|---|---|
| [[references/go-style-guide|Go Style Guide]] | 42 | 40 | connector hub — central Go knowledge hub |
| [[skills/wiki-query|wiki-query]] | 41 | 4 | sink hub — muitas páginas linkam pra cá |
| [[references/go-error-handling|Go Error Handling]] | 19 | 6 | connector hub |
| [[references/42-chat-platform-architecture|42 Chat Platform Architecture]] | 17 | 1 | sink hub |
| [[references/42-chat-engineering-requirements|42 Chat Engineering Requirements]] | 15 | 1 | sink hub |
| [[references/go-naming|Go Naming]] | 12 | 6 | connector hub |
| [[skills/skill-forge|skill-forge]] | 11 | 3 | |
| [[skills/wiki-ingest|wiki-ingest]] | 11 | 5 | |
| [[skills/agent-run|agent-run]] | 11 | 3 | |
| [[concepts/obsidian-flow|Fluxo Obsidian]] | 11 | 5 | |

## Tag Cluster Cohesion

### Most cohesive (bem-linkados)
- **#gherkin** — 5 pages, cohesion=0.60
- **#websocket** — 5 pages, cohesion=0.50
- **#real-time** — 5 pages, cohesion=0.50
- **#bdd** — 8 pages, cohesion=0.39
- **#coding-standards** — 21 pages, cohesion=0.36

### Most fragmented (cross-linker targets)
- **#brand** — 8 pages, cohesion=0.00 ⚠️
- **#implementation** — 14 pages, cohesion=0.00 ⚠️
- **#tasks** — 5 pages, cohesion=0.00
- **#agent** — 13 pages, cohesion=0.01
- **#thinking** — 9 pages, cohesion=0.03

## Surprising Connections (top 8)

| Connection | Score | Reason |
|---|---|---|
| [[synthesis/sdd-go|SDD×Go]] → [[references/go-style-guide|Go Style Guide]] | 5 | cross-category (synthesis→references), ^[ambiguous] |
| [[synthesis/sdd-go|SDD×Go]] → [[references/go-modular-architecture|Go Modular Architecture]] | 5 | cross-category, ^[ambiguous] |
| [[synthesis/sdd-go|SDD×Go]] → [[references/go-testing|Go Testing]] | 5 | cross-category, ^[ambiguous] |
| [[synthesis/sdd-go|SDD×Go]] → [[concepts/sdd-workflow|SDD Workflow]] | 5 | cross-category (synthesis→concepts), ^[ambiguous] |
| [[synthesis/sdd-go|SDD×Go]] → [[references/go-error-handling|Go Error Handling]] | 5 | cross-category, ^[ambiguous] |
| [[synthesis/thinking-architecture|Thinking×Architecture]] → [[references/adr-template|ADR Template]] | 4 | cross-category, ^[inferred] |
| [[synthesis/thinking-architecture|Thinking×Architecture]] → [[references/red-team-adversarial|Red Team Adversarial]] | 4 | cross-category, ^[inferred] |
| [[synthesis/thinking-go|Thinking×Go]] → [[references/mode-selection-guide|Mode Selection Guide]] | 4 | cross-category, ^[inferred] |

## Orphan-Adjacent (dead-ends near hubs)

- [[journal/2026-06-14-readfile-truncation-pitfall]] — linked from 1 hub ([[concepts/obsidian-flow|Fluxo Obsidian]]), 0 outbound links

## Tier Suggestions

↑ core    [[references/go-style-guide|Go Style Guide]] — 42 incoming, currently tier=supporting
↑ core    [[skills/wiki-query|wiki-query]] — 41 incoming, currently tier=supporting
↑ core    [[references/go-error-handling|Go Error Handling]] — 19 incoming, currently unset
↑ core    [[references/42-chat-platform-architecture|42 Chat Platform Architecture]] — 17 incoming, currently unset
↑ core    [[references/42-chat-engineering-requirements|42 Chat Engineering Requirements]] — 15 incoming, currently unset

## Questions Worth Asking

1. Resolve: `synthesis/sdd-go.md` has 5+ ^[ambiguous] connections — claims linking SDD and Go patterns need verification
2. Audit: Should `#brand` tag be removed or consolidated? (8 pages, 0 internal links)
3. Audit: Should `#implementation` tag be split? (14 pages, cohesion=0.0)
4. Link: `journal/2026-06-14-readfile-truncation-pitfall` — dead-end linked from 1 hub, needs outbound links
5. Explore: `go-style-guide` is the #1 hub with 42 incoming links — is the MoC structure working as expected?

<!-- GRAPH_SNAPSHOT: {"nodes": 182, "edges": 597, "top_hubs": ["references/go-style-guide.md", "skills/wiki-query.md", "references/go-error-handling.md", "references/42-chat-platform-architecture.md", "references/42-chat-engineering-requirements.md"], "fragmented_tags": ["brand", "implementation", "tasks", "agent", "thinking"], "cohesive_tags": ["gherkin", "websocket", "real-time", "bdd", "coding-standards"]} -->
