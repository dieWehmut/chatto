// 智能 API 地址配置
const getApiBaseUrl = () => {
  // 本地开发环境
  if (import.meta.env.DEV) {
    console.log('🔧 开发模式: 使用代理服务器')
    return '/api' // 使用 Vite 代理
  }

  // GitHub Pages 生产环境
  if (window.location.hostname.includes('github.io')) {
    const prodApiUrl = import.meta.env.VITE_PROD_API_URL
    if (!prodApiUrl || prodApiUrl === 'https://hc.lan') {
      console.error('❌ 错误: 请在 .env.production 文件中配置正确的 VITE_PROD_API_URL')
      alert('API 配置错误，请联系管理员')
      return 'http://localhost:8000' // 备用地址
    }
    console.log('� GitHub Pages 模式: 使用生产服务器', prodApiUrl)
    return prodApiUrl
  }

  // 其他生产环境
  const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
  console.log('🚀 生产模式: 使用配置的 API 地址', apiUrl)
  return apiUrl
}

export const API_BASE_URL = getApiBaseUrl()

console.log('� API 基础地址:', API_BASE_URL)

export async function apiGet(path) {
  const res = await fetch(`${API_BASE_URL}${path}`);
  if (!res.ok) {
    throw new Error(`GET ${path} failed: ${res.status}`);
  }
  return res.json();
}

export async function apiPost(path, body) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    let errorData;
    try {
      errorData = await res.json();
    } catch {
      const text = await res.text().catch(() => "");
      throw {
        response: { data: { detail: `Request failed: ${res.status} ${text}` } },
      };
    }
    throw { response: { data: errorData } };
  }
  return res.json();
}

export async function apiPut(path, body) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    let errorData;
    try {
      errorData = await res.json();
    } catch {
      const text = await res.text().catch(() => "");
      throw {
        response: { data: { detail: `Request failed: ${res.status} ${text}` } },
      };
    }
    throw { response: { data: errorData } };
  }
  return res.json();
}