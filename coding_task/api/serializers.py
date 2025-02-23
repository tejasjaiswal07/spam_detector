from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from drf_spectacular.utils import extend_schema_field
from .models import UserProfile, Contact, SpamReport

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be in format: '+999999999'"
            )
        ]
    )
    name = serializers.CharField(max_length=100)
    password = serializers.CharField(
        write_only=True,
        min_length=6,
        style={'input_type': 'password'},
        validators=[
            RegexValidator(
                regex=r'^(?=.*[A-Za-z])(?=.*\d).{6,}$',
                message="Password must be at least 6 characters and contain both letters and numbers"
            )
        ]
    )
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = ['username', 'password', 'phone_number', 'name', 'email']
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'required': True}
        }

    def validate_phone_number(self, value):
        if UserProfile.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("This phone number is already registered")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken")
        return value

    def create(self, validated_data):
        phone_number = validated_data.pop('phone_number')
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            name=validated_data['name']
        )
        
        UserProfile.objects.create(
            user=user,
            phone_number=phone_number
        )
        return user

class ContactSerializer(serializers.ModelSerializer):
    spam_likelihood = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = ['id', 'name', 'phone_number', 'spam_likelihood', 'spam_reported']
        read_only_fields = ['spam_reported']

    @extend_schema_field(str)
    def get_spam_likelihood(self, obj) -> str:
        spam_count = SpamReport.objects.filter(phone_number=obj.phone_number).count()
        if spam_count > 5:
            return "Very High"
        elif spam_count > 2:
            return "High"
        elif spam_count > 0:
            return "Medium"
        return "Low"

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)

class SpamReportSerializer(serializers.ModelSerializer):
    reporter_username = serializers.CharField(source='reporter.username', read_only=True)

    class Meta:
        model = SpamReport
        fields = ['id', 'phone_number', 'timestamp', 'reporter_username']
        read_only_fields = ['timestamp', 'reporter_username']

class SearchResultSerializer(serializers.Serializer):
    name = serializers.CharField()
    phone_number = serializers.CharField()
    spam_likelihood = serializers.CharField()
    is_registered = serializers.BooleanField()
    contact_count = serializers.IntegerField()