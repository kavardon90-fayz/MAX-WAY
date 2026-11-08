import math
import re
import uuid
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.db import transaction, IntegrityError

from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .permissions import IsAdminOrReadOnly

from .models import (
    Product,
    Customer,
    Order,
    OrderProduct,
    Category,
)

from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductWriteSerializer,
    CustomerSerializer,
    OrderSerializer,
    OrderProductSerializer,
)


# ==========================================
# HOME
# ==========================================

def home(request):
    products = Product.objects.all()

    return render(request, 'shop/home.html', {
        'products': products
    })


# ==========================================
# CART
# ==========================================

@require_POST
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})

    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1

    request.session['cart'] = cart

    return redirect('home')


def cart(request):
    cart_data = request.session.get('cart', {})

    products = Product.objects.filter(
        id__in=cart_data.keys()
    )

    cart_items = []
    grand_total = 0

    for product in products:

        quantity = cart_data[str(product.id)]
        total = product.price * quantity

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total': total,
        })

        grand_total += total

    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'grand_total': grand_total,
    })






@require_POST
def increase_cart(request, product_id):
    cart_data = request.session.get('cart', {})

    if not isinstance(cart_data, dict):
        cart_data = {}

    product_id = str(product_id)

    if Product.objects.filter(id=product_id).exists():
        try:
            quantity = int(cart_data.get(product_id, 0))
        except (ValueError, TypeError):
            quantity = 0

        cart_data[product_id] = max(0, quantity) + 1

    request.session['cart'] = cart_data
    request.session.modified = True

    return redirect('cart')




@require_POST
def decrease_cart(request, product_id):
    cart_data = request.session.get('cart', {})

    if not isinstance(cart_data, dict):
        cart_data = {}

    product_id = str(product_id)

    if product_id in cart_data:
        try:
            quantity = int(cart_data[product_id])
        except (ValueError, TypeError):
            quantity = 0

        if quantity <= 1:
            del cart_data[product_id]
        else:
            cart_data[product_id] = quantity - 1

    request.session['cart'] = cart_data
    request.session.modified = True

    return redirect('cart')




@require_POST
def remove_from_cart(request, product_id):
    cart_data = request.session.get('cart', {})

    if not isinstance(cart_data, dict):
        cart_data = {}

    product_id = str(product_id)
    cart_data.pop(product_id, None)

    request.session['cart'] = cart_data
    request.session.modified = True

    return redirect('cart')



# ==========================================
# ORDER PAGE
# ==========================================

def order_page(request):
    if not request.session.session_key:
        request.session.create()

    checkout_token = request.session.get('checkout_token')

    if not checkout_token:
        checkout_token = str(uuid.uuid4())
        request.session['checkout_token'] = checkout_token

    cart_data = request.session.get('cart', {})

    if not isinstance(cart_data, dict):
        cart_data = {}

    valid_cart = {}

    for product_id, quantity in cart_data.items():
        try:
            product_id = str(int(product_id))
            quantity = int(quantity)
        except (ValueError, TypeError):
            continue

        if quantity > 0:
            valid_cart[product_id] = quantity

    cart_data = valid_cart

    products = list(
        Product.objects.filter(id__in=cart_data.keys())
    )

    valid_ids = {str(product.id) for product in products}

    cart_data = {
        product_id: quantity
        for product_id, quantity in cart_data.items()
        if product_id in valid_ids
    }

    cart_items = []
    grand_total = 0

    for product in products:
        quantity = cart_data[str(product.id)]
        total = product.price * quantity

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total': total,
        })

        grand_total += total

    # ==========================================
    # BUYURTMA QABUL QILISH
    # ==========================================

    if request.method == 'POST':

        submitted_token = request.POST.get('checkout_token', '')
        session_token = request.session.get('checkout_token')

        if not submitted_token or submitted_token != session_token:
            return redirect('order_page')

        if Order.objects.filter(checkout_token=submitted_token).exists():
            request.session['checkout_token'] = str(uuid.uuid4())
            request.session.modified = True
            return redirect('home')

        if not cart_items:
            return redirect('cart')

        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()

        # ==========================================
        # TELEFON RAQAMINI TEKSHIRISH
        # ==========================================

        phone_digits = re.sub(r'\D', '', phone)

        if not re.fullmatch(r'(?:998)?\d{9}', phone_digits):
            return redirect('order_page')

        if len(phone_digits) == 12 and phone_digits.startswith('998'):
            phone_digits = phone_digits[3:]

        phone = '+998' + phone_digits

        # ==========================================
        # MAJBURIY MAYDONLARNI TEKSHIRISH
        # ==========================================

        if not all([
            first_name,
            last_name,
            phone,
            address,
        ]):
            return redirect('order_page')

        payment_type = request.POST.get('payment_type')
        delivery_type = request.POST.get('delivery_type')

        if payment_type not in ('1', '2'):
            return redirect('order_page')

        if delivery_type not in ('1', '2'):
            return redirect('order_page')

        # ==========================================
        # KOORDINATALARNI TEKSHIRISH
        # ==========================================

        latitude_raw = request.POST.get('latitude', '').strip()
        longitude_raw = request.POST.get('longitude', '').strip()

        # Ikkala koordinata birgalikda yuborilishi kerak.
        # Ikkalasi bo'sh bo'lsa, manzil orqali buyurtma qabul qilinadi.
        if bool(latitude_raw) != bool(longitude_raw):
            return redirect('order_page')

        try:
            latitude = float(latitude_raw) if latitude_raw else None
            longitude = float(longitude_raw) if longitude_raw else None
        except (ValueError, TypeError):
            return redirect('order_page')

        # NaN va Infinity qiymatlarini rad etish.
        if latitude is not None and not math.isfinite(latitude):
            return redirect('order_page')

        if longitude is not None and not math.isfinite(longitude):
            return redirect('order_page')

        # Geografik chegaralarni tekshirish.
        if latitude is not None and not -90 <= latitude <= 90:
            return redirect('order_page')

        if longitude is not None and not -180 <= longitude <= 180:
            return redirect('order_page')

        # ==========================================
        # BUYURTMA VA MAHSULOTLARNI SAQLASH
        # ==========================================

        try:
            with transaction.atomic():

                existing_customer = Customer.objects.filter(
                    phone_number=phone
                ).first()

                if existing_customer is None:
                    customer = Customer.objects.create(
                        phone_number=phone,
                        first_name=first_name,
                        last_name=last_name,
                    )
                else:
                    # Mavjud mijoz ma'lumotlarini o'zgartirmaymiz.
                    customer = None

                order = Order.objects.create(
                    payment_type=int(payment_type),
                    delivery_type=int(delivery_type),
                    address=address,
                    latitude=latitude,
                    longitude=longitude,
                    customer=customer,
                    guest_first_name=first_name,
                    guest_last_name=last_name,
                    guest_phone=phone,
                    checkout_token=submitted_token,
                )

                for product in products:
                    quantity = cart_data[str(product.id)]

                    OrderProduct.objects.create(
                        count=quantity,
                        price=product.price,
                        product_title=product.title,
                        product=product,
                        order=order,
                    )

        except IntegrityError:
            # Bir xil token bilan parallel buyurtma kelgan bo'lsa,
            # takroriy buyurtmani yaratmaymiz.
            if Order.objects.filter(
                checkout_token=submitted_token
            ).exists():
                request.session['cart'] = {}
                request.session['checkout_token'] = str(uuid.uuid4())
                request.session.modified = True
                return redirect('home')

            # Boshqa ma'lumotlar bazasi xatosini yashirmaymiz.
            raise

        # ==========================================
        # MUVAFFAQIYATLI BUYURTMADAN KEYIN
        # ==========================================

        request.session['cart'] = {}
        request.session['checkout_token'] = str(uuid.uuid4())
        request.session.modified = True

        return redirect('home')

    # ==========================================
    # ORDER PAGE
    # ==========================================

    return render(
        request,
        'shop/order.html',
        {
            'cart_items': cart_items,
            'grand_total': grand_total,
            'checkout_token': checkout_token,
        }
    )


# ==========================================
# DRF API
# ==========================================

class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductWriteSerializer
        return ProductSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()
    def get_permissions(self):
        if self.action == "destroy":
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Customer.objects.all()

        return Customer.objects.filter(user=user)

    def perform_create(self, serializer):
        from rest_framework.exceptions import ValidationError

        if self.request.user.is_staff:
            serializer.save()
            return

        if Customer.objects.filter(user=self.request.user).exists():
            raise ValidationError({
                "detail": "Sizda mijoz profili allaqachon mavjud."
            })

        serializer.save(user=self.request.user)


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Order.objects.all()

        return Order.objects.filter(customer__user=user)

    def perform_create(self, serializer):
        user = self.request.user

        if user.is_staff:
            serializer.save()
            return

        try:
            customer = user.customer_profile
        except Customer.DoesNotExist:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({
                "customer": "Buyurtma berishdan oldin mijoz profilingizni yarating."
            })

        serializer.save(customer=customer)


class OrderProductViewSet(viewsets.ModelViewSet):
    serializer_class = OrderProductSerializer
    queryset = OrderProduct.objects.all()

    def get_permissions(self):
        if self.action in ["list", "retrieve", "create"]:
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return OrderProduct.objects.all()

        return OrderProduct.objects.filter(
            order__customer__user=user
        )

    def perform_create(self, serializer):
        product = serializer.validated_data["product"]

        serializer.save(
            price=product.price,
            product_title=product.title,
        )

    def perform_update(self, serializer):
        product = serializer.validated_data.get(
            "product",
            serializer.instance.product,
        )

        if product is None:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({
                "product": "Mahsulot tanlanishi shart."
            })

        serializer.save(
            price=product.price,
            product_title=product.title,
        )
