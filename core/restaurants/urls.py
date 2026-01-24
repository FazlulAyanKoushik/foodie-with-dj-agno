from django.urls import path
from .views import (
    RestaurantListCreateView,
    RestaurantDetailView,
    MenuListCreateView,
    MenuDetailView,
    IngredientListCreateView,
    IngredientDetailView
)

app_name = 'restaurants'

urlpatterns = [
    # Restaurants
    path('restaurants/', RestaurantListCreateView.as_view(), name='restaurant-list'),
    path('restaurants/<int:pk>/', RestaurantDetailView.as_view(), name='restaurant-detail'),

    # Menus
    path('menus/', MenuListCreateView.as_view(), name='menu-list'),
    path('menus/<int:pk>/', MenuDetailView.as_view(), name='menu-detail'),

    # Ingredients
    path('ingredients/', IngredientListCreateView.as_view(), name='ingredient-list'),
    path('ingredients/<int:pk>/', IngredientDetailView.as_view(), name='ingredient-detail'),
]
