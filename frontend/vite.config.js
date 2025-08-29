import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  // 修复 GitHub Pages 的 base 路径
  base: '/chatto1.0.0/',
  build: {
    outDir: 'dist',
    sourcemap: false,
    assetsDir: 'assets',
    // 确保资源路径正确
    rollupOptions: {
      output: {
        // 确保资源文件使用相对路径
        assetFileNames: 'assets/[name].[hash].[ext]',
        chunkFileNames: 'assets/[name].[hash].js',
        entryFileNames: 'assets/[name].[hash].js'
      }
    }
  },
  server: {
    port: 5173,
    host: true,
    open: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})