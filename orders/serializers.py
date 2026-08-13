from rest_framework import serializers
from .models import FoodItem, Order, OrderItem


class FoodItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = FoodItem
        fields = [
            'id',
            'name',
            'description',
            'price',
            'image',
            'is_available',
            'created_at',
            'updated_at',
        ]


class OrderItemInputSerializer(serializers.Serializer):

    food_item = serializers.IntegerField()

    quantity = serializers.IntegerField(min_value=1)


class OrderItemSerializer(serializers.ModelSerializer):

    name = serializers.CharField(
        source='food_item.name',
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'food_item',
            'name',
            'quantity',
            'price',
            'subtotal',
        ]


class OrderSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id',
            'customer_name',
            'address',
            'phone',
            'status',
            'total_amount',
            'items',
            'created_at',
            'updated_at',
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    
    items = OrderItemInputSerializer(
        many=True,
        write_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id',
            'customer_name',
            'address',
            'phone',
            'items',
        ]

    def validate_customer_name(self, value):

        if not value.strip():
            raise serializers.ValidationError(
                "Customer name cannot be empty."
            )

        return value.strip()

    def validate_address(self, value):

        if not value.strip():
            raise serializers.ValidationError(
                "Address cannot be empty."
            )

        return value.strip()

    def validate_phone(self, value):

        value = value.strip()

        if not value.isdigit():
            raise serializers.ValidationError(
                "Phone number must contain only digits."
            )

        if len(value) < 10 or len(value) > 15:
            raise serializers.ValidationError(
                "Enter a valid phone number."
            )

        return value

    def validate_items(self, items):

        if not items:
            raise serializers.ValidationError(
                "At least one item is required."
            )

        food_item_ids = [
            item['food_item']
            for item in items
        ]

        if len(food_item_ids) != len(set(food_item_ids)):
            raise serializers.ValidationError(
                "Duplicate food items are not allowed."
            )

        food_items = FoodItem.objects.filter(
            id__in=food_item_ids
        )

        food_item_map = {
            item.id: item
            for item in food_items
        }

        for item in items:

            food_item_id = item['food_item']

            if food_item_id not in food_item_map:
                raise serializers.ValidationError(
                    f"Food item {food_item_id} does not exist."
                )

            food_item = food_item_map[food_item_id]

            if not food_item.is_available:
                raise serializers.ValidationError(
                    f"{food_item.name} is currently unavailable."
                )

        return items

    def create(self, validated_data):

        items_data = validated_data.pop('items')

        order = Order.objects.create(
            **validated_data
        )

        total = 0

        food_item_ids = [
            item['food_item']
            for item in items_data
        ]

        food_items = FoodItem.objects.filter(
            id__in=food_item_ids
        )

        food_item_map = {
            item.id: item
            for item in food_items
        }

        for item_data in items_data:

            food_item = food_item_map[
                item_data['food_item']
            ]

            quantity = item_data['quantity']

            price = food_item.price

            subtotal = price * quantity

            OrderItem.objects.create(
                order=order,
                food_item=food_item,
                quantity=quantity,
                price=price,
                subtotal=subtotal
            )

            total += subtotal

        order.total_amount = total

        order.save(
            update_fields=[
                'total_amount',
                'updated_at'
            ]
        )

        return order