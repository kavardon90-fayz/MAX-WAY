from django.shortcuts import render, redirect

from rest_framework import viewsets

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


def increase_cart(request, product_id):
    cart_data = request.session.get('cart', {})

    product_id = str(product_id)

    if product_id in cart_data:
        cart_data[product_id] += 1

    request.session['cart'] = cart_data

    return redirect('cart')


def decrease_cart(request, product_id):
    cart_data = request.session.get('cart', {})

    product_id = str(product_id)

    if product_id in cart_data:

        cart_data[product_id] -= 1

        if cart_data[product_id] <= 0:
            del cart_data[product_id]

    request.session['cart'] = cart_data

    return redirect('cart')


def remove_from_cart(request, product_id):
    cart_data = request.session.get('cart', {})

    product_id = str(product_id)

    if product_id in cart_data:
        del cart_data[product_id]

    request.session['cart'] = cart_data

    return redirect('cart')


# ==========================================
# ORDER PAGE
# ==========================================

def order_page(request):

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

    # ==========================================
    # BUYURTMA QABUL QILISH
    # ==========================================

    if request.method == 'POST':

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')

        address = request.POST.get('address')

        payment_type = request.POST.get('payment_type')
        delivery_type = request.POST.get('delivery_type')

        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        # ==========================================
        # CUSTOMER
        # ==========================================

        customer, created = Customer.objects.get_or_create(
            phone_number=phone,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
            }
        )

        if not created:

            customer.first_name = first_name
            customer.last_name = last_name

            customer.save()

        # ==========================================
        # ORDER
        # ==========================================

        order = Order.objects.create(

            payment_type=int(payment_type),

            delivery_type=int(delivery_type),

            address=address,

            latitude=float(latitude)
            if latitude else None,

            longitude=float(longitude)
            if longitude else None,

            customer=customer,
        )

        # ==========================================
        # ORDER PRODUCT
        # ==========================================

        for product in products:

            quantity = cart_data[str(product.id)]

            OrderProduct.objects.create(

                count=quantity,

                price=product.price,

                product=product,

                order=order,
            )

        # ==========================================
        # SAVATNI TOZALASH
        # ==========================================

        request.session['cart'] = {}

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
        }
    )


# ==========================================
# DRF API
# ==========================================

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class OrderProductViewSet(viewsets.ModelViewSet):
    queryset = OrderProduct.objects.all()
    serializer_class = OrderProductSerializer