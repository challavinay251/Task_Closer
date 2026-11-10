
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import Employee
from .forms import EmployeeCreateForm, EmployeeUpdateForm, EmployeeProfileForm


# ==========================================
# ADMIN ACCESS DECORATOR
# ==========================================

def admin_required(view_func):

    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect('accounts:login')

        if request.user.role != 'ADMIN':
            messages.error(
                request,
                'You do not have permission to access this page.'
            )

            return redirect('dashboard:employee_dashboard')

        return view_func(request, *args, **kwargs)

    return login_required(wrapper)


# ==========================================
# EMPLOYEE LIST
# ==========================================

@admin_required
def employee_list(request):

    employees = Employee.objects.select_related(
        'user',
        'manager'
    ).all()

    context = {
        'employees': employees,
        'total_employees': employees.count(),
        'active_employees': employees.filter(
            employment_status=Employee.EmploymentStatus.ACTIVE,
            user__is_active=True
        ).count(),
        'inactive_employees': employees.filter(
            employment_status=Employee.EmploymentStatus.INACTIVE
        ).count(),
    }

    return render(
        request,
        'employees/employee_list.html',
        context
    )


# ==========================================
# ADD EMPLOYEE
# ==========================================

@admin_required
def employee_create(request):

    if request.method == 'POST':

        form = EmployeeCreateForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            employee = form.save()

            messages.success(
                request,
                f'Employee {employee.user.username} created successfully.'
            )

            return redirect(
                'employees:employee_detail',
                pk=employee.pk
            )

        messages.error(
            request,
            'Please correct the errors in the form.'
        )

    else:

        form = EmployeeCreateForm()

    return render(
        request,
        'employees/employee_form.html',
        {
            'form': form,
            'page_title': 'Add New Employee',
            'button_text': 'Create Employee',
        }
    )


# ==========================================
# EMPLOYEE DETAILS
# ==========================================

@admin_required
def employee_detail(request, pk):

    employee = get_object_or_404(
        Employee.objects.select_related('user', 'manager'),
        pk=pk
    )

    return render(
        request,
        'employees/employee_detail.html',
        {
            'employee': employee
        }
    )


# ==========================================
# EDIT EMPLOYEE
# ==========================================

@admin_required
def employee_update(request, pk):

    employee = get_object_or_404(
        Employee.objects.select_related('user'),
        pk=pk
    )

    if request.method == 'POST':

        form = EmployeeUpdateForm(
            request.POST,
            request.FILES,
            instance=employee
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Employee information updated successfully.'
            )

            return redirect(
                'employees:employee_detail',
                pk=employee.pk
            )

        messages.error(
            request,
            'Please correct the errors in the form.'
        )

    else:

        form = EmployeeUpdateForm(
            instance=employee
        )

    return render(
        request,
        'employees/employee_form.html',
        {
            'form': form,
            'employee': employee,
            'page_title': 'Edit Employee',
            'button_text': 'Update Employee',
        }
    )


# ==========================================
# ACTIVATE / DEACTIVATE EMPLOYEE
# ==========================================

@admin_required
@require_POST
def employee_toggle_status(request, pk):

    employee = get_object_or_404(
        Employee.objects.select_related('user'),
        pk=pk
    )

    if employee.employment_status == Employee.EmploymentStatus.RESIGNED:

        messages.error(
            request,
            'Resigned employee accounts cannot be reactivated through this action.'
        )

        return redirect(
            'employees:employee_detail',
            pk=employee.pk
        )

    if employee.user.is_active:

        employee.user.is_active = False

        employee.employment_status = (
            Employee.EmploymentStatus.INACTIVE
        )

        status_message = 'Employee account deactivated successfully.'

    else:

        employee.user.is_active = True

        employee.employment_status = (
            Employee.EmploymentStatus.ACTIVE
        )

        status_message = 'Employee account activated successfully.'

    employee.user.save(update_fields=['is_active'])

    employee.save(update_fields=[
        'employment_status',
        'updated_at'
    ])

    messages.success(
        request,
        status_message
    )

    return redirect(
        'employees:employee_detail',
        pk=employee.pk
    )


# ==========================================
# EMPLOYEE MY PROFILE
# ==========================================

@login_required
def employee_profile(request):

    # Allow only employee accounts
    if request.user.role != 'EMPLOYEE':
        messages.error(
            request,
            'You do not have permission to access this page.'
        )
        return redirect('dashboard:admin_dashboard')

    # Get only the logged-in employee's profile
    employee = get_object_or_404(
        Employee.objects.select_related('user', 'manager'),
        user=request.user
    )

    if request.method == 'POST':

        form = EmployeeProfileForm(
            request.POST,
            request.FILES,
            instance=employee
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Your profile has been updated successfully.'
            )

            return redirect('employees:employee_profile')

        messages.error(
            request,
            'Please correct the errors in the form.'
        )

    else:

        form = EmployeeProfileForm(
            instance=employee
        )

    return render(
        request,
        'employees/employee_profile.html',
        {
            'employee': employee,
            'form': form,
        }
    )

