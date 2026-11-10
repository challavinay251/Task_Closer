
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    model = CustomUser

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'phone',
        'is_active',
        'is_staff',
    )

    list_filter = (
        'role',
        'is_active',
        'is_staff',
        'is_superuser',
    )

    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
        'phone',
    )

    ordering = ('username',)

    fieldsets = (
        ('Login Information', {
            'fields': (
                'username',
                'password',
            )
        }),

        ('Personal Information', {
            'fields': (
                'first_name',
                'last_name',
                'email',
                'phone',
                'profile_picture',
            )
        }),

        ('Role & Permissions', {
            'fields': (
                'role',
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),

        ('Account Information', {
            'fields': (
                'last_login',
            )
        }),
    )

    add_fieldsets = (
        ('Create User Account', {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'first_name',
                'last_name',
                'role',
                'phone',
                'profile_picture',
                'password1',
                'password2',
                'is_active',
                'is_staff',
            ),
        }),
    )

    filter_horizontal = (
        'groups',
        'user_permissions',
    )
