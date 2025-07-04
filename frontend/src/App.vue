<script>
import ProductList from './components/ProductList.vue'
import ShoppingCart from './components/ShoppingCart.vue'
import LoginForm from './components/LoginForm.vue'

export default {
  name: 'App',
  components: {
    ProductList,
    ShoppingCart,
    LoginForm
  },
  data() {
    return {
      currentView: 'products',
      cartCount: 0,
      isLoggedIn: false,
      currentUser: null
    }
  },
  mounted() {
    this.checkAuth()
  },
  methods: {
    async checkAuth() {
      const user = localStorage.getItem('user')
      
      if (user) {
        // 驗證 session 是否仍然有效
        try {
          const response = await fetch('http://localhost:8000/api/me', {
            credentials: 'include'
          })
          
          if (response.ok) {
            this.isLoggedIn = true
            this.currentUser = JSON.parse(user)
            this.updateCartCount()
          } else {
            // Session 已過期，清除本地資料
            localStorage.removeItem('user')
          }
        } catch (error) {
          console.error('檢查登入狀態失敗:', error)
          localStorage.removeItem('user')
        }
      }
    },
    
    handleLoginSuccess(user) {
      this.isLoggedIn = true
      this.currentUser = user
      this.updateCartCount()
    },
    
    async logout() {
      try {
        await fetch('http://localhost:8000/api/logout', {
          method: 'POST',
          credentials: 'include'
        })
      } catch (error) {
        console.error('登出失敗:', error)
      }
      
      localStorage.removeItem('user')
      this.isLoggedIn = false
      this.currentUser = null
      this.cartCount = 0
    },
    
    async updateCartCount() {
      if (!this.isLoggedIn) return
      
      try {
        const response = await fetch('http://localhost:8000/api/cart', {
          credentials: 'include'
        })
        
        if (response.ok) {
          const cartItems = await response.json()
          this.cartCount = cartItems.reduce((total, item) => total + item.quantity, 0)
        } else if (response.status === 401) {
          // Session 過期，登出用戶
          this.logout()
        }
      } catch (error) {
        console.error('更新購物車數量失敗:', error)
      }
    }
  }
}
</script>

<template>
  <div id="app">
    <!-- 登入頁面 -->
    <LoginForm 
      v-if="!isLoggedIn" 
      @login-success="handleLoginSuccess"
    />
    
    <!-- 主要應用 -->
    <div v-else>
      <!-- 頂部導航欄 -->
      <header class="site-header">
        <div class="header-container">
          <div class="logo-section">
            <h1 class="site-logo">
              <span class="logo-icon">🛍️</span>
              購物商城
            </h1>
          </div>
          
          <nav class="main-nav">
            <button 
              @click="currentView = 'products'" 
              :class="{ active: currentView === 'products' }"
              class="nav-btn"
            >
              <i class="nav-icon">🏪</i>
              商品列表
            </button>
            <button 
              @click="currentView = 'cart'" 
              :class="{ active: currentView === 'cart' }"
              class="nav-btn cart-nav"
            >
              <i class="nav-icon">🛒</i>
              購物車
              <span v-if="cartCount > 0" class="cart-badge">{{ cartCount }}</span>
            </button>
          </nav>
          
          <div class="user-section">
            <div class="user-info">
              <i class="user-icon">👤</i>
              <span class="username">{{ currentUser.username }}</span>
              <button @click="logout" class="logout-btn">登出</button>
            </div>
          </div>
        </div>
      </header>
    
    <!-- 主要內容區域 -->
    <main class="main-content">
      <div class="content-container">
        <ProductList 
          v-if="currentView === 'products'" 
          @cart-updated="updateCartCount"
        />
        <ShoppingCart 
          v-else-if="currentView === 'cart'" 
          @cart-updated="updateCartCount"
          @go-to-products="currentView = 'products'"
        />
      </div>
    </main>
    
    <!-- 頁腳 -->
    <footer class="site-footer">
      <div class="footer-container">
        <div class="footer-section">
          <h4>購物指南</h4>
          <ul>
            <li><a href="#">如何購買</a></li>
            <li><a href="#">付款方式</a></li>
            <li><a href="#">配送資訊</a></li>
            <li><a href="#">退換貨政策</a></li>
          </ul>
        </div>
        
        <div class="footer-section">
          <h4>客戶服務</h4>
          <ul>
            <li><a href="#">聯絡我們</a></li>
            <li><a href="#">常見問題</a></li>
            <li><a href="#">線上客服</a></li>
            <li><a href="#">意見回饋</a></li>
          </ul>
        </div>
        
        <div class="footer-section">
          <h4>關於我們</h4>
          <ul>
            <li><a href="#">公司介紹</a></li>
            <li><a href="#">隱私政策</a></li>
            <li><a href="#">服務條款</a></li>
            <li><a href="#">合作夥伴</a></li>
          </ul>
        </div>
        
        <div class="footer-section">
          <h4>追蹤我們</h4>
          <div class="social-links">
            <a href="#" class="social-link">📘 Facebook</a>
            <a href="#" class="social-link">📷 Instagram</a>
            <a href="#" class="social-link">🐦 Twitter</a>
            <a href="#" class="social-link">📺 YouTube</a>
          </div>
        </div>
      </div>
      
      <div class="footer-bottom">
        <div class="footer-container">
          <p>&copy; 2024 購物商城. 保留所有權利.</p>
          <div class="payment-methods">
            <span>支援付款方式：</span>
            <span class="payment-icon">💳</span>
            <span class="payment-icon">🏦</span>
            <span class="payment-icon">📱</span>
          </div>
        </div>
      </div>
    </footer>
    </div>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f5f7fa;
  color: #333;
  line-height: 1.6;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 頂部導航欄 */
.site-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-container {
  max-width: 1900px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 70px;
}

.logo-section {
  display: flex;
  align-items: center;
}

.site-logo {
  font-size: 24px;
  font-weight: bold;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  font-size: 28px;
}

.main-nav {
  display: flex;
  gap: 5px;
}

.nav-btn {
  background: transparent;
  color: white;
  border: 2px solid transparent;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
}

.nav-btn:hover {
  background: rgba(255,255,255,0.1);
  border-color: rgba(255,255,255,0.3);
}

.nav-btn.active {
  background: rgba(255,255,255,0.2);
  border-color: rgba(255,255,255,0.5);
}

.nav-icon {
  font-size: 18px;
}

.cart-nav {
  position: relative;
}

.cart-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #ff4757;
  color: white;
  border-radius: 50%;
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

.user-section {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  background: rgba(255,255,255,0.1);
  border-radius: 20px;
  font-size: 14px;
}

.user-icon {
  font-size: 16px;
}

.username {
  font-weight: 500;
  color: white;
}

.logout-btn {
  background: rgba(255,255,255,0.1);
  color: white;
  border: 1px solid rgba(255,255,255,0.3);
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s ease;
  margin-left: 8px;
}

.logout-btn:hover {
  background: rgba(255,255,255,0.2);
  border-color: rgba(255,255,255,0.5);
}

/* 主要內容區域 */
.main-content {
  flex: 1;
  padding: 40px 0;
}

.content-container {
  max-width: 1900px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 頁腳 */
.site-footer {
  background: #2c3e50;
  color: white;
  margin-top: auto;
}

.footer-container {
  max-width: 1900px;
  margin: 0 auto;
  padding: 0 20px;
}

.site-footer .footer-container:first-child {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 40px;
  padding: 50px 20px 30px;
}

.footer-section h4 {
  margin-bottom: 20px;
  font-size: 18px;
  color: #ecf0f1;
}

.footer-section ul {
  list-style: none;
}

.footer-section ul li {
  margin-bottom: 10px;
}

.footer-section ul li a {
  color: #bdc3c7;
  text-decoration: none;
  transition: color 0.3s;
}

.footer-section ul li a:hover {
  color: #ecf0f1;
}

.social-links {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.social-link {
  color: #bdc3c7;
  text-decoration: none;
  transition: color 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.social-link:hover {
  color: #ecf0f1;
}

.footer-bottom {
  border-top: 1px solid #34495e;
  padding: 20px 0;
}

.footer-bottom .footer-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #bdc3c7;
  font-size: 14px;
}

.payment-methods {
  display: flex;
  align-items: center;
  gap: 10px;
}

.payment-icon {
  font-size: 18px;
}

/* 響應式設計 */
@media (max-width: 1024px) {
  .header-container {
    padding: 0 15px;
  }
  
  .content-container {
    padding: 0 15px;
  }
  
  .footer-container {
    padding: 0 15px;
  }
}

@media (max-width: 768px) {
  .header-container {
    flex-direction: column;
    height: auto;
    padding: 15px;
    gap: 15px;
  }
  
  .main-nav {
    width: 100%;
    justify-content: center;
  }
  
  .nav-btn {
    flex: 1;
    justify-content: center;
  }
  
  .user-section {
    order: -1;
  }
  
  .site-footer .footer-container:first-child {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 30px;
    padding: 30px 15px 20px;
  }
  
  .footer-bottom .footer-container {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .main-content {
    padding: 20px 0;
  }
}

@media (max-width: 480px) {
  .site-logo {
    font-size: 20px;
  }
  
  .nav-btn {
    padding: 8px 12px;
    font-size: 14px;
  }
  
  .site-footer .footer-container:first-child {
    grid-template-columns: 1fr;
    gap: 25px;
  }
}
</style>
