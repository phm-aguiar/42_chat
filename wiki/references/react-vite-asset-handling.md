---
title: React + Vite Asset Handling
category: references
tags: [react, vite, assets, images, svg, fonts]
sources: ["_raw/asset-image-optimization.md", "_raw/asset-svg-components.md", "_raw/asset-fonts.md", "_raw/asset-public-dir.md"]
summary: "4 regras HIGH de asset handling React+Vite: otimização de imagens (WebP/AVIF, lazy loading), SVG como React components com SVGR, fontes self-hosted com font-display: swap, e public/ vs import."
provenance:
  extracted: 0.85
  inferred: 0.10
  ambiguous: 0.05
base_confidence: 0.55
lifecycle: draft
lifecycle_changed: "2026-06-16"
tier: supporting
created: 2026-06-16
rag_score: 0.4829
updated: 2026-06-16
---
# React + Vite Asset Handling

4 regras de asset handling para React + Vite. Todas com impacto **HIGH**.

## 1. Image Optimization {#image-optimization}

**Impacto: HIGH (40-70% reduction in image payload)**

**Correto:**
```tsx
{/* Critical above-fold */}
<img src="/images/hero.webp" alt="Hero" width={1200} height={600} fetchPriority="high" />

{/* Below-fold — lazy load */}
<img src="/images/feature.webp" alt="Feature" width={400} height={300}
     loading="lazy" decoding="async" />
```

**Responsive images com fallback:**
```tsx
<picture>
  <source srcSet="/hero-480.webp 480w, /hero-768.webp 768w, /hero-1200.webp 1200w"
          type="image/webp"
          sizes="(max-width: 480px) 480px, (max-width: 768px) 768px, 1200px" />
  <img src="/hero-1200.jpg" alt="Hero" width={1200} height={600} loading="lazy" />
</picture>
```

**Vite image optimizer plugin:**
```ts
import { ViteImageOptimizer } from 'vite-plugin-image-optimizer'
plugins: [ViteImageOptimizer({ png: { quality: 80 }, jpeg: { quality: 80 }, webp: { lossless: true } })]
```

**Inline para imagens pequenas:**
```ts
build: { assetsInlineLimit: 4096 }  // Inline images < 4KB as base64
```

**Reusable Image component:**
```tsx
export function Image({ src, alt, width, height, priority = false }: ImageProps) {
  return <img src={src} alt={alt} width={width} height={height}
              loading={priority ? 'eager' : 'lazy'}
              decoding={priority ? 'sync' : 'async'}
              fetchPriority={priority ? 'high' : 'auto'} />
}
```

## 2. SVG as React Components {#svg-components}

**Impacto: HIGH (Better styling and integration)**

SVGs como `<img>` não podem ser estilizados com CSS. Use SVGR para importar como componentes React.

```bash
npm install vite-plugin-svgr -D
```

```ts
import svgr from 'vite-plugin-svgr'

plugins: [svgr({
  svgrOptions: {
    plugins: ['@svgr/plugin-svgo', '@svgr/plugin-jsx'],
    svgoConfig: { plugins: [{ name: 'removeViewBox', active: false }] },
  },
})]
```

**Uso:**
```tsx
import Logo from './assets/logo.svg?react'
import logoUrl from './assets/logo.svg'

<Logo className="w-8 h-8 text-blue-600 hover:text-blue-700" />  {/* Componente — estilo CSS */}
<img src={logoUrl} alt="Logo" />                                  {/* URL — sem estilo */}
```

**Dynamic colors via `currentColor`:**
```tsx
import SearchIcon from './assets/search.svg?react'
<button className={active ? 'text-blue-600' : 'text-gray-400'}>
  <SearchIcon className="w-5 h-5" /> Search
</button>
```

**Icon component pattern com tree shaking:**
```tsx
const icons = { home: HomeIcon, settings: SettingsIcon, user: UserIcon } as const
type IconName = keyof typeof icons

export function Icon({ name, size = 24, ...props }: IconProps) {
  const IconComponent = icons[name]
  return <IconComponent width={size} height={size} {...props} />
}
// <Icon name="home" size={20} className="text-gray-600" />
```

## 3. Web Font Loading {#fonts}

**Impacto: HIGH (Font loading affects LCP and CLS)**

**Incorreto:** Google Fonts CDN — request render-blocking, DNS extra, GDPR concerns.

**Correto — Self-hosted, subsetted, `font-display: swap`:**
```css
@font-face {
  font-family: 'Inter';
  src: url('/src/assets/fonts/Inter-Regular.woff2') format('woff2');
  font-weight: 400;
  font-style: normal;
  font-display: swap;
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+2000-206F;
}
```

**Preload da fonte crítica:**
```html
<link rel="preload" href="/src/assets/fonts/Inter-Regular.woff2"
      as="font" type="font/woff2" crossorigin />
```

**Vite config para font output:**
```ts
assetFileNames: (assetInfo) => {
  if (/\.(woff2?|ttf|otf|eot)$/.test(assetInfo.name))
    return 'assets/fonts/[name]-[hash][extname]'
  return 'assets/[name]-[hash][extname]'
}
```

## 4. Public Directory vs Import {#public-dir}

**Impacto: HIGH (Wrong asset handling breaks caching and increases bundle size)**

Prefira **importar** assets via JavaScript. Use `public/` apenas para arquivos que precisam manter nomes exatos.

**Import (com hashing):**
```tsx
import logo from './assets/logo.png'  // → /assets/logo-a1b2c3d4.png
import ArrowIcon from './assets/arrow.svg?react'
<img src={logo} alt="Logo" />
```

**public/ (sem hashing — apenas para nomes fixos):**
```
public/
├── favicon.ico       # Browser espera path exato
├── robots.txt        # Crawlers esperam /robots.txt
├── manifest.json     # PWA manifest em URL fixa
├── _redirects         # Config de hosting (Netlify)
└── og-image.png      # Open Graph — URL compartilhada
```

Dynamic imports para assets:
```tsx
const flags = import.meta.glob('./assets/flags/*.svg', { eager: true, as: 'url' })
const src = flags[`./assets/flags/${code}.svg`]
```

---

← Back to [[references/react-vite-performance|React + Vite Performance MoC]]

