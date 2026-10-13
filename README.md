## 🔗 Foydali havolalar

| Resurs | Havola |
|---|---|
| 📦 GitHub Repository | https://github.com/kavardon90-fayz/MAX-WAY |
| 📖 Swagger API | http://13.48.55.73/api/docs/ |
| 📋 OpenAPI Schema | http://13.48.55.73/api/schema/ |

> **Eslatma:** Swagger va OpenAPI hujjatlari AWS serveriga joylashtirilgan va yuqoridagi havolalar orqali ochiladi.

## 🧪 API test natijalari

API endpointlari Swagger orqali tekshirildi.

### JWT Authentication

JWT token olish:

```text
POST /api/token/
```

Token olingandan so‘ng ruxsat talab qiladigan endpointlarga murojaat qilish mumkin.

### Category

Kategoriya yaratish:

```text
POST /shop/categories/
```

Natija: `HTTP 201 Created`

### Product

Mahsulotni olish:

```text
GET /shop/products/1/
```

Natija: `HTTP 200 OK`

### Customer

Mijoz yaratish:

```text
POST /shop/customers/
```

Natija: `HTTP 201 Created`

### Order

Buyurtma yaratish:

```text
POST /shop/orders/
```

Natija: `HTTP 201 Created`

### Order Product

Buyurtmaga mahsulot qo‘shish:

```text
POST /shop/order-products/
```

Natija: `HTTP 201 Created`

### API Documentation

Barcha API endpointlarini Swagger orqali ko‘rish va test qilish mumkin:

http://13.48.55.73/api/docs/

Ushbu loyiha davomida asosiy CRUD operatsiyalari va JWT autentifikatsiyasi tekshirildi.
