from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class User(AbstractUser):
    name = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return self.username

class UserProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='profile'
    )
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number format: '+999999999'. Max 15 digits."
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=10,
        unique=True
    )
    email = models.EmailField(blank=True, null=True)
    spam_count = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} ({self.phone_number})"

    class Meta:
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['email'])
        ]

class Contact(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='contacts'
    )
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=17) 
    spam_reported = models.BooleanField(default=False)

    @property
    def spam_likelihood(self):
        total_users = UserProfile.objects.count()
        if total_users == 0:
            return "Low"
        
        spam_reports = SpamReport.objects.filter(
            phone_number=self.phone_number
        ).count()
        
        spam_percentage = (spam_reports / total_users) * 100
        
        if spam_percentage > 30:
            return "Very High"
        elif spam_percentage > 15:
            return "High"
        elif spam_percentage > 5:
            return "Medium"
        return "Low"

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['owner', 'phone_number'])
        ]
        unique_together = ['owner', 'phone_number']

class SpamReport(models.Model):
    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reported_spams'
    )
    phone_number = models.CharField(max_length=17)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['reporter', 'phone_number'])
        ]
        unique_together = ['reporter', 'phone_number']