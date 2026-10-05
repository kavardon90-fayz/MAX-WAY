# 🍔 MAX WAY — Food Delivery API

**MAX WAY** — oziq-ovqat buyurtma qilish va yetkazib berish uchun ishlab chiqilgan Django REST Framework asosidagi web API loyihasi.

Loyiha orqali mahsulotlarni ko‘rish, kategoriyalar bilan ishlash, mijoz yaratish, buyurtma berish va buyurtma tarkibini boshqarish mumkin.

## 🚀 Texnologiyalar

* Python 3.13
* Django 6.1
* Django REST Framework 3.18
* Simple JWT
* drf-spectacular
* SQLite
* Pillow
* Swagger / OpenAPI
* Git & GitHub

## 📌 Asosiy imkoniyatlar

* 🔐 JWT orqali autentifikatsiya
* 📂 Kategoriyalar bilan ishlash
* 🍔 Mahsulotlarni boshqarish
* 👤 Mijozlarni boshqarish
* 🛒 Buyurtmalar yaratish
* 📦 Buyurtma tarkibini boshqarish
* 🖼 Mahsulot rasmlarini yuklash
* 📍 Yetkazib berish manzili va koordinatalari
* 💳 To‘lov turi
* 🚚 Yetkazib berish turi
* 📖 Swagger orqali API hujjatlari

## 🔑 API autentifikatsiyasi

Loyiha JWT authentication tizimidan foydalanadi.

Token olish:

```text
POST /api/token/
```

Access token yangilash:

```text
POST /api/token/refresh/
```

Swagger'da tokenni olgandan so‘ng **Authorize** tugmasi orqali JWT tokenni kiritish mumkin.

## 📚 Swagger API Documentation

Loyihani ishga tushirgandan so‘ng Swagger hujjatlari quyidagi manzilda mavjud:

```text
http://127.0.0.1:8000/api/docs/
```

Swagger orqali API endpointlarni ko‘rish va test qilish mumkin.

## 📋 Asosiy API endpointlar

### Categories

```text
/shop/categories/
```

Kategoriyalarni ko‘rish, yaratish, o‘zgartirish va o‘chirish.

### Products

```text
/shop/products/
```

Mahsulotlarni boshqarish.

### Customers

```text
/shop/customers/
```

Mijozlarni boshqarish.

### Orders

```text
/shop/orders/
```

Buyurtmalarni boshqarish.

### Order Products

```text
/shop/order-products/
```

Buyurtma tarkibidagi mahsulotlarni boshqarish.

## 🗂 Loyiha tuzilishi

```text
MAX WAY/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── shop/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── ...
│
├── products/
├── media/
├── .gitignore
├── db.sqlite3
├── manage.py
└── README.md
```

## ⚙️ Loyihani ishga tushirish

Repository'ni yuklab olgandan so‘ng virtual environment yaratish:

```bash
python -m venv .venv
```

Virtual environment'ni faollashtirish:

Windows:

```bash
.venv\Scripts\activate
```

Kerakli paketlarni o‘rnatish:

```bash
pip install -r requirements.txt
```

Migrationlarni bajarish:

```bash
python manage.py migrate
```

Serverni ishga tushirish:

```bash
python manage.py runserver
```

Server:

```text
http://127.0.0.1:8000/
```

Swagger:

```text
http://127.0.0.1:8000/api/docs/
```

## 👨‍💻 Muallif

**Bahrom Baxtiyor Normatov**

MAX WAY — Django REST Framework kurs loyihasi.

## 📄 Loyiha holati

🚧 **Development / Course Project**

Loyiha Django REST Framework asosida ishlab chiqilgan va keyingi bosqichlarda production serverga deploy qilish rejalashtirilgan.

---

⭐ Agar loyiha foydali bo‘lsa, repository'ga Star qoldiring.
