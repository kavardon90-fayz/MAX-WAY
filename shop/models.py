
from django.db import models
from django.db.models import Q


class Category(models.Model):
    title = models.CharField(null=False, blank=False, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at", "-id")

    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.CharField(null=False, blank=False, max_length=100)
    description = models.TextField(null=False, blank=False)
    category = models.ForeignKey(
        Category,
        null=True,
        on_delete=models.SET_NULL
    )
    cost = models.IntegerField(null=False, blank=False)
    price = models.IntegerField(null=False, blank=False)
    image = models.ImageField(upload_to='products')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at", "-id")
        constraints = [
            models.CheckConstraint(
                condition=Q(cost__gte=1),
                name='product_cost_gte_1',
            ),
            models.CheckConstraint(
                condition=Q(price__gte=1),
                name='product_price_gte_1',
            ),
        ]

    def __str__(self):
        return self.title


class Customer(models.Model):
    user = models.OneToOneField(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customer_profile'
    )

    first_name = models.CharField(null=False, blank=False, max_length=100)
    last_name = models.CharField(null=False, blank=False, max_length=100)
    phone_number = models.CharField(
        null=False,
        unique=True,
        blank=False,
        max_length=100
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at", "-id")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Order(models.Model):
    PAYMENT_CHOICES = [
        (1, 'Naqd'),
        (2, 'Karta'),
    ]

    DELIVERY_CHOICES = [
        (1, 'Dostavka kerak'),
        (2, 'Dostavka kerak emas'),
    ]

    payment_type = models.IntegerField(
        choices=PAYMENT_CHOICES,
        null=False,
        blank=False,
    )

    delivery_type = models.IntegerField(
        choices=DELIVERY_CHOICES,
        null=False,
        blank=False,
        default=1,
    )

    status = models.IntegerField(null=False, blank=True, default=1)

    address = models.CharField(null=False, blank=False, max_length=250)

    guest_first_name = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    guest_last_name = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    guest_phone = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    customer = models.ForeignKey(
        Customer,
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )

    checkout_token = models.UUIDField(
        null=True,
        blank=True,
        unique=True,
        editable=False,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at", "-id")


class OrderProduct(models.Model):
    count = models.IntegerField(null=False, blank=False)
    price = models.IntegerField(null=False, blank=False)

    product_title = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    product = models.ForeignKey(
        Product,
        null=True,
        on_delete=models.SET_NULL
    )

    order = models.ForeignKey(
        Order,
        null=True,
        on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ("-created_at", "-id")
        constraints = [
            models.CheckConstraint(
                condition=Q(count__gte=1),
                name='orderproduct_count_gte_1',
            ),
            models.CheckConstraint(
                condition=Q(price__gte=1),
                name='orderproduct_price_gte_1',
            ),
        ]
