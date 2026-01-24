from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User
from accounts.choices import UserRole
from restaurants.models import Restaurant, Menu

class RBACScenarioTests(APITestCase):
    def setUp(self):
        # Create Super Admin
        self.super_admin = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpassword',
            first_name='Admin',
            role=UserRole.SUPER_ADMIN
        )

        # URL constants
        self.create_restaurant_with_owner_url = reverse('restaurants:restaurant-list')
        self.restaurant_list_url = reverse('restaurants:restaurant-list')
        self.user_list_url = reverse('accounts:user-list')

    def test_super_admin_create_restaurant_and_owner(self):
        """
        Test that Super Admin can create a restaurant and owner simultaneously.
        """
        self.client.force_authenticate(user=self.super_admin)
        data = {
            'email': 'owner@example.com',
            'password': 'ownerpassword',
            'first_name': 'Owner',
            'restaurant_name': 'Test Restaurant',
            'restaurant_description': 'A test restaurant description.'
        }
        response = self.client.post(self.create_restaurant_with_owner_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='owner@example.com').exists())
        self.assertTrue(Restaurant.objects.filter(name='Test Restaurant').exists())

        # Verify Owner Role
        owner = User.objects.get(email='owner@example.com')
        self.assertEqual(owner.role, UserRole.RESTAURANT_OWNER)

        # Verify Restaurant Ownership
        restaurant = Restaurant.objects.get(name='Test Restaurant')
        self.assertEqual(restaurant.owner, owner)

    def test_restaurant_owner_flow(self):
        """
        Test Restaurant Owner capabilities: Update Restaurant, Create Menu.
        """
        # 1. Setup: Create Owner and Restaurant
        owner = User.objects.create_user(
            email='owner2@example.com',
            password='ownerpassword',
            role=UserRole.RESTAURANT_OWNER
        )
        restaurant = Restaurant.objects.create(
            owner=owner,
            name='My Restaurant',
            description='Original Description'
        )

        # 2. Login as Owner
        self.client.force_authenticate(user=owner)

        # 3. Update Restaurant
        update_url = reverse('restaurants:restaurant-detail', kwargs={'pk': restaurant.id})
        update_data = {'description': 'Updated Description', 'name': 'My Restaurant'}
        response = self.client.put(update_url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        restaurant.refresh_from_db()
        self.assertEqual(restaurant.description, 'Updated Description')

        # 4. Create Menu
        menu_url = reverse('restaurants:menu-list')
        menu_data = {
            'name': 'Tasty Burger',
            'price': '12.99'
        }
        response = self.client.post(menu_url, menu_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Menu.objects.filter(name='Tasty Burger', restaurant=restaurant).exists())

    def test_admin_list_users_filter(self):
        """
        Test Admin can list users and filter by role.
        """
        self.client.force_authenticate(user=self.super_admin)

        # Create user to filter
        User.objects.create_user(email='user@example.com', password='password', role=UserRole.USER)
        User.objects.create_user(email='owner3@example.com', password='password', role=UserRole.RESTAURANT_OWNER)

        response = self.client.get(self.user_list_url, {'role': 'restaurant_owner'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        if 'results' in data:
             data = data['results']

        if len(data) != 1:
             # print(f"DEBUG: Found {len(data)} users: {data}")
             pass
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['email'], 'owner3@example.com')

    def test_permissions_enforcement(self):
        """
        Verify that non-admins cannot create users/restaurants.
        """
        # Create normal user
        user = User.objects.create_user(email='normal@example.com', password='password', role=UserRole.USER)
        self.client.force_authenticate(user=user)

        # Try to create restaurant with owner
        data = {
            'email': 'hacker@example.com',
            'password': 'password',
            'restaurant_name': 'Hacker Rest',
            'restaurant_description': '...'
        }
        response = self.client.post(self.create_restaurant_with_owner_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
