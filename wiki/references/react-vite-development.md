---
title: React + Vite Development
category: references
tags: [react, vite, dev, hmr, fast-refresh]
sources: ["_raw/dev-dependency-prebundling.md", "_raw/dev-fast-refresh.md", "_raw/dev-hmr-config.md"]
summary: 3 regras HIGH de dev React+Vite: dependency pre-bundling (2-5x faster cold start), estrutura de componentes para Fast Refresh e configuração de HMR (Docker/WSL/polling).
provenance:
  extracted: 0.85
  inferred: 0.10
  ambiguous: 0.05
base_confidence: 0.55
lifecycle: draft
lifecycle_changed: "2026-06-16"
tier: supporting
created: 2026-06-16
updated: 2026-06-16
---
# React + Vite Development

3 regras de configuração de desenvolvimento para React + Vite. Todas com impacto **HIGH**.

## 1. Dependency Pre-bundling {#dependency-prebundling}

**Impacto: HIGH (2-5x faster cold start)**

```ts
export default defineConfig({
  optimizeDeps: {
    include: [
      'react', 'react-dom', 'react-router-dom',
      '@tanstack/react-query', 'zustand', 'axios', 'date-fns',
      'react-dom/client',
    ],
    esbuildOptions: {
      define: { global: 'globalThis' },
    },
  },
})
```

**Warmup (Vite 5+):** Pré-transforma arquivos críticos no start:
```ts
server: {
  warmup: {
    clientFiles: ['./src/main.tsx', './src/App.tsx', './src/components/index.ts'],
  },
}
```

Comandos úteis:
```bash
vite --force                           # Force re-bundling
DEBUG=vite:deps vite                   # Debug pre-bundling
ls node_modules/.vite/deps/            # Check output
```

## 2. Fast Refresh Patterns {#fast-refresh}

**Impacto: HIGH (Instant updates without losing state)**

| Pattern | Fast Refresh | Notas |
|---------|--------------|-------|
| Default export function | Funciona | Recomendado |
| Named export function | Geralmente funciona | Nome deve ser PascalCase |
| Anonymous function | **Falha** | Sempre nomeie componentes |
| Múltiplos componentes/arquivo | Pode quebrar | Um componente por arquivo |
| Non-component exports | Pode quebrar | Separar em utility files |

**Incorreto:**
- Module-level side effects (`const x = await fetch(...)`)
- Múltiplos componentes + exports não-componente no mesmo arquivo
- Funções anônimas como default export

**Correto:**
```tsx
// Um componente default export por arquivo
export default function Counter() {
  const [count, setCount] = useState(0)
  return <button onClick={() => setCount(c => c + 1)}>Count: {count}</button>
}

// Constantes em arquivo separado: constants/counter.ts
export const MAX_COUNT = 100

// Data fetching via hooks, não module-level
import { useQuery } from '@tanstack/react-query'
export default function UserProfile() {
  const { data: user } = useQuery({ queryKey: ['user'], queryFn: () => fetchUser() })
  // ...
}
```

**HOCs com displayName:**
```tsx
function WithAuth(WrappedComponent) {
  function WithAuth(props) {
    const { user } = useAuth()
    if (!user) return <Navigate to="/login" />
    return <WrappedComponent {...props} />
  }
  WithAuth.displayName = `WithAuth(${WrappedComponent.displayName || WrappedComponent.name})`
  return WithAuth
}
```

## 3. HMR Configuration {#hmr-config}

**Impacto: HIGH (Fast, reliable hot updates)**

**Default:**
```ts
server: {
  hmr: { overlay: true, protocol: 'ws' },
  watch: {
    usePolling: process.env.USE_POLLING === 'true',
    ignored: ['**/node_modules/**', '**/dist/**'],
  },
}
```

**Docker/WSL:**
```ts
server: {
  host: '0.0.0.0',
  hmr: { host: 'localhost', clientPort: 5173 },
  watch: { usePolling: true, interval: 1000 },
}
```

**Custom HMR handling** (evita memory leaks):
```ts
if (import.meta.hot) {
  import.meta.hot.dispose(() => {
    apiClient.interceptors.request.clear()
    apiClient.interceptors.response.clear()
  })
}
```

**Troubleshooting:**
| Issue | Causa | Solução |
|-------|-------|---------|
| Full page reload | Export não é componente | Verificar default exports |
| State lost | Module-level state | Usar state management library |
| Changes not detected | File system events | Habilitar polling |
| Connection errors | Port/protocol mismatch | Configurar hmr.clientPort |
| Slow updates | Cadeia de deps longa | Otimizar com optimizeDeps |

---

← Back to [[references/react-vite-performance|React + Vite Performance MoC]]

