<template>
  <div class="product-list">
    <!-- 頂部篩選欄 -->
    <div class="filter-bar">
      <div class="filter-section">
        <label>分類篩選：</label>
        <select v-model="selectedCategory" @change="filterProducts">
          <option value="">全部分類</option>
          <option v-for="category in categories" :key="category" :value="category">
            {{ category }}
          </option>
        </select>
      </div>
      <div class="sort-section">
        <label>排序：</label>
        <select v-model="sortBy" @change="sortProducts">
          <option value="name">名稱</option>
          <option value="price-low">價格：低到高</option>
          <option value="price-high">價格：高到低</option>
          <option value="stock">庫存量</option>
        </select>
      </div>
      <div class="results-count">
        共 {{ filteredProducts.length }} 項商品
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      載入中...
    </div>
    
    <div v-else class="products-container">
      <!-- 商品網格 -->
      <div class="products-grid">
        <div v-for="product in filteredProducts" :key="product.id" class="product-card">
          <div class="product-image-container">
            <img :src="product.image_url || `https://picsum.photos/250/200?random=${product.id}`" :alt="product.name" />
            <div v-if="product.stock === 0" class="out-of-stock-badge">缺貨</div>
          </div>
          
          <div class="product-details">
            <div class="product-category">{{ product.category }}</div>
            <h3 class="product-title">{{ product.name }}</h3>
            <p class="product-description">{{ product.description }}</p>
            
            <div class="product-pricing">
              <div class="price">NT$ {{ product.price.toLocaleString() }}</div>
              <div class="stock-info" :class="{ 'low-stock': product.stock < 5 }">
                庫存：{{ product.stock }}
              </div>
            </div>
            
            <div class="product-actions">
              <div class="quantity-selector">
                <label>數量：</label>
                <select :value="getQuantity(product.id)" @input="updateQuantity(product.id, $event.target.value)" :disabled="product.stock === 0">
                  <option v-for="n in Math.min(product.stock, 10)" :key="n" :value="n">{{ n }}</option>
                </select>
              </div>
              
              <button 
                @click="addToCart(product)" 
                :disabled="product.stock === 0"
                class="add-to-cart-btn"
                :class="{ 'out-of-stock': product.stock === 0 }"
              >
                <i class="cart-icon">🛒</i>
                {{ product.stock === 0 ? '暫時缺貨' : '加入購物車' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProductList',
  data() {
    return {
      products: [],
      filteredProducts: [],
      quantities: {},
      loading: false,
      selectedCategory: '',
      sortBy: 'name',
      categories: []
    }
  },
  computed: {
    getQuantity() {
      return (productId) => {
        return this.quantities[productId] || 1
      }
    }
  },
  mounted() {
    this.loadProducts()
  },
  methods: {
    async loadProducts() {
      this.loading = true
      try {
        const response = await fetch('http://localhost:8000/api/products')
        if (response.ok) {
          this.products = await response.json()
          this.filteredProducts = [...this.products]
          this.extractCategories()
          this.initializeQuantities()
          this.sortProducts()
        }
      } catch (error) {
        console.error('載入商品失敗:', error)
      } finally {
        this.loading = false
      }
    },
    
    extractCategories() {
      this.categories = [...new Set(this.products.map(p => p.category).filter(Boolean))]
    },
    
    initializeQuantities() {
      const quantities = {}
      this.products.forEach(product => {
        quantities[product.id] = 1
      })
      this.quantities = quantities
    },
    
    filterProducts() {
      if (this.selectedCategory) {
        this.filteredProducts = this.products.filter(p => p.category === this.selectedCategory)
      } else {
        this.filteredProducts = [...this.products]
      }
      this.sortProducts()
    },
    
    sortProducts() {
      switch (this.sortBy) {
        case 'price-low':
          this.filteredProducts.sort((a, b) => a.price - b.price)
          break
        case 'price-high':
          this.filteredProducts.sort((a, b) => b.price - a.price)
          break
        case 'stock':
          this.filteredProducts.sort((a, b) => b.stock - a.stock)
          break
        case 'name':
        default:
          this.filteredProducts.sort((a, b) => a.name.localeCompare(b.name))
          break
      }
    },
    
    updateQuantity(productId, value) {
      this.$set(this.quantities, productId, parseInt(value))
    },
    
    async addToCart(product) {
      const quantity = this.getQuantity(product.id)
      
      try {
        const response = await fetch('http://localhost:8000/api/cart', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            product_id: product.id,
            quantity: quantity
          }),
          credentials: 'include'
        })
        
        if (response.ok) {
          this.$emit('cart-updated')
          this.showSuccessMessage(`${product.name} 已加入購物車！`)
        } else if (response.status === 401) {
          alert('登入已過期，請重新登入')
          localStorage.removeItem('user')
          window.location.reload()
        } else {
          const error = await response.json()
          alert(`加入購物車失敗：${error.detail}`)
        }
      } catch (error) {
        console.error('加入購物車失敗:', error)
        alert('加入購物車失敗，請稍後再試')
      }
    },
    
    showSuccessMessage(message) {
      // 簡單的成功提示
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
.product-list {
  max-width: 1900px;
  margin: 0 auto;
  padding: 0 20px;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 20px;
  margin-bottom: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border: 1px solid #e0e0e0;
}

.filter-section, .sort-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-section label, .sort-section label {
  font-weight: 600;
  color: #333;
}

.filter-section select, .sort-section select {
  padding: 8px 12px;
  border: 2px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  min-width: 150px;
}

.results-count {
  color: #666;
  font-weight: 500;
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

.products-container {
  background: white;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 25px;
}

.product-card {
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  background: white;
  transition: all 0.3s ease;
  overflow: hidden;
  position: relative;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
  border-color: #667eea;
}

.product-image-container {
  position: relative;
  height: 220px;
  overflow: hidden;
  background: #f8f9fa;
}

.product-image-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.product-card:hover .product-image-container img {
  transform: scale(1.05);
}

.out-of-stock-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: #ff4757;
  color: white;
  padding: 5px 10px;
  border-radius: 15px;
  font-size: 12px;
  font-weight: bold;
}

.product-details {
  padding: 20px;
}

.product-category {
  color: #667eea;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.product-title {
  margin: 0 0 10px 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  line-height: 1.4;
  height: 50px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.product-description {
  color: #666;
  font-size: 14px;
  line-height: 1.5;
  margin: 0 0 15px 0;
  height: 42px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.product-pricing {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.price {
  font-size: 24px;
  font-weight: bold;
  color: #e74c3c;
}

.stock-info {
  font-size: 14px;
  color: #27ae60;
  font-weight: 500;
}

.stock-info.low-stock {
  color: #f39c12;
}

.product-actions {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.quantity-selector {
  display: flex;
  align-items: center;
  gap: 10px;
}

.quantity-selector label {
  font-weight: 500;
  color: #333;
}

.quantity-selector select {
  padding: 6px 10px;
  border: 2px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.add-to-cart-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.add-to-cart-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.add-to-cart-btn:disabled,
.add-to-cart-btn.out-of-stock {
  background: #bbb;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.cart-icon {
  font-size: 18px;
}

/* 成功提示樣式 */
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
@media (max-width: 768px) {
  .filter-bar {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .filter-section, .sort-section {
    justify-content: space-between;
  }
  
  .products-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
  }
  
  .products-container {
    padding: 20px;
  }
}
</style> 