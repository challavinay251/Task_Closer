
from django.contrib import admin
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):

    # ==========================================
    # EMPLOYEE LIST DISPLAY
    # ==========================================

    list_display = (
        'employee_id',
        'employee_name',
        'department',
        'designation',
        'manager',
        'employment_status',
        'date_of_joining',
    )

    # ==========================================
    # SEARCH
    # ==========================================

    search_fields = (
        'employee_id',
        'user__username',
        'user__first_name',
        'user__last_name',
        'user__email',
        'department',
        'designation',
    )

    # ==========================================
    # FILTERS
    # ==========================================

    list_filter = (
        'employment_status',
        'department',
        'designation',
        'gender',
    )

    # ==========================================
    # ORDERING
    # ==========================================

    ordering = ('employee_id',)

    # ==========================================
    # READ-ONLY FIELDS
    # ==========================================

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    # ==========================================
    # FIELD ORGANIZATION
    # ==========================================

    fieldsets = (

        ('User Account', {
            'fields': (
                'user',
                'employee_id',
            )
        }),

        ('Employment Information', {
            'fields': (
                'department',
                'designation',
                'manager',
                'employment_status',
                'date_of_joining',
            )
        }),

        ('Personal Information', {
            'fields': (
                'gender',
                'date_of_birth',
                'address',
            )
        }),

        ('System Information', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),

    )

    # ==========================================
    # CUSTOM EMPLOYEE NAME
    # ==========================================

    @admin.display(description='Employee Name')
    def employee_name(self, obj):

        full_name = obj.user.get_full_name()

        return full_name if full_name else obj.user.username
