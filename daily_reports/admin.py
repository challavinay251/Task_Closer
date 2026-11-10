
from django.contrib import admin

from .models import DailyReport, WorkEntry, WorkEntryImage


# ==========================================
# WORK ENTRY IMAGE INLINE
# ==========================================

class WorkEntryImageInline(admin.TabularInline):

    model = WorkEntryImage

    extra = 1

    fields = (
        'image',
        'caption',
        'uploaded_at',
    )

    readonly_fields = (
        'uploaded_at',
    )


# ==========================================
# WORK ENTRY INLINE
# ==========================================

class WorkEntryInline(admin.TabularInline):

    model = WorkEntry

    extra = 0

    show_change_link = True

    fields = (
        'title',
        'task',
        'hours_spent',
        'task_progress',
        'video',
        'display_order',
    )

    readonly_fields = ()


# ==========================================
# DAILY REPORT ADMIN
# ==========================================

@admin.register(DailyReport)
class DailyReportAdmin(admin.ModelAdmin):

    list_display = (
        'employee_name',
        'employee_id',
        'report_date',
        'status',
        'reviewed_by',
        'submitted_at',
    )

    search_fields = (
        'employee__user__username',
        'employee__user__first_name',
        'employee__user__last_name',
        'employee__employee_id',
        'summary',
    )

    list_filter = (
        'status',
        'report_date',
    )

    ordering = (
        '-report_date',
        '-created_at',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
        'submitted_at',
        'reviewed_at',
    )

    inlines = (
        WorkEntryInline,
    )

    fieldsets = (

        ('Employee Information', {
            'fields': (
                'employee',
                'report_date',
            )
        }),

        ('Daily Work Summary', {
            'fields': (
                'summary',
                'challenges',
                'pending_work',
                'tomorrow_plan',
            )
        }),

        ('Review Information', {
            'fields': (
                'status',
                'admin_feedback',
                'reviewed_by',
                'reviewed_at',
                'submitted_at',
            )
        }),

        ('System Information', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),

    )

    @admin.display(description='Employee')
    def employee_name(self, obj):

        full_name = obj.employee.user.get_full_name()

        return full_name or obj.employee.user.username

    @admin.display(description='Employee ID')
    def employee_id(self, obj):

        return obj.employee.employee_id


# ==========================================
# WORK ENTRY ADMIN
# ==========================================

@admin.register(WorkEntry)
class WorkEntryAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'daily_report',
        'task',
        'hours_spent',
        'task_progress',
        'image_count',
        'created_at',
    )

    search_fields = (
        'title',
        'description',
        'daily_report__employee__user__username',
        'daily_report__employee__employee_id',
    )

    list_filter = (
        'created_at',
    )

    ordering = (
        '-created_at',
    )

    inlines = (
        WorkEntryImageInline,
    )

    @admin.display(description='Images')
    def image_count(self, obj):

        return obj.images.count()


# ==========================================
# WORK ENTRY IMAGE ADMIN
# ==========================================

@admin.register(WorkEntryImage)
class WorkEntryImageAdmin(admin.ModelAdmin):

    list_display = (
        'work_entry',
        'caption',
        'uploaded_at',
    )

    search_fields = (
        'work_entry__title',
        'caption',
    )

    ordering = (
        '-uploaded_at',
    )
