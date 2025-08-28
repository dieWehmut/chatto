<template>
  <div class="login-container">
    <div class="header-icons">
      <span class="icon">💭</span>
      <span class="icon">🤝</span>
      <span class="icon">✨</span>
    </div>
    <h1> 欢迎 </h1>
    <div class="subtitle">
      <span class="subtitle-icon"></span>
      <a href="https://diewehmut.github.io/dieSWNexus/" target="_blank" class="main-site-link">
        总站 🏠
      </a>
    </div>
    
    <div class="login-form">
      <div class="form-header">
        <span class="form-icon">🔐</span>
        <span class="form-title">身份验证</span>
      </div>
      
      <div class="input-group">
        <span class="input-icon">🎫</span>
        <input 
          v-model="inviteCode" 
          type="text" 
          placeholder="请输入您的邀请码" 
          @keyup.enter="login"
          class="invite-input"
        />
      </div>
      
      <button @click="login" :disabled="isLoading" class="login-btn">
        <span class="btn-icon">{{ isLoading ? '⏳' : '🚀' }}</span>
        {{ isLoading ? '验证中...' : '开始聊天' }}
      </button>
      
      <p v-if="errorMessage" class="error">
        <span class="error-icon">⚠️</span>
        {{ errorMessage }}
      </p>
      

    </div>
    

  </div>
</template>

<script>
import { ref } from 'vue';
import { saveUserInfo } from '../utils/storage';
import { apiPost } from '../utils/api';

export default {
  setup() {
    const inviteCode = ref('');
    const errorMessage = ref('');
    const isLoading = ref(false);

    const login = async () => {
      errorMessage.value = '';
      const code = inviteCode.value.trim();
      if (!code) {
        errorMessage.value = '请输入邀请码';
        return;
      }

      isLoading.value = true;
      try {
        const response = await apiPost('/auth/login', { invite_code: code });
        saveUserInfo(response);
        // 重新加载页面以切换到聊天界面
        window.location.reload();
      } catch (err) {
        console.error(err);
        errorMessage.value = err.response?.data?.detail || '邀请码无效，请重试';
      } finally {
        isLoading.value = false;
      }
    };

    return {
      inviteCode,
      login,
      errorMessage,
      isLoading,
    };
  },
};
</script>

<style scoped>
.login-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #cbd5e0 100%);
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.header-icons {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
  opacity: 0.6;
}

.header-icons .icon {
  font-size: 1.8em;
  filter: grayscale(50%) brightness(0.9);
  transition: all 0.3s ease;
  animation: float 3s ease-in-out infinite;
}

.header-icons .icon:nth-child(1) { animation-delay: 0s; }
.header-icons .icon:nth-child(2) { animation-delay: 1s; }
.header-icons .icon:nth-child(3) { animation-delay: 2s; }

.header-icons .icon:hover {
  filter: grayscale(20%) brightness(1.1);
  transform: scale(1.1);
}

h1 {
  color: #475569;
  margin-bottom: 15px;
  font-size: 2.2em;
  font-weight: 300;
  text-shadow: none;
  letter-spacing: -0.5px;
  opacity: 0.9;
}

.subtitle {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 35px;
}

.subtitle-icon {
  font-size: 1.1em;
  opacity: 0.6;
  filter: grayscale(40%);
}

.main-site-link {
  color: #64748b;
  text-decoration: none;
  font-size: 1.1em;
  font-weight: 400;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  transition: all 0.3s ease;
  border-bottom: 1px solid transparent;
}

.main-site-link:hover {
  color: #475569;
  border-bottom-color: #64748b;
  transform: translateY(-1px);
}

.login-form {
  background: rgba(255, 255, 255, 0.95);
  padding: 50px 40px;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.08);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  width: 100%;
  max-width: 400px;
  text-align: center;
  position: relative;
}

.form-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 30px;
}

.form-icon {
  font-size: 1.5em;
  opacity: 0.7;
  filter: grayscale(30%);
}

.form-title {
  color: #64748b;
  font-size: 1.1em;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.input-group {
  position: relative;
  margin-bottom: 25px;
}

.input-icon {
  position: absolute;
  left: 18px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.2em;
  opacity: 0.5;
  filter: grayscale(50%);
  z-index: 2;
  pointer-events: none;
}

.invite-input {
  padding: 18px 20px 18px 55px;
  width: 100%;
  box-sizing: border-box;
  border: 2px solid rgba(203, 213, 224, 0.5);
  border-radius: 12px;
  font-size: 16px;
  font-weight: 400;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.9);
  color: #2d3748;
}

.invite-input:focus {
  outline: none;
  border-color: #94a3b8;
  box-shadow: 0 0 0 3px rgba(148, 163, 184, 0.1);
  background: rgba(255, 255, 255, 1);
}

.invite-input:focus + .input-icon {
  opacity: 0.8;
  filter: grayscale(20%);
}

.invite-input::placeholder {
  color: #a0aec0;
}

.login-btn {
  width: 100%;
  padding: 18px;
  background: linear-gradient(135deg, #94a3b8, #64748b);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(148, 163, 184, 0.2);
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-icon {
  font-size: 1.1em;
  filter: brightness(1.2);
}

.login-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #64748b, #475569);
  transform: translateY(-1px);
  box-shadow: 0 8px 25px rgba(148, 163, 184, 0.25);
}

.login-btn:disabled {
  background: linear-gradient(135deg, #e2e8f0, #cbd5e0);
  color: #a0aec0;
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 2px 8px rgba(148, 163, 184, 0.1);
}

.error {
  color: #94a3b8;
  margin-top: 15px;
  text-align: center;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.error-icon {
  font-size: 1em;
  opacity: 0.8;
  filter: sepia(100%) saturate(0%) brightness(0.8);
}

.footer-decorations {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 30px;
  opacity: 0.4;
}

.decoration {
  font-size: 1.2em;
  filter: grayscale(60%) brightness(0.8);
  animation: twinkle 2s ease-in-out infinite;
}

.decoration:nth-child(1) { animation-delay: 0s; }
.decoration:nth-child(2) { animation-delay: 0.4s; }
.decoration:nth-child(3) { animation-delay: 0.8s; }
.decoration:nth-child(4) { animation-delay: 1.2s; }
.decoration:nth-child(5) { animation-delay: 1.6s; }

.bottom-decorations {
  position: absolute;
  bottom: 30px;
  display: flex;
  gap: 30px;
  opacity: 0.3;
}

.floating-icon {
  font-size: 1.5em;
  filter: grayscale(70%) brightness(0.7);
  animation: gentle-float 4s ease-in-out infinite;
}

.floating-icon:nth-child(1) { animation-delay: 0s; }
.floating-icon:nth-child(2) { animation-delay: 1s; }
.floating-icon:nth-child(3) { animation-delay: 2s; }
.floating-icon:nth-child(4) { animation-delay: 3s; }

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-8px); }
}

@keyframes twinkle {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.8; }
}

@keyframes gentle-float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  25% { transform: translateY(-5px) rotate(2deg); }
  75% { transform: translateY(-3px) rotate(-2deg); }
}

/* 响应式设计 */
@media (max-width: 480px) {
  .header-icons {
    gap: 15px;
  }
  
  .header-icons .icon {
    font-size: 1.5em;
  }
  
  h1 {
    font-size: 1.8em;
  }
  
  .bottom-decorations {
    gap: 20px;
  }
  
  .floating-icon {
    font-size: 1.2em;
  }
}
</style>