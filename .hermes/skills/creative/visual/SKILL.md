---
name: visual
description: "Toolkit visual: 13 modos de design/diagramas/animação. Mermaid, SVG arch, Excalidraw, design HTML, sketch, p5.js, Manim, ASCII, infográficos, web-designs, Pretext, TouchDesigner, humanize."
version: 1.0.0
author: Hermes Agent (consolidado de 13 skills)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [visual, design, diagramas, animação, arte, toolkit, consolidado]
    category: creative
    absorbed_from: [mermaid-visualizer, architecture-diagram, excalidraw, claude-design, sketch, p5js, manim-video, ascii-art, baoyu-infographic, popular-web-designs, pretext, touchdesigner-mcp, humanizer]
---

# Visual Toolkit — 13 Modos de Design e Diagramas

Toolkit consolidado. Cada modo é independente. Identifique o modo pelo gatilho e siga o fluxo resumido. Detalhes completos nas skills originais em `~/.hermes/skills/`.

---

## 1. mermaid — Diagramas Mermaid (fluxogramas, sequência, mindmap)

**Gatilho:** "diagrama", "fluxograma", "visualizar processo", "gráfico de estados", "mindmap"

**Fluxo:**
1. Analise o conteúdo → escolha o tipo: `graph TB/LR` (fluxo), `sequenceDiagram` (sequência), `mindmap` (hierarquia), `stateDiagram` (estados)
2. Aplique regras críticas de sintaxe: sem `1. ` em texto de nós (use `①` ou `[Step 1: ...]`); subgraphs com `subgraph id["Nome"]`; referencie IDs, não nomes
3. Gere código Mermaid em ```mermaid ``` fence
4. Output com explicação breve + menção de compatibilidade (Obsidian, GitHub)

**Paleta padrão:** verde=input, roxo=processamento, laranja=ações, ciano=output, azul=títulos

**Pitfalls:**
- **Regra #1:** `[1. Perception]` quebra parsing → use `[1.Perception]`, `[① Perception]` ou `[(1) Perception]`
- Sem emoji em texto de nós — usar labels textuais ou cores
- Subgraph sem quotes quebra se tiver espaço no nome
- Flechas: `-->` sólida, `-.->` tracejada, `==>` grossa

---

## 2. arch-diagram — Diagrama de Arquitetura SVG (dark theme)

**Gatilho:** "diagrama de arquitetura", "infraestrutura cloud", "sistema microserviços", "topologia"

**Fluxo:**
1. Identifique componentes, conexões, tecnologias
2. Gere HTML standalone com SVG inline (grid `#020617`, JetBrains Mono)
3. Paleta: frontend=`#22d3ee`, backend=`#34d399`, database=`#a78bfa`, cloud=`#fbbf24`, security=`#fb7185`
4. Double-rect (fundo opaco + semitransparente) p/ evitar vazamento de setas
5. Salve `diagram.html`; `xdg-open diagram.html`

**Pitfalls:**
- Legend fora das boundary boxes (20px abaixo da menor Y)
- Setas ANTES dos componentes (z-order); message bus no gap entre serviços
- Altura: 60px serviços, 80-120px grandes, gap mínimo 40px

---

## 3. excalidraw — Diagramas Hand-Drawn (.excalidraw JSON)

**Gatilho:** "desenho à mão", "rascunho de diagrama", "excalidraw", "whiteboard"

**Fluxo:**
1. Gere array JSON de elementos (rectangle, ellipse, diamond, arrow, text)
2. Use container binding: shape tem `boundElements: [{id:"t1", type:"text"}]`, text tem `containerId:"r1"` + `fontFamily:1`
3. Envelope padrão: `{"type":"excalidraw","version":2,"elements":[...],"appState":{"viewBackgroundColor":"#ffffff"}}`
4. Salve `.excalidraw` → abra em excalidraw.com (drag-and-drop)
5. Upload opcional: `python scripts/upload.py arquivo.excalidraw` → URL compartilhável

**Paleta:** azul claro=input, verde=output, laranja=external, roxo=processamento, vermelho=crítico

**Pitfalls:**
- **NUNCA `"label":{"text":"..."}` em shapes** — propriedade inválida. Sempre container binding: shape com `boundElements`, text com `containerId` + `fontFamily:1`
- fontSize mínimo 16 (body), 20 (títulos). Sem emoji — fonte Virgil não renderiza
- Ordem z correta: bg → shape → texto do shape → arrow → próxima shape

---

## 4. design — Design HTML de Alta Fidelidade (landing, protótipo, deck)

**Gatilho:** "design de landing page", "protótipo interativo", "deck de slides", "mockup fiel"

**Fluxo:**
1. Brief: audiência, fidelidade, formato, marca
2. Contexto: docs da marca, screenshots, tokens do repo
3. Sistema de design: cores, tipografia, spacing, motion
4. Artefato HTML standalone (CSS/JS inline)
5. Verifique: abra no browser, cheque console, ajuste

**Anti-slop:** sem gradientes agressivos, glassmorphism, emoji decorativo, cards SaaS genéricos, métricas fake

**Pitfalls:**
- Cada elemento deve ser intencional — não HTML genérico
- Decks: canvas 1920×1080, navegação teclado, slide count
- Motion: `prefers-reduced-motion`, sem loops decorativos
- Se houver repo, inspecione tokens/componentes reais antes de inventar

---

## 5. sketch — Mockups HTML Descartáveis (2-3 variantes)

**Gatilho:** "rascunha essa tela", "mostra umas opções", "compara layout A vs B", "variantes de UI"

**Fluxo:**
1. Intake rápido (se faltar contexto): feel, referências, ação principal
2. Produza 2-3 variantes como HTML standalone — cada uma com stance diferente (densidade, ênfase, layout)
3. Cada variante: `sketches/NNN-stance/index.html` + `README.md`
4. Verifique com `browser_vision` cada variante
5. Apresente tabela comparativa head-to-head + opinião

**Stances:** densidade (compacto vs arejado), ênfase (conteúdo vs ação), layout (single-col vs sidebar vs split-pane)

**Pitfalls:**
- 2 variantes que só diferem em accent color = perda de tempo
- Conteúdo fake realista (nomes reais, frases), nunca "Lorem ipsum"
- Interatividade mínima: 1 ação principal clicável + 1 transição de estado + hovers
- Sketch é descartável — se precisar preservar, promova para código real

---

## 6. p5js — Arte Generativa e Animações (canvas, WebGL, shaders)

**Gatilho:** "p5.js", "arte generativa", "creative coding", "visualização interativa", "shader", "partículas"

**Fluxo:**
1. Conceito criativo: mood, paleta, motion, diferencial
2. Modo: generative art, data viz, interactive, animation, 3D, image processing, audio-reactive
3. HTML standalone: p5.js 1.11.3 CDN → `preload()` → `setup()` → `draw()` → classes
4. Preview no browser, ajuste
5. Export: `saveCanvas('out','png')` (tecla S), `saveGif('out',5)` (G), Puppeteer p/ MP4

**Criativo:** nunca `fill(255,0,0)` cru — paleta 3-7 cores; nunca `background(0)` liso — textura/gradiente; 1 detalhe extra não pedido

**Pitfalls:**
- `p5.disableFriendlyErrors = true` ANTES do `setup()` (10x overhead)
- `pixelDensity(1)` para retina; `randomSeed()`+`noiseSeed()` para reprodutibilidade
- Hot loops: `Math.*` em vez de wrappers p5; `colorMode(HSB, 360, 100, 100, 100)`

---

## 7. manim — Animações Matemáticas/Explicativas (3Blue1Brown style)

**Gatilho:** "animação matemática", "explicação animada", "3Blue1Brown", "derivação visual", "Manim"

**Fluxo:**
1. Planeje arco narrativo em `plan.md`: cenas, arco de revelação, "aha moment"
2. Escreva `script.py` — uma classe por cena, cada uma renderizável independente
3. Renderize: `manim -ql script.py Cena1 Cena2` (draft) → `manim -qh` (produção)
4. Stitch com ffmpeg: `ffmpeg -f concat -i concat.txt -c copy final.mp4`

**Paleta 3B1B:** bg=`#1C1C1C`, primary=`#58C4DD` (azul), secondary=`#83C167` (verde), accent=`#FFFF00` (amarelo)

**Pitfalls:**
- Raw strings p/ LaTeX: `MathTex(r"\frac{1}{2}")`, nunca sem `r`
- Fontes monospace (`font="Menlo"`) — Pango quebra kerning com proporcionais
- `self.wait()` após cada animação: 1s normal, 2s pós-revelação, 3s "aha moment"
- Opacity: primário=1.0, contexto=0.4, estrutura=0.15
- Nunca animar mobject não-adicionado à cena
- Pré-requisitos: LaTeX (`texlive-full`), ffmpeg, `pip install manim`

---

## 8. ascii — Arte ASCII (banners, cowsay, boxes, imagens)

**Gatilho:** "ASCII art", "banner texto", "cowsay", "borda decorativa", "imagem para ASCII"

**Fluxo:**
1. Texto → banner: `python3 -m pyfiglet "TEXTO" -f slant` (571 fontes)
2. Mensagem em balão: `cowsay -f tux "mensagem"`
3. Borda decorativa: `echo "texto" | boxes -d stone` (70+ designs)
4. Imagem → ASCII: `ascii-image-converter imagem.png -C` (colorido)
5. QR code: `curl -s "qrenco.de/Hello+World"`
6. Fallback: gere ASCII manual com Unicode box-drawing (`╔╗╚╝║═`), block (`░▒▓█`), geométrico (`◆●▲★`)

**Fontes recomendadas:** `slant` (limpo), `doom` (bold), `big` (banner), `cyberlarge` (tech), `gothic` (dramático)

**Pitfalls:**
- `pyfiglet` → `pip install pyfiglet`; fallback: `curl -s "https://asciified.thelicato.io/api/v2/ascii?text=Hello&font=Slant"`
- Largura máx 60 chars, altura 15-25 linhas
- Imagem→ASCII: `ascii-image-converter` (snap/go) ou `jp2a` (JPEG, `apt install jp2a`)
- `toilet` gera ANSI escapes — terminal apenas, não arquivos

---

## 9. infographic — Infográficos (21 layouts × 21 estilos)

**Gatilho:** "infográfico", "信息图", "visual summary", "高密度信息大图", "poster informativo"

**Fluxo:**
1. Analise conteúdo → `source.md`
2. Estruture → `structured-content.md` (título, seções com conceito + visual + dados)
3. Recomende 3-5 combos layout×estilo
4. Confirme: combo, aspecto, idioma
5. Monte prompt → `prompts/infographic.md`
6. Gere com `image_generate`

**Layouts:** `bento-grid` (default), `linear-progression` (timeline), `binary-comparison`, `funnel`, `dashboard`
**Estilos:** `craft-handmade` (default), `technical-schematic`, `chalkboard`, `ikea-manual`

**Pitfalls:**
- **Integridade dos dados:** nunca parafraseie estatísticas
- **Remova credenciais** (API keys, tokens) do conteúdo fonte
- Uma mensagem por seção; consistência de estilo obrigatória
- `image_generate`: só landscape/portrait/square — ratios custom mapeiam pro mais próximo

---

## 10. web-designs — 54 Sistemas de Design Reais (Stripe, Linear, Vercel...)

**Gatilho:** "estilo Stripe", "parecido com Linear", "design da Vercel", "landing page estilo [marca]"

**Fluxo:**
1. Identifique a marca/site → carregue template: `skill_view(name="popular-web-designs", file_path="templates/stripe.md")`
2. Extraia: paleta de cores, fontes (com substituto CDN), estilos de componente, spacing, shadows
3. Gere HTML standalone usando os tokens extraídos como CSS custom properties
4. Use Google Fonts como substituto para fontes proprietárias (ex: Source Sans 3 → sohne-var da Stripe)

**Mapeamento rápido:** Stripe=`stripe.md`, Linear=`linear.app.md`, Vercel=`vercel.md`, Notion=`notion.md`, Apple=`apple.md`, Airbnb=`airbnb.md`, Spotify=`spotify.md`, SpaceX=`spacex.md`

**Pitfalls:**
- Fontes proprietárias não disponíveis em CDN → use substituto Google Fonts do template
- Combine com `claude-design` para o processo/taste, este skill para o vocabulário visual
- Não recrie UI proprietária idêntica — extraia princípios, não clone

---

## 11. pretext — Demos Criativas com Tipografia (texto fluindo ao redor de obstáculos)

**Gatilho:** "pretext demo", "texto fluindo ao redor", "tipografia cinética", "texto como geometria"

**Fluxo:**
1. Padrão: reflow-around-obstacle, text-as-geometry, shatter/particles, kinetic type
2. Template: `templates/hello-orb-flow.html`
3. Corpus: prosa real significativa (nunca lorem ipsum)
4. Estética: fonte proporcional, fundo escuro, paleta, interação
5. Sirva com `python3 -m http.server`, abra no browser

**Stack:** `@chenglou/pretext@0.0.6` via `esm.sh`, Canvas 2D, `Intl.Segmenter`
**Padrão chave:** `layoutNextLineRange(prepared, cursor, lineWidth)` em loop por linha

**Pitfalls:**
- Font string canvas === CSS; se Inter 404, fallback quebra medições
- `prepare()` UMA vez, nunca no loop; `layoutNextLineRange` é barato (60fps)
- `esm.sh`, NÃO `unpkg` (raw TS quebra); fontes proporcionais, não monospace

---

## 12. touchdesigner — Controle de TouchDesigner via MCP (36 ferramentas nativas)

**Gatilho:** "TouchDesigner", "TD visual", "VJ loop", "instalação audiovisual", "real-time generative", "GLSL ao vivo"

**Pré-requisitos:** TouchDesigner rodando + `twozero.tox` carregado + MCP habilitado na porta 40404

**Fluxo:**
1. Setup: `bash scripts/setup.sh` (download .tox, configura MCP)
2. Discover: `td_get_par_info` + `td_get_hints` + `td_get_focus` ANTES de construir
3. Build: `td_create_operator(type="noiseTOP", parent="/project1", name="bg", parameters={...})`
4. Wire: `td_execute_python` com `.outputConnectors[0].connect()`
5. Verify: `td_get_errors(recursive=true)` + `td_get_perf()`
6. Capture: `td_get_screenshot(path="/project1/out")`

**Audio-reactive recipe (verificada):** AudioFileIn → AudioSpectrum (FFT=512, outlength=256, timeslice=ON) → Math (gain=10) → CHOPtoTOP (dataformat='r', rowscropped) → GLSL TOP input

**Pitfalls:**
- **NUNCA adivinhe parâmetros** — `td_get_par_info` primeiro. Training data errado p/ TD 2025.32
- Non-Commercial TD: resolução máx 1280×1280; codecs: `prores` (macOS), `mjpa` fallback
- GLSL time: Constant TOP rgba32float + `absTime.seconds` — NÃO `uTDCurrentTime`
- Split cleanup/criação em chamadas MCP separadas (mesmo nome na mesma chamada = "Invalid OP object")
- AudioSpectrum: NUNCA Lag/Filter CHOP p/ smoothing (expandem samples, zeram valores)

---

## 13. humanize — Humanizar Texto (remover padrões de IA)

**Gatilho:** "humaniza esse texto", "tira cara de ChatGPT", "deixa mais natural", "reescreve sem slop de IA"

**Fluxo:**
1. Identifique padrões de IA: 29 categorias documentadas
2. Refaça trechos problemáticos preservando significado
3. Adicione personalidade: opiniões, ritmo variado, primeira pessoa quando couber, complexidade genuína
4. Auto-auditoria: "O que torna isso obviamente gerado por IA?" → revise mais uma vez
5. Output: draft → auditoria → versão final

**Padrões mais comuns:** ênfase indevida em importância ("pivotal moment", "serves as a testament"), vocabulário AI ("delve", "showcase", "tapestry", "crucial", "foster"), frases de chatbot ("I hope this helps", "Certainly!"), hedging excessivo, em-dash abuso, finais genéricos otimistas

**Pitfalls:**
- Texto "limpo" sem voz ainda soa artificial — adicione personalidade
- Ritmo variado: frases curtas + longas. Opiniões > neutralidade
- Se usuário der amostra de voz, MATCHE-A: comprimento frase, vocabulário, pontuação
- Edição de arquivos: `patch` (cirúrgico) em vez de `write_file`

---

## Decisão Rápida

| O usuário quer... | Modo |
|---|---|
| Diagrama técnico (fluxo, arquitetura, sequência) | `mermaid` |
| Arquitetura cloud/infra dark SVG | `arch-diagram` |
| Desenho à mão, whiteboard editável | `excalidraw` |
| Landing page, protótipo fiel, deck | `design` |
| Comparar 2-3 direções de UI | `sketch` |
| Arte generativa, partículas, shaders, canvas | `p5js` |
| Animação matemática 3Blue1Brown | `manim` |
| Banner ASCII, cowsay, borda decorativa | `ascii` |
| Infográfico informativo (imagem) | `infographic` |
| Página estilo marca famosa (Stripe, Linear) | `web-designs` |
| Demo tipografia cinética (pretext) | `pretext` |
| TouchDesigner ao vivo (MCP) | `touchdesigner` |
| Reescrever texto removendo padrões IA | `humanize` |

---

## Skills Originais

`~/.hermes/skills/creative/`: architecture-diagram, ascii-art, baoyu-infographic, claude-design, excalidraw, humanizer, manim-video, p5js, popular-web-designs, pretext, sketch, touchdesigner-mcp
`~/.hermes/skills/visual/`: mermaid-visualizer
