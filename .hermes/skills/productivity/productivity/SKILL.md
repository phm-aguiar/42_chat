---
name: productivity
description: "Toolkit de produtividade e integrações locais. Modos: pptx, pdf-edit, ocr, maps, hue."
version: 1.0.0
author: phm-aguiar
platforms: [linux]
metadata:
  hermes:
    category: productivity
    modes: [pptx, pdf-edit, ocr, maps, hue]
    umbrella_for:
      - powerpoint
      - nano-pdf
      - ocr-and-documents
      - maps
      - openhue
    note: "Airtable, Google Workspace, Notion, Teams, X/Twitter, Himalaya, Yuanbao, GIF/Tenor removidos — requerem API keys externas."
---

# Productivity Toolkit

> Ferramentas de produtividade locais e gratuitas. Sem APIs externas.

## Modo: pptx
**Gatilho:** ".pptx", "deck", "slides", "apresentação"
**Fluxo:**
1. Extrair texto: `python -m markitdown <file>.pptx`
2. Editar: `python scripts/office/unpack.py` → editar XML → `python scripts/clean.py`
3. Criar do zero: `pptxgenjs` (Node.js)
4. QA visual: converter para imagens e inspecionar
**Pitfalls:** Thumbnail.py gera preview; nunca centralizar body text; verificar leftover placeholders com `grep -iE "xxxx|lorem|ipsum"`

## Modo: pdf-edit
**Gatilho:** "editar PDF", "corrigir PDF", "arrumar PDF"
**Fluxo:** `nano-pdf edit <file>.pdf <page> "<instrução em linguagem natural>"`
**Pitfalls:** Página pode ser 0-based ou 1-based; verificar output após edição.

## Modo: ocr
**Gatilho:** "extrair texto", "OCR", "PDF para texto", "scan"
**Fluxo:**
1. `python -m pymupdf extract <file>.pdf` (texto)
2. `marker-pdf <file>.pdf` (markdown, melhor para docs complexos)
**Pitfalls:** PDFs escaneados precisam de OCR engine adicional.

## Modo: maps
**Gatilho:** "onde fica", "distância", "perto de", "rota", "coordenadas"
**Fluxo:**
```bash
MAPS=~/.hermes/skills/maps/scripts/maps_client.py
python3 $MAPS search "lugar"
python3 $MAPS nearby --near "lugar" --category restaurante
python3 $MAPS distance "origem" --to "destino"
```
**Pitfalls:** Nominatim max 1 req/s (script gerencia); OSRM cobre melhor Europa/América do Norte.

## Modo: hue
**Gatilho:** "luz", "lâmpada", "Hue", "iluminação", "cena"
**Fluxo:**
```bash
openhue get light          # listar
openhue set light "nome" --on --brightness 50
openhue set scene "Relax" --room "Quarto"
```
**Pitfalls:** Primeira execução requer apertar botão físico na bridge; nomes case-sensitive; bridge precisa estar na mesma rede.
