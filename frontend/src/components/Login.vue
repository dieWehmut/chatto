<template>
  <div class="login-container">
    <h1>欢迎</h1>
    <div class="login-form">
      <input 
        v-model="inviteCode" 
        type="text" 
        placeholder="请输入邀请码" 
        @keyup.enter="login"
        class="invite-input"
      />
      <button @click="login" :disabled="isLoading" class="login-btn">
        {{ isLoading ? '登录中...' : '进入聊天' }}
      </button>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

h1 {
  color: white;
  margin-bottom: 30px;
  font-size: 2.5em;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.login-form {
  background: white;
  padding: 40px;
  border-radius: 15px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  margin-bottom: 30px;
}

.invite-input {
  margin-bottom: 20px;
  padding: 15px;
  width: 300px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.invite-input:focus {
  outline: none;
  border-color: #667eea;
}

.login-btn {
  width: 100%;
  padding: 15px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.login-btn:hover:not(:disabled) {
  background: #5a67d8;
}

.login-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.error {
  color: #e53e3e;
  margin-top: 10px;
  text-align: center;
}

</style>