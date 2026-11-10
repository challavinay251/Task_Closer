from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

from employees.models import Employee
from tasks.models import Task


# ==========================================
# DAILY REPORT
# ==========================================

class DailyReport(models.Model):

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        SUBMITTED = 'SUBMITTED', 'Submitted'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        REVISION = 'REVISION', 'Revision Requested'

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='daily_reports'
    )

    report_date = models.DateField()

    summary = models.TextField(
        help_text='Summary of your work for the day.'
    )

    challenges = models.TextField(blank=True)

    pending_work = models.TextField(blank=True)

    tomorrow_plan = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    admin_feedback = models.TextField(blank=True)

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_daily_reports'
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    submitted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Daily Report'
        verbose_name_plural = 'Daily Reports'
        ordering = ['-report_date', '-created_at']

        constraints = [
            models.UniqueConstraint(
                fields=['employee', 'report_date'],
                name='unique_employee_daily_report'
            )
        ]

    def __str__(self):
        return f'{self.employee.employee_id} - {self.report_date}'


# ==========================================
# WORK ENTRY
# ==========================================

class WorkEntry(models.Model):

    daily_report = models.ForeignKey(
        DailyReport,
        on_delete=models.CASCADE,
        related_name='work_entries'
    )

    task = models.ForeignKey(
        Task,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_entries'
    )

    title = models.CharField(max_length=200)

    description = models.TextField()

    hours_spent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Task completion percentage reported by employee
    task_progress = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text='Current task completion percentage (0-100).'
    )

    video = models.FileField(
        upload_to='daily_reports/videos/',
        blank=True,
        null=True
    )

    display_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):

        super().clean()

        if self.hours_spent is not None and self.hours_spent < 0:
            raise ValidationError({
                'hours_spent': 'Hours spent cannot be negative.'
            })

        if self.task_progress is not None and self.task_progress > 100:
            raise ValidationError({
                'task_progress': 'Task progress cannot exceed 100%.'
            })

        if self.task_id and self.daily_report_id:

            if self.task.assigned_to_id != self.daily_report.employee_id:
                raise ValidationError({
                    'task': 'You can only select tasks assigned to this employee.'
                })

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Work Entry'
        verbose_name_plural = 'Work Entries'
        ordering = ['display_order', 'id']


# ==========================================
# WORK ENTRY IMAGES
# ==========================================

class WorkEntryImage(models.Model):

    work_entry = models.ForeignKey(
        WorkEntry,
        on_delete=models.CASCADE,
        related_name='images'
    )

    image = models.ImageField(
        upload_to='daily_reports/images/'
    )

    caption = models.CharField(
        max_length=200,
        blank=True
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Image for {self.work_entry.title}'

    class Meta:
        verbose_name = 'Work Entry Image'
        verbose_name_plural = 'Work Entry Images'
        ordering = ['uploaded_at']
