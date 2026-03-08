/*import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})*/
import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
  proxy: {
    // 1. 特殊处理：指向 Python 的 AI 服务 (最长匹配放在最前面)
    '/api/wen/analyze': {
      target: 'http://localhost:5000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '')
    },

    // 2. 统一处理：所有其他 /api 请求全部指向 Java 8080
    // 删掉之前的 /api/tongue, /api/wen/save 等零碎规则，统一归到 /api 下
    '/api': {
      target: 'http://localhost:8080',
      changeOrigin: true,
      // 如果 Java 后端没有额外的前缀，这里不需要 rewrite
    },
    '/uploads': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
  }
}
})
