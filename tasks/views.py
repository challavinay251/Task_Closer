
from functools import wraps

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Task
from .forms import TaskCreateForm
from employees.models import Employee


def admin_required(view_func):

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):

        if request.user.role != 'ADMIN':
            messages.error(
                request,
                'You do not have permission to access this page.'
            )

            return redirect('dashboard:employee_dashboard')

        return view_func(request, *args, **kwargs)

    return wrapper


# =========================================
# ADMIN TASK LIST
# =========================================

@admin_required
def task_list(request):

    tasks = Task.objects.select_related(
        'assigned_to__user',
        'assigned_by'
    ).all()

    context = {
        'tasks': tasks,

        'total_tasks': tasks.count(),

        'pending_tasks': tasks.filter(
            status=Task.Status.PENDING
        ).count(),

        'in_progress_tasks': tasks.filter(
            status=Task.Status.IN_PROGRESS
        ).count(),

        'completed_tasks': tasks.filter(
            status=Task.Status.COMPLETED
        ).count(),
    }

    return render(
        request,
        'tasks/task_list.html',
        context
    )


# =========================================
# ADMIN CREATE TASK
# =========================================

@admin_required
def task_create(request):

    if request.method == 'POST':

        form = TaskCreateForm(
            request.POST
        )

        if form.is_valid():

            task = form.save(commit=False)

            task.assigned_by = request.user

            task.status = Task.Status.PENDING

            task.progress = 0

            task.save()

            messages.success(
                request,
                f'Task "{task.title}" assigned successfully.'
            )

            return redirect(
                'tasks:task_detail',
                pk=task.pk
            )

        messages.error(
            request,
            'Please correct the errors in the form.'
        )

    else:

        form = TaskCreateForm()

    context = {
        'form': form,
        'page_title': 'Create New Task',
        'button_text': 'Assign Task',
    }

    return render(
        request,
        'tasks/task_form.html',
        context
    )


# =========================================
# ADMIN TASK DETAILS
# =========================================

@admin_required
def task_detail(request, pk):

    task = get_object_or_404(
        Task.objects.select_related(
            'assigned_to__user',
            'assigned_by'
        ),
        pk=pk
    )

    context = {
        'task': task,
    }

    return render(
        request,
        'tasks/task_detail.html',
        context
    )


# =========================================
# EMPLOYEE TASK LIST
# =========================================

@login_required
def employee_task_list(request):

    if request.user.role != 'EMPLOYEE':
        return redirect('dashboard:admin_dashboard')

    employee = get_object_or_404(
        Employee,
        user=request.user
    )

    tasks = Task.objects.filter(
        assigned_to=employee
    ).select_related(
        'assigned_by'
    ).order_by('-created_at')

    context = {
        'tasks': tasks,

        'total_tasks': tasks.count(),

        'pending_tasks': tasks.filter(
            status=Task.Status.PENDING
        ).count(),

        'in_progress_tasks': tasks.filter(
            status=Task.Status.IN_PROGRESS
        ).count(),

        'completed_tasks': tasks.filter(
            status=Task.Status.COMPLETED
        ).count(),
    }

    return render(
        request,
        'tasks/employee_task_list.html',
        context
    )
