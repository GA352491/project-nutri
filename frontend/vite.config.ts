import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { visualizer } from 'rollup-plugin-visualizer'
import fs from 'fs'
import path from 'path'

export default defineConfig(({ mode }) => {
  // Load environment variables from frontend directory and root directory
  const env = loadEnv(mode, process.cwd(), '')

  // Also inspect root .env for APP_DOMAIN / APP_SCHEME if not present in frontend/.env
  let rootDomain = env.VITE_APP_DOMAIN || env.APP_DOMAIN
  let rootScheme = env.VITE_APP_SCHEME || env.APP_SCHEME

  if (!rootDomain || !rootScheme) {
    const rootEnvPath = path.resolve(process.cwd(), '../.env')
    if (fs.existsSync(rootEnvPath)) {
      const content = fs.readFileSync(rootEnvPath, 'utf-8')
      content.split('\n').forEach(line => {
        const trimmed = line.trim()
        if (!trimmed || trimmed.startsWith('#')) return
        const [k, ...v] = trimmed.split('=')
        const val = v.join('=').trim()
        if (k === 'APP_DOMAIN' && !rootDomain) rootDomain = val
        if (k === 'APP_SCHEME' && !rootScheme) rootScheme = val
      })
    }
  }

  const domain = rootDomain || 'localhost'
  const scheme = rootScheme || 'http'
  const target = (port: number) => `${scheme}://${domain}:${port}`

  return {
    plugins: [
      vue(),
      tailwindcss(),
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
        '/api/v1/auth': target(8001),
        '/api/v1/compliance': target(8002),
        '/api/v1/user': target(8003),
        '/api/v1/profile': target(8003),
        '/api/v1/onboarding': target(8003),
        '/api/v1/recipes': target(8004),
        '/api/v1/diary': target(8005),
        '/api/v1/grocery': target(8006),
        '/api/v1/subscriptions': target(8007),
        '/api/v1/subscription': target(8007),
        '/api/v1/referrals': target(8007),
        '/api/v1/family': target(8007),
        '/api/v1/plan': target(8009),
        '/api/v1/notifications': target(8010),
        '/api/v1/chat': {
          target: target(8012),
          ws: true
        },
        '/api/v1/appointments': target(8013),
        '/api/v1/video': target(8014),
        '/api/v1/ai-chat': {
          target: target(8015),
          ws: true
        },
        '/api/v1/payment': target(8016),
        '/api/v1/delivery': target(8017),
        '/api/v1/wearables': target(8018),
        '/api/v1/wearable': target(8018),
        '/api/v1/admin': target(8020),
        '/api/v1/food-recognition': target(8011),
        '/api/v1/marketplace': target(8025),
      }
    }
  }
})
