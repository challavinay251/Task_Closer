from django import forms
from django.utils import timezone

from .models import Task
from employees.models import Employee


class TaskCreateForm(forms.ModelForm):

    class Meta:
        model = Task

        fields = [
            'title',
            'description',
            'assigned_to',
            'priority',
            'start_date',
            'due_date',
        ]

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter task title',
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe the task and its requirements',
                'rows': 5,
            }),

            'assigned_to': forms.Select(attrs={
                'class': 'form-select',
            }),

            'priority': forms.Select(attrs={
                'class': 'form-select',
            }),

            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),

            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
        }

        labels = {
            'title': 'Task Title',
            'description': 'Task Description',
            'assigned_to': 'Assign Employee',
            'priority': 'Task Priority',
            'start_date': 'Start Date',
            'due_date': 'Due Date',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['assigned_to'].queryset = (
            Employee.objects.filter(
                employment_status=Employee.EmploymentStatus.ACTIVE,
                user__is_active=True
            )
            .select_related('user')
            .order_by('user__first_name', 'user__username')
        )

        self.fields['assigned_to'].label_from_instance = (
            lambda employee: (
                f"{employee.user.get_full_name() or employee.user.username}"
                f" ({employee.employee_id})"
            )
        )

        self.fields['start_date'].initial = timezone.localdate()

        self.fields['due_date'].help_text = (
            'Select the deadline for completing this task.'
        )

    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get('start_date')
        due_date = cleaned_data.get('due_date')

        if start_date and due_date and due_date < start_date:
            self.add_error(
                'due_date',
                'Due date cannot be earlier than the start date.'
            )

        return cleaned_data
