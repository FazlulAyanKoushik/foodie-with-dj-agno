"""
Django signals for automatic knowledge base synchronization.
Triggers Celery tasks when restaurant data is created, updated, or deleted.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from restaurants.models import Restaurant, Menu, Ingredients, MenuIngredientsConnector
from restaurants.tasks import (
    sync_restaurant_to_knowledge,
    sync_menu_to_knowledge,
    sync_ingredient_to_knowledge,
    remove_from_knowledge,
)
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Restaurant)
def restaurant_saved(sender, instance, created, **kwargs):
    """
    Sync restaurant to knowledge base when created or updated.
    """
    try:
        sync_restaurant_to_knowledge.delay(str(instance.uid))
        logger.info(f"Queued knowledge sync for restaurant: {instance.name}")
    except Exception as e:
        logger.error(f"Error queuing restaurant sync: {str(e)}", exc_info=True)


@receiver(post_delete, sender=Restaurant)
def restaurant_deleted(sender, instance, **kwargs):
    """
    Remove restaurant from knowledge base when deleted.
    """
    try:
        remove_from_knowledge.delay(str(instance.uid), "restaurant", str(instance.uid))
        logger.info(f"Queued knowledge removal for restaurant: {instance.name}")
    except Exception as e:
        logger.error(f"Error queuing restaurant removal: {str(e)}", exc_info=True)


@receiver(post_save, sender=Menu)
def menu_saved(sender, instance, created, **kwargs):
    """
    Sync menu item to knowledge base when created or updated.
    """
    try:
        sync_menu_to_knowledge.delay(str(instance.uid))
        logger.info(f"Queued knowledge sync for menu: {instance.name}")
    except Exception as e:
        logger.error(f"Error queuing menu sync: {str(e)}", exc_info=True)


@receiver(post_delete, sender=Menu)
def menu_deleted(sender, instance, **kwargs):
    """
    Remove menu item from knowledge base when deleted.
    """
    try:
        remove_from_knowledge.delay(
            str(instance.restaurant.uid),
            "menu",
            str(instance.uid)
        )
        logger.info(f"Queued knowledge removal for menu: {instance.name}")
    except Exception as e:
        logger.error(f"Error queuing menu removal: {str(e)}", exc_info=True)


@receiver(post_save, sender=Ingredients)
def ingredient_saved(sender, instance, created, **kwargs):
    """
    Sync ingredient to knowledge base when created or updated.
    """
    try:
        sync_ingredient_to_knowledge.delay(str(instance.uid))
        logger.info(f"Queued knowledge sync for ingredient: {instance.name}")
    except Exception as e:
        logger.error(f"Error queuing ingredient sync: {str(e)}", exc_info=True)


@receiver(post_delete, sender=Ingredients)
def ingredient_deleted(sender, instance, **kwargs):
    """
    Remove ingredient from knowledge base when deleted.
    """
    try:
        remove_from_knowledge.delay(
            str(instance.restaurant.uid),
            "ingredient",
            str(instance.uid)
        )
        logger.info(f"Queued knowledge removal for ingredient: {instance.name}")
    except Exception as e:
        logger.error(f"Error queuing ingredient removal: {str(e)}", exc_info=True)


@receiver(post_save, sender=MenuIngredientsConnector)
def menu_ingredient_connector_saved(sender, instance, created, **kwargs):
    """
    Re-sync menu when menu-ingredient relationship changes.
    """
    try:
        sync_menu_to_knowledge.delay(str(instance.menu.uid))
        logger.info(f"Queued menu re-sync due to ingredient change: {instance.menu.name}")
    except Exception as e:
        logger.error(f"Error queuing menu re-sync: {str(e)}", exc_info=True)


@receiver(post_delete, sender=MenuIngredientsConnector)
def menu_ingredient_connector_deleted(sender, instance, **kwargs):
    """
    Re-sync menu when menu-ingredient relationship is removed.
    """
    try:
        sync_menu_to_knowledge.delay(str(instance.menu.uid))
        logger.info(f"Queued menu re-sync due to ingredient removal: {instance.menu.name}")
    except Exception as e:
        logger.error(f"Error queuing menu re-sync: {str(e)}", exc_info=True)
