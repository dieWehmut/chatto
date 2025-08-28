// 根据环境自动选择 API 地址
const getApiBaseUrl = () => {
  // 如果是 GitHub Pages 环境
  if (window.location.hostname.includes("github.io")) {
    // 从环境变量或默认配置获取服务器地址
    // 请在部署前将此地址替换为您的实际服务器地址
    const serverUrl =
      import.meta.env.VITE_PROD_API_URL || "http://YOUR_SERVER_IP:8000";
    if (serverUrl === "http://YOUR_SERVER_IP:8000") {
      console.warn(
        "警告: 请在 .env 文件中配置 VITE_PROD_API_URL 环境变量为您的服务器地址"
      );
    }
    return serverUrl;
  }
  // 本地开发环境
  return import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
};

export const API_BASE_URL = getApiBaseUrl();

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
