<template>
  <div class="chat-container">
    <div class="chat-header">
      <div class="user-info">
        <h3>{{ userInfo?.is_admin ? '管理员面板' : '聊天室' }}</h3>
        <span class="username">{{ userInfo?.username }}</span>
      </div>
      <button @click="logout" class="logout-btn">退出登录</button>
    </div>
    
    <div class="chat-content">
      <!-- 管理员用户列表 -->
      <div v-if="userInfo?.is_admin" class="users-panel">
        <h4>所有用户 ({{ allUsers.length }})</h4>
        <div class="users-list">
          <div 
            v-for="user in allUsers" 
            :key="user.id" 
            class="user-item"
            :class="{ active: selectedUserId === user.id, offline: !user.is_online }"
            @click="selectUser(user.id)"
          >
            <span class="user-name">{{ user.username }}</span>
            <span class="user-code">{{ user.invite_code }}</span>
            <span class="online-status" :class="{ offline: !user.is_online }">
              {{ user.is_online ? '🟢 在线' : '🔴 离线' }}
            </span>
          </div>
        </div>
      </div>

      <div class="chat-area">
        <div class="chat-box" ref="chatBox">
          <div v-if="messages.length === 0" class="no-messages">
            {{ userInfo?.is_admin ? '选择一个用户开始聊天' : '开始聊天吧！' }}
          </div>
          <div 
            v-for="message in messages" 
            :key="message.id" 
            class="message"
            :class="{ 
              'own-message': isOwnMessage(message),
              'other-message': !isOwnMessage(message)
            }"
          >
            <div class="message-header">
              <strong>{{ message.username }}</strong>
              <span class="timestamp">{{ formatTime(message.timestamp) }}</span>
              <button 
                v-if="message.can_delete" 
                @click="deleteMessage(message.id)"
                class="delete-btn"
                title="撤回消息"
              >
                🗑️
              </button>
            </div>
            <div class="message-content">
              <!-- 文本消息 -->
              <div v-if="message.message_type === 'text'">{{ message.content }}</div>
              
              <!-- 图片消息 -->
              <div v-else-if="message.message_type === 'image'" class="image-message">
                <img 
                  :src="`/api/chat/download/${message.id}`" 
                  :alt="message.file_name"
                  @click="openImage(`/api/chat/download/${message.id}`, message.file_name)"
                  class="message-image"
                />
                <div class="file-info">
                  {{ message.file_name }} ({{ formatFileSize(message.file_size) }})
                </div>
              </div>
              
              <!-- 文件消息 -->
              <div v-else-if="message.message_type === 'file'" class="file-message">
                <div class="file-icon">📄</div>
                <div class="file-details">
                  <div class="file-name">{{ message.file_name }}</div>
                  <div class="file-size">{{ formatFileSize(message.file_size) }}</div>
                  <button 
                    @click="downloadFile(message.id, message.file_name)"
                    class="download-btn"
                  >
                    下载
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="input-area">
          <!-- 文件预览区域 -->
          <div v-if="selectedFile" class="file-preview">
            <div class="file-preview-content">
              <div class="file-icon">
                <span v-if="isImageFile(selectedFile)">🖼️</span>
                <span v-else>📄</span>
              </div>
              <div class="file-info">
                <div class="file-name">{{ selectedFile.name }}</div>
                <div class="file-size">{{ formatFileSize(selectedFile.size) }}</div>
              </div>
              <button @click="removeSelectedFile" class="remove-file-btn" title="移除文件">
                ✕
              </button>
            </div>
          </div>

          <!-- 输入区域 -->
          <div class="message-input-container">
            <input
              v-model="newMessage"
              @keyup.enter="sendMessage"
              :placeholder="getInputPlaceholder()"
              class="message-input"
              :disabled="!canSendMessage()"
            />
            
            <!-- 文件上传按钮 -->
            <input
              ref="fileInput"
              type="file"
              @change="handleFileSelect"
              accept="image/*,.pdf,.doc,.docx,.txt,.xls,.xlsx"
              style="display: none"
            />
            
            <div class="input-buttons">
              <button 
                @click="triggerFileUpload" 
                :disabled="!canSendMessage()"
                class="file-btn"
                title="发送文件/图片"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M21.44 11.05l-9.19 9.19c-1.78 1.78-4.61 1.78-6.39 0s-1.78-4.61 0-6.39l9.19-9.19c1.05-1.05 2.73-1.05 3.78 0s1.05 2.73 0 3.78l-9.19 9.19c-.34.34-.87.34-1.21 0s-.34-.87 0-1.21l8.48-8.48"/>
                </svg>
              </button>
              
              <!-- 发送按钮 -->
              <button 
                @click="sendMessage" 
                :disabled="!canSendMessage() || (!newMessage.trim() && !selectedFile)"
                class="send-btn"
              >
                <svg v-if="selectedFile" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
                </svg>
                <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick, onUnmounted } from 'vue';
import { getUserInfo, clearUserInfo } from '../utils/storage';
import { apiGet, apiPost } from '../utils/api';

export default {
  setup() {
    const messages = ref([]);
    const users = ref([]);
    const onlineUsers = ref([]);
    const allUsers = ref([]);
    const newMessage = ref('');
    const userInfo = ref(null);
    const selectedUserId = ref(null);
    const selectedFile = ref(null);
    const fileInput = ref(null);

    const logout = async () => {
      // 设置用户离线状态
      if (userInfo.value) {
        try {
          await apiPost('/auth/update_online_status', {
            user_id: userInfo.value.user_id,
            is_online: false
          });
        } catch (err) {
          console.error('更新离线状态失败:', err);
        }
      }
      clearUserInfo();
      window.location.reload();
    };

    const updateOnlineStatus = async (isOnline) => {
      if (!userInfo.value) return;
      
      try {
        await apiPost('/auth/update_online_status', {
          user_id: userInfo.value.user_id,
          is_online: isOnline
        });
      } catch (err) {
        console.error('更新在线状态失败:', err);
      }
    };

    const loadUsers = async () => {
      try {
        const response = await apiGet('/chat/users');
        users.value = response;
        allUsers.value = response.filter(u => !u.is_admin); // 显示所有非管理员用户
        onlineUsers.value = response.filter(u => !u.is_admin && u.is_online);
        console.log('所有用户列表:', allUsers.value);
      } catch (err) {
        console.error('加载用户列表失败:', err);
      }
    };

    const deleteMessage = async (messageId) => {
      if (!confirm('确定要撤回这条消息吗？')) return;
      
      try {
        await apiPost('/chat/delete_message', {
          user_id: userInfo.value.user_id,
          message_id: messageId
        });
        
        // 重新加载聊天记录
        await loadChatHistory();
      } catch (err) {
        console.error('删除消息失败:', err);
        alert('撤回消息失败：' + (err.response?.data?.detail || err.message));
      }
    };

    const selectUser = (userId) => {
      selectedUserId.value = userId;
      loadChatHistory();
    };

    const isOwnMessage = (message) => {
      return message.username === userInfo.value?.username;
    };

    const loadChatHistory = async () => {
      if (!userInfo.value) return;
      
      try {
        let url = `/chat/chat_history/${userInfo.value.user_id}`;
        
        // 如果是管理员且选择了用户，添加target_user_id参数
        if (userInfo.value.is_admin && selectedUserId.value) {
          url += `?target_user_id=${selectedUserId.value}`;
        }
          
        const response = await apiGet(url);
        messages.value = response.messages || [];
        await nextTick();
        scrollToBottom();
      } catch (err) {
        console.error('加载聊天记录失败:', err);
      }
    };

    const sendMessage = async () => {
      // 如果选择了文件，发送文件（可以包含文字说明）
      if (selectedFile.value) {
        await sendFile();
      }
      // 如果只是文本消息
      else if (newMessage.value.trim()) {
        await sendTextMessage();
      }
    };

    const sendTextMessage = async () => {
      const text = newMessage.value.trim();
      if (!text || !canSendMessage()) return;

      try {
        const requestData = {
          user_id: userInfo.value.user_id,
          content: text
        };

        // 如果是管理员，添加目标用户ID
        if (userInfo.value.is_admin && selectedUserId.value) {
          requestData.target_user_id = selectedUserId.value;
        }

        await apiPost('/chat/send_message', requestData);
        
        newMessage.value = '';
        await loadChatHistory();
      } catch (err) {
        console.error('发送消息失败:', err);
        alert('消息发送失败，请重试');
      }
    };

    const sendFile = async () => {
      if (!selectedFile.value || !canSendMessage()) return;

      try {
        const formData = new FormData();
        formData.append('file', selectedFile.value);
        formData.append('user_id', userInfo.value.user_id.toString());
        
        // 如果有文字说明，也一起发送
        if (newMessage.value.trim()) {
          formData.append('description', newMessage.value.trim());
        }
        
        // 如果是管理员，添加目标用户ID
        if (userInfo.value.is_admin && selectedUserId.value) {
          formData.append('target_user_id', selectedUserId.value.toString());
        }

        const response = await fetch('/api/chat/upload_file', {
          method: 'POST',
          headers: {
            // 不设置Content-Type，让浏览器自动设置multipart/form-data边界
          },
          body: formData
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
        }
        
        selectedFile.value = null;
        newMessage.value = '';
        if (fileInput.value) {
          fileInput.value.value = '';
        }
        
        await loadChatHistory();
      } catch (err) {
        console.error('发送文件失败:', err);
        alert('文件发送失败：' + err.message);
      }
    };

    const triggerFileUpload = () => {
      if (fileInput.value) {
        fileInput.value.click();
      }
    };

    const handleFileSelect = (event) => {
      const file = event.target.files[0];
      if (!file) return;

      // 检查文件大小 (10MB)
      const maxSize = 10 * 1024 * 1024;
      if (file.size > maxSize) {
        alert('文件大小不能超过10MB');
        if (fileInput.value) {
          fileInput.value.value = '';
        }
        return;
      }

      // 检查文件类型
      const allowedTypes = [
        'image/jpeg', 'image/png', 'image/gif', 'image/webp',
        'text/plain', 'application/pdf', 
        'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      ];

      if (!allowedTypes.includes(file.type)) {
        alert('不支持的文件类型。支持图片、PDF、Word文档、Excel表格和文本文件。');
        if (fileInput.value) {
          fileInput.value.value = '';
        }
        return;
      }

      selectedFile.value = file;
      // 清空文本输入框，文件和文本分开发送
      newMessage.value = '';
    };

    const removeSelectedFile = () => {
      selectedFile.value = null;
      if (fileInput.value) {
        fileInput.value.value = '';
      }
    };

    const isImageFile = (file) => {
      return file && file.type.startsWith('image/');
    };

    const downloadFile = (messageId, fileName) => {
      const link = document.createElement('a');
      link.href = `/api/chat/download/${messageId}`;
      link.download = fileName || 'download';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    };

    const openImage = (url, fileName) => {
      window.open(url, '_blank');
    };

    const formatFileSize = (bytes) => {
      if (!bytes) return '0 B';
      const sizes = ['B', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(1024));
      return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
    };

    const canSendMessage = () => {
      if (!userInfo.value) return false;
      if (userInfo.value.is_admin) {
        return selectedUserId.value !== null;
      }
      return true;
    };

    const getInputPlaceholder = () => {
      if (!userInfo.value) return '请先登录...';
      if (userInfo.value.is_admin && !selectedUserId.value) {
        return '请先选择一个用户...';
      }
      if (selectedFile.value) {
        return '文件已选择，可以添加文字说明或直接发送...';
      }
      return '输入消息...';
    };

    const formatTime = (timestamp) => {
      const date = new Date(timestamp);
      return date.toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    };

    const scrollToBottom = () => {
      const chatBox = document.querySelector('.chat-box');
      if (chatBox) {
        setTimeout(() => {
          chatBox.scrollTop = chatBox.scrollHeight;
        }, 100);
      }
    };

    onMounted(async () => {
      userInfo.value = getUserInfo();
      console.log('当前用户信息:', userInfo.value);
      
      if (!userInfo.value) {
        window.location.reload();
        return;
      }

      // 设置用户在线状态
      await updateOnlineStatus(true);

      await loadChatHistory();
      
      if (userInfo.value.is_admin) {
        await loadUsers();
      }

      // 定期刷新聊天记录和用户列表
      setInterval(async () => {
        await loadChatHistory();
        if (userInfo.value.is_admin) {
          await loadUsers();
        }
        // 保持在线状态
        await updateOnlineStatus(true);
      }, 3000);
    });

    // 页面卸载时设置离线状态
    onUnmounted(async () => {
      await updateOnlineStatus(false);
    });

    // 监听页面关闭事件
    window.addEventListener('beforeunload', () => {
      if (userInfo.value) {
        // 使用navigator.sendBeacon发送异步请求
        navigator.sendBeacon('/api/auth/update_online_status', JSON.stringify({
          user_id: userInfo.value.user_id,
          is_online: false
        }));
      }
    });

    return {
      messages,
      users,
      onlineUsers,
      allUsers,
      newMessage,
      userInfo,
      selectedUserId,
      selectedFile,
      fileInput,
      sendMessage,
      loadChatHistory,
      selectUser,
      logout,
      canSendMessage,
      getInputPlaceholder,
      formatTime,
      isOwnMessage,
      deleteMessage,
      triggerFileUpload,
      handleFileSelect,
      removeSelectedFile,
      isImageFile,
      downloadFile,
      openImage,
      formatFileSize,
    };
  },
};
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f5f5;
}

.chat-header {
  background: #667eea;
  color: white;
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-info h3 {
  margin: 0;
  font-size: 1.2em;
}

.username {
  font-size: 0.9em;
  opacity: 0.9;
}

.logout-btn {
  background: rgba(255,255,255,0.2);
  border: 1px solid rgba(255,255,255,0.3);
  color: white;
  padding: 8px 16px;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.logout-btn:hover {
  background: rgba(255,255,255,0.3);
}

.chat-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.users-panel {
  width: 250px;
  background: white;
  border-right: 1px solid #ddd;
  padding: 20px;
  overflow-y: auto;
}

.users-panel h4 {
  margin: 0 0 15px 0;
  color: #333;
}

.user-item {
  padding: 12px;
  margin: 5px 0;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s;
  border: 1px solid #eee;
}

.user-item:hover {
  background: #f0f0f0;
}

.user-item.active {
  background: #667eea;
  color: white;
}

.user-item.offline {
  opacity: 0.6;
}

.user-item.offline .user-name {
  color: #999;
}

.user-name {
  display: block;
  font-weight: bold;
}

.user-code {
  display: block;
  font-size: 0.8em;
  opacity: 0.7;
  margin-top: 4px;
}

.online-status {
  display: block;
  font-size: 0.7em;
  color: #4CAF50;
  margin-top: 2px;
}

.online-status.offline {
  color: #f44336;
}

.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-box {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: white;
}

.no-messages {
  text-align: center;
  color: #999;
  margin-top: 50px;
  font-style: italic;
}

.message {
  margin-bottom: 15px;
  max-width: 70%;
}

.own-message {
  margin-left: auto;
  margin-right: 0;
}

.other-message {
  margin-left: 0;
  margin-right: auto;
}

.own-message .message-content {
  background: #667eea;
  color: white;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
  font-size: 0.9em;
}

.delete-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.8em;
  opacity: 0.7;
  transition: opacity 0.3s;
  padding: 2px 4px;
  border-radius: 3px;
}

.delete-btn:hover {
  opacity: 1;
  background: rgba(255, 0, 0, 0.1);
}

.timestamp {
  color: #999;
  font-size: 0.8em;
}

.message-content {
  background: #f0f0f0;
  padding: 10px 15px;
  border-radius: 15px;
  word-wrap: break-word;
}

.input-area {
  padding: 20px;
  background: white;
  border-top: 1px solid #ddd;
}

.file-preview {
  margin-bottom: 15px;
}

.file-preview-content {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #f8f9fa;
  border: 2px dashed #667eea;
  border-radius: 8px;
  position: relative;
}

.file-preview .file-icon {
  font-size: 24px;
}

.file-preview .file-info {
  flex: 1;
}

.file-preview .file-name {
  font-weight: 500;
  color: #333;
  margin-bottom: 2px;
}

.file-preview .file-size {
  font-size: 0.85em;
  color: #666;
}

.remove-file-btn {
  background: #dc3545;
  color: white;
  border: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  transition: background-color 0.2s;
}

.remove-file-btn:hover {
  background: #c82333;
}

.message-input-container {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.message-input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e9ecef;
  border-radius: 25px;
  outline: none;
  font-size: 14px;
  resize: none;
  transition: border-color 0.2s;
}

.message-input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.message-input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.input-buttons {
  display: flex;
  gap: 8px;
}

.file-btn {
  width: 48px;
  height: 48px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(40, 167, 69, 0.3);
}

.file-btn:hover:not(:disabled) {
  background: #218838;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(40, 167, 69, 0.4);
}

.file-btn:active:not(:disabled) {
  transform: translateY(0);
}

.file-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
  box-shadow: none;
}

.send-btn {
  width: 48px;
  height: 48px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(102, 126, 234, 0.3);
}

.send-btn:hover:not(:disabled) {
  background: #5a67d8;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.4);
}

.send-btn:active:not(:disabled) {
  transform: translateY(0);
}

.send-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
  box-shadow: none;
}

/* 文件消息样式 */
.image-message {
  max-width: 300px;
}

.message-image {
  max-width: 100%;
  max-height: 200px;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s;
}

.message-image:hover {
  transform: scale(1.02);
}

.file-message {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #f9f9f9;
  max-width: 300px;
}

.file-icon {
  font-size: 24px;
}

.file-details {
  flex: 1;
}

.file-name {
  font-weight: bold;
  margin-bottom: 4px;
  word-break: break-word;
}

.file-size {
  font-size: 0.8em;
  color: #666;
  margin-bottom: 8px;
}

.file-info {
  font-size: 0.8em;
  color: #666;
  margin-top: 5px;
}

.download-btn {
  padding: 4px 8px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8em;
  transition: background-color 0.3s;
}

.download-btn:hover {
  background: #0056b3;
}
</style>