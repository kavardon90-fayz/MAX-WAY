# MAX WAY — Food Delivery API

MAX WAY — oziq-ovqat va taom mahsulotlari, kategoriyalar, mijozlar hamda buyurtmalar bilan ishlash uchun yaratilgan REST API loyihasi.

## Loyiha imkoniyatlari

- Mahsulotlar va kategoriyalarni ko‘rish hamda boshqarish
- Mijozlar va buyurtmalar bilan ishlash
- JWT orqali autentifikatsiya
- Ruxsatlarni boshqarish
- Mahsulot rasmlarini yuklash
- Swagger/OpenAPI orqali API hujjatlarini ko‘rish va so‘rovlarni sinash
- Docker orqali loyihani ishga tushirish

## Texnologiyalar

- Python 3.13
- Django 6.1
- Django REST Framework 3.18.1
- Simple JWT 5.5.1
- drf-spectacular 0.30.0
- SQLite
- Pillow
- Docker va Docker Compose
- Swagger/OpenAPI
- Git va GitHub
- AWS EC2 va Nginx

## Foydali havolalar

| Resurs | Havola |
|---|---|
| GitHub Repository | https://github.com/kavardon90-fayz/MAX-WAY |
| AWS Swagger | http://13.48.55.73/api/docs/ |
| AWS OpenAPI Schema | http://13.48.55.73/api/schema/ |
| Lokal Swagger | http://127.0.0.1:8000/api/docs/ |

**Eslatma:** AWS manzillari server va tarmoq sozlamalari ishlayotganida ochiladi. Lokal Swagger uchun Docker konteyneri ishga tushirilgan bo‘lishi kerak.

## API endpointlari

| Vazifa | Endpoint |
|---|---|
| JWT token olish | `POST /api/token/` |
| Access tokenni yangilash | `POST /api/token/refresh/` |
| Kategoriyalar | `/shop/categories/` |
| Mahsulotlar | `/shop/products/` |
| Mijozlar | `/shop/customers/` |
| Buyurtmalar | `/shop/orders/` |
| Buyurtma mahsulotlari | `/shop/order-products/` |

## Autentifikatsiya va ruxsatlar

JWT yordamida foydalanuvchi autentifikatsiyasi qo‘llanadi. Mahsulotlar va kategoriyalar uchun o‘qish hamda o‘zgartirish ruxsatlari ajratilgan. Mijozlar, buyurtmalar va buyurtma tarkibi bilan ishlash administrator ruxsatlari bilan cheklanadi.

## CRUD va testlar

Mahsulotlar hamda kategoriyalar uchun yaratish, ko‘rish, yangilash va o‘chirish amallari Swagger orqali tekshirildi.

Django testlari Docker konteynerida bajarildi:

```powershell
docker compose exec web python manage.py test shop
```

Oxirgi tekshiruvda **7 ta test muvaffaqiyatli o‘tdi**.

Django tizim tekshiruvi:

```powershell
docker compose exec web python manage.py check
```

Natija: `System check identified no issues (0 silenced).`

## Docker orqali ishga tushirish

Loyiha papkasida Docker Desktop ishga tushirilgan bo‘lishi kerak.

Konteynerlarni ishga tushirish:

```powershell
docker compose up -d --build
```

Konteynerlar holatini tekshirish:

```powershell
docker compose ps
```

Lokal Swagger manzili:

http://127.0.0.1:8000/api/docs/

## Loyiha muallifi

Bahrom Normatov

Ushbu loyiha Django REST Framework, JWT autentifikatsiyasi, Docker va AWS EC2 yordamida REST API yaratish ko‘nikmalarini namoyish etish uchun tayyorlangan.