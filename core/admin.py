from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # override what fields will show in the list of the users
    list_display = (
        'first_name',
        'last_name',
        'phone_number',
        'is_active',
        'is_staff',
    )

    # override ordering the users list
    ordering = ('first_name', 'last_name')

    # override what fields to show when click on a user 
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff',
         'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # override how to add a new user 
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'first_name', 'last_name', 'email', 'password1',
                       'password2', ),
        }),
    )

    # override search fields in the users list
    search_fields = ('phone_number', 'email')

    # override the filter side menu
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
