# admin page

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, Contact, SpamReport

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'get_phone_number', 'email', 'is_staff')
    
    def get_phone_number(self, obj):
        return obj.profile.phone_number if hasattr(obj, 'profile') else ''
    get_phone_number.short_description = 'Phone Number'

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'owner', 'spam_reported')
    search_fields = ('name', 'phone_number')
    list_filter = ('spam_reported',)

@admin.register(SpamReport)
class SpamReportAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'reporter', 'timestamp')
    search_fields = ('phone_number',)
    list_filter = ('timestamp',)

admin.site.register(User, CustomUserAdmin)