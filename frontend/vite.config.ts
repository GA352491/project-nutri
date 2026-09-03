import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { visualizer } from 'rollup-plugin-visualizer'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
    // Generate stats.html on build to analyze bundle chunks
    visualizer({
      filename: 'dist/stats.html',
      open: false,
      gzipSize: true,
      brotliSize: true,
    }),
  ],
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('vue') || id.includes('pinia')) {
              return 'vendor-vue'
            }
            if (id.includes('chart.js') || id.includes('vue-chartjs')) {
              return 'vendor-charts'
            }
            if (id.includes('@tanstack') || id.includes('axios')) {
              return 'vendor-query'
            }
          }
        }
      }
    },
    chunkSizeWarningLimit: 600
  },
  server: {
    host: '0.0.0.0',   // Listen on all interfaces — allows LAN / phone access
    port: 5173,
    proxy: {
      '/api/v1/auth': 'http://localhost:8001',
      '/api/v1/compliance': 'http://localhost:8002',
      '/api/v1/user': 'http://localhost:8003',
      '/api/v1/profile': 'http://localhost:8003',
      '/api/v1/onboarding': 'http://localhost:8003',
      '/api/v1/recipes': 'http://localhost:8004',
      '/api/v1/diary': 'http://localhost:8005',
      '/api/v1/grocery': 'http://localhost:8006',
      '/api/v1/subscriptions': 'http://localhost:8007',
      '/api/v1/subscription': 'http://localhost:8007',
      '/api/v1/referrals': 'http://localhost:8007',
      '/api/v1/family': 'http://localhost:8007',
      '/api/v1/plan': 'http://localhost:8009',
      '/api/v1/notifications': 'http://localhost:8010',
      '/api/v1/chat': {
        target: 'http://localhost:8012',
        ws: true
      },
      '/api/v1/appointments': 'http://localhost:8013',
      '/api/v1/video': 'http://localhost:8014',
      '/api/v1/ai-chat': {
        target: 'http://localhost:8015',
        ws: true
      },
      '/api/v1/payment': 'http://localhost:8016',
      '/api/v1/delivery': 'http://localhost:8017',
      '/api/v1/wearables': 'http://localhost:8018',
      '/api/v1/wearable': 'http://localhost:8018',
      '/api/v1/admin': 'http://localhost:8019',
      '/api/v1/food-recognition': 'http://localhost:8020',
      '/api/v1/marketplace': 'http://localhost:8025',
    }
  }
})
