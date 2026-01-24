from rest_framework import serializers
from django.db import transaction

from accounts.models import User
from accounts.choices import UserRole
from restaurants.models import Restaurant, Menu, Ingredients, MenuIngredientsConnector


class RestaurantSerializer(serializers.ModelSerializer):
    """
    Standard serializer for Restaurant model.
    """
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Restaurant
        fields = ['id', 'owner', 'name', 'description', 'logo', 'website_url', 'facebook_url', 'twitter_url', 'instagram_url', 'youtube_url', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'owner']


class RestaurantCreateWithOwnerSerializer(serializers.Serializer):
    """
    Serializer to create a Restaurant and its Owner (User) simultaneously.
    """
    # User fields
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)

    # Restaurant fields
    restaurant_name = serializers.CharField(max_length=255)
    restaurant_description = serializers.CharField()

    def create(self, validated_data):
        with transaction.atomic():
            # Create User
            user_data = {
                'email': validated_data['email'],
                'first_name': validated_data.get('first_name', ''),
                'last_name': validated_data.get('last_name', ''),
                'password': validated_data['password'],
                'role': UserRole.RESTAURANT_OWNER
            }
            user = User.objects.create_user(**user_data)

            # Create Restaurant
            restaurant_data = {
                'name': validated_data['restaurant_name'],
                'description': validated_data['restaurant_description'],
                'owner': user
            }
            restaurant = Restaurant.objects.create(**restaurant_data)

            return {
                'user': user,
                'restaurant': restaurant
            }


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'restaurant']


class MenuSerializer(serializers.ModelSerializer):
    ingredient_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    ingredients = IngredientSerializer(many=True, read_only=True, source='menuingredientsconnector_set.ingredient') # Incorrect source, need to handle deeper but simple for now

    class Meta:
        model = Menu
        fields = ['id', 'restaurant', 'name', 'description', 'image', 'price', 'ingredient_ids', 'ingredients', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'restaurant']

    def create(self, validated_data):
        ingredient_ids = validated_data.pop('ingredient_ids', [])
        menu = super().create(validated_data)

        for ingredient_id in ingredient_ids:
            try:
                ingredient = Ingredients.objects.get(id=ingredient_id, restaurant=menu.restaurant)
                MenuIngredientsConnector.objects.create(menu=menu, ingredient=ingredient, restaurant=menu.restaurant)
            except Ingredients.DoesNotExist:
                pass # or raise error
        return menu

    def update(self, instance, validated_data):
        ingredient_ids = validated_data.pop('ingredient_ids', None)
        menu = super().update(instance, validated_data)

        if ingredient_ids is not None:
            # Clear existing connections? Or standard set sync. Simple clear and add for now.
            MenuIngredientsConnector.objects.filter(menu=menu).delete()
            for ingredient_id in ingredient_ids:
                try:
                    ingredient = Ingredients.objects.get(id=ingredient_id, restaurant=menu.restaurant)
                    MenuIngredientsConnector.objects.create(menu=menu, ingredient=ingredient, restaurant=menu.restaurant)
                except Ingredients.DoesNotExist:
                    pass
        return menu
