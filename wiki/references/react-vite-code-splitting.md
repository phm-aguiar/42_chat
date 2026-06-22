---
title: React + Vite Code Splitting
category: references
tags: [react, vite, code-splitting, lazy-loading, suspense]
sources: ["_raw/split-route-lazy.md", "_raw/split-suspense-boundaries.md", "_raw/split-dynamic-imports.md", "_raw/split-component-lazy.md", "_raw/split-prefetch-hints.md"]
summary: "5 regras CRITICAL de code splitting React+Vite: route-based lazy loading (50-80% menor), Suspense boundaries estratégicos, dynamic imports para libs pesadas, lazy de componentes não-críticos e prefetch hints."
provenance:
  extracted: 0.85
  inferred: 0.10
  ambiguous: 0.05
base_confidence: 0.59
lifecycle: draft
lifecycle_changed: "2026-06-16"
tier: supporting
created: 2026-06-16
rag_score: 0.4825
updated: 2026-06-16
---
# React + Vite Code Splitting

5 regras de code splitting para React + Vite. Todas com impacto **CRITICAL**.

## 1. Route-Based Lazy Loading {#route-lazy}

**Impacto: CRITICAL (50-80% smaller initial bundle)**

**Incorreto:** Imports eager de todas as páginas no bundle inicial.

**Correto:**
```tsx
import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

const Home = lazy(() => import('./pages/Home'))
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Settings = lazy(() => import('./pages/Settings'))

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  )
}
```

Preload on hover:
```tsx
<Link to="/dashboard" onMouseEnter={() => import('./pages/Dashboard')} onFocus={...}>
  Dashboard
</Link>
```

Vite nomeia chunks automaticamente baseado no path do arquivo — sem necessidade de magic comments.

## 2. Strategic Suspense Boundaries {#suspense-boundaries}

**Impacto: CRITICAL (Progressive loading, better UX)**

**Incorreto:** Um único `<Suspense>` na raiz bloqueia a UI inteira.

**Correto:** Boundaries por seção:
```tsx
function App() {
  return (
    <div className="app-layout">
      <Header />  {/* Carrega imediatamente */}

      <div className="main-layout">
        <Suspense fallback={<SidebarSkeleton />}>
          <Sidebar />
        </Suspense>

        <Suspense fallback={<ContentSkeleton />}>
          <MainContent />
        </Suspense>
      </div>

      <Footer />  {/* Carrega imediatamente */}
    </div>
  )
}
```

Suspense aninhado para UIs complexas:
```tsx
function Dashboard() {
  return (
    <div className="dashboard-grid">
      <Suspense fallback={<WidgetSkeleton />}><StatsWidget /></Suspense>
      <Suspense fallback={<WidgetSkeleton />}><ChartWidget /></Suspense>
      <Suspense fallback={<WidgetSkeleton />}><RecentActivityWidget /></Suspense>
    </div>
  )
}
```

Combine com Error Boundaries:
```tsx
<ErrorBoundary fallback={<ErrorFallback />}>
  <Suspense fallback={<PageLoader />}>
    <Routes>...</Routes>
  </Suspense>
</ErrorBoundary>
```

## 3. Dynamic Imports for Heavy Components {#dynamic-imports}

**Impacto: CRITICAL (30-50% reduction in initial bundle)**

Bibliotecas que devem ser dynamic imported:
- Charts (Chart.js, Recharts, D3)
- Rich text editors (React Quill, TipTap, Slate)
- Code editors (Monaco, CodeMirror)
- PDF libraries (react-pdf, pdf-lib)
- Date pickers com locales
- Map libraries (Mapbox, Google Maps)
- Markdown renderers

**Correto:**
```tsx
const Chart = lazy(() => import('./components/Chart'))
const Editor = lazy(() => import('./components/Editor'))

// Conditional import for libraries
async function exportToPDF() {
  const { PDFDocument } = await import('pdf-lib')
  // ...
}

// Feature-flag based loading
const AdminPanel = user.isAdmin ? lazy(() => import('./AdminPanel')) : null
```

## 4. Lazy Load Non-Critical Components {#component-lazy}

**Impacto: CRITICAL (20-40% smaller initial bundle)**

| Component Type | Lazy Load? | Razão |
|---------------|------------|-------|
| Modals/Dialogs | Sim | Só exibidos em interação |
| Drawers/Panels | Sim | Ocultos por padrão |
| Below-fold content | Sim | Fora do viewport inicial |
| Tabs (não-default) | Sim | Ocultos até selecionados |
| Header/Navigation | Não | Sempre visível |
| Above-fold content | Não | Crítico para FCP |

Pattern com `lazyWithPreload`:
```tsx
export function lazyWithPreload<T extends ComponentType<any>>(
  factory: () => Promise<{ default: T }>
): PreloadableComponent<T> {
  const Component = lazy(factory) as PreloadableComponent<T>
  Component.preload = factory
  return Component
}

const SettingsPanel = lazyWithPreload(() => import('./components/SettingsPanel'))

// Preload on hover
<button onMouseEnter={() => SettingsPanel.preload()}>Settings</button>
```

Intersection Observer para below-fold:
```tsx
const { ref, inView } = useInView({ triggerOnce: true, rootMargin: '200px' })
{inView && <Suspense fallback={<Skeleton />}><CustomerReviews /></Suspense>}
```

## 5. Prefetch Code Chunks on User Intent {#prefetch-hints}

**Impacto: CRITICAL (Instant navigation perceived speed)**

| Estratégia | Trigger | Melhor para |
|-----------|---------|-------------|
| Hover/Focus | Sinal de intenção | Navigation links |
| Viewport Entry | Posição de scroll | Seções below-fold |
| Idle Time | Após initial load | Rotas comuns |
| `modulepreload` | Page load | Vendors críticos |

**PrefetchLink component:**
```tsx
function PrefetchLink({ preload, ...props }: PrefetchLinkProps) {
  return (
    <Link {...props}
      onMouseEnter={(e) => { preload?.(); props.onMouseEnter?.(e) }}
      onFocus={(e) => { preload?.(); props.onFocus?.(e) }}
    />
  )
}
```

**Prefetch on idle:**
```tsx
function usePrefetchAfterIdle(preloadFns: Array<() => Promise<any>>, delay = 2000) {
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      preloadFns.forEach((fn) => {
        if ('requestIdleCallback' in window) {
          requestIdleCallback(() => fn(), { timeout: 5000 })
        } else { setTimeout(fn, 100) }
      })
    }, delay)
    return () => clearTimeout(timeoutId)
  }, [])
}
```

---

← Back to [[references/react-vite-performance|React + Vite Performance MoC]]

