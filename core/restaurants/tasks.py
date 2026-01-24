"""
Celery tasks for knowledge base synchronization.
Handles async updates to ChromaDB when restaurant data changes.
"""
from celery import shared_task
from django.apps import apps
import logging

logger = logging.getLogger(__name__)


@shared_task
def sync_restaurant_to_knowledge(restaurant_uid: str):
    """
    Sync a restaurant's complete data to its knowledge base.

    Args:
        restaurant_uid: Restaurant UID to sync
    """
    try:
        from restaurants.models import Restaurant, Menu, MenuIngredientsConnector
        from chat.knowledge import get_restaurant_knowledge

        # Get restaurant
        restaurant = Restaurant.objects.get(uid=restaurant_uid)

        # Get knowledge base
        knowledge = get_restaurant_knowledge(str(restaurant.uid))

        # Get all menus for this restaurant to provide a high-level overview
        menus = Menu.objects.filter(restaurant=restaurant)
        menu_items_list = [f"- {m.name}: ${m.price}" for m in menus]
        menu_overview = "\n".join(menu_items_list) if menu_items_list else "No menu items currently available."

        # Prepare restaurant document
        restaurant_doc = f"""
RESTAURANT: {restaurant.name}
DESCRIPTION: {restaurant.description}
WEBSITE: {restaurant.website_url or 'N/A'}
FACEBOOK: {restaurant.facebook_url or 'N/A'}
TWITTER: {restaurant.twitter_url or 'N/A'}
INSTAGRAM: {restaurant.instagram_url or 'N/A'}
YOUTUBE: {restaurant.youtube_url or 'N/A'}

FULL MENU OVERVIEW:
{menu_overview}
"""
        logger.info(f"restaurant_doc:  {restaurant_doc}")

        # Add restaurant info to knowledge base
        knowledge.insert(
            text_content=restaurant_doc,
            metadata={
                "type": "restaurant",
                "restaurant_uid": str(restaurant.uid),
                "restaurant_name": restaurant.name,
            }
        )

        logger.info(f"Synced restaurant {restaurant.name} to knowledge base")

    except Exception as e:
        logger.error(f"Error syncing restaurant {restaurant_uid}: {str(e)}", exc_info=True)


@shared_task
def sync_menu_to_knowledge(menu_uid: str):
    """
    Sync a menu item with its ingredients to knowledge base.

    Args:
        menu_uid: Menu UID to sync
    """
    try:
        from restaurants.models import Menu, MenuIngredientsConnector, Ingredients
        from chat.knowledge import get_restaurant_knowledge

        # Get menu item
        menu = Menu.objects.get(uid=menu_uid)
        restaurant = menu.restaurant

        # Get knowledge base for this restaurant
        knowledge = get_restaurant_knowledge(str(restaurant.uid))

        # Get ingredients for this menu item
        menu_ingredients = MenuIngredientsConnector.objects.filter(menu=menu).select_related('ingredient')
        ingredient_names = [mi.ingredient.name for mi in menu_ingredients]
        ingredient_details = [
            f"{mi.ingredient.name}: {mi.ingredient.description or 'No description'}"
            for mi in menu_ingredients
        ]

        # Prepare menu document with extra keywords for better search
        menu_doc = f"""
MENU ITEM / FOOD: {menu.name}
RESTAURANT: {restaurant.name}
DESCRIPTION: {menu.description or 'No description provided'}
PRICE: ${menu.price}
INGREDIENTS: {', '.join(ingredient_names) if ingredient_names else 'No ingredients listed'}

FOOD DETAILS:
{chr(10).join(ingredient_details) if ingredient_details else 'No ingredient details available'}
"""

        # Add menu to knowledge base
        knowledge.insert(
            text_content=menu_doc,
            metadata={
                "type": "menu",
                "restaurant_uid": str(restaurant.uid),
                "restaurant_name": restaurant.name,
                "menu_uid": str(menu.uid),
                "menu_name": menu.name,
                "price": str(menu.price),
                "ingredients": ingredient_names,
            }
        )

        logger.info(f"Synced menu item {menu.name} to knowledge base")

    except Exception as e:
        logger.error(f"Error syncing menu {menu_uid}: {str(e)}", exc_info=True)


@shared_task
def sync_ingredient_to_knowledge(ingredient_uid: str):
    """
    Sync an ingredient to knowledge base.
    Also re-syncs all menu items using this ingredient.

    Args:
        ingredient_uid: Ingredient UID to sync
    """
    try:
        from restaurants.models import Ingredients, MenuIngredientsConnector
        from chat.knowledge import get_restaurant_knowledge

        # Get ingredient
        ingredient = Ingredients.objects.get(uid=ingredient_uid)
        restaurant = ingredient.restaurant

        # Get knowledge base
        knowledge = get_restaurant_knowledge(str(restaurant.uid))

        # Prepare ingredient document
        ingredient_doc = f"""
Ingredient: {ingredient.name}
Restaurant: {restaurant.name}
Description: {ingredient.description or 'No description provided'}
"""

        # Add ingredient to knowledge base
        knowledge.insert(
            text_content=ingredient_doc,
            metadata={
                "type": "ingredient",
                "restaurant_uid": str(restaurant.uid),
                "restaurant_name": restaurant.name,
                "ingredient_uid": str(ingredient.uid),
                "ingredient_name": ingredient.name,
            }
        )

        # Re-sync all menu items using this ingredient
        menu_connectors = MenuIngredientsConnector.objects.filter(ingredient=ingredient)
        for connector in menu_connectors:
            sync_menu_to_knowledge.delay(str(connector.menu.uid))

        logger.info(f"Synced ingredient {ingredient.name} to knowledge base")

    except Exception as e:
        logger.error(f"Error syncing ingredient {ingredient_uid}: {str(e)}", exc_info=True)


@shared_task
def remove_from_knowledge(restaurant_uid: str, doc_type: str, doc_uid: str):
    """
    Remove a document from the knowledge base.

    Args:
        restaurant_uid: Restaurant UID
        doc_type: Type of document (restaurant, menu, ingredient)
        doc_uid: Document UID to remove
    """
    try:
        from chat.knowledge import get_restaurant_knowledge

        # Get knowledge base
        knowledge = get_restaurant_knowledge(restaurant_uid)

        # Remove by metadata
        metadata_key = f"{doc_type}_uid"
        knowledge.remove_vectors_by_metadata({metadata_key: doc_uid})
        logger.info(f"Removed {doc_type} {doc_uid} from knowledge base")

    except Exception as e:
        logger.error(f"Error removing {doc_type} {doc_uid}: {str(e)}", exc_info=True)


@shared_task
def bulk_sync_restaurant_knowledge(restaurant_uid: str):
    """
    Perform a complete sync of all restaurant data to knowledge base.
    Useful for initial setup or rebuilding knowledge base.

    Args:
        restaurant_uid: Restaurant UID to sync
    """
    try:
        from restaurants.models import Restaurant, Menu

        # Sync restaurant info
        sync_restaurant_to_knowledge(restaurant_uid)

        # Get all menus for this restaurant
        restaurant = Restaurant.objects.get(uid=restaurant_uid)
        menus = Menu.objects.filter(restaurant=restaurant)

        # Sync each menu (which will also sync ingredients)
        for menu in menus:
            sync_menu_to_knowledge.delay(str(menu.uid))

        logger.info(f"Bulk sync initiated for restaurant {restaurant_uid}")

    except Exception as e:
        logger.error(f"Error in bulk sync for restaurant {restaurant_uid}: {str(e)}", exc_info=True)
