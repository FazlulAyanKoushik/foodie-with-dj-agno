"""
Django management command to sync restaurant data to knowledge base.
Usage:
    python manage.py sync_knowledge_base                    # Sync all restaurants
    python manage.py sync_knowledge_base --restaurant <uid>  # Sync specific restaurant
"""
from django.core.management.base import BaseCommand
from restaurants.models import Restaurant
from restaurants.tasks import bulk_sync_restaurant_knowledge


class Command(BaseCommand):
    help = 'Sync restaurant data to ChromaDB knowledge base'

    def add_arguments(self, parser):
        parser.add_argument(
            '--restaurant',
            type=str,
            help='Restaurant UID to sync (if not provided, syncs all restaurants)',
        )

    def handle(self, *args, **options):
        restaurant_uid = options.get('restaurant')

        if restaurant_uid:
            # Sync specific restaurant
            try:
                restaurant = Restaurant.objects.get(uid=restaurant_uid)
                self.stdout.write(f'Syncing restaurant: {restaurant.name}...')
                bulk_sync_restaurant_knowledge.delay(str(restaurant.uid))
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully queued sync for {restaurant.name}')
                )
            except Restaurant.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Restaurant with UID {restaurant_uid} not found')
                )
        else:
            # Sync all restaurants
            restaurants = Restaurant.objects.all()
            count = restaurants.count()

            if count == 0:
                self.stdout.write(self.style.WARNING('No restaurants found'))
                return

            self.stdout.write(f'Syncing {count} restaurant(s)...')

            for restaurant in restaurants:
                bulk_sync_restaurant_knowledge.delay(str(restaurant.uid))
                self.stdout.write(f'  - Queued: {restaurant.name}')

            self.stdout.write(
                self.style.SUCCESS(f'Successfully queued sync for {count} restaurant(s)')
            )
            self.stdout.write('Note: Sync tasks are running in the background via Celery')
