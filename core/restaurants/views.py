from rest_framework import generics, status, filters, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from commons.permissions import IsSuperAdmin, IsPlatformAdmin, IsRestaurantOwner
from restaurants.models import Restaurant, Menu, Ingredients
from restaurants.serializers import (
    RestaurantSerializer,
    RestaurantCreateWithOwnerSerializer,
    MenuSerializer,
    IngredientSerializer
)
from core.utils.message import Message


class RestaurantListCreateView(generics.ListCreateAPIView):
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RestaurantCreateWithOwnerSerializer
        return RestaurantSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
             return [IsAuthenticated(), (IsSuperAdmin | IsPlatformAdmin)()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['super_admin', 'platform_admin']:
            return Restaurant.objects.all()
        elif user.role == 'restaurant_owner':
            return Restaurant.objects.filter(owner=user)
        return Restaurant.objects.none()

    @swagger_auto_schema(
        operation_description="Create a Restaurant and its Owner (User) simultaneously (Admin only).",
        responses={201: openapi.Response("Created", RestaurantSerializer)}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response({
                'message': Message(resource="Restaurant & Owner").created_success(),
                'data': {
                    'restaurant': RestaurantSerializer(result['restaurant']).data,
                }
            }, status=status.HTTP_201_CREATED)
        return Response({
             'message': Message(resource="Restaurant & Owner").created_failed(),
             'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class RestaurantDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Restaurant.objects.all()

    def get_serializer_class(self):
        return RestaurantSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            return [IsAuthenticated(), (IsSuperAdmin | IsPlatformAdmin | IsRestaurantOwner)()]
        elif self.request.method == 'DELETE':
            return [IsAuthenticated(), (IsSuperAdmin | IsPlatformAdmin)()]
        return [IsAuthenticated()]

    def get_queryset(self):
         # Same logic to ensure owners can't "Retrieve" others by ID even if they guess it
        user = self.request.user
        if user.role in ['super_admin', 'platform_admin']:
            return Restaurant.objects.all()
        elif user.role == 'restaurant_owner':
            return Restaurant.objects.filter(owner=user)
        return Restaurant.objects.none()




class MenuListCreateView(generics.ListCreateAPIView):

    def get_serializer_class(self):
        return MenuSerializer

    permission_classes = [IsAuthenticated, IsRestaurantOwner | IsSuperAdmin | IsPlatformAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['super_admin', 'platform_admin']:
            return Menu.objects.all()
        return Menu.objects.filter(restaurant__owner=user)

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'restaurant_owner':
            restaurant = Restaurant.objects.filter(owner=user).first()
            if restaurant:
                serializer.save(restaurant=restaurant)
            else:
                # Should handle nicely, but validation error is ok
                raise serializers.ValidationError("No restaurant found for this user.")
        else:
            serializer.save()


class MenuDetailView(generics.RetrieveUpdateDestroyAPIView):

    def get_serializer_class(self):
        return MenuSerializer

    permission_classes = [IsAuthenticated, IsRestaurantOwner | IsSuperAdmin | IsPlatformAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['super_admin', 'platform_admin']:
            return Menu.objects.all()
        return Menu.objects.filter(restaurant__owner=user)


class IngredientListCreateView(generics.ListCreateAPIView):

    def get_serializer_class(self):
        return IngredientSerializer

    permission_classes = [IsAuthenticated, IsRestaurantOwner | IsSuperAdmin | IsPlatformAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['super_admin', 'platform_admin']:
             return Ingredients.objects.all()
        return Ingredients.objects.filter(restaurant__owner=user)

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'restaurant_owner':
            restaurant = Restaurant.objects.filter(owner=user).first()
            if restaurant:
                serializer.save(restaurant=restaurant)
            else:
                raise serializers.ValidationError("No restaurant found for this user.")
        else:
            serializer.save()


class IngredientDetailView(generics.RetrieveUpdateDestroyAPIView):

    def get_serializer_class(self):
        return IngredientSerializer

    permission_classes = [IsAuthenticated, IsRestaurantOwner | IsSuperAdmin | IsPlatformAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['super_admin', 'platform_admin']:
             return Ingredients.objects.all()
        return Ingredients.objects.filter(restaurant__owner=user)
