from rest_framework import serializers
from .models import Category, Product, Customer, Order, OrderProduct


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
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


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = '__all__'