# 🛍️ Storefront (Django – Advanced Variation)

**Duration:** Jun 2025 – Sep 2025  
**Repository:** [GitHub](#)  

An alternative version of the Storefront e-commerce application with a different architecture and advanced features.  

---

## 🚀 Features

### 🛒 Cart System
- Implemented **session-based carts** for anonymous users.  
- Used **Django signals** to automatically **merge session carts with user carts** upon login.  

### 🔐 Authentication
- Built **custom authentication** using **phone number + password** instead of username/email.  
- Added **phone number validation** for secure account creation.  

### ⚡ Caching
- Integrated **DRF-extensions response caching** with **Redis**.  
- Enabled **automatic cache invalidation** on updates/deletes.  

### ⭐ Favorites
- Implemented a **favorites system** using **Django’s ContentType framework**.  
- Supported **generic relationships** (e.g., products, categories, or any model).  

### 🔧 Other Enhancements
- Reused core e-commerce features (**products, orders, admin dashboard**).  
- Modified data flows for **scalability and flexibility**.  

---

## 📦 Tech Stack
- **Backend:** Django, Django REST Framework  
- **Authentication:** Custom phone/password system  
- **Caching:** Redis + DRF-extensions  
- **Database:** PostgreSQL (or SQLite for dev)  
- **Utilities:** Django signals, ContentType framework  

---

## 📑 Notes
This variation focuses on **flexibility and extensibility**:  
- Anonymous users can shop and merge carts later.  
- Phone number authentication offers a real-world login flow.  
- Generic favorites system supports multiple models.  
