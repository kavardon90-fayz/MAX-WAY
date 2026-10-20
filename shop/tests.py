from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Category


class APIPermissionsTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(
            username="regular_test_user",
            password="Test-password-123",
        )
        cls.admin = User.objects.create_superuser(
            username="admin_test_user",
            email="admin-test@example.com",
            password="Test-password-123",
        )
        Category.objects.create(title="Test category")

    def test_anonymous_user_cannot_read_products(self):
        response = self.client.get("/shop/products/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_read_products(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/shop/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_regular_user_cannot_create_category(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/shop/categories/",
            {"title": "Unauthorized category"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_category(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            "/shop/categories/",
            {"title": "Admin category"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_regular_user_cannot_access_customers(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/shop/customers/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_user_cannot_access_orders(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/shop/orders/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_user_cannot_access_order_products(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/shop/order-products/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
