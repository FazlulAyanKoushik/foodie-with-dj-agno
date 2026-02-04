from rest_framework import serializers
from django.db import transaction

from accounts.models import User
from accounts.choices import UserRole
from restaurants.models import Restaurant, Menu, Ingredients, MenuIngredientsConnector, Allergen


class RestaurantSerializer(serializers.ModelSerializer):
    """
    Standard serializer for Restaurant model.
    """
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Restaurant
        fields = ['id', 'uid', 'owner', 'name', 'description', 'logo', 'website_url', 'facebook_url', 'twitter_url', 'instagram_url', 'youtube_url', 'created_at', 'updated_at']
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



class AllergenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergen
        fields = ['id', 'name', 'name_ja', 'allergen_type']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ['id', 'restaurant', 'name', 'description', 'image', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'restaurant']


class MenuSerializer(serializers.ModelSerializer):
    ingredient_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, help_text='Ingredient IDs.'
    )
    ingredient_names = serializers.ListField(
        child=serializers.CharField(),  required=False, help_text='Ingredient names.'
    )
    allergen_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, write_only=True
    )

    ingredients = IngredientSerializer(many=True, read_only=True, source='menuingredientsconnector_set.ingredient')
    allergens = AllergenSerializer(many=True, read_only=True)

    class Meta:
        model = Menu
        fields = ['id', 'restaurant', 'name', 'description', 'image', 'price', 'ingredient_ids', 'ingredient_names', 'ingredients', 'allergens', 'allergen_ids', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'restaurant', 'ingredients', 'allergens']
        write_only_fields = ['ingredient_ids', 'ingredient_names', 'allergen_ids']

    def create(self, validated_data):
        ingredient_ids = validated_data.pop('ingredient_ids', [])
        ingredient_names = validated_data.pop('ingredient_names', [])
        allergen_ids = validated_data.pop('allergen_ids', [])

        if not ingredient_ids and not ingredient_names:
            raise serializers.ValidationError({'ingredients': 'At least one ingredient is required.'})

        menu = super().create(validated_data)

        if allergen_ids:
            menu.allergens.set(allergen_ids)

        if ingredient_names:
            for ingredient_name in ingredient_names:
                ingredient, _ = Ingredients.objects.get_or_create(name=ingredient_name, restaurant=menu.restaurant)
                MenuIngredientsConnector.objects.create(menu=menu, ingredient=ingredient, restaurant=menu.restaurant)

        if ingredient_ids:
            for ingredient_id in ingredient_ids:
                try:
                    ingredient = Ingredients.objects.get(id=ingredient_id, restaurant=menu.restaurant)
                    MenuIngredientsConnector.objects.create(menu=menu, ingredient=ingredient,
                                                            restaurant=menu.restaurant)
                except Ingredients.DoesNotExist:
                    pass
        return menu

    def update(self, instance, validated_data):
        ingredient_ids = validated_data.pop('ingredient_ids', None)
        allergen_ids = validated_data.pop('allergen_ids', None)

        menu = super().update(instance, validated_data)

        if allergen_ids is not None:
            menu.allergens.set(allergen_ids)

        if ingredient_ids is not None:
            MenuIngredientsConnector.objects.filter(menu=menu).delete()
            for ingredient_id in ingredient_ids:
                try:
                    ingredient = Ingredients.objects.get(id=ingredient_id, restaurant=menu.restaurant)
                    MenuIngredientsConnector.objects.create(menu=menu, ingredient=ingredient, restaurant=menu.restaurant)
                except Ingredients.DoesNotExist:
                    pass
        return menu
