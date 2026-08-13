from decimal import Decimal

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from .models import FoodItem, Order


class FoodItemAPITestCase(APITestCase):

    def setUp(self):

        self.food = FoodItem.objects.create(
            name='Chicken Burger',
            description='Juicy chicken burger',
            price=Decimal('150.00'),
            is_available=True
        )

    def test_get_menu(self):

        response = self.client.get(
            reverse('menu-list')
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['count'],
            1
        )

    def test_get_single_menu_item(self):

        response = self.client.get(
            reverse(
                'menu-detail',
                args=[self.food.id]
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['name'],
            'Chicken Burger'
        )


class OrderAPITestCase(APITestCase):

    def setUp(self):

        self.food = FoodItem.objects.create(
            name='Pizza',
            description='Cheese pizza',
            price=Decimal('200.00'),
            is_available=True
        )

    def create_order(self):

        return self.client.post(
            reverse('orders-list'),
            {
                'customer_name': 'John',
                'address': 'Main Street',
                'phone': '9876543210',
                'items': [
                    {
                        'food_item': self.food.id,
                        'quantity': 2
                    }
                ]
            },
            format='json'
        )

    def test_create_order(self):

        response = self.create_order()

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            response.data['total_amount'],
            '400.00'
        )

        self.assertEqual(
            response.data['status'],
            'ORDER_RECEIVED'
        )

    def test_get_orders(self):

        self.create_order()

        response = self.client.get(
            reverse('orders-list')
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['count'],
            1
        )

    def test_get_single_order(self):

        response = self.create_order()

        order_id = response.data['id']

        response = self.client.get(
            reverse(
                'orders-detail',
                args=[order_id]
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['id'],
            order_id
        )

    def test_update_order(self):

        response = self.create_order()

        order_id = response.data['id']

        response = self.client.patch(
            reverse(
                'orders-detail',
                args=[order_id]
            ),
            {
                'customer_name': 'David'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['customer_name'],
            'David'
        )

    def test_delete_order(self):

        response = self.create_order()

        order_id = response.data['id']

        response = self.client.delete(
            reverse(
                'orders-detail',
                args=[order_id]
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertFalse(
            Order.objects.filter(
                id=order_id
            ).exists()
        )

    def test_empty_items_validation(self):

        response = self.client.post(
            reverse('orders-list'),
            {
                'customer_name': 'John',
                'address': 'Main Street',
                'phone': '9876543210',
                'items': []
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_invalid_quantity(self):

        response = self.client.post(
            reverse('orders-list'),
            {
                'customer_name': 'John',
                'address': 'Main Street',
                'phone': '9876543210',
                'items': [
                    {
                        'food_item': self.food.id,
                        'quantity': 0
                    }
                ]
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_invalid_phone(self):

        response = self.client.post(
            reverse('orders-list'),
            {
                'customer_name': 'John',
                'address': 'Main Street',
                'phone': 'abc',
                'items': [
                    {
                        'food_item': self.food.id,
                        'quantity': 1
                    }
                ]
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_unavailable_food_item(self):

        self.food.is_available = False
        self.food.save()

        response = self.create_order()

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_update_order_status(self):

        response = self.create_order()

        order_id = response.data['id']

        response = self.client.patch(
            reverse(
                'orders-update-status',
                args=[order_id]
            ),
            {
                'status': 'PREPARING'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['status'],
            'PREPARING'
        )

    def test_invalid_order_status(self):

        response = self.create_order()

        order_id = response.data['id']

        response = self.client.patch(
            reverse(
                'orders-update-status',
                args=[order_id]
            ),
            {
                'status': 'INVALID_STATUS'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )