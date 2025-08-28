<template>
  <div class="chat-container">
    <div class="chat-header">
      <div class="user-info">
        <h3>{{ userInfo?.is_admin ? '管理员面板' : '聊天室' }}</h3>
        
      </div>
      <div class="header-buttons">
        <button v-if="userInfo?.is_admin" @click="showUserManagement = true" class="manage-btn">
          👥 用户管理
        </button>
        <button @click="logout" class="logout-btn">退出登录</button>
      </div>
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

      <!-- 普通用户界面：直接显示聊天区域 -->

      <div class="chat-area" :class="{ 'full-width': !userInfo?.is_admin }">
        <!-- 普通用户：显示管理员在线状态 -->
        <div v-if="!userInfo?.is_admin" class="admin-status-bar">
          <div class="admin-status">
            <span class="status-label">管理员状态:</span>
            <span v-if="adminOnlineStatus" class="status-indicator online">
              👑 {{ adminOnlineStatus.username }} - 🟢 在线
            </span>
            <span v-else class="status-indicator offline">
              👑 管理员 - 🔴 离线
            </span>
          </div>
        </div>
        
        <!-- 管理员：聊天工具栏 -->
        <div v-if="userInfo?.is_admin && selectedUserId" class="chat-toolbar">
          <div class="toolbar-left">
            <span class="selected-user-info">
              与 <strong>{{ getSelectedUserName() }}</strong> 的对话
            </span>
          </div>
          <div class="toolbar-right">
            <button @click="clearChatHistory" class="clear-btn" title="清空聊天记录">
              🧹 清屏
            </button>
          </div>
        </div>
        
        <div class="chat-box" ref="chatBoxRef">
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
              <template v-if="isOwnMessage(message)">
                <!-- 自己的消息：名字、时间、删除按钮 -->
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
              </template>
              <template v-else>
                <!-- 他人的消息：名字、时间、删除按钮 -->
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
              </template>
            </div>
            <div class="message-content">
              <!-- 文本消息 -->
              <div v-if="message.message_type === 'text'" class="text-message">
                {{ message.content }}
              </div>
              
              <!-- 图片消息 -->
              <div v-else-if="message.message_type === 'image'" class="image-message">
                <!-- 显示文字说明部分 -->
                <div v-if="getFileDescription(message.content)" class="file-description">
                  {{ getFileDescription(message.content) }}
                </div>
                <img 
                  :src="`/api/chat/download/${message.id}`" 
                  :alt="message.file_name"
                  @click="previewFile(message)"
                  class="message-image"
                />
                <div class="file-info">
                  🖼️ {{ message.file_name || '图片文件' }} ({{ formatFileSize(message.file_size) }})
                  <button 
                    @click="previewFile(message)"
                    class="preview-btn"
                    title="预览图片"
                  >
                    🔍 预览
                  </button>
                </div>
              </div>
              
              <!-- 文件消息 -->
              <div v-else-if="message.message_type === 'file'" class="file-message">
                <!-- 显示文字说明部分 -->
                <div v-if="getFileDescription(message.content)" class="file-description">
                  {{ getFileDescription(message.content) }}
                </div>
                <div class="file-container">
                  <div class="file-icon">{{ getFileIcon(message.file_name) }}</div>
                  <div class="file-details">
                    <div class="file-name">{{ message.file_name || '未知文件' }}</div>
                    <div class="file-size">{{ formatFileSize(message.file_size) }}</div>
                    <div class="file-actions">
                      <!-- 预览按钮（根据文件类型决定是否显示） -->
                      <button 
                        v-if="canPreviewFile(message.file_name)"
                        @click="previewFile(message)"
                        class="preview-btn"
                        title="预览文件"
                      >
                        👁️ 预览
                      </button>
                      <!-- 用系统应用打开按钮 -->
                      <button 
                        @click="openWithApp(message.id, message.file_name)"
                        class="open-app-btn"
                        title="用默认应用打开"
                      >
                        🔗 打开
                      </button>
                      <button 
                        @click="downloadFile(message.id, message.file_name)"
                        class="download-btn"
                      >
                        📥 下载
                      </button>
                    </div>
                  </div>
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
            <textarea
              v-model="newMessage"
              @keydown="handleKeyDown"
              :placeholder="getInputPlaceholder()"
              class="message-input"
              :disabled="!canSendMessage()"
              ref="textareaRef"
              rows="1"
            ></textarea>
            
            <!-- 文件上传按钮 -->
            <input
              ref="fileInput"
              type="file"
              @change="handleFileSelect"
              style="display: none"
            />
            
            <div class="input-buttons">
              <button 
                @click="triggerFileUpload" 
                :disabled="!canSendMessage()"
                class="file-btn"
                title="📎 发送任意文件"
              >
                📎
              </button>
              
              <!-- 发送按钮 -->
              <button 
                @click="sendMessage" 
                :disabled="!canSendMessage() || (!newMessage.trim() && !selectedFile)"
                class="send-btn"
                :title="selectedFile ? '🚀 发送文件' : '💬 发送消息'"
              >
                {{ selectedFile ? '🚀' : '💬' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 文件预览模态框 -->
    <div v-if="previewModal.show" class="preview-modal" @click="closePreview">
      <div class="preview-modal-content" @click.stop>
        <div class="preview-header">
          <h3 class="preview-title">{{ previewModal.fileName }}</h3>
          <button @click="closePreview" class="close-btn" title="关闭预览">✕</button>
        </div>
        
        <div class="preview-body">
          <!-- 图片预览 -->
          <div v-if="previewModal.type === 'image'" class="image-preview">
            <img 
              :src="previewModal.url" 
              :alt="previewModal.fileName"
              class="preview-image"
              @load="onImageLoad"
            />
          </div>
          
          <!-- 代码文件预览 -->
          <div v-else-if="previewModal.type === 'code'" class="code-preview">
            <div v-if="previewModal.loading" class="loading">
              📄 正在加载文件内容...
            </div>
            <div v-else-if="previewModal.error" class="error">
              ❌ 加载失败: {{ previewModal.error }}
            </div>
            <pre v-else class="code-content"><code>{{ previewModal.content }}</code></pre>
          </div>
          
          <!-- 其他文件预览提示 -->
          <div v-else class="unsupported-preview">
            <div class="file-icon-large">{{ getFileIcon(previewModal.fileName) }}</div>
            <h4>{{ previewModal.fileName }}</h4>
            <p>此文件类型暂不支持在线预览</p>
            <div class="preview-actions">
              <button @click="downloadFromPreview" class="action-btn download">
                📥 下载文件
              </button>
              <button @click="openWithAppFromPreview" class="action-btn open">
                🔗 用默认应用打开
              </button>
            </div>
          </div>
        </div>
        
        <div class="preview-footer">
          <div class="file-info-detailed">
            <span>文件大小: {{ formatFileSize(previewModal.fileSize) }}</span>
            <span v-if="previewModal.type === 'image'" class="image-dimensions">
              {{ previewModal.dimensions }}
            </span>
          </div>
          <div class="preview-actions">
            <button @click="downloadFromPreview" class="action-btn">📥 下载</button>
            <button @click="openWithAppFromPreview" class="action-btn">🔗 打开</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 用户管理模态框 -->
  <div v-if="showUserManagement" class="modal-overlay" @click="closeUserManagement">
    <div class="modal-content user-management-modal" @click.stop>
      <div class="modal-header">
        <h3>👥 用户管理</h3>
        <button @click="closeUserManagement" class="close-btn">✕</button>
      </div>
      
      <div class="modal-body">
        <!-- 创建新用户 -->
        <div class="section">
          <h4>📝 创建新用户</h4>
          <div class="form-group">
            <label>用户名:</label>
            <input v-model="newUserForm.username" type="text" placeholder="输入用户名" />
          </div>
          <div class="form-group">
            <label>邀请码:</label>
            <input v-model="newUserForm.invite_code" type="text" placeholder="输入邀请码" />
          </div>
          <div class="form-group">
            <label>
              <input v-model="newUserForm.is_admin" type="checkbox" />
              管理员权限
            </label>
          </div>
          <button @click="createUser" class="action-btn primary" :disabled="!newUserForm.username || !newUserForm.invite_code">
            ➕ 创建用户
          </button>
        </div>

        <!-- 用户列表 -->
        <div class="section">
          <h4>👥 用户列表</h4>
          <div class="users-table">
            <div class="table-header">
              <span>用户名</span>
              <span>邀请码</span>
              <span>权限</span>
              <span>状态</span>
              <span>操作</span>
            </div>
            <div v-for="user in managementUsers" :key="user.id" class="table-row">
              <span class="username">{{ user.username }}</span>
              <span class="invite-code">{{ user.invite_code }}</span>
              <span class="admin-badge" :class="{ admin: user.is_admin }">
                {{ user.is_admin ? '👑 管理员' : '👤 普通用户' }}
              </span>
              <span class="status" :class="{ online: user.is_online }">
                {{ user.is_online ? '🟢 在线' : '🔴 离线' }}
              </span>
              <div class="actions">
                <button @click="startEditUser(user)" class="edit-btn" title="编辑用户">
                  ✏️
                </button>
                <button v-if="user.id !== userInfo.user_id" @click="deleteUser(user)" 
                        class="delete-btn" title="删除用户">
                  🗑️
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 编辑用户模态框 -->
  <div v-if="showEditUser" class="modal-overlay" @click="closeEditUser">
    <div class="modal-content edit-user-modal" @click.stop>
      <div class="modal-header">
        <h3>✏️ 编辑用户</h3>
        <button @click="closeEditUser" class="close-btn">✕</button>
      </div>
      
      <div class="modal-body">
        <div class="form-group">
          <label>用户名:</label>
          <input v-model="editUserForm.username" type="text" placeholder="输入新用户名" />
        </div>
        <div class="form-group">
          <label>邀请码:</label>
          <input v-model="editUserForm.invite_code" type="text" placeholder="输入新邀请码" />
        </div>
        <div class="form-group">
          <label>
            <input v-model="editUserForm.is_admin" type="checkbox" />
            管理员权限
          </label>
        </div>
        <div class="modal-actions">
          <button @click="closeEditUser" class="cancel-btn">取消</button>
          <button @click="updateUser" class="action-btn primary">保存修改</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick, onUnmounted, watch } from 'vue';
import { getUserInfo, clearUserInfo } from '../utils/storage';
import { apiGet, apiPost, apiPut } from '../utils/api';

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
    const textareaRef = ref(null);
    const chatBoxRef = ref(null);
    
    // 管理员在线状态（用于普通用户界面）
    const adminOnlineStatus = ref(null);
    
    // 用户管理相关状态
    const showUserManagement = ref(false);
    const showEditUser = ref(false);
    const managementUsers = ref([]);
    const newUserForm = ref({
      username: '',
      invite_code: '',
      is_admin: false
    });
    const editUserForm = ref({
      id: null,
      username: '',
      invite_code: '',
      is_admin: false
    });
    
    // 文件预览相关
    const previewModal = ref({
      show: false,
      type: '', // 'image', 'code', 'other'
      fileName: '',
      fileSize: 0,
      url: '',
      content: '',
      loading: false,
      error: '',
      messageId: null,
      dimensions: ''
    });

    // 处理键盘事件
    const handleKeyDown = (event) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
      }
    };

    // 自动调整文本域高度
    const adjustTextareaHeight = () => {
      const textarea = textareaRef.value;
      if (textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
      }
    };

    // 监听输入变化
    const watchNewMessage = () => {
      nextTick(() => {
        adjustTextareaHeight();
      });
    };

    // 提取文件描述（从content中提取文字说明部分）
    const getFileDescription = (content) => {
      if (!content) return '';
      // 匹配格式：[IMAGE/FILE] 文件名 - 说明内容
      const match = content.match(/\[(IMAGE|FILE)\] .+ - (.+)/);
      return match ? match[2] : '';
    };

    // 根据文件类型获取对应的emoji图标
    const getFileIcon = (fileName) => {
      if (!fileName) return '📄';
      
      const extension = fileName.toLowerCase().split('.').pop();
      const iconMap = {
        'pdf': '📋',
        'doc': '📝',
        'docx': '📝',
        'txt': '📄',
        'xls': '📊',
        'xlsx': '📊',
        'ppt': '📊',
        'pptx': '📊',
        'zip': '🗜️',
        'rar': '🗜️',
        '7z': '🗜️',
        'mp3': '🎵',
        'mp4': '🎬',
        'avi': '🎬',
        'mov': '🎬',
        'jpg': '🖼️',
        'jpeg': '🖼️',
        'png': '🖼️',
        'gif': '🖼️',
        'webp': '🖼️'
      };
      
      return iconMap[extension] || '📄';
    };

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
        
        if (userInfo.value?.is_admin) {
          // 管理员看到所有用户
          allUsers.value = response;
          onlineUsers.value = response.filter(u => u.is_online);
        } else {
          // 普通用户看到所有用户（包括管理员）
          allUsers.value = response;
          onlineUsers.value = response.filter(u => u.is_online);
          
          // 设置管理员在线状态
          const onlineAdmin = response.find(u => u.is_admin && u.is_online);
          adminOnlineStatus.value = onlineAdmin || null;
        }
        
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
        
        // 重新加载聊天记录，不自动滚动（保持当前位置）
        await loadChatHistory(false);
      } catch (err) {
        console.error('删除消息失败:', err);
        alert('撤回消息失败：' + (err.response?.data?.detail || err.message));
      }
    };

    const selectUser = (userId) => {
      selectedUserId.value = userId;
      loadChatHistory(true); // 选择用户时，滚动到底部
    };

    const isOwnMessage = (message) => {
      return message.username === userInfo.value?.username;
    };

    const loadChatHistory = async (shouldScrollToBottom = false) => {
      if (!userInfo.value) return;
      
      try {
        let url = `/chat/chat_history/${userInfo.value.user_id}`;
        
        // 如果是管理员且选择了用户，添加target_user_id参数
        if (userInfo.value.is_admin && selectedUserId.value) {
          url += `?target_user_id=${selectedUserId.value}`;
        }
          
        const response = await apiGet(url);
        const oldMessagesLength = messages.value.length;
        messages.value = response.messages || [];
        
        // 调试：检查文件消息的数据
        const fileMessages = messages.value.filter(m => m.message_type === 'file' || m.message_type === 'image');
        if (fileMessages.length > 0) {
          console.log('文件消息数据:', fileMessages.map(m => ({
            id: m.id,
            file_name: m.file_name,
            message_type: m.message_type,
            content: m.content
          })));
        }
        
        await nextTick();
        
        // 只在以下情况下自动滚动到底部：
        // 1. 明确要求滚动到底部（shouldScrollToBottom = true）
        // 2. 这是新消息（消息数量增加了）
        // 3. 用户当前就在底部附近（距离底部小于100px）
        if (shouldScrollToBottom || 
            (messages.value.length > oldMessagesLength) ||
            isNearBottom()) {
          scrollToBottom();
        }
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
        await loadChatHistory(true); // 发送消息后滚动到底部
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
        
        await loadChatHistory(true); // 发送文件后滚动到底部
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
        alert('⚠️ 文件大小不能超过10MB');
        if (fileInput.value) {
          fileInput.value.value = '';
        }
        return;
      }

      selectedFile.value = file;
      // 保留文本输入框的内容作为文件说明
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

    // 判断文件是否可以预览
    const canPreviewFile = (fileName) => {
      if (!fileName) return false;
      
      const extension = fileName.toLowerCase().split('.').pop();
      const previewableExtensions = [
        // 图片
        'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg',
        // 代码和文本
        'txt', 'md', 'json', 'xml', 'html', 'css', 'js', 'ts', 'jsx', 'tsx',
        'py', 'java', 'cpp', 'c', 'h', 'cs', 'php', 'rb', 'go', 'rs', 'swift',
        'kt', 'scala', 'sql', 'yml', 'yaml', 'ini', 'conf', 'log',
        'vue', 'svelte', 'astro'
      ];
      
      return previewableExtensions.includes(extension);
    };

    // 获取文件预览类型
    const getFilePreviewType = (fileName) => {
      if (!fileName) return 'other';
      
      const extension = fileName.toLowerCase().split('.').pop();
      
      // 图片类型
      if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg'].includes(extension)) {
        return 'image';
      }
      
      // 代码和文本类型
      if ([
        'txt', 'md', 'json', 'xml', 'html', 'css', 'js', 'ts', 'jsx', 'tsx',
        'py', 'java', 'cpp', 'c', 'h', 'cs', 'php', 'rb', 'go', 'rs', 'swift',
        'kt', 'scala', 'sql', 'yml', 'yaml', 'ini', 'conf', 'log',
        'vue', 'svelte', 'astro'
      ].includes(extension)) {
        return 'code';
      }
      
      return 'other';
    };

    // 预览文件
    const previewFile = async (message) => {
      const previewType = getFilePreviewType(message.file_name);
      
      previewModal.value = {
        show: true,
        type: previewType,
        fileName: message.file_name,
        fileSize: message.file_size,
        messageId: message.id,
        url: `/api/chat/download/${message.id}`,
        content: '',
        loading: false,
        error: '',
        dimensions: ''
      };
      
      // 如果是代码文件，需要加载内容
      if (previewType === 'code') {
        await loadFileContent(message.id);
      }
    };

    // 加载文件内容（用于代码预览）
    const loadFileContent = async (messageId) => {
      previewModal.value.loading = true;
      previewModal.value.error = '';
      
      try {
        const response = await fetch(`/api/chat/download/${messageId}`);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const text = await response.text();
        previewModal.value.content = text;
      } catch (error) {
        console.error('加载文件内容失败:', error);
        previewModal.value.error = error.message;
      } finally {
        previewModal.value.loading = false;
      }
    };

    // 图片加载完成时获取尺寸
    const onImageLoad = (event) => {
      const img = event.target;
      previewModal.value.dimensions = `${img.naturalWidth} × ${img.naturalHeight}`;
    };

    // 关闭预览
    const closePreview = () => {
      previewModal.value.show = false;
      // 清理数据
      setTimeout(() => {
        previewModal.value = {
          show: false,
          type: '',
          fileName: '',
          fileSize: 0,
          url: '',
          content: '',
          loading: false,
          error: '',
          messageId: null,
          dimensions: ''
        };
      }, 300);
    };

    // 从预览框下载文件
    const downloadFromPreview = () => {
      if (previewModal.value.messageId) {
        downloadFile(previewModal.value.messageId, previewModal.value.fileName);
      }
    };

    // 用系统应用打开文件
    const openWithApp = async (messageId, fileName) => {
      try {
        // 首先下载文件到临时位置
        const link = document.createElement('a');
        link.href = `/api/chat/download/${messageId}`;
        link.target = '_blank'; // 在新标签页打开，让浏览器处理
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } catch (error) {
        console.error('打开文件失败:', error);
        alert('打开文件失败，请尝试下载后手动打开');
      }
    };

    // 从预览框用系统应用打开
    const openWithAppFromPreview = () => {
      if (previewModal.value.messageId) {
        openWithApp(previewModal.value.messageId, previewModal.value.fileName);
      }
    };

    const openImage = (url, fileName) => {
      // 这个方法保留用于兼容，但推荐使用previewFile
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
      if (!userInfo.value) return '📝 请先登录...';
      if (userInfo.value.is_admin && !selectedUserId.value) {
        return '👆 请先选择一个用户...';
      }
      if (selectedFile.value) {
        return '📎 文件已选择，可以添加说明文字 ✨';
      }
      return '💭 输入消息...';
    };

    const formatTime = (timestamp) => {
      // 创建Date对象，JavaScript会自动处理时区转换
      let date = new Date(timestamp);
      
      // 如果时间戳看起来是UTC格式，确保正确解析
      if (typeof timestamp === 'string' && !timestamp.includes('+') && !timestamp.endsWith('Z')) {
        // 如果后端返回的时间戳没有时区信息，假设它是UTC时间
        date = new Date(timestamp + 'Z');
      }
      
      const now = new Date();
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      const messageDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());
      
      // 如果是今天的消息，只显示时间
      if (messageDate.getTime() === today.getTime()) {
        return date.toLocaleTimeString('zh-CN', { 
          hour: '2-digit', 
          minute: '2-digit'
        });
      }
      // 如果是昨天的消息，显示"昨天 + 时间"
      else if (messageDate.getTime() === today.getTime() - 24 * 60 * 60 * 1000) {
        return '昨天 ' + date.toLocaleTimeString('zh-CN', { 
          hour: '2-digit', 
          minute: '2-digit'
        });
      }
      // 其他日期，显示月日 + 时间
      else {
        return date.toLocaleDateString('zh-CN', { 
          month: '2-digit', 
          day: '2-digit'
        }) + ' ' + date.toLocaleTimeString('zh-CN', { 
          hour: '2-digit', 
          minute: '2-digit'
        });
      }
    };

    const scrollToBottom = () => {
      const chatBox = chatBoxRef.value;
      if (chatBox) {
        setTimeout(() => {
          chatBox.scrollTop = chatBox.scrollHeight;
        }, 100);
      }
    };

    const isNearBottom = () => {
      const chatBox = chatBoxRef.value;
      if (!chatBox) return true; // 如果没有chatBox，默认认为在底部
      
      const { scrollTop, scrollHeight, clientHeight } = chatBox;
      // 如果距离底部小于100px，认为用户在底部附近
      return scrollHeight - scrollTop - clientHeight < 100;
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

      await loadChatHistory(true); // 初始加载时滚动到底部
      
      // 加载用户列表（管理员和普通用户都需要）
      await loadUsers();

      // 监听textarea输入变化，自动调整高度
      watch(newMessage, () => {
        nextTick(() => {
          adjustTextareaHeight();
        });
      });

      // 定期刷新聊天记录和用户列表
      setInterval(async () => {
        await loadChatHistory(false); // 定期刷新时不自动滚动
        await loadUsers(); // 普通用户也需要刷新以获取管理员状态
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

    // 用户管理方法
    const closeUserManagement = () => {
      showUserManagement.value = false;
      resetNewUserForm();
    };

    const resetNewUserForm = () => {
      newUserForm.value = {
        username: '',
        invite_code: '',
        is_admin: false
      };
    };

    const loadManagementUsers = async () => {
      try {
        const response = await apiGet(`/auth/admin/users?admin_user_id=${userInfo.value.user_id}`);
        managementUsers.value = response;
      } catch (error) {
        console.error('加载用户列表失败:', error);
        alert('加载用户列表失败：' + (error.response?.data?.detail || error.message));
      }
    };

    const createUser = async () => {
      try {
        const response = await apiPost('/auth/admin/create_user', {
          admin_user_id: userInfo.value.user_id,
          username: newUserForm.value.username,
          invite_code: newUserForm.value.invite_code,
          is_admin: newUserForm.value.is_admin
        });
        
        managementUsers.value.unshift(response);
        resetNewUserForm();
        alert('用户创建成功！');
      } catch (error) {
        console.error('创建用户失败:', error);
        alert('创建用户失败：' + (error.response?.data?.detail || error.message));
      }
    };

    const startEditUser = (user) => {
      editUserForm.value = {
        id: user.id,
        username: user.username,
        invite_code: user.invite_code,
        is_admin: user.is_admin
      };
      showEditUser.value = true;
    };

    const closeEditUser = () => {
      showEditUser.value = false;
      editUserForm.value = {
        id: null,
        username: '',
        invite_code: '',
        is_admin: false
      };
    };

    const updateUser = async () => {
      try {
        const response = await apiPut('/auth/admin/update_user', {
          admin_user_id: userInfo.value.user_id,
          target_user_id: editUserForm.value.id,
          new_username: editUserForm.value.username,
          new_invite_code: editUserForm.value.invite_code,
          is_admin: editUserForm.value.is_admin
        });
        
        // 更新列表中的用户信息
        const index = managementUsers.value.findIndex(u => u.id === editUserForm.value.id);
        if (index !== -1) {
          managementUsers.value[index] = response;
        }
        
        closeEditUser();
        alert('用户信息更新成功！');
      } catch (error) {
        console.error('更新用户失败:', error);
        alert('更新用户失败：' + (error.response?.data?.detail || error.message));
      }
    };

    const deleteUser = async (user) => {
      if (!confirm(`确定要删除用户 "${user.username}" 吗？此操作不可恢复！`)) {
        return;
      }
      
      try {
        await apiGet(`/auth/admin/delete_user?admin_user_id=${userInfo.value.user_id}&target_user_id=${user.id}`);
        
        // 从列表中移除用户
        managementUsers.value = managementUsers.value.filter(u => u.id !== user.id);
        alert('用户删除成功！');
      } catch (error) {
        console.error('删除用户失败:', error);
        alert('删除用户失败：' + (error.response?.data?.detail || error.message));
      }
    };

    // 获取选中用户的名称
    const getSelectedUserName = () => {
      if (!selectedUserId.value) return '';
      const user = allUsers.value.find(u => u.id === selectedUserId.value);
      return user ? user.username : '未知用户';
    };

    // 清空聊天记录
    const clearChatHistory = async () => {
      if (!selectedUserId.value) {
        alert('请先选择一个用户');
        return;
      }
      
      const userName = getSelectedUserName();
      if (!confirm(`确定要清空与用户 "${userName}" 的所有聊天记录吗？此操作不可恢复！`)) {
        return;
      }
      
      try {
        await apiPost('/chat/clear_chat_history', {
          admin_user_id: userInfo.value.user_id,
          target_user_id: selectedUserId.value
        });
        
        // 清空当前显示的消息
        messages.value = [];
        alert('聊天记录已清空！');
      } catch (error) {
        console.error('清空聊天记录失败:', error);
        alert('清空聊天记录失败：' + (error.response?.data?.detail || error.message));
      }
    };

    // 监听用户管理模态框的打开
    watch(showUserManagement, (newValue) => {
      if (newValue) {
        loadManagementUsers();
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
      textareaRef,
      chatBoxRef,
      previewModal,
      adminOnlineStatus, // 添加管理员在线状态
      // 用户管理相关
      showUserManagement,
      showEditUser,
      managementUsers,
      newUserForm,
      editUserForm,
      closeUserManagement,
      createUser,
      startEditUser,
      closeEditUser,
      updateUser,
      deleteUser,
      getSelectedUserName,
      clearChatHistory,
      // 原有方法
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
      handleKeyDown,
      getFileDescription,
      getFileIcon,
      watchNewMessage,
      canPreviewFile,
      previewFile,
      closePreview,
      onImageLoad,
      downloadFromPreview,
      openWithApp,
      openWithAppFromPreview,
    };
  },
};
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #cbd5e0 100%);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.chat-header {
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(10px);
  color: #333;
  padding: 20px 25px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 20px rgba(0,0,0,0.1);
  border-radius: 0 0 20px 20px;
}

.user-info h3 {
  margin: 0;
  font-size: 1.3em;
  font-weight: 600;
  color: #4a5568;
}

.username {
  font-size: 0.9em;
  color: #64748b;
  font-weight: 500;
}

.logout-btn {
  background: linear-gradient(45deg, #ff6b6b, #ee5a52);
  border: none;
  color: white;
  padding: 10px 20px;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
}

.logout-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
}

.chat-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.users-panel {
  width: 280px;
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(10px);
  border-right: 1px solid rgba(255,255,255,0.3);
  padding: 25px;
  overflow-y: auto;
  border-radius: 0 0 0 20px;
  box-shadow: 2px 0 15px rgba(0,0,0,0.05);
}

.users-panel h4 {
  margin: 0 0 20px 0;
  color: #4a5568;
  font-weight: 600;
  font-size: 1.1em;
}

.user-item {
  padding: 15px;
  margin: 8px 0;
  border-radius: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(255,255,255,0.7);
}

.user-item:hover {
  background: rgba(148, 163, 184, 0.2);
  transform: translateX(5px);
  box-shadow: 0 4px 15px rgba(148, 163, 184, 0.15);
}

.user-item.active {
  background: linear-gradient(45deg, #94a3b8, #64748b);
  color: white;
  box-shadow: 0 4px 20px rgba(148, 163, 184, 0.3);
}

.user-item.offline {
  opacity: 0.6;
}

.user-name {
  display: block;
  font-weight: 600;
  font-size: 1em;
}

.user-code {
  display: block;
  font-size: 0.8em;
  opacity: 0.7;
  margin-top: 4px;
}

.user-role {
  display: block;
  font-size: 0.8em;
  opacity: 0.8;
  margin-top: 4px;
  font-weight: 500;
}

.online-status {
  display: block;
  font-size: 0.8em;
  margin-top: 6px;
  font-weight: 500;
}

.online-status.offline {
  color: #f56565;
}

.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-area.full-width {
  width: 100%;
  max-width: none;
}

/* 管理员状态栏样式 */
.admin-status-bar {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-bottom: 1px solid #e2e8f0;
  padding: 12px 20px;
  border-radius: 20px 20px 0 0;
  backdrop-filter: blur(10px);
}

.admin-status {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.9em;
}

.status-label {
  font-weight: 600;
  color: #64748b;
}

.status-indicator {
  font-weight: 500;
  padding: 6px 12px;
  border-radius: 20px;
  transition: all 0.3s ease;
}

.status-indicator.online {
  background: linear-gradient(135deg, #dcfce7, #bbf7d0);
  color: #166534;
  box-shadow: 0 2px 8px rgba(34, 197, 94, 0.2);
}

.status-indicator.offline {
  background: linear-gradient(135deg, #fee2e2, #fecaca);
  color: #991b1b;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.2);
}

/* 聊天工具栏样式 */
.chat-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  border-bottom: 1px solid #e2e8f0;
  padding: 10px 20px;
  backdrop-filter: blur(10px);
}

.toolbar-left {
  display: flex;
  align-items: center;
}

.selected-user-info {
  font-size: 0.95em;
  color: #475569;
  font-weight: 500;
}

.toolbar-right {
  display: flex;
  gap: 10px;
}

.clear-btn {
  padding: 6px 12px;
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.85em;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.clear-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
  background: linear-gradient(135deg, #dc2626, #b91c1c);
}

.clear-btn:active {
  transform: translateY(0);
}

.chat-box {
  flex: 1;
  overflow-y: auto;
  padding: 25px;
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(10px);
  border-radius: 20px 20px 0 0;
}

.no-messages {
  text-align: center;
  color: #a0aec0;
  margin-top: 50px;
  font-style: italic;
  font-size: 1.1em;
}

.message {
  margin-bottom: 20px;
  max-width: 75%;
  animation: slideIn 0.3s ease-out;
  display: flex;
  flex-direction: column;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.own-message {
  margin-left: auto;
  margin-right: 0px;
  max-width: 70%;
  align-self: flex-end;
}

.other-message {
  margin-left: 20px;
  margin-right: auto;
  max-width: 70%;
  align-self: flex-start;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 0.9em;
  padding: 0 5px;
  width: 100%;
}

.own-message .message-header {
  justify-content: flex-end;
  text-align: right;
  gap: 10px;
}

.other-message .message-header {
  justify-content: flex-start;
  gap: 10px;
}

.delete-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2em;
  opacity: 0.6;
  transition: all 0.3s ease;
  padding: 4px 8px;
  border-radius: 15px;
}

.delete-btn:hover {
  opacity: 1;
  background: rgba(255, 0, 0, 0.1);
  transform: scale(1.1);
}

.timestamp {
  color: #a0aec0;
  font-size: 0.85em;
  font-weight: 500;
}

.own-message .timestamp {
  color: #64748b;
}

.own-message strong {
  color: #475569;
}

.other-message .timestamp {
  color: #a0aec0;
}

.other-message strong {
  color: #4a5568;
}

.message-content {
  background: rgba(255,255,255,0.9);
  padding: 12px 18px;
  border-radius: 20px;
  word-wrap: break-word;
  box-shadow: 0 2px 15px rgba(0,0,0,0.06);
  border: 1px solid rgba(226, 232, 240, 0.8);
  line-height: 1.6;
  font-size: 0.95em;
  min-width: auto;
  width: fit-content;
  max-width: 100%;
  transition: all 0.3s ease;
}

.own-message .message-content {
  background: linear-gradient(135deg, #e2e8f0, #cbd5e0);
  color: #2d3748;
  border: 1px solid rgba(203, 213, 224, 0.8);
  align-self: flex-end;
}

.other-message .message-content {
  align-self: flex-start;
}

.message-content:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 20px rgba(0,0,0,0.12);
}

/* 文字说明样式 */
.file-description {
  background: rgba(255,255,255,0.9);
  padding: 8px 12px;
  border-radius: 15px;
  margin-bottom: 10px;
  font-size: 0.9em;
  color: #4a5568;
  border-left: 3px solid #94a3b8;
}

.own-message .file-description {
  background: rgba(255,255,255,0.8);
  color: #2d3748;
  border-left: 3px solid #64748b;
}

.input-area {
  padding: 25px;
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(226, 232, 240, 0.8);
  border-radius: 0 0 20px 20px;
}

.file-preview {
  margin-bottom: 15px;
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.file-preview-content {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px 20px;
  background: linear-gradient(135deg, rgba(226, 232, 240, 0.3), rgba(203, 213, 224, 0.3));
  border: 2px dashed rgba(148, 163, 184, 0.5);
  border-radius: 20px;
  position: relative;
  backdrop-filter: blur(5px);
}

.file-preview .file-icon {
  font-size: 28px;
  animation: bounce 0.5s ease-out;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-10px); }
  60% { transform: translateY(-5px); }
}

.file-preview .file-info {
  flex: 1;
}

.file-preview .file-name {
  font-weight: 600;
  color: #4a5568;
  margin-bottom: 4px;
  font-size: 0.95em;
}

.file-preview .file-size {
  font-size: 0.85em;
  color: #718096;
}

.remove-file-btn {
  background: linear-gradient(45deg, #ff6b6b, #ee5a52);
  color: white;
  border: none;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(255, 107, 107, 0.3);
}

.remove-file-btn:hover {
  background: linear-gradient(45deg, #ee5a52, #dc3545);
  transform: scale(1.1);
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
}

.message-input-container {
  display: flex;
  gap: 15px;
  align-items: flex-end;
}

.message-input {
  flex: 1;
  padding: 15px 20px;
  border: 2px solid rgba(148, 163, 184, 0.3);
  border-radius: 25px;
  outline: none;
  font-size: 14px;
  resize: none;
  transition: all 0.3s ease;
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(5px);
  font-family: inherit;
  line-height: 1.4;
  min-height: 48px;
  max-height: 120px;
  overflow-y: auto;
}

.message-input:focus {
  border-color: #94a3b8;
  box-shadow: 0 0 0 3px rgba(148, 163, 184, 0.15);
  background: rgba(255,255,255,1);
}

.message-input:disabled {
  background: rgba(245, 245, 245, 0.9);
  cursor: not-allowed;
  opacity: 0.7;
}

.input-buttons {
  display: flex;
  gap: 10px;
}

.file-btn, .send-btn {
  width: 48px;
  height: 48px;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  font-size: 1.4em;
  font-weight: bold;
  box-shadow: 0 4px 15px rgba(0,0,0,0.15);
}

.file-btn {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
}

.file-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #218838, #1a9974);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(40, 167, 69, 0.3);
}

.send-btn {
  background: linear-gradient(135deg, #94a3b8, #64748b);
  color: white;
}

.send-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #64748b, #475569);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(148, 163, 184, 0.3);
}

.file-btn:active:not(:disabled),
.send-btn:active:not(:disabled) {
  transform: translateY(0);
}

.file-btn:disabled,
.send-btn:disabled {
  background: linear-gradient(135deg, #a0aec0, #718096);
  cursor: not-allowed;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* 文件消息样式优化 */
.image-message {
  max-width: 350px;
}

.message-image {
  max-width: 100%;
  max-height: 250px;
  border-radius: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.message-image:hover {
  transform: scale(1.02);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.file-message {
  max-width: 350px;
}

.file-container {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 15px;
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(5px);
  transition: all 0.3s ease;
}

.own-message .file-container {
  background: rgba(255,255,255,0.8);
  border-color: rgba(148, 163, 184, 0.4);
}

.file-container:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.file-icon {
  font-size: 28px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

.file-details {
  flex: 1;
}

.file-name {
  font-weight: 600;
  margin-bottom: 6px;
  word-break: break-word;
  color: #4a5568;
  font-size: 0.9em;
}

.own-message .file-name {
  color: #2d3748; /* 改为深色，确保在浅灰色背景上可见 */
}

.file-size {
  font-size: 0.8em;
  color: #718096;
  margin-bottom: 10px;
}

.own-message .file-size {
  color: #4a5568; /* 改为深色，确保在浅灰色背景上可见 */
}

.file-info {
  font-size: 0.85em;
  color: #64748b;
  margin-top: 8px;
  padding: 6px 10px;
  background: rgba(226, 232, 240, 0.6);
  border-radius: 10px;
  text-align: center;
}

.own-message .file-info {
  color: #475569;
  background: rgba(203, 213, 224, 0.6);
}

.download-btn {
  padding: 8px 16px;
  background: linear-gradient(135deg, #64748b, #475569);
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.85em;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(100, 116, 139, 0.3);
  margin-right: 8px;
}

.download-btn:hover {
  background: linear-gradient(135deg, #475569, #334155);
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(100, 116, 139, 0.4);
}

.file-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 10px;
}

.preview-btn {
  padding: 6px 12px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  border: none;
  border-radius: 15px;
  cursor: pointer;
  font-size: 0.8em;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.preview-btn:hover {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.open-app-btn {
  padding: 6px 12px;
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: none;
  border-radius: 15px;
  cursor: pointer;
  font-size: 0.8em;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
}

.open-app-btn:hover {
  background: linear-gradient(135deg, #059669, #047857);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

/* 文件预览模态框样式 */
.preview-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(10px);
  animation: modalFadeIn 0.3s ease-out;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    backdrop-filter: blur(0);
  }
  to {
    opacity: 1;
    backdrop-filter: blur(10px);
  }
}

.preview-modal-content {
  background: white;
  border-radius: 20px;
  max-width: 90vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
  animation: modalSlideIn 0.3s ease-out;
  overflow: hidden;
}

@keyframes modalSlideIn {
  from {
    transform: scale(0.9) translateY(20px);
    opacity: 0;
  }
  to {
    transform: scale(1) translateY(0);
    opacity: 1;
  }
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
}

.preview-title {
  margin: 0;
  font-size: 1.2em;
  color: #2d3748;
  font-weight: 600;
  word-break: break-word;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5em;
  cursor: pointer;
  color: #64748b;
  padding: 8px;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  transform: scale(1.1);
}

.preview-body {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  overflow: auto;
  position: relative;
}

.image-preview {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  max-width: 100%;
  max-height: 100%;
}

.preview-image {
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.code-preview {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #1e293b;
}

.loading, .error {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  font-size: 1.1em;
  color: #64748b;
}

.error {
  color: #ef4444;
}

.code-content {
  flex: 1;
  margin: 0;
  padding: 25px;
  background: #1e293b;
  color: #e2e8f0;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.6;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

.unsupported-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  text-align: center;
  color: #64748b;
}

.file-icon-large {
  font-size: 4em;
  margin-bottom: 20px;
  animation: pulse 2s infinite;
}

.unsupported-preview h4 {
  margin: 10px 0;
  color: #2d3748;
  font-size: 1.3em;
  word-break: break-word;
}

.unsupported-preview p {
  margin: 15px 0;
  font-size: 1em;
}

.preview-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;
  flex-wrap: wrap;
  gap: 15px;
}

.file-info-detailed {
  display: flex;
  gap: 20px;
  font-size: 0.9em;
  color: #64748b;
  flex-wrap: wrap;
}

.image-dimensions {
  color: #3b82f6;
  font-weight: 500;
}

.preview-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 15px;
  cursor: pointer;
  font-size: 0.9em;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.action-btn.download {
  background: linear-gradient(135deg, #64748b, #475569);
  color: white;
}

.action-btn.open {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.action-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .preview-modal-content {
    max-width: 95vw;
    max-height: 95vh;
    margin: 10px;
  }
  
  .preview-header,
  .preview-footer {
    padding: 15px 20px;
  }
  
  .preview-title {
    font-size: 1.1em;
  }
  
  .file-info-detailed {
    font-size: 0.8em;
  }
  
  .preview-actions {
    flex-wrap: wrap;
  }
  
  .action-btn {
    font-size: 0.8em;
    padding: 6px 12px;
  }
}

.text-message {
  word-wrap: break-word;
  white-space: pre-wrap;
}

/* 用户管理样式 */
.header-buttons {
  display: flex;
  gap: 10px;
  align-items: center;
}

.manage-btn {
  padding: 8px 16px;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.9em;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.manage-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  max-height: 90vh;
  overflow-y: auto;
  animation: modalSlideIn 0.3s ease-out;
}

.user-management-modal {
  width: 90%;
  max-width: 800px;
}

.edit-user-modal {
  width: 90%;
  max-width: 400px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.3em;
  color: #374151;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5em;
  color: #9ca3af;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.modal-body {
  padding: 24px;
}

.section {
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid #f3f4f6;
}

.section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.section h4 {
  margin: 0 0 16px 0;
  font-size: 1.1em;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #374151;
}

.form-group input[type="text"] {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.95em;
  transition: border-color 0.2s ease;
}

.form-group input[type="text"]:focus {
  outline: none;
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.form-group input[type="checkbox"] {
  margin-right: 8px;
}

.action-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 0.95em;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.action-btn.primary {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.action-btn.primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

.users-table {
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e5e7eb;
}

.table-header {
  display: grid;
  grid-template-columns: 1.5fr 1.5fr 1fr 1fr 1fr;
  gap: 16px;
  padding: 12px 16px;
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
  font-size: 0.9em;
}

.table-row {
  display: grid;
  grid-template-columns: 1.5fr 1.5fr 1fr 1fr 1fr;
  gap: 16px;
  padding: 12px 16px;
  border-top: 1px solid #e5e7eb;
  align-items: center;
  transition: background-color 0.2s ease;
}

.table-row:hover {
  background: #f9fafb;
}

.table-row .username {
  font-weight: 500;
  color: #374151;
}

.table-row .invite-code {
  font-family: 'Monaco', 'Menlo', monospace;
  background: #f3f4f6;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85em;
}

.admin-badge {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.8em;
  font-weight: 500;
  text-align: center;
}

.admin-badge.admin {
  background: #fef3c7;
  color: #92400e;
}

.admin-badge:not(.admin) {
  background: #f3f4f6;
  color: #6b7280;
}

.status {
  font-size: 0.85em;
  font-weight: 500;
}

.status.online {
  color: #059669;
}

.status:not(.online) {
  color: #9ca3af;
}

.actions {
  display: flex;
  gap: 8px;
}

.edit-btn, .delete-btn {
  padding: 6px 8px;
  border: none;
  border-radius: 6px;
  font-size: 0.9em;
  cursor: pointer;
  transition: all 0.2s ease;
}

.edit-btn {
  background: #dbeafe;
  color: #1d4ed8;
}

.edit-btn:hover {
  background: #bfdbfe;
}

.delete-btn {
  background: #fee2e2;
  color: #dc2626;
}

.delete-btn:hover {
  background: #fecaca;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.cancel-btn {
  padding: 10px 20px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: white;
  color: #374151;
  font-size: 0.95em;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cancel-btn:hover {
  background: #f9fafb;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
</style>