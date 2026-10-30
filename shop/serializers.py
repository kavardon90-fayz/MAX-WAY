
from rest_framework import serializers
from .models import Category, Product, Customer, Order, OrderProduct


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if request is not None and not getattr(user, 'is_staff', False):
            self.fields.pop('cost', None)

    image = serializers.ImageField()

    category_title = serializers.CharField(
        source='category.title',
        read_only=True
    )

    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'description',
            'category',
            'category_title',
            'cost',
            'price',
            'image',
            'created_at',
        ]


class ProductWriteSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    category_title = serializers.CharField(
        source='category.title',
        read_only=True
    )

    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'description',
            'category',
            'category_title',
            'cost',
            'price',
            'image',
            'created_at',
        ]
        read_only_fields = ['id', 'category_title', 'created_at']


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            'id',
            'first_name',
            'last_name',
            'phone_number',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'payment_type',
            'delivery_type',
            'status',
            'address',
            'latitude',
            'longitude',
            'customer',
            'created_at',
        ]
        read_only_fields = ['status', 'created_at']


class OrderProductSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField(min_value=1)
    price = serializers.IntegerField(read_only=True)
    product_title = serializers.CharField(read_only=True)

    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        required=True,
        allow_null=False,
    )

    order = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(),
        required=True,
        allow_null=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance is not None:
            self.fields['order'].read_only = True

    class Meta:
        model = OrderProduct
        fields = [
            'id',
            'count',
            'price',
            'product_title',
            'created_at',
            'product',
            'order',
        ]
        read_only_fields = [
            'id',
            'price',
            'product_title',
            'created_at',
        ]
