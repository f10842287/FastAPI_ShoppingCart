<template>
  <div class="shopping-cart">
    <div class="cart-header">
      <h2>購物車</h2>
      <div class="cart-meta" v-if="cartItems.length > 0">
        <span class="item-count">{{ totalQuantity }} 件商品</span>
        <button @click="clearCart" class="clear-cart-btn">清空購物車</button>
      </div>
    </div>
    
    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      載入中...
    </div>
    
    <div v-else-if="cartItems.length === 0" class="empty-cart">
      <div class="empty-cart-icon">🛒</div>
      <h3>您的購物車是空的</h3>
      <p>快去選購您喜歡的商品吧！</p>
      <button @click="$emit('go-to-products')" class="continue-shopping-btn">
        繼續購物
      </button>
    </div>
    
    <div v-else class="cart-content">
      <!-- 購物車項目列表 -->
      <div class="cart-items-section">
        <div class="cart-items-header">
          <div class="header-product">商品</div>
          <div class="header-price">單價</div>
          <div class="header-quantity">數量</div>
          <div class="header-total">小計</div>
          <div class="header-actions">操作</div>
        </div>
        
        <div class="cart-items-list">
          <div v-for="item in cartItems" :key="item.id" class="cart-item">
            <div class="item-product">
              <div class="product-image">
                <img :src="item.product.image_url || `https://picsum.photos/80/80?random=${item.product.id}`" :alt="item.product.name" />
              </div>
              <div class="product-info">
                <h4 class="product-name">{{ item.product.name }}</h4>
                <p class="product-category">{{ item.product.category }}</p>
                <p class="product-description">{{ item.product.description }}</p>
                <div class="stock-status" :class="{ 'low-stock': item.product.stock < 5 }">
                  庫存：{{ item.product.stock }}
                </div>
              </div>
            </div>
            
            <div class="item-price">
              NT$ {{ item.product.price.toLocaleString() }}
            </div>
            
            <div class="item-quantity">
              <div class="quantity-controls">
                <button 
                  @click="updateQuantity(item.id, item.quantity - 1)" 
                  :disabled="item.quantity <= 1"
                  class="quantity-btn"
                >
                  −
                </button>
                <span class="quantity-display">{{ item.quantity }}</span>
                <button 
                  @click="updateQuantity(item.id, item.quantity + 1)" 
                  :disabled="item.quantity >= item.product.stock"
                  class="quantity-btn"
                >
                  +
                </button>
              </div>
              <div class="quantity-info">
                最多 {{ item.product.stock }} 件
              </div>
            </div>
            
            <div class="item-total">
              NT$ {{ (item.product.price * item.quantity).toLocaleString() }}
            </div>
            
            <div class="item-actions">
              <button @click="removeFromCart(item.id)" class="remove-btn">
                <i class="remove-icon">🗑️</i>
                移除
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 購物車摘要 -->
      <div class="cart-summary-section">
        <div class="cart-summary">
          <h3>訂單摘要</h3>
          
          <div class="summary-details">
            <div class="summary-row">
              <span>商品總數：</span>
              <span>{{ totalQuantity }} 件</span>
            </div>
            <div class="summary-row">
              <span>商品金額：</span>
              <span>NT$ {{ totalAmount.toLocaleString() }}</span>
            </div>
            <div class="summary-row">
              <span>運費：</span>
              <span class="shipping-fee">{{ shippingFee === 0 ? '免運費' : `NT$ ${shippingFee.toLocaleString()}` }}</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-row total-row">
              <span>總計：</span>
              <span class="total-amount">NT$ {{ finalTotal.toLocaleString() }}</span>
            </div>
          </div>
          
          <div class="checkout-section">
            <button class="checkout-btn" @click="checkout">
              <i class="checkout-icon">💳</i>
              立即結帳
            </button>
            <button class="continue-shopping-btn-small" @click="$emit('go-to-products')">
              繼續購物
            </button>
          </div>
          
          <div class="security-info">
            <i class="security-icon">🔒</i>
            <span>安全結帳保護</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ShoppingCart',
  data() {
    return {
      cartItems: [],
      loading: false
    }
  },
  computed: {
    totalQuantity() {
      return this.cartItems.reduce((total, item) => total + item.quantity, 0)
    },
    totalAmount() {
      return this.cartItems.reduce((total, item) => total + (item.product.price * item.quantity), 0)
    },
    shippingFee() {
      // 滿2000免運費
      return this.totalAmount >= 2000 ? 0 : 100
    },
    finalTotal() {
      return this.totalAmount + this.shippingFee
    }
  },
  mounted() {
    this.loadCart()
  },
  methods: {
    async loadCart() {
      this.loading = true
      
      try {
        const response = await fetch('http://localhost:8000/api/cart', {
          credentials: 'include'
        })
        
        if (response.ok) {
          this.cartItems = await response.json()
        } else if (response.status === 401) {
          localStorage.removeItem('user')
          window.location.reload()
        }
      } catch (error) {
        console.error('載入購物車失敗:', error)
      } finally {
        this.loading = false
      }
    },
    
    async updateQuantity(cartItemId, newQuantity) {
      if (newQuantity < 1) return
      
      try {
        const response = await fetch(`http://localhost:8000/api/cart/${cartItemId}?quantity=${newQuantity}`, {
          method: 'PUT',
          credentials: 'include'
        })
        
        if (response.ok) {
          await this.loadCart()
          this.$emit('cart-updated')
        } else if (response.status === 401) {
          localStorage.removeItem('user')
          window.location.reload()
        } else {
          alert('更新數量失敗')
        }
      } catch (error) {
        console.error('更新數量失敗:', error)
      }
    },
    
    async removeFromCart(cartItemId) {
      if (!confirm('確定要移除這個商品嗎？')) return
      
      try {
        const response = await fetch(`http://localhost:8000/api/cart/${cartItemId}`, {
          method: 'DELETE',
          credentials: 'include'
        })
        
        if (response.ok) {
          await this.loadCart()
          this.$emit('cart-updated')
          this.showSuccessMessage('商品已從購物車移除')
        } else if (response.status === 401) {
          localStorage.removeItem('user')
          window.location.reload()
        } else {
          alert('移除商品失敗')
        }
      } catch (error) {
        console.error('移除商品失敗:', error)
      }
    },
    
    async clearCart() {
      if (!confirm('確定要清空整個購物車嗎？')) return
      
      try {
        // 逐一移除所有商品
        for (const item of this.cartItems) {
          await fetch(`http://localhost:8000/api/cart/${item.id}`, {
            method: 'DELETE',
            credentials: 'include'
          })
        }
        
        await this.loadCart()
        this.$emit('cart-updated')
        this.showSuccessMessage('購物車已清空')
      } catch (error) {
        console.error('清空購物車失敗:', error)
      }
    },
    
    checkout() {
      if (this.cartItems.length === 0) {
        alert('購物車是空的！')
        return
      }
      
      // 模擬結帳流程
      const orderSummary = `
訂單摘要：
- 商品數量：${this.totalQuantity} 件
- 商品金額：NT$ ${this.totalAmount.toLocaleString()}
- 運費：${this.shippingFee === 0 ? '免運費' : `NT$ ${this.shippingFee.toLocaleString()}`}
- 總計：NT$ ${this.finalTotal.toLocaleString()}

感謝您的購買！
      `
      
      alert(orderSummary)
      
      // 清空購物車
      this.clearCart()
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
    },
    
    refreshCart() {
      this.loadCart()
    }
  }
}
</script>

<style scoped>
.shopping-cart {
  max-width: 1900px;
  margin: 0 auto;
  padding: 0 20px;
}

.cart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #e0e0e0;
}

.cart-header h2 {
  margin: 0;
  font-size: 28px;
  color: #333;
  font-weight: 600;
}

.cart-meta {
  display: flex;
  align-items: center;
  gap: 20px;
}

.item-count {
  color: #666;
  font-size: 16px;
  font-weight: 500;
}

.clear-cart-btn {
  background: #ff4757;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.clear-cart-btn:hover {
  background: #ff3742;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: #666;
  font-size: 18px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-cart {
  text-align: center;
  padding: 80px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.empty-cart-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.empty-cart h3 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 24px;
}

.empty-cart p {
  color: #666;
  margin-bottom: 30px;
  font-size: 16px;
}

.continue-shopping-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  transition: transform 0.3s;
}

.continue-shopping-btn:hover {
  transform: translateY(-2px);
}

.cart-content {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 30px;
}

.cart-items-section {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.cart-items-header {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 1fr;
  gap: 20px;
  padding: 20px;
  background: #f8f9fa;
  font-weight: 600;
  color: #333;
  border-bottom: 1px solid #e0e0e0;
}

.cart-items-list {
  /* Items will be divided by borders in cart-item styles */
}

.cart-item {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 1fr;
  gap: 20px;
  padding: 25px 20px;
  border-bottom: 1px solid #f0f0f0;
  align-items: center;
}

.cart-item:last-child {
  border-bottom: none;
}

.item-product {
  display: flex;
  gap: 15px;
  align-items: flex-start;
}

.product-image {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  background: #f5f5f5;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-info {
  flex: 1;
}

.product-name {
  margin: 0 0 5px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  line-height: 1.4;
}

.product-category {
  margin: 0 0 5px 0;
  font-size: 12px;
  color: #667eea;
  font-weight: 500;
  text-transform: uppercase;
}

.product-description {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #666;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.stock-status {
  font-size: 12px;
  color: #27ae60;
  font-weight: 500;
}

.stock-status.low-stock {
  color: #f39c12;
}

.item-price {
  font-size: 18px;
  font-weight: 600;
  color: #e74c3c;
}

.item-quantity {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.quantity-controls {
  display: flex;
  align-items: center;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.quantity-btn {
  width: 35px;
  height: 35px;
  border: none;
  background: #f8f9fa;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  transition: background 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.quantity-btn:hover:not(:disabled) {
  background: #e9ecef;
}

.quantity-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.quantity-display {
  width: 50px;
  height: 35px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  background: white;
}

.quantity-info {
  font-size: 12px;
  color: #666;
}

.item-total {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  text-align: right;
}

.item-actions {
  display: flex;
  justify-content: center;
}

.remove-btn {
  background: #ff4757;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: background 0.3s;
}

.remove-btn:hover {
  background: #ff3742;
}

.cart-summary-section {
  position: sticky;
  top: 20px;
  height: fit-content;
}

.cart-summary {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border: 1px solid #e0e0e0;
}

.cart-summary h3 {
  margin: 0 0 20px 0;
  font-size: 20px;
  color: #333;
}

.summary-details {
  margin-bottom: 25px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 16px;
}

.shipping-fee {
  color: #27ae60;
  font-weight: 500;
}

.summary-divider {
  height: 1px;
  background: #e0e0e0;
  margin: 15px 0;
}

.total-row {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  margin-bottom: 0;
}

.total-amount {
  color: #e74c3c;
}

.checkout-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.checkout-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 15px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: transform 0.3s;
}

.checkout-btn:hover {
  transform: translateY(-2px);
}

.continue-shopping-btn-small {
  background: transparent;
  color: #667eea;
  border: 2px solid #667eea;
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.continue-shopping-btn-small:hover {
  background: #667eea;
  color: white;
}

.security-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #666;
  font-size: 14px;
  padding-top: 15px;
  border-top: 1px solid #e0e0e0;
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
@media (max-width: 1024px) {
  .cart-content {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .cart-summary-section {
    position: static;
  }
}

@media (max-width: 768px) {
  .cart-items-header {
    display: none;
  }
  
  .cart-item {
    grid-template-columns: 1fr;
    gap: 15px;
    text-align: left;
  }
  
  .item-product {
    flex-direction: column;
    text-align: center;
  }
  
  .item-quantity {
    flex-direction: row;
    justify-content: space-between;
  }
  
  .cart-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
}
</style> 