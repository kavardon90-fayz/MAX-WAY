## 🔗 Foydali havolalar## 🔗 Foydali havolalar

| Resurs | Havola |
|---|---|
| 📦 GitHub Repository | [MAX WAY](https://github.com/kavardon90-fayz/MAX-WAY) |
| 📖 Swagger API Documentation (AWS) | [Swagger](http://13.48.55.73/api/docs/) |
| 📋 OpenAPI Schema (AWS) | [OpenAPI Schema](http://13.48.55.73/api/schema/) |
| 🧪 Local Swagger (Docker) | http://127.0.0.1:8000/api/docs/ |

**Eslatma:** AWS havolalari server ishlayotgan va ulanishga ruxsat berilgan paytda ochiladi. Lokal Swagger esa Docker konteyneri kompyuteringizda ishlayotganida ochiladi.

## 🧪 API test natijalari

Asosiy API endpointlari Swagger orqali tekshirildi.

### JWT Authentication

Token olish:

```text
POST /api/token/
```

Natija: `HTTP 200 OK`

Refresh token orqali yangi access token olish:

```text
POST /api/token/refresh/
```

Natija: `HTTP 200 OK`

### Category

Kategoriyalar ro‘yxatini olish:

```text
GET /shop/categories/
```

Natija: `HTTP 200 OK`

### Product

Mahsulotlar ro‘yxatini olish:

```text
GET /shop/products/
```

Natija: `HTTP 200 OK`

Mahsulot yaratish va rasm yuklash, shuningdek mahsulot narxini `PATCH` orqali yangilash ham tekshirildi.

### Customer

Mijozlar ro‘yxatini olish:

```text
GET /shop/customers/
```

Natija: `HTTP 200 OK`

### Order

Buyurtmalar ro‘yxatini olish:

```text
GET /shop/orders/
```

Natija: `HTTP 200 OK`

### Order Product

Buyurtma tarkibidagi mahsulotlar ro‘yxatini olish:

```text
GET /shop/order-products/
```

Natija: `HTTP 200 OK`

### API Documentation

Barcha endpointlarni ko‘rish va qo‘llab-quvvatlanadigan so‘rovlarni Swagger orqali sinash mumkin:

[AWS Swagger Documentation](http://13.48.55.73/api/docs/)

Ushbu loyiha Django REST Framework yordamida ishlab chiqilgan. Loyihada CRUD operatsiyalari, JWT autentifikatsiyasi, Docker orqali ishga tushirish va Swagger/OpenAPI hujjatlari bilan ishlash imkoniyatlari mavjud.