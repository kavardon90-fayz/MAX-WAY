from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    home,
    add_to_cart,
    cart,
    increase_cart,
    decrease_cart,
    remove_from_cart,
    order_page,
    CategoryViewSet,
    ProductViewSet,
    CustomerViewSet,
    OrderViewSet,
    OrderProductViewSet,
)


router = DefaultRouter()

router.register(
    'categories',
    CategoryViewSet,
    basename='category'
)

router.register(
    'products',
    ProductViewSet,
    basename='product'
)

router.register(
    'customers',
    CustomerViewSet,
    basename='customer'
)

router.register(
    'orders',
    OrderViewSet,
    basename='order'
)

router.register(
    'order-products',
    OrderProductViewSet,
    basename='order-product'
)


urlpatterns = [

    # =========================
    # HOME
    # =========================

    path(
        '',
        home,
        name='home'
    ),

    # =========================
    # CART
    # =========================

    path(
        'add-to-cart/<int:product_id>/',
        add_to_cart,
        name='add_to_cart'
    ),

    path(
        'cart/',
        cart,
        name='cart'
    ),

    path(
        'cart/increase/<int:product_id>/',
        increase_cart,
        name='increase_cart'
    ),

    path(
        'cart/decrease/<int:product_id>/',
        decrease_cart,
        name='decrease_cart'
    ),

    path(
        'cart/remove/<int:product_id>/',
        remove_from_cart,
        name='remove_from_cart'
    ),

    # =========================
    # ORDER PAGE
    # =========================

    path(
        'order/',
        order_page,
        name='order_page'
    ),
]


urlpatterns += router.urls