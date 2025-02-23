from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
import random
from api.models import UserProfile, Contact, SpamReport

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Populates database with realistic sample data'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=100)
        parser.add_argument('--contacts', type=int, default=500)
        parser.add_argument('--spam', type=int, default=200)

    def handle(self, *args, **options):
        self.create_users(options['users'])
        self.create_contacts(options['contacts'])
        self.create_spam_reports(options['spam'])

    def create_users(self, count):
        for _ in range(count):
            try:
                user = User.objects.create_user(
                    username=fake.unique.user_name(),
                    password='testpass123'
                )
                UserProfile.objects.create(
                    user=user,
                    name=fake.name(),
                    phone_number=f'+91{fake.msisdn()[3:]}',
                    email=fake.email() if random.random() > 0.3 else None
                )
            except Exception as e:
                print(f"Error creating user: {e}")

    def create_contacts(self, count):
        users = list(User.objects.all())
        
        phone_numbers = [f'+91{fake.msisdn()[3:]}' for _ in range(count//2)]
        
        for _ in range(count):
            owner = random.choice(users)
            
            phone_number = random.choice(phone_numbers) if random.random() > 0.5 else f'+91{fake.msisdn()[3:]}'
            
            Contact.objects.create(
                owner=owner,
                name=fake.name(),
                phone_number=phone_number,
                spam_reported=random.random() > 0.8
            )

    def create_spam_reports(self, count):
        users = list(User.objects.all())
        numbers = list(
            Contact.objects.values_list('phone_number', flat=True).distinct()
        ) + [p.phone_number for p in UserProfile.objects.all()]
        
        for _ in range(count):
            SpamReport.objects.create(
                reporter=random.choice(users),
                phone_number=random.choice(numbers)
            )