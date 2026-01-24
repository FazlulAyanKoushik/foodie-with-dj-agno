from django.contrib import admin
from .models import Restaurant, Menu, Ingredients, MenuIngredientsConnector

class MenuIngredientsConnectorInline(admin.TabularInline):
    model = MenuIngredientsConnector
    extra = 1
    autocomplete_fields = ['ingredient']

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('id','uid','name', 'owner', 'website_url', 'created_at')
    search_fields = ('name', 'owner__email', 'owner__first_name', 'owner__last_name')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'price', 'created_at')
    search_fields = ('name', 'restaurant__name')
    list_filter = ('restaurant', 'created_at')
    ordering = ('restaurant', 'name')
    inlines = [MenuIngredientsConnectorInline]

@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'created_at')
    search_fields = ('name', 'restaurant__name')
    list_filter = ('restaurant', 'menuingredientsconnector__menu', 'created_at')
    ordering = ('restaurant', 'name')

@admin.register(MenuIngredientsConnector)
class MenuIngredientsConnectorAdmin(admin.ModelAdmin):
    list_display = ('menu', 'ingredient', 'restaurant', 'created_at')
    search_fields = ('menu__name', 'ingredient__name', 'restaurant__name')
    list_filter = ('restaurant', 'menu')
    ordering = ('restaurant', 'menu')
