import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

const apiHost = process.env.VITE_API_HOST || 'localhost'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: `http://${apiHost}:8080`,
        changeOrigin: true,
      },
      '/ws': {
        target: `ws://${apiHost}:8080`,
        ws: true,
      },
    },
  },
})
