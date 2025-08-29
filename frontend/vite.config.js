import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ command, mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd(), '')
  
  // 判断是否为 GitHub Pages 构建
  const isGitHubPages = mode === 'production' || process.env.GITHUB_PAGES === 'true'
  
  return {
    plugins: [vue()],
    
    // 🔥 关键修复：本地开发用根路径，生产环境用 GitHub Pages 路径
    base: mode === 'development' ? '/' : '/chatto1.0.0/',
    
    // 定义全局变量
    define: {
      __IS_GITHUB_PAGES__: isGitHubPages
    },
    
    build: {
      outDir: 'dist',
      sourcemap: false,
      assetsDir: 'assets',
      rollupOptions: {
        output: {
          assetFileNames: 'assets/[name].[hash].[ext]',
          chunkFileNames: 'assets/[name].[hash].js',
          entryFileNames: 'assets/[name].[hash].js'
        }
      }
    },
    
    server: {
      port: 5173,
      host: '0.0.0.0', // 允许外部访问
      open: true,
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
          // 添加错误处理
          configure: (proxy, options) => {
            proxy.on('error', (err, req, res) => {
              console.log('proxy error', err)
            })
            proxy.on('proxyReq', (proxyReq, req, res) => {
              console.log('Sending Request to the Target:', req.method, req.url)
            })
            proxy.on('proxyRes', (proxyRes, req, res) => {
              console.log('Received Response from the Target:', proxyRes.statusCode, req.url)
            })
          }
        }
      }
    }
  }
})