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
    // 代理配置
    proxy: {
      '/api': {
        target: 'http://localhost:5000', // 后端接口地址（FastAPI 运行在 5000 端口）
        changeOrigin: true,             // 是否允许跨域
        rewrite: (path) => path.replace(/^\/api/, '')  // 移除 /api 前缀转发给后端
      }
    }
  }
})
