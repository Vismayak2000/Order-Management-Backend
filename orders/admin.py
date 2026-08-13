from django.contrib import admin

from .models import (
    FoodItem,
    Order,
    OrderItem,
)


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'name',
        'price',
        'is_available',
        'created_at',
    ]

    list_filter = [
        'is_available',
    ]

    search_fields = [
        'name',
        'description',
    ]


class OrderItemInline(admin.TabularInline):

    model = OrderItem

    extra = 0

    readonly_fields = [
        'price',
        'subtotal',
    ]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'customer_name',
        'phone',
        'status',
        'total_amount',
        'created_at',
    ]

    list_filter = [
        'status',
    ]

    search_fields = [
        'customer_name',
        'phone',
    ]

    inlines = [
        OrderItemInline,
    ]