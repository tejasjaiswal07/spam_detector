from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import UserProfile, Contact, SpamReport
from rest_framework import status

User = get_user_model()

class SearchTests(APITestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            password='Test123',
            name='John Doe'
        )
        self.profile1 = UserProfile.objects.create(
            user=self.user1,
            phone_number='+1234567890',
            email='john@example.com'
        )
        
        self.user2 = User.objects.create_user(
            username='testuser2',
            password='Test123',
            name='Johnny Smith'
        )
        self.profile2 = UserProfile.objects.create(
            user=self.user2,
            phone_number='+1234567891'
        )
        
        # Create contacts
        Contact.objects.create(
            owner=self.user1,
            name='John Wilson',
            phone_number='+1234567892'
        )
        Contact.objects.create(
            owner=self.user2,
            name='Johnson Brown',
            phone_number='+1234567893'
        )
        
        # Login test user
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser1',
            'password': 'Test123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_name_search_ordering(self):
        response = self.client.get('/api/search/?q=john&type=name')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        results = response.data
        self.assertTrue(len(results) >= 3)
        
        # Exact match should come first
        self.assertEqual(results[0]['name'], 'John Doe')
        
        # Names starting with 'John' should come before those containing 'john'
        john_start_count = len([r for r in results if r['name'].lower().startswith('john')])
        self.assertTrue(john_start_count >= 2)
    
    def test_phone_search_registered_user(self):
        response = self.client.get('/api/search/?q=+1234567890&type=phone')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        results = response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['phone_number'], '+1234567890')
        self.assertTrue(results[0]['is_registered'])
    
    def test_email_visibility(self):
        # Create a contact relationship
        Contact.objects.create(
            owner=self.user2,
            name='Test Contact',
            phone_number=self.profile1.phone_number
        )
        
        # Login as user2
        self.client.credentials()  # Clear previous credentials
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser2',
            'password': 'Test123'
        })
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Search for user1's number
        response = self.client.get(f'/api/search/?q={self.profile1.phone_number}&type=phone')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Email should be visible since user2 is in user1's contacts
        self.assertEqual(response.data[0]['email'], 'john@example.com')

class SpamTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='Test123',
            name='Test User'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            phone_number='+1234567890'
        )
        
        # Login
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'Test123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_spam_reporting(self):
        response = self.client.post('/api/spam-reports/', {
            'phone_number': '+9876543210'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_duplicate_reports(self):
        # First report
        self.client.post('/api/spam-reports/', {
            'phone_number': '+9876543210'
        })
        
        # Duplicate report
        response = self.client.post('/api/spam-reports/', {
            'phone_number': '+9876543210'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_spam_likelihood(self):
        # Create multiple spam reports
        test_number = '+9876543210'
        SpamReport.objects.create(reporter=self.user, phone_number=test_number)
        
        response = self.client.get('/api/search/?q=' + test_number + '&type=phone')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['spam_likelihood'], 'Medium') 