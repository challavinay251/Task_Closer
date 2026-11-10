
from django import forms
from django.forms import inlineformset_factory

from .models import DailyReport, WorkEntry, WorkEntryImage
from tasks.models import Task


# ==========================================
# DAILY REPORT FORM
# ==========================================

class DailyReportForm(forms.ModelForm):

    class Meta:
        model = DailyReport

        fields = (
            'report_date',
            'summary',
            'challenges',
            'pending_work',
            'tomorrow_plan',
        )

        widgets = {
            'report_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),

            'summary': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Summarize the work completed today...',
                'rows': 4,
            }),

            'challenges': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Mention any challenges faced today...',
                'rows': 3,
            }),

            'pending_work': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Mention any pending work...',
                'rows': 3,
            }),

            'tomorrow_plan': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your plan for tomorrow...',
                'rows': 3,
            }),
        }


# ==========================================
# WORK ENTRY FORM
# ==========================================

class WorkEntryForm(forms.ModelForm):

    class Meta:
        model = WorkEntry

        fields = (
            'task',
            'title',
            'description',
            'hours_spent',
            'task_progress',
            'video',
        )

        widgets = {

            'task': forms.Select(attrs={
                'class': 'form-select',
            }),

            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter work activity title',
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe the work completed...',
                'rows': 3,
            }),

            'hours_spent': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Hours spent',
                'min': '0',
                'step': '0.25',
            }),

            'task_progress': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter progress percentage (0-100)',
                'min': '0',
                'max': '100',
                'step': '1',
            }),

            'video': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'video/*',
            }),
        }

    def __init__(self, *args, employee=None, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields['task'].required = False
        self.fields['task_progress'].required = False

        self.fields['task'].queryset = Task.objects.none()

        if employee:

            self.fields['task'].queryset = (
                Task.objects.filter(
                    assigned_to=employee
                ).order_by('-created_at')
            )

    def clean_task_progress(self):

        progress = self.cleaned_data.get('task_progress')

        if progress is not None and not 0 <= progress <= 100:
            raise forms.ValidationError(
                'Progress must be between 0 and 100%.'
            )

        return progress


# ==========================================
# WORK ENTRY IMAGE FORM
# ==========================================

class WorkEntryImageForm(forms.ModelForm):

    class Meta:
        model = WorkEntryImage

        fields = (
            'image',
            'caption',
        )

        widgets = {

            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),

            'caption': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional image description',
            }),
        }


# ==========================================
# WORK ENTRY FORMSET
# ==========================================

WorkEntryFormSet = inlineformset_factory(
    DailyReport,
    WorkEntry,
    form=WorkEntryForm,
    extra=1,
    can_delete=True,
    max_num=20,
    validate_max=True,
)
