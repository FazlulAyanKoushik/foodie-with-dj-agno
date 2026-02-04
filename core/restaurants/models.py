from django.db import models
from commons.models import BaseModel

# Create your models here.
class Restaurant(BaseModel):
    owner = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    logo = models.ImageField(upload_to='restaurant/logos/', blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    facebook_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.owner}"


class Allergen(BaseModel):
    ALLERGEN_TYPES = (
        ('mandatory', 'Mandatory'),
        ('recommended', 'Recommended'),
    )
    name = models.CharField(max_length=255)
    name_ja = models.CharField(max_length=255, help_text="Japanese name of the allergen")
    allergen_type = models.CharField(max_length=20, choices=ALLERGEN_TYPES)

    def __str__(self):
        return f"{self.name} ({self.name_ja})"


class Menu(BaseModel):
    restaurant = models.ForeignKey('restaurants.Restaurant', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='restaurant/menus/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    allergens = models.ManyToManyField(Allergen, blank=True, related_name='menus')

    def __str__(self):
        return f"{self.name} - {self.restaurant}"


class Ingredients(BaseModel):
    restaurant = models.ForeignKey('restaurants.Restaurant', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='restaurant/ingredients/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.restaurant}"


class MenuIngredientsConnector(BaseModel):
    restaurant = models.ForeignKey('restaurants.Restaurant', on_delete=models.CASCADE)
    menu = models.ForeignKey('restaurants.Menu', on_delete=models.CASCADE)
    ingredient = models.ForeignKey('restaurants.Ingredients', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.menu} - {self.ingredient}"


