
from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'assigned_employee',
        'assigned_by',
        'priority',
        'status',
        'progress',
        'start_date',
        'due_date',
        'created_at',
    )

    list_filter = (
        'priority',
        'status',
        'start_date',
        'due_date',
        'created_at',
    )

    search_fields = (
        'title',
        'description',
        'assigned_to__employee_id',
        'assigned_to__user__username',
        'assigned_to__user__first_name',
        'assigned_to__user__last_name',
        'assigned_by__username',
    )

    ordering = ('-created_at',)

    readonly_fields = (
        'created_at',
        'updated_at',
        'completed_at',
    )

    fieldsets = (
        (
            'Task Information',
            {
                'fields': (
                    'title',
                    'description',
                )
            }
        ),

        (
            'Task Assignment',
            {
                'fields': (
                    'assigned_to',
                    'assigned_by',
                )
            }
        ),

        (
            'Task Progress',
            {
                'fields': (
                    'priority',
                    'status',
                    'progress',
                )
            }
        ),

        (
            'Task Schedule',
            {
                'fields': (
                    'start_date',
                    'due_date',
                    'completed_at',
                )
            }
        ),

        (
            'System Information',
            {
                'fields': (
                    'created_at',
                    'updated_at',
                ),
                'classes': ('collapse',)
            }
        ),
    )

    @admin.display(description='Employee')
    def assigned_employee(self, obj):
        employee_name = obj.assigned_to.user.get_full_name()

        return employee_name if employee_name else obj.assigned_to.user.username
