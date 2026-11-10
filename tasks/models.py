
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

from employees.models import Employee


class Task(models.Model):

    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        URGENT = 'URGENT', 'Urgent'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        ON_HOLD = 'ON_HOLD', 'On Hold'

    # Basic Task Information

    title = models.CharField(max_length=200)

    description = models.TextField()

    # Employee Assignment

    assigned_to = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='assigned_tasks'
    )

    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tasks'
    )

    # Task Priority and Status

    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    progress = models.PositiveSmallIntegerField(default=0)

    # Task Dates

    start_date = models.DateField()

    due_date = models.DateField()

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # System Information

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):

        super().clean()

        if (
            self.start_date
            and self.due_date
            and self.due_date < self.start_date
        ):
            raise ValidationError({
                'due_date': 'Due date cannot be earlier than the start date.'
            })

        if self.progress is not None and self.progress > 100:
            raise ValidationError({
                'progress': 'Progress cannot exceed 100%.'
            })

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        ordering = ['-created_at']
