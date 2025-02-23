from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.contrib.auth import get_user_model
from django.db.models import F, Count, Q
from .models import SpamReport, UserProfile, Contact
from .serializers import (
    UserRegistrationSerializer, 
    ContactSerializer, 
    SpamReportSerializer,
    SearchResultSerializer
)
from drf_spectacular.utils import extend_schema, extend_schema_view

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user registration and management.
    
    register:
        Register a new user with required name and phone number.
        
        Parameters:
            - username: Unique username
            - password: Secure password (min 6 chars)
            - phone_number: Unique phone number in international format
            - name: User's full name
            - email: Optional email address
            
        Returns:
            201: User created successfully
            400: Validation errors
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]  
    http_method_names = ['post'] 
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'User registered successfully',
                'username': user.username
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema_view(
    list=extend_schema(description='List all contacts for the authenticated user'),
    create=extend_schema(description='Create a new contact'),
    retrieve=extend_schema(description='Get a specific contact by ID'),
    update=extend_schema(description='Update a contact'),
    destroy=extend_schema(description='Delete a contact')
)
class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Contact.objects.filter(owner=self.request.user)

@extend_schema_view(
    list=extend_schema(description='List all spam reports by the user'),
    create=extend_schema(description='Report a number as spam'),
    retrieve=extend_schema(description='Get a specific spam report by ID')
)
class SpamReportViewSet(viewsets.ModelViewSet):
    """
    API endpoint for spam reporting and checking.
    
    create:
        Report a phone number as spam.
        
        Parameters:
            - phone_number: The number to report
            
        Returns:
            201: Report created
            400: Already reported or invalid
    """
    serializer_class = SpamReportSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        return SpamReport.objects.filter(reporter=self.request.user)

    def create(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')
        
        
        if not phone_number:
            return Response(
                {'error': 'Phone number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

       
        if SpamReport.objects.filter(
            reporter=request.user,
            phone_number=phone_number
        ).exists():
            return Response(
                {'error': 'You have already reported this number'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            # Create spam report
            report = SpamReport.objects.create(
                reporter=request.user,
                phone_number=phone_number
            )

           
            Contact.objects.filter(phone_number=phone_number).update(
                spam_reported=True
            )

            
            UserProfile.objects.filter(phone_number=phone_number).update(
                spam_count=F('spam_count') + 1
            )

        serializer = self.get_serializer(report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class SearchView(generics.GenericAPIView):
    """
    API endpoint for searching the global database.
    
    To test this endpoint:
    1. First register a user:
       POST /api/auth/register/
       {
           "username": "testuser",
           "password": "Test123",
           "phone_number": "+1234567890",
           "name": "Test User"
       }
       
    2. Then login to get token:
       POST /api/auth/login/
       {
           "username": "testuser",
           "password": "Test123"
       }
       
    3. Use the access token in Authorization header:
       GET /api/search/?q=john&type=name
       Headers: {
           "Authorization": "Bearer <your_access_token>"
       }
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SearchResultSerializer

    def get(self, request):
        if not request.auth:
            return Response({
                'error': 'Authentication required',
                'instructions': 'Please login at /api/auth/login/ to get a token',
                'example': {
                    'login': {
                        'url': '/api/auth/login/',
                        'method': 'POST',
                        'body': {
                            'username': 'testuser',
                            'password': 'Test123'
                        }
                    },
                    'search': {
                        'url': '/api/search/?q=john&type=name',
                        'method': 'GET',
                        'headers': {
                            'Authorization': 'Bearer <your_access_token>'
                        }
                    }
                }
            }, status=status.HTTP_401_UNAUTHORIZED)

        query = request.query_params.get('q', '')
        search_type = request.query_params.get('type', 'name')

        if not query:
            return Response(
                {'error': 'Search query is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if search_type == 'phone':
            return self._search_by_phone(query)
        return self._search_by_name(query)

    def _search_by_name(self, query):
        # Search in both registered users and contacts
        user_results = UserProfile.objects.filter(
            user__name__icontains=query
        ).values('user__name', 'phone_number')
        
        contact_results = Contact.objects.filter(
            name__icontains=query
        ).values('name', 'phone_number')
        
        
        all_results = list(user_results) + list(contact_results)
        
        
        def sort_key(result):
            name = result.get('user__name') or result.get('name')
            if name.lower() == query.lower():
                return (0, name)
            elif name.lower().startswith(query.lower()):
                return (1, name)
            return (2, name)
        
        return sorted(all_results, key=sort_key)

    def _search_by_phone(self, query):
     
        try:
            user_profile = UserProfile.objects.get(phone_number=query)
           
            return Response([{
                'name': user_profile.user.name,
                'phone_number': query,
                'is_registered': True,
                'spam_likelihood': self._get_spam_likelihood(
                    SpamReport.objects.filter(phone_number=query).count()
                )
            }])
        except UserProfile.DoesNotExist:
            contacts = Contact.objects.filter(
                phone_number=query
            ).values('name', 'phone_number').annotate(
                contact_count=Count('name')  # Count how many users have this contact
            ).distinct()
            return Response(self._format_search_results(contacts))

    def _format_search_results(self, contacts):
        if not contacts:
            return Response({
                'message': 'No results found',
                'results': []
            }, status=status.HTTP_200_OK)
        
        results = []
        for contact in contacts:
           
            try:
                profile = UserProfile.objects.get(phone_number=contact['phone_number'])
                 
                email = None
                if Contact.objects.filter(
                    owner=profile.user,
                    phone_number=self.request.user.profile.phone_number
                ).exists():
                    email = profile.email
            except UserProfile.DoesNotExist:
                email = None

            results.append({
                'name': contact['name'],
                'phone_number': contact['phone_number'],
                'spam_likelihood': self._get_spam_likelihood(
                    SpamReport.objects.filter(phone_number=contact['phone_number']).count()
                ),
                'email': email,
                'is_registered': profile is not None if 'profile' in locals() else False,
                'contact_count': contact.get('contact_count', 1)
            })
        return results

    def _get_spam_likelihood(self, count: int) -> str:
        if count > 5:
            return "Very High"
        elif count > 2:
            return "High"
        elif count > 0:
            return "Medium"
        return "Low"

    def _get_email_if_allowed(self, user_profile, requesting_user):
        """Only show email if requesting user is in the person's contacts"""
        if Contact.objects.filter(
            owner=user_profile.user,
            phone_number=requesting_user.profile.phone_number
        ).exists():
            return user_profile.email
        return None