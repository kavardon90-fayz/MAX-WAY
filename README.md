## 🔗 Foydali havolalar

| Resurs               | Havola                                       |
| -------------------- | -------------------------------------------- |
| 📦 GitHub Repository | `https://github.com/kavardon90-fayz/MAX-WAY` |
| 📖 Swagger API       | `http://127.0.0.1:8000/api/docs/`            |
| 📋 OpenAPI Schema    | `http://127.0.0.1:8000/api/schema/`          |

> **Eslatma:** Swagger va OpenAPI manzillari loyiha lokal serverda ishga tushirilganda ishlaydi. Deploy qilingandan keyin ular production server manziliga almashtiriladi.

## 🧪 API test natijalari

API endpointlar Swagger orqali muvaffaqiyatli test qilindi.

### JWT Authentication

JWT token olish:

```text
POST /api/token/
```

Token muvaffaqiyatli olingandan so‘ng himoyalangan endpointlarga murojaat qilish mumkin.

### Category

Kategoriya yaratish:

```text
POST /shop/categories/
```

Natija:

```text
HTTP 201 Created
```

### Product

Mahsulotni olish:

```text
GET /shop/products/1/
```

Natija:

```text
HTTP 200 OK
```

Misol:

```json
{
  "id": 1,
  "title": "osh",
  "category": 3,
  "category_title": "milliy taomlar",
  "cost": 25000,
  "price": 25000
}
```

### Customer

Mijoz yaratish:

```text
POST /shop/customers/
```

Natija:

```text
HTTP 201 Created
```

### Order

Buyurtma yaratish:

```text
POST /shop/orders/
```

Natija:

```text
HTTP 201 Created
```

### Order Product

Buyurtmaga mahsulot qo‘shish:

```text
POST /shop/order-products/
```

Natija:

```text
HTTP 201 Created
```

Misol:

```json
{
  "id": 24,
  "count": 1,
  "price": 30000
}
```

### API Documentation

Barcha endpointlarni Swagger orqali ko‘rish va test qilish mumkin:

```text
http://127.0.0.1:8000/api/docs/
```

Ushbu loyiha davomida asosiy CRUD operatsiyalari va JWT authentication muvaffaqiyatli tekshirildi.

