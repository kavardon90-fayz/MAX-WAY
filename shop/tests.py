from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
from .serializers import ProductSerializer
from .models import Category, Customer, Order, OrderProduct, Product


class APIPermissionsTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()

        cls.user = User.objects.create_user(
            username="regular_test_user",
            password="Test-password-123",
        )
        cls.other_user = User.objects.create_user(
            username="other_test_user",
            password="Test-password-123",
        )
        cls.admin = User.objects.create_superuser(
            username="admin_test_user",
            email="admin-test@example.com",
            password="Test-password-123",
        )

        cls.category = Category.objects.create(title="Test category")

        cls.customer = Customer.objects.create(
            user=cls.user,
            first_name="Regular",
            last_name="Test",
            phone_number="998901111111",
        )
        cls.other_customer = Customer.objects.create(
            user=cls.other_user,
            first_name="Other",
            last_name="Test",
            phone_number="998902222222",
        )

        cls.order = Order.objects.create(
            customer=cls.customer,
            payment_type=1,
            delivery_type=1,
            address="Regular test address",
        )
        cls.order_product = OrderProduct.objects.create(
            order=cls.order,
            count=1,
            price=1000,
            product_title="Regular user's product",
        )
        cls.other_order = Order.objects.create(
            customer=cls.other_customer,
            payment_type=1,
            delivery_type=1,
            address="Other test address",
        )

        cls.other_order_product = OrderProduct.objects.create(
            order=cls.other_order,
            count=1,
            price=1000,
            product_title="Other user's product",
        )

    def test_anonymous_user_can_read_products(self):
        response = self.client.get("/shop/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_user_can_read_categories(self):
        response = self.client.get("/shop/categories/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_user_can_read_products(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/shop/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_regular_user_api_response_hides_product_cost(self):
            product = Product.objects.create(
                title="Public test product",
                description="Test description",
                category=self.category,
                cost=10000,
                price=25000,
                image=SimpleUploadedFile(
                    "public-test.jpg",
                    b"test-image-content",
                    content_type="image/jpeg",
                ),
            )

            self.client.force_authenticate(user=self.user)
            response = self.client.get("/shop/products/")

            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
            )

            product_data = next(
                item for item in response.data["results"]
                if item["id"] == product.id
            )
            self.assertNotIn("cost", product_data)

    def test_regular_user_cannot_see_product_cost(self):
        request = APIRequestFactory().get("/shop/products/")
        request.user = self.user

        serializer = ProductSerializer(
            context={"request": request}
        )

        self.assertNotIn("cost", serializer.fields)

    def test_admin_can_see_product_cost(self):
        request = APIRequestFactory().get("/shop/products/")
        request.user = self.admin

        serializer = ProductSerializer(
            context={"request": request}
        )

        self.assertIn("cost", serializer.fields)

    def test_regular_user_cannot_create_product(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/shop/products/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

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

    def test_admin_order_product_uses_server_product_price_and_title(self):
        self.client.force_authenticate(user=self.admin)

        product = Product.objects.create(
            title="Real product title",
            description="Test description",
            category=self.category,
            cost=10000,
            price=25000,
            image=SimpleUploadedFile(
                "test.jpg",
                b"test-image-content",
                content_type="image/jpeg",
            ),
        )

        response = self.client.post(
            "/shop/order-products/",
            {
                "count": 2,
                "price": 1,
                "product_title": "Fake product title",
                "product": product.id,
                "order": self.order.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            getattr(response, "data", response.content),
        )

        item = OrderProduct.objects.get(id=response.data["id"])
        self.assertEqual(item.price, product.price)
        self.assertEqual(item.product_title, product.title)

    def test_admin_order_product_update_refreshes_price_and_title(self):
        self.client.force_authenticate(user=self.admin)

        old_product = Product.objects.create(
            title="Old product",
            description="Test description",
            category=self.category,
            cost=10000,
            price=20000,
            image=SimpleUploadedFile(
                "old.jpg",
                b"old-image-content",
                content_type="image/jpeg",
            ),
        )

        new_product = Product.objects.create(
            title="New product",
            description="Test description",
            category=self.category,
            cost=15000,
            price=35000,
            image=SimpleUploadedFile(
                "new.jpg",
                b"new-image-content",
                content_type="image/jpeg",
            ),
        )

        item = OrderProduct.objects.create(
            count=1,
            price=old_product.price,
            product_title=old_product.title,
            product=old_product,
            order=self.order,
        )

        response = self.client.patch(
            f"/shop/order-products/{item.id}/",
            {"product": new_product.id},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            getattr(response, "data", response.content),
        )

        item.refresh_from_db()
        self.assertEqual(item.product_id, new_product.id)
        self.assertEqual(item.price, new_product.price)
        self.assertEqual(item.product_title, new_product.title)

    def test_regular_user_can_read_customers_endpoint(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/shop/customers/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_regular_user_cannot_read_other_users_order_product(self):
            self.client.force_authenticate(user=self.user)

            response = self.client.get(
                f"/shop/order-products/{self.other_order_product.id}/"
            )

            self.assertEqual(
                response.status_code,
                status.HTTP_404_NOT_FOUND,
            )
    def test_admin_cannot_move_order_product_to_another_order(self):
        self.client.force_authenticate(user=self.admin)

        item = self.order_product

        response = self.client.patch(
            f"/shop/order-products/{item.id}/",
            {"order": self.other_order.id},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            getattr(response, "data", response.content),
        )

        item.refresh_from_db()
        self.assertEqual(item.order_id, self.order.id)
    def test_regular_user_can_update_own_customer(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            f"/shop/customers/{self.customer.id}/",
            {"first_name": "Updated"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.first_name, "Updated")

    def test_regular_user_cannot_create_second_customer(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/shop/customers/",
            {
                "first_name": "Second",
                "last_name": "Customer",
                "phone_number": "998903333333",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(
            Customer.objects.filter(phone_number="998903333333").exists()
        )

    def test_regular_user_can_read_orders_endpoint(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/shop/orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_regular_user_cannot_create_order(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/shop/orders/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    def test_order_customer_is_read_only(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            "/shop/orders/",
            {
                "payment_type": 1,
                "delivery_type": 1,
                "address": "Test address",
                "customer": self.other_customer.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            getattr(response, "data", response.content),
        )

        created_order = Order.objects.get(id=response.data["id"])
        self.assertIsNone(created_order.customer_id)
    def test_regular_user_cannot_update_order(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            f"/shop/orders/{self.order.id}/",
            {"address": "Unauthorized change"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_user_cannot_delete_order(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"/shop/orders/{self.order.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Order.objects.filter(id=self.order.id).exists())

    def test_regular_user_can_read_order_products_endpoint(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/shop/order-products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_cannot_create_order_product_with_unknown_product(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            "/shop/order-products/",
            {
                "count": 1,
                "product": 999999,
                "order": self.order.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_admin_cannot_create_order_product_with_unknown_order(self):
        self.client.force_authenticate(user=self.admin)

        product = Product.objects.create(
            title="Unknown order test product",
            description="Test description",
            category=self.category,
            cost=10000,
            price=25000,
            image=SimpleUploadedFile(
                "unknown-order-test.jpg",
                b"test-image-content",
                content_type="image/jpeg",
            ),
        )

        response = self.client.post(
            "/shop/order-products/",
            {
                "count": 1,
                "product": product.id,
                "order": 999999,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_admin_cannot_create_order_product_without_product(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            "/shop/order-products/",
            {
                "count": 1,
                "order": self.order.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_admin_cannot_create_order_product_without_order(self):
        self.client.force_authenticate(user=self.admin)

        product = Product.objects.create(
            title="Missing order test product",
            description="Test description",
            category=self.category,
            cost=10000,
            price=25000,
            image=SimpleUploadedFile(
                "missing-order-test.jpg",
                b"test-image-content",
                content_type="image/jpeg",
            ),
        )

        response = self.client.post(
            "/shop/order-products/",
            {
                "count": 1,
                "product": product.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
    def test_admin_cannot_create_order_product_with_zero_count(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            "/shop/order-products/",
            {
                "count": 0,
                "product": self.order_product.product_id,
                "order": self.order.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_admin_cannot_create_order_product_with_negative_count(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            "/shop/order-products/",
            {
                "count": -1,
                "product": self.order_product.product_id,
                "order": self.order.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
    def test_regular_user_cannot_create_order_product(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/shop/order-products/",
            {},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_user_cannot_update_order_product(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            f"/shop/order-products/{self.order_product.id}/",
            {"count": 99, "price": 1},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.order_product.refresh_from_db()
        self.assertEqual(self.order_product.count, 1)
        self.assertEqual(self.order_product.price, 1000)

    def test_regular_user_cannot_delete_order_product(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(
            f"/shop/order-products/{self.order_product.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(
            OrderProduct.objects.filter(id=self.order_product.id).exists()
        )

    def test_user_cannot_read_another_customer(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            f"/shop/customers/{self.other_customer.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_update_another_customer(self):
        self.client.force_authenticate(user=self.user)

        original_first_name = self.other_customer.first_name
        original_last_name = self.other_customer.last_name
        original_phone = self.other_customer.phone_number

        response = self.client.patch(
            f"/shop/customers/{self.other_customer.id}/",
            {
                "first_name": "Unauthorized",
                "last_name": "Change",
                "phone_number": "+998901234567",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.other_customer.refresh_from_db()
        self.assertEqual(self.other_customer.first_name, original_first_name)
        self.assertEqual(self.other_customer.last_name, original_last_name)
        self.assertEqual(self.other_customer.phone_number, original_phone)

    def test_user_cannot_delete_another_customer(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            f"/shop/customers/{self.other_customer.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertTrue(
            Customer.objects.filter(id=self.other_customer.id).exists()
        )

    def test_user_cannot_read_another_users_order(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            f"/shop/orders/{self.other_order.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_read_another_users_order_product(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            f"/shop/order-products/{self.other_order_product.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    def test_database_rejects_zero_order_product_price(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                OrderProduct.objects.create(
                    order=self.order,
                    count=1,
                    price=0,
                    product_title="Invalid zero price",
                )

    def test_database_rejects_negative_order_product_price(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                OrderProduct.objects.create(
                    order=self.order,
                    count=1,
                    price=-1,
                    product_title="Invalid negative price",
                )
class CheckoutTests(APITestCase):
    def test_empty_cart_does_not_create_order(self):
        before = Order.objects.count()

        session = self.client.session
        session["cart"] = {}
        session.save()

        response = self.client.get("/shop/order/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Order.objects.count(), before)

    def test_invalid_payment_type_does_not_create_order(self):
        product = Product.objects.create(
            title="Invalid payment test product",
            description="Test description",
            cost=10000,
            price=15000,
            image=SimpleUploadedFile(
                "test.jpg",
                b"fake-image-content",
                content_type="image/jpeg",
            ),
        )

        orders_before = Order.objects.count()
        customers_before = Customer.objects.count()
        items_before = OrderProduct.objects.count()

        self.client.get("/shop/order/")

        session = self.client.session
        session["cart"] = {str(product.id): 1}
        session.save()

        self.client.get("/shop/order/")
        token = self.client.session.get("checkout_token")

        response = self.client.post(
            "/shop/order/",
            {
                "checkout_token": token,
                "first_name": "Invalid",
                "last_name": "Payment",
                "phone": "901234567",
                "address": "Test address",
                "payment_type": "999",
                "delivery_type": "1",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(Order.objects.count(), orders_before)
        self.assertEqual(Customer.objects.count(), customers_before)
        self.assertEqual(OrderProduct.objects.count(), items_before)

    def test_invalid_coordinates_do_not_create_order(self):
        product = Product.objects.create(
            title="Invalid coordinates test product",
            description="Test description",
            cost=10000,
            price=15000,
            image=SimpleUploadedFile(
                "test.jpg",
                b"fake-image-content",
                content_type="image/jpeg",
            ),
        )

        orders_before = Order.objects.count()
        customers_before = Customer.objects.count()
        items_before = OrderProduct.objects.count()

        self.client.get("/shop/order/")

        session = self.client.session
        session["cart"] = {str(product.id): 1}
        session.save()

        self.client.get("/shop/order/")
        token = self.client.session.get("checkout_token")

        response = self.client.post(
            "/shop/order/",
            {
                "checkout_token": token,
                "first_name": "Invalid",
                "last_name": "Coordinates",
                "phone": "901234567",
                "address": "Test address",
                "payment_type": "1",
                "delivery_type": "1",
                "latitude": "invalid",
                "longitude": "invalid",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(Order.objects.count(), orders_before)
        self.assertEqual(Customer.objects.count(), customers_before)
        self.assertEqual(OrderProduct.objects.count(), items_before)
    def test_guest_checkout_does_not_modify_existing_customer(self):
        customer = Customer.objects.create(
            first_name="Original",
            last_name="Customer",
            phone_number="+998901234567",
        )

        product = Product.objects.create(
            title="Guest checkout security product",
            description="Test description",
            cost=10000,
            price=15000,
            image=SimpleUploadedFile(
                "guest-security-test.jpg",
                b"fake-image-content",
                content_type="image/jpeg",
            ),
        )

        self.client.get("/shop/order/")

        session = self.client.session
        session["cart"] = {str(product.id): 1}
        session.save()

        self.client.get("/shop/order/")
        token = self.client.session.get("checkout_token")
        orders_before = Order.objects.count()

        response = self.client.post(
            "/shop/order/",
            {
                "checkout_token": token,
                "first_name": "Someone Else",
                "last_name": "Different Name",
                "phone": "901234567",
                "address": "Guest test address",
                "payment_type": "1",
                "delivery_type": "1",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        customer.refresh_from_db()
        self.assertEqual(customer.first_name, "Original")
        self.assertEqual(customer.last_name, "Customer")
        self.assertEqual(customer.phone_number, "+998901234567")

        self.assertEqual(Order.objects.count(), orders_before + 1)

        order = Order.objects.latest("id")
        self.assertNotEqual(order.customer_id, customer.id)

    def test_checkout_with_product_creates_order_and_order_product(self):
        product = Product.objects.create(
            title="Checkout test product",
            description="Test description",
            cost=10000,
            price=15000,
            image=SimpleUploadedFile(
                "test.jpg",
                b"fake-image-content",
                content_type="image/jpeg",
            ),
        )

        before = Order.objects.count()

        self.client.get("/shop/order/")

        session = self.client.session
        session["cart"] = {str(product.id): 2}
        session.save()

        response = self.client.get("/shop/order/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        session = self.client.session
        token = session.get("checkout_token")

        response = self.client.post(
            "/shop/order/",
            {
                "checkout_token": token,
                "first_name": "Checkout",
                "last_name": "Tester",
                "phone": "901234567",
                "address": "Test address",
                "payment_type": "1",
                "delivery_type": "1",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(Order.objects.count(), before + 1)

        order = Order.objects.latest("id")
        item = OrderProduct.objects.get(order=order)

        self.assertEqual(item.product_id, product.id)
        self.assertEqual(item.count, 2)
        self.assertEqual(item.price, product.price)
        order_products_before = OrderProduct.objects.count()

        duplicate_response = self.client.post(
            "/shop/order/",
            {
                "checkout_token": token,
                "first_name": "Checkout",
                "last_name": "Tester",
                "phone": "901234567",
                "address": "Test address",
                "payment_type": "1",
                "delivery_type": "1",
            },
        )

        self.assertEqual(
            duplicate_response.status_code,
            status.HTTP_302_FOUND,
        )
        self.assertEqual(Order.objects.count(), before + 1)
        self.assertEqual(
            OrderProduct.objects.count(),
            order_products_before,
        )
class CartMethodSecurityTests(APITestCase):

    def setUp(self):
        self.product = Product.objects.create(
            title="Cart security test",
            description="Test product",
            cost=10000,
            price=15000,
            image=SimpleUploadedFile(
                "cart-test.jpg",
                b"test-image-content",
                content_type="image/jpeg",
            ),
        )

    def test_add_to_cart_rejects_get(self):
        response = self.client.get(
            f"/shop/add-to-cart/{self.product.id}/"
        )
        self.assertEqual(response.status_code, 405)

    def test_increase_cart_rejects_get(self):
        response = self.client.get(
            f"/shop/cart/increase/{self.product.id}/"
        )
        self.assertEqual(response.status_code, 405)

    def test_decrease_cart_rejects_get(self):
        response = self.client.get(
            f"/shop/cart/decrease/{self.product.id}/"
        )
        self.assertEqual(response.status_code, 405)

    def test_remove_from_cart_rejects_get(self):
        response = self.client.get(
            f"/shop/cart/remove/{self.product.id}/"
        )
        self.assertEqual(response.status_code, 405)

        class CartMethodSecurityTests(APITestCase):

            def setUp(self):
                self.product = Product.objects.create(
                    title="Cart security test",
                    description="Test product",
                    cost=10000,
                    price=15000,
                    image=SimpleUploadedFile(
                        "cart-test.jpg",
                        b"test-image-content",
                        content_type="image/jpeg",
                    ),
                )

            def test_add_to_cart_rejects_get(self):
                response = self.client.get(
                    f"/shop/add-to-cart/{self.product.id}/"
                )
                self.assertEqual(response.status_code, 405)

            def test_increase_cart_rejects_get(self):
                response = self.client.get(
                    f"/shop/cart/increase/{self.product.id}/"
                )
                self.assertEqual(response.status_code, 405)

            def test_decrease_cart_rejects_get(self):
                response = self.client.get(
                    f"/shop/cart/decrease/{self.product.id}/"
                )
                self.assertEqual(response.status_code, 405)

            def test_remove_from_cart_rejects_get(self):
                response = self.client.get(
                    f"/shop/cart/remove/{self.product.id}/"
                )
                self.assertEqual(response.status_code, 405)
