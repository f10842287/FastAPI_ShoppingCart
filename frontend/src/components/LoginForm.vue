<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h2>{{ isLogin ? '登入' : '註冊' }}</h2>
        <p>{{ isLogin ? '歡迎回來！請登入您的帳戶' : '創建新帳戶開始購物' }}</p>
      </div>
      
      <form @submit.prevent="handleSubmit" class="login-form">
        <div class="form-group">
          <label for="username">用戶名</label>
          <input
            type="text"
            id="username"
            v-model="formData.username"
            required
            placeholder="請輸入用戶名"
            :disabled="loading"
          />
        </div>
        
        <div v-if="!isLogin" class="form-group">
          <label for="email">電子郵箱</label>
          <input
            type="email"
            id="email"
            v-model="formData.email"
            required
            placeholder="請輸入電子郵箱"
            :disabled="loading"
          />
        </div>
        
        <div class="form-group">
          <label for="password">密碼</label>
          <input
            type="password"
            id="password"
            v-model="formData.password"
            required
            placeholder="請輸入密碼"
            :disabled="loading"
          />
        </div>
        
        <div v-if="!isLogin" class="form-group">
          <label for="confirmPassword">確認密碼</label>
          <input
            type="password"
            id="confirmPassword"
            v-model="formData.confirmPassword"
            required
            placeholder="請再次輸入密碼"
            :disabled="loading"
          />
        </div>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        
        <button type="submit" class="submit-btn" :disabled="loading">
          <span v-if="loading" class="loading-spinner"></span>
          {{ loading ? '處理中...' : (isLogin ? '登入' : '註冊') }}
        </button>
      </form>
      
      <div class="switch-mode">
        <p>
          {{ isLogin ? '還沒有帳戶？' : '已有帳戶？' }}
          <button @click="toggleMode" class="switch-btn">
            {{ isLogin ? '立即註冊' : '立即登入' }}
          </button>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoginForm',
  data() {
    return {
      isLogin: true,
      loading: false,
      error: '',
      formData: {
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      }
    }
  },
  methods: {
    toggleMode() {
      this.isLogin = !this.isLogin
      this.error = ''
      this.formData = {
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      }
    },
    
    validateForm() {
      if (!this.formData.username.trim()) {
        this.error = '請輸入用戶名'
        return false
      }
      
      if (!this.isLogin && !this.formData.email.trim()) {
        this.error = '請輸入電子郵箱'
        return false
      }
      
      if (!this.formData.password) {
        this.error = '請輸入密碼'
        return false
      }
      
      if (this.formData.password.length < 6) {
        this.error = '密碼至少需要6個字符'
        return false
      }
      
      if (!this.isLogin && this.formData.password !== this.formData.confirmPassword) {
        this.error = '兩次輸入的密碼不一致'
        return false
      }
      
      return true
    },
    
    async handleSubmit() {
      this.error = ''
      
      if (!this.validateForm()) {
        return
      }
      
      this.loading = true
      
      try {
        const endpoint = this.isLogin ? '/api/login' : '/api/register'
        const payload = this.isLogin 
          ? {
              username: this.formData.username,
              password: this.formData.password
            }
          : {
              username: this.formData.username,
              email: this.formData.email,
              password: this.formData.password
            }
        
        const response = await fetch(`http://localhost:8000${endpoint}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
          credentials: 'include'
        })
        
        const data = await response.json()
        
        if (response.ok) {
          // 儲存用戶基本資訊
          localStorage.setItem('user', JSON.stringify(data))
          
          // 發送登入成功事件
          this.$emit('login-success', data)
          
          this.showSuccessMessage(this.isLogin ? '登入成功！' : '註冊成功！')
        } else {
          this.error = data.detail || '操作失敗，請稍後再試'
        }
      } catch (error) {
        console.error('認證錯誤:', error)
        this.error = '網路錯誤，請檢查網路連接'
      } finally {
        this.loading = false
      }
    },
    
    showSuccessMessage(message) {
      const toast = document.createElement('div')
      toast.className = 'success-toast'
      toast.textContent = message
      document.body.appendChild(toast)
      
      setTimeout(() => {
        toast.classList.add('show')
      }, 100)
      
      setTimeout(() => {
        toast.classList.remove('show')
        setTimeout(() => document.body.removeChild(toast), 300)
      }, 3000)
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
  padding: 40px;
  width: 100%;
  max-width: 420px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  margin: 0 0 10px 0;
  font-size: 28px;
  font-weight: 600;
  color: #333;
}

.login-header p {
  margin: 0;
  color: #666;
  font-size: 16px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
  font-size: 14px;
}

.form-group input {
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.form-group input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.error-message {
  background: #fee;
  color: #d63031;
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #fab1a0;
  font-size: 14px;
  text-align: center;
}

.submit-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 14px 20px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-top: 10px;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid transparent;
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.switch-mode {
  text-align: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.switch-mode p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.switch-btn {
  background: none;
  border: none;
  color: #667eea;
  font-weight: 600;
  cursor: pointer;
  text-decoration: underline;
  margin-left: 5px;
}

.switch-btn:hover {
  color: #764ba2;
}

.success-toast {
  position: fixed;
  top: 20px;
  right: 20px;
  background: #27ae60;
  color: white;
  padding: 15px 25px;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
  transform: translateX(100%);
  transition: transform 0.3s ease;
  z-index: 1000;
  font-weight: 500;
}

.success-toast.show {
  transform: translateX(0);
}

/* 響應式設計 */
@media (max-width: 480px) {
  .login-card {
    padding: 30px 20px;
  }
  
  .login-header h2 {
    font-size: 24px;
  }
}
</style> 