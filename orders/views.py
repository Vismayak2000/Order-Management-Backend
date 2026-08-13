from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import FoodItem, Order
from .serializers import (
    FoodItemSerializer,
    OrderSerializer,
    OrderCreateSerializer,
)


class FoodItemViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = FoodItem.objects.filter(
        is_available=True
    )

    serializer_class = FoodItemSerializer

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = [
        'is_available',
    ]

    search_fields = [
        'name',
        'description',
    ]

    ordering_fields = [
        'name',
        'price',
        'created_at',
    ]

    ordering = [
        'name',
    ]


class OrderViewSet(viewsets.ModelViewSet):
    
    queryset = Order.objects.prefetch_related(
        'items__food_item'
    ).all()

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = [
        'status',
    ]

    search_fields = [
        'customer_name',
        'phone',
    ]

    ordering_fields = [
        'created_at',
        'total_amount',
    ]

    ordering = [
        '-created_at',
    ]

    def get_serializer_class(self):

        if self.action == 'create':
            return OrderCreateSerializer

        return OrderSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        order = serializer.save()

        response_serializer = OrderSerializer(
            order
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )

    @action(
        detail=True,
        methods=['patch'],
        url_path='status'
    )
    def update_status(self, request, pk=None):

        order = self.get_object()

        new_status = request.data.get('status')

        valid_statuses = dict(
            Order.STATUS_CHOICES
        ).keys()

        if not new_status:

            return Response(
                {
                    'error': 'Status is required.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_status not in valid_statuses:

            return Response(
                {
                    'error': 'Invalid order status.',
                    'allowed_statuses': list(
                        valid_statuses
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status

        order.save()

        serializer = OrderSerializer(order)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )