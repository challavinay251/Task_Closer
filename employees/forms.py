
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction

from .models import Employee


User = get_user_model()


# ==========================================
# EMPLOYEE CREATION FORM
# ==========================================

class EmployeeCreateForm(forms.Form):

    # User Account Information
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username'
        })
    )

    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter first name'
        })
    )

    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter last name'
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email address'
        })
    )

    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter phone number'
        })
    )

    profile_picture = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control'
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )

    # Employment Information
    employee_id = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter employee ID'
        })
    )

    department = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter department'
        })
    )

    designation = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter designation'
        })
    )

    manager = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        empty_label='Select reporting manager',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    gender = forms.ChoiceField(
        choices=[
            ('', 'Select gender'),
            *Employee.Gender.choices
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    date_of_joining = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter residential address'
        })
    )

    # ==========================================
    # INITIALIZE FORM
    # ==========================================

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['manager'].queryset = User.objects.filter(
            role=User.Role.ADMIN,
            is_active=True
        ).order_by('username')

    # ==========================================
    # VALIDATE USERNAME
    # ==========================================

    def clean_username(self):

        username = self.cleaned_data['username']

        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(
                'This username is already registered.'
            )

        return username

    # ==========================================
    # VALIDATE EMAIL
    # ==========================================

    def clean_email(self):

        email = self.cleaned_data['email']

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                'This email address is already registered.'
            )

        return email

    # ==========================================
    # VALIDATE EMPLOYEE ID
    # ==========================================

    def clean_employee_id(self):

        employee_id = self.cleaned_data['employee_id']

        if Employee.objects.filter(
            employee_id__iexact=employee_id
        ).exists():

            raise forms.ValidationError(
                'This employee ID already exists.'
            )

        return employee_id

    # ==========================================
    # VALIDATE PASSWORD
    # ==========================================

    def clean(self):

        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:

            if password != confirm_password:
                self.add_error(
                    'confirm_password',
                    'Passwords do not match.'
                )

            else:
                try:
                    validate_password(password)
                except forms.ValidationError as error:
                    self.add_error('password', error)

        return cleaned_data

    # ==========================================
    # CREATE EMPLOYEE ACCOUNT AND PROFILE
    # ==========================================

    @transaction.atomic
    def save(self):

        data = self.cleaned_data

        # Create Custom User Account
        user = User(
            username=data['username'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data.get('phone', ''),
            role=User.Role.EMPLOYEE,
            is_active=True
        )

        if data.get('profile_picture'):
            user.profile_picture = data['profile_picture']

        user.set_password(data['password'])
        user.save()

        # Create Employee Profile
        employee = Employee.objects.create(
            user=user,
            employee_id=data['employee_id'],
            department=data['department'],
            designation=data['designation'],
            manager=data.get('manager'),
            gender=data.get('gender', ''),
            date_of_birth=data.get('date_of_birth'),
            date_of_joining=data.get('date_of_joining'),
            address=data.get('address', ''),
            employment_status=Employee.EmploymentStatus.ACTIVE
        )

        return employee


# ==========================================
# EMPLOYEE UPDATE FORM
# ==========================================

class EmployeeUpdateForm(forms.ModelForm):

    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control'
        })
    )

    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    profile_picture = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control'
        })
    )

    class Meta:

        model = Employee

        fields = [
            'employee_id',
            'department',
            'designation',
            'manager',
            'gender',
            'date_of_birth',
            'date_of_joining',
            'address',
            'employment_status',
        ]

        widgets = {
            'employee_id': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'designation': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'manager': forms.Select(attrs={
                'class': 'form-select'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'date_of_joining': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'employment_status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    # ==========================================
    # INITIALIZE UPDATE FORM
    # ==========================================

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields['manager'].queryset = User.objects.filter(
            role=User.Role.ADMIN,
            is_active=True
        ).order_by('username')

        if self.instance and self.instance.pk:

            user = self.instance.user

            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            self.fields['phone'].initial = user.phone

    # ==========================================
    # VALIDATE EMAIL
    # ==========================================

    def clean_email(self):

        email = self.cleaned_data['email']

        existing_user = User.objects.filter(
            email__iexact=email
        ).exclude(pk=self.instance.user_id)

        if existing_user.exists():
            raise forms.ValidationError(
                'This email address is already registered.'
            )

        return email

    # ==========================================
    # SAVE EMPLOYEE AND USER INFORMATION
    # ==========================================

    @transaction.atomic
    def save(self, commit=True):

        employee = super().save(commit=False)

        user = employee.user

        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']

        if self.cleaned_data.get('profile_picture'):
            user.profile_picture = self.cleaned_data['profile_picture']

        if commit:
            user.save()
            employee.save()

        return employee


# ==========================================
# EMPLOYEE SELF PROFILE UPDATE FORM
# ==========================================

class EmployeeProfileForm(forms.ModelForm):

    # User Account Information
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter first name'
        })
    )

    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter last name'
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email address'
        })
    )

    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter phone number'
        })
    )

    profile_picture = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control'
        })
    )

    class Meta:
        model = Employee

        fields = [
            'gender',
            'date_of_birth',
            'address',
        ]

        widgets = {
            'gender': forms.Select(attrs={
                'class': 'form-select'
            }),

            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),

            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter your residential address'
            }),
        }

    # ==========================================
    # INITIALIZE FORM
    # ==========================================

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            user = self.instance.user

            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            self.fields['phone'].initial = user.phone

    # ==========================================
    # VALIDATE EMAIL
    # ==========================================

    def clean_email(self):

        email = self.cleaned_data['email']

        existing_user = User.objects.filter(
            email__iexact=email
        ).exclude(
            pk=self.instance.user_id
        )

        if existing_user.exists():
            raise forms.ValidationError(
                'This email address is already registered.'
            )

        return email

    # ==========================================
    # SAVE EMPLOYEE PROFILE
    # ==========================================

    @transaction.atomic
    def save(self, commit=True):

        employee = super().save(commit=False)

        user = employee.user

        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']

        profile_picture = self.cleaned_data.get('profile_picture')

        if profile_picture is False:
            user.profile_picture = None
        elif profile_picture:
            user.profile_picture = profile_picture

        if commit:
            user.save()
            employee.save()

        return employee
