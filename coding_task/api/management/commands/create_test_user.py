from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from coding_task.api.models import UserProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates a test user for API testing'

    def handle(self, *args, **options):
        
        UserProfile.objects.filter(phone_number='+1234567890').delete()
        
        User.objects.filter(username='testuser').delete()
        
        try:
            # Create new test user
            user = User.objects.create_user(
                username='testuser',
                password='Test123',
                name='Test User'
            )
            
            UserProfile.objects.create(
                user=user,
                phone_number='+1234567890'
            )
            
            self.stdout.write(self.style.SUCCESS('''
Test user created successfully!

Use these credentials to test the API:
Username: testuser
Password: Test123

1. Get token:
   curl -X POST http://127.0.0.1:8000/api/auth/login/ \\
        -H "Content-Type: application/json" \\
        -d '{"username":"testuser","password":"Test123"}'

2. Use token for search:
   curl http://127.0.0.1:8000/api/search/?q=john&type=name \\
        -H "Authorization: Bearer <your_access_token>"
'''))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating test user: {str(e)}')) 